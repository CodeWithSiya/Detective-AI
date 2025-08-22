from abc import ABC, abstractmethod
from app.ai.ai_model import AiModel
from typing import Any, Dict

class AiAnalyser(ABC):
    """
    Abstract service class for AI analysis business logic.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025 
    """

    def __init__(self, ai_model: AiModel):
        """
        Create an instance of the AI Analyser.

        :param ai_model: The model used to analyse.
        """
        self.ai_model = ai_model

    @abstractmethod
    def analyse(self, input_data: Any) -> Dict[str, Any]:
        """Perform analysis using the AI model."""
        pass

    @abstractmethod
    def preprocess(self, raw_input: Any) -> Any:
        """Preprocess input for analysis."""
        pass

    @abstractmethod
    def postprocess(self, model_output: Any) -> Dict[str, Any]:
        """Format analysis results into structured JSON."""
        pass