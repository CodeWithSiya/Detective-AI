from abc import ABC, abstractmethod
from typing import Any, Dict

class AiModel(ABC):
    """
    Abstract base class for AI models using Hugging Face.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025 
    """
    
    def __init__(self, model_name: str, device: str):
        """Create an instance of the AI model."""
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None

    @abstractmethod
    def load(self) -> None:
        """Load the model and tokenizer."""
        pass
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded or not."""
        return self.model is not None and self.tokenizer is not None
    
    def unload(self) -> None:
        """Unload the model and tokenizer to free memory."""
        self.model = None
        self.tokenizer = None
    
    def get_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "loaded": self.is_loaded()
        }