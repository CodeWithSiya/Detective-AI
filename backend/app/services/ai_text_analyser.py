from abc import ABC
from .ai_analyser import AiAnalyser
from app.ai.ai_text_model import AiTextModel
from typing import Any, Dict

class AiTextAnalyser(AiAnalyser):
    """
    Service class for AI text analysis business logic.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025 
    """ 

    def __init__(self, ai_model: AiTextModel):
        """
        Create an instance of the AI Text Analyser.
        """
        super().__init__(ai_model)
        self.ai_model: AiTextModel = ai_model 

    def analyse(self, input_data: Any) -> Dict[str, Any]:
        """
        Perform analysis using the AI model to detect AI generated content.
        
        :param input_data: Text content to analyse
        """
        # Ensure model is loaded.
        if not self.ai_model.is_loaded():
            self.ai_model.load()

        # Preprocess input.
        processed_text = self.preprocess(input_data)

        # Get model prediction.
        prediction = self.ai_model.predict(processed_text)

        # Postprocess results.
        return self.postprocess(prediction)

    def preprocess(self, raw_input: Any) -> Any:
        """Preprocess text input for analysis."""
        return raw_input

    def postprocess(self, model_output: Any) -> Dict[str, Any]:
        """Format text analysis results into structured JSON."""
        return model_output