import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoConfig, AutoModel, PreTrainedModel
from typing import Any, Optional, Dict
from .ai_model import AiModel

class DetectionModel(PreTrainedModel):
    """
    Desklib Detection Transformer Implementation.

    Adapted From: https://github.com/desklib/ai-text-detector

    This model wraps a Hugging Face transformer and adds:
    - Mean pooling to create sentence-level embeddings
    - A binary classifier head for AI-generated vs human text.
    """
    # Automatically configure the transformer model.
    config_class = AutoConfig

    def __init__(self, config):
        """
        Initialise the detection model instance.

        :param config: Transformer configuration object.
        """
        super().__init__(config)

        # Initialise the base transformer model.
        self.model = AutoModel.from_config(config)
        
        # Define a classifier head.
        self.classifier = nn.Linear(config.hidden_size, 1)

        # Initialise weights (handled by PreTrainedModel).
        self.init_weights()

    def forward(self, input_ids, attention_mask, labels = None):
        """
        Perform a forward pass through the transformer.

        :param input_ids: Token IDs of shape [batch_size, seq_len].
        :param attention_mask: Mask tensor of shape [batch_size, seq_len].
        :param labels: Optional ground-truth labels [batch_size].
        :return: Dictionary with logits and optional loss.
        """
        # Pass inputs through the pretrained transformer.
        outputs = self.model(input_ids, attention_mask=attention_mask)
        last_hidden_state = outputs[0]

        # Mean pooling (convert sequence embeddings into a fixed size vector).
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
        sum_embeddings = torch.sum(last_hidden_state * input_mask_expanded, dim=1)
        sum_mask = torch.clamp(input_mask_expanded.sum(dim=1), min=1e-9)
        pooled_output = sum_embeddings / sum_mask

        # Classification layer.
        logits = self.classifier(pooled_output)

        loss = None
        if labels is not None:
            # Binary Cross-Entropy Error with Logits.
            loss_fct = nn.BCEWithLogitsLoss()
            loss = loss_fct(logits.view(-1), labels.float())

        # Prepare output dictionary.
        output = {"logits": logits}
        if loss is not None:
            output["loss"] = loss
        return output

class AiTextModel(AiModel):
    """
    Text analysis model for AI generated content.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025
    """

    def __init__(self, model_name: str = "desklib/ai-text-detector-v1.01", device: Optional[str] = None):
        """
        Create an instance of the AI text analysis model.

        :param model_name: Hugging Face model name
        :param device: "cpu" or "cuda". Defaults to GPU if available.
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        super().__init__(model_name = model_name, device = device)

        self.device = device  
        self.threshold = 0.5
        
    def load(self) -> None:
        """
        Load the text model and tokenizer.
        """
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = DetectionModel.from_pretrained(self.model_name)
            self.max_length = min(self.tokenizer.max_length, 1024) # TODO: Find out max length of the model we will use.
            self.model.to(torch.device(self.device)) # type: ignore
            self.model.eval()

        except Exception as e:
            raise RuntimeError(f"Failed to load model {self.model_name}: {str(e)}")
        
    def predict(self, text: str) -> Dict[str, Any]:
        """
        :param text: Input text to analyse.
        :return: Dictionary containing probability and prediction
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load() first.")
        
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

        return {
            'probability': probability,
            'is_ai_generated': is_ai_generated,
            'confidence': confidence
        }