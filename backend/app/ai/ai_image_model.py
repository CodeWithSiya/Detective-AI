#type:ignore
import torch
import torch.nn.functional as F  
from torchvision import transforms
from PIL import Image
from timm import create_model
from huggingface_hub import hf_hub_download
from typing import Any, Optional, Dict, Tuple
from threading import Lock
from functools import lru_cache
import hashlib
import os
from .ai_model import AiModel

class AiImageModel(AiModel):
    """
    Image analysis model for AI generated content.

    Adapted from: https://huggingface.co/Dafilab/ai-image-detector

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025
    """

    _instance = None
    _lock = Lock()

    def __new__(cls, model_name: str = "Dafilab/ai-image-detector", device: Optional[str] = None):
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
                    cls._instance = super(AiImageModel, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, model_name: str = "Dafilab/ai-image-detector", device: Optional[str] = None):
        """
        Initialize the AI image analysis model (only once).

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
        self.img_size = 380
        self.threshold = 0.5
        self.label_mapping = {1: "human", 0: "ai"}
        self._initialized = True

    @classmethod
    def get_instance(cls, model_name: str = "Dafilab/ai-image-detector", device: Optional[str] = None):
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
            # Clear the cache before resetting instance
            if cls._instance is not None and hasattr(cls._instance, '_cached_predict'):
                cls._instance._cached_predict.cache_clear()
            cls._instance = None

    def load(self) -> None:
        """
        Load the image analysis model and preprocessing transforms.
        """
        try:
            # Download model from HuggingFace Hub.
            model_path = hf_hub_download(repo_id=self.model_name, filename="pytorch_model.pth")
            
            # Create preprocessing transforms.
            self.tokenizer = transforms.Compose([
                transforms.Resize(self.img_size + 20),
                transforms.CenterCrop(self.img_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            
            # Load the EfficientNet model.
            self.model = create_model('efficientnet_b4', pretrained=False, num_classes=2)
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.to(torch.device(self.device))
            self.model.eval()

        except Exception as e:
            raise RuntimeError(f"Failed to load model {self.model_name}: {str(e)}")
    
    @property
    def transform(self):
        """
        Access transforms through tokenizer property for consistency with base class.
        """
        return self.tokenizer
         
    def _get_image_hash(self, image_path: str) -> str:
        """
        Generate hash for image file to use in caching.
        
        :param image_path: Path to image file
        :return: SHA256 hash of image file
        """
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
                return hashlib.sha256(image_data).hexdigest()
        except Exception:
            # Fallback to path-based hash if file reading fails
            return hashlib.sha256(image_path.encode('utf-8')).hexdigest()
        
    @lru_cache(maxsize=128) 
    def _cached_predict(self, image_hash: str, image_path: str) -> Tuple[str, float, bool]:
        """
        Internal cached prediction method.
        Uses image hash as first parameter to ensure cache uniqueness.
        
        :param image_hash: SHA256 hash of the image (for cache key)
        :param image_path: Path to image file
        :return: Tuple of (label, confidence, is_ai_generated)
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load() first.")
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Load and preprocess image
        try:
            img = Image.open(image_path).convert("RGB")
            img_tensor = self.transform(img).unsqueeze(0).to(self.device)
        except Exception as e:
            raise ValueError(f"Failed to process image {image_path}: {str(e)}")
        
        # Perform prediction
        with torch.no_grad():
            logits = self.model(img_tensor)
            probs = F.softmax(logits, dim=1)  # Use F.softmax instead of torch.nn.functional.softmax
            predicted_class = torch.argmax(probs, dim=1).item()
            confidence = probs[0, predicted_class].item()
        
        label = self.label_mapping[predicted_class]
        is_ai_generated = predicted_class == 0  # 0 = ai, 1 = human
        
        return label, confidence, is_ai_generated
    
    def predict(self, image_path: str) -> Dict[str, Any]:
        """
        Predict whether an image is AI-generated or human-created.

        :param image_path: Path to image file to analyse
        :return: Dictionary containing prediction results
        """
        # Generate hash for caching
        image_hash = self._get_image_hash(image_path)
        
        # Get cached result
        label, confidence, is_ai_generated = self._cached_predict(image_hash, image_path)
        
        # Calculate probability (confidence adjusted based on prediction)
        probability = confidence if is_ai_generated else (1 - confidence)
        
        # Standardized return structure matching text model
        return {
            'probability': probability,
            'is_ai_generated': is_ai_generated,
            'confidence': confidence,
            # Optional metadata
            'metadata': {
                'label': label,
                'prediction_class': 0 if is_ai_generated else 1
            }
        }
    
    def clear_cache(self):
        """
        Clear the prediction cache.
        """
        if hasattr(self, '_cached_predict'):
            self._cached_predict.cache_clear()