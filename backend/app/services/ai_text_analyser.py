from abc import ABC
from .ai_analyser import AiAnalyser
from app.ai.ai_text_model import AiTextModel
from app.services.claude_service import ClaudeService
from typing import Any, Dict, Optional

class AiTextAnalyser(AiAnalyser):
    """
    Service class for AI text analysis logic.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025 
    """ 

    def __init__(self, ai_model: AiTextModel, use_claude: bool = True):
        """
        Create an instance of the AI Text Analyser.

        :param ai_model: The base AI text detection model
        :param use_claude: Whether to use Claude or not.
        """
        super().__init__(ai_model)
        self.ai_model: AiTextModel = ai_model 
        self.use_claude = use_claude

        # Initialise Claude service if API key is available.
        self.claude_service = None
        if use_claude:
            try:
                self.claude_service = ClaudeService()
            except ValueError:
                print("Warning: Claude API key not found. Enhanced analysis disabled.")
                self.use_claude = False

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

        # Get base model prediction.
        base_prediction = self.ai_model.predict(processed_text)

        # Enhanced analysis with Claude if available.
        enhanced_analysis = None
        if self.use_claude and self.claude_service:
            try:
                enhanced_analysis = self.claude_service.analyse_text_patterns(
                    processed_text, base_prediction
                )
            except Exception as e:
                print(f"Claude analysis failed: {e}")

        # Combine results.
        final_result = self.postprocess(base_prediction, enhanced_analysis)

        return final_result

    def preprocess(self, raw_input: Any) -> Any:
        """
        Preprocess text input for analysis.
        
        :param raw_input: Raw text input
        :return: Cleaned text
        """
        # Basic text cleaning
        text = raw_input.strip()
        # Remove excessive whitespace
        text = ' '.join(text.split())
        return text

    def postprocess(self, model_output: Any, enhanced_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format text analysis results into structured JSON.
        
        :param model_output: Basic model prediction results
        :param enhanced_analysis: Claude enhanced analysis results
        :return: Combined formatted results
        """
        # Extract basic model results
        probability = float(model_output.get('probability', 0.0))
        is_ai_generated = bool(model_output.get('is_ai_generated', False))
        confidence = float(model_output.get('confidence', 0.0))
        
        # Base result structure
        result = {
            'prediction': {
                'is_ai_generated': is_ai_generated,
                'probability': round(probability, 3),
                'confidence': round(confidence, 3)
            },
            'analysis': {
                'detection_reasons': [],
                'analysis_details': {
                    'found_keywords': [],
                    'found_patterns': [],
                    'found_transitions': [],
                    'found_jargon': [],
                    'found_buzzwords': [],
                    'found_human_indicators': []
                }
            },
            'metadata': {
                'enhanced_analysis_used': bool(enhanced_analysis and enhanced_analysis.get('detection_reasons')),
                'model_threshold': 0.5
            }
        }
        
        # Merge enhanced analysis if available
        if enhanced_analysis and enhanced_analysis.get('detection_reasons'):
            # Update detection reasons from Claude
            result['analysis']['detection_reasons'] = enhanced_analysis.get('detection_reasons', [])
            
            # Update analysis details from Claude
            claude_details = enhanced_analysis.get('analysis_details', {})
            result['analysis']['analysis_details'].update(claude_details)
        else:
            # Provide basic analysis based on model output only
            if is_ai_generated:
                reason_type = 'critical' if probability > 0.8 else 'warning'
                impact = 'High' if probability > 0.8 else 'Medium'
                
                result['analysis']['detection_reasons'].append({
                    'type': reason_type,
                    'title': 'AI Content Detected',
                    'description': f'Model detected AI-generated content with {probability:.1%} confidence',
                    'impact': impact
                })
            else:
                result['analysis']['detection_reasons'].append({
                    'type': 'success',
                    'title': 'Human Content Detected',
                    'description': f'Content appears to be human-written with {1 - probability:.1%} confidence',
                    'impact': 'Positive'
                })
        
        return result