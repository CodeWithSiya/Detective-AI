import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoConfig, AutoModel, PreTrainedModel
from typing import Any, Optional, Dict, Tuple
from threading import Lock
from functools import lru_cache
import hashlib
from .ai_model import AiModel

class ShortTextDetectionModel(PreTrainedModel):
    """
    Custom model optimized for short text AI detection (5-30 characters).
    
    Uses attention pooling and multi-head attention for better feature extraction
    from limited context in very short texts.
    """
    config_class = AutoConfig

    def __init__(self, config):
        """
        Initialize the short text detection model.
        
        :param config: Transformer configuration object
        """
        super().__init__(config)
        
        # Base transformer model.
        self.backbone = AutoModel.from_pretrained("distilbert-base-uncased")
        hidden_size = self.backbone.config.hidden_size

        # Attention pooling layer for weighted token representation.
        self.attention_pooling = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.Tanh(),
            nn.Linear(hidden_size // 2, 1)
        )

        # Multi-head attention for capturing different feature aspects.
        self.multi_head_attention = nn.MultiheadAttention(
            embed_dim=hidden_size,
            num_heads=8,
            dropout=0.1,
            batch_first=True
        )

        # Feature extraction layers with normalization and dropout.
        self.feature_extractor = nn.Sequential(
            nn.Linear(hidden_size * 2, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.LayerNorm(hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
        )

        # Binary classification head.
        self.classifier = nn.Linear(hidden_size // 2, 1)
        self.init_weights()

    def attention_pool(self, hidden_states, attention_mask):
        """
        Apply attention pooling to create weighted representation.
        
        :param hidden_states: Token representations [batch_size, seq_len, hidden_size]
        :param attention_mask: Padding mask [batch_size, seq_len]
        :return: Pooled representation [batch_size, hidden_size]
        """
        attention_weights = self.attention_pooling(hidden_states)
        attention_weights = attention_weights.squeeze(-1)
        attention_weights = attention_weights.masked_fill(~attention_mask.bool(), -1e9)
        attention_weights = torch.nn.functional.softmax(attention_weights, dim=-1)
        pooled = torch.sum(hidden_states * attention_weights.unsqueeze(-1), dim=1)
        return pooled

    def forward(self, input_ids, attention_mask, labels=None):
        """
        Forward pass through the short text model.
        
        :param input_ids: Token IDs [batch_size, seq_len]
        :param attention_mask: Attention mask [batch_size, seq_len]
        :param labels: Optional labels for training [batch_size]
        :return: Dictionary with logits and optional loss
        """
        # Pass through backbone transformer.
        outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        hidden_states = outputs.last_hidden_state

        # Attention pooling for weighted representation.
        attention_pooled = self.attention_pool(hidden_states, attention_mask)

        # Multi-head attention for CLS-like representation.
        attn_output, _ = self.multi_head_attention(
            hidden_states, hidden_states, hidden_states,
            key_padding_mask=~attention_mask.bool()
        )
        cls_representation = attn_output[:, 0, :]

        # Combine representations and extract features.
        combined_features = torch.cat([attention_pooled, cls_representation], dim=-1)
        features = self.feature_extractor(combined_features)
        logits = self.classifier(features).squeeze(-1)

        # Compute loss if labels provided.
        loss = None
        if labels is not None:
            loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, labels.float())

        return {"loss": loss, "logits": logits}

class AiShortTextModel(AiModel):
    """
    Short text analysis model for AI generated content (5-30 characters).
    Implemented as a thread-safe singleton with LRU caching for Django applications.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 24/09/2025
    """
    
    _instance = None
    _lock = Lock()

    def __new__(cls, model_name: str = "CodeWithSiya/short-text-model", device: Optional[str] = None):
        """
        Create or return the singleton instance.
        
        :param model_name: Hugging Face model name
        :param device: "cpu" or "cuda". Defaults to GPU if available.
        :return: Singleton instance
        """
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern.
                if cls._instance is None:
                    cls._instance = super(AiShortTextModel, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = "CodeWithSiya/short-text-model", device: Optional[str] = None):
        """
        Initialize the AI short text analysis model (only once).

        :param model_name: Hugging Face model name
        :param device: "cpu" or "cuda". Defaults to GPU if available.
        """
        # Prevent re-initialization of the singleton instance.
        if self._initialized:
            return
            
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        super().__init__(model_name=model_name, device=device)

        self.device = device  
        self.threshold = 0.5
        self.max_length = 128  # Shorter max length for efficiency.
        self._initialized = True
        
    @classmethod
    def get_instance(cls, model_name: str = "CodeWithSiya/short-text-model", device: Optional[str] = None):
        """
        Alternative method to get the singleton instance.
        
        :param model_name: Hugging Face model name
        :param device: "cpu" or "cuda". Defaults to GPU if available.
        :return: Singleton instance
        """
        return cls(model_name=model_name, device=device)
    
    @classmethod
    def reset_instance(cls):
        """
        Reset the singleton instance.
        """
        with cls._lock:
            # Clear the cache before resetting instance.
            if cls._instance is not None and hasattr(cls._instance, '_cached_predict'):
                cls._instance._cached_predict.cache_clear()
            cls._instance = None
        
    def load(self) -> None:
        """
        Load the short text model and tokenizer.
        """
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = ShortTextDetectionModel.from_pretrained(self.model_name)
            self.model.to(torch.device(self.device))  # type: ignore
            self.model.eval()

        except Exception as e:
            raise RuntimeError(f"Failed to load short text model {self.model_name}: {str(e)}")

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for consistent caching.
        
        :param text: Input text
        :return: Normalized text
        """
        # Strip whitespace and normalize newlines for consistent caching.
        return text.strip().replace('\r\n', '\n').replace('\r', '\n')

    @lru_cache(maxsize=512)
    def _cached_predict(self, text_hash: str, text: str) -> Tuple[float, bool, float]:
        """
        Internal cached prediction method.
        Uses text hash as first parameter to ensure cache uniqueness.
        
        :param text_hash: SHA256 hash of the text (for cache key)
        :param text: Input text to analyse
        :return: Tuple of (probability, is_ai_generated, confidence)
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load() first.")
        
        # Perform prediction
        encoded = self.tokenizer(
            text,
            padding='max_length',
            truncation=True,
            max_length=self.max_length,
            return_tensors='pt'
        )

        input_ids = encoded['input_ids'].to(self.device)
        attention_mask = encoded['attention_mask'].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs["logits"]
            probability = torch.sigmoid(logits).item()

        is_ai_generated = probability >= self.threshold
        confidence = probability if is_ai_generated else (1 - probability)

        return probability, is_ai_generated, confidence

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predict if short text is AI-generated.
        
        :param text: Input text to analyse (optimized for 5-30 characters)
        :return: Dictionary containing probability and prediction
        """
        # Normalize text for consistent results
        normalized_text = self._normalize_text(text)
        
        # Create hash for caching
        text_hash = hashlib.sha256(normalized_text.encode('utf-8')).hexdigest()
        
        # Get cached result
        probability, is_ai_generated, confidence = self._cached_predict(text_hash, normalized_text)
        
        return {
            'probability': probability,
            'is_ai_generated': is_ai_generated,
            'confidence': confidence
        }
    
    def clear_cache(self):
        """
        Clear the prediction cache.
        """
        if hasattr(self, '_cached_predict'):
            self._cached_predict.cache_clear()