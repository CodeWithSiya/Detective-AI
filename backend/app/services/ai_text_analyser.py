from abc import ABC
from .ai_analyser import AiAnalyser
from app.ai.ai_text_model import AiTextModel
from app.ai.ai_short_text_model import AiShortTextModel
from app.services.claude_service import ClaudeService
from app.models.text_analysis_result import TextAnalysisResult
from app.models.text_submission import TextSubmission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from typing import Any, Dict, Optional
import time
import re

class AiTextAnalyser(AiAnalyser):
    """
    Service class for AI text analysis logic.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025 
    """ 

    def __init__(self, ai_model: Optional[AiTextModel] = None, use_claude: bool = True):
        """
        Create an instance of the AI Text Analyser with dual model support.

        :param ai_model: The base AI text detection model (optional for backward compatibility)
        :param use_claude: Whether to use Claude or not.
        """
        # Initialize both models - ai_model parameter is now optional
        self.long_text_model = ai_model if ai_model is not None else AiTextModel()
        self.short_text_model = AiShortTextModel()
        
        # Pass the long_text_model to parent for backward compatibility
        super().__init__(self.long_text_model)
        
        self.use_claude = use_claude
        self.short_text_threshold = 50  # Character threshold for model selection

        # Initialize Claude service
        self.claude_service = None
        if use_claude:
            try:
                self.claude_service = ClaudeService()
            except ValueError:
                print("Warning: Claude API key not found. Enhanced analysis disabled.")
                self.use_claude = False

    def analyse(self, input_data: Any, user=None, submission=None) -> Dict[str, Any]:
        """
        Perform analysis using the appropriate AI model based on text length.
        
        :param input_data: Text content to analyse
        :param user: User instance (None for users without an account)
        :param submission: Related submission object (Optional)
        :return: Analysis results
        """
        # Start timing
        start_time = time.time()
        analysis_result = None

        try: 
            # Preprocess input.
            processed_text = self.preprocess(input_data)

            # Select appropriate model based on text length.
            selected_model, model_type = self._select_model(processed_text)

            # Ensure selected model is loaded.
            if not selected_model.is_loaded():
                selected_model.load()

            # Get base model prediction from selected model
            base_prediction = selected_model.predict(processed_text)

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

            # Add statistics to result.
            final_result['statistics'] = self.calculate_statistics(processed_text, enhanced_analysis)

            # Add model selection metadata
            final_result['metadata']['model_used'] = model_type
            final_result['metadata']['text_length'] = len(processed_text.strip())
            final_result['metadata']['threshold'] = self.short_text_threshold

            # Calculate and add processing time to results.
            end_time = time.time()
            processing_time_ms = (end_time - start_time) * 1000
            final_result['metadata']['processing_time_ms'] = round(processing_time_ms, 2)

            # Save analysis result for registered users.
            if user and user.is_authenticated:
                print("User is authenticated so we are saving their result!")
                analysis_result = self._save_analysis_result(final_result, user, submission, processed_text, processing_time_ms)

            # Add analysis info to result if saved successfully.
            if analysis_result:
                final_result['analysis_id'] = str(analysis_result.id)

            return final_result

        except Exception as e:
            # Handle analysis failure.
            print(f"Analysis failed: {e}")

            # If we have a user and started creating an analysis, mark it as failed.
            if user and user.is_authenticated and analysis_result:
                try:
                    analysis_result.status = TextAnalysisResult.Status.FAILED
                    analysis_result.completed_at = timezone.now()
                    analysis_result.calculate_processing_time()
                    analysis_result.save()
                except Exception as save_error:
                    print(f"Failed to mark analysis as failed: {save_error}")

            # Re-raise the exception so the view can handle it.
            raise
    
    def _select_model(self, text: str):
        """
        Select appropriate model based on text length.
        
        :param text: Input text
        :return: Selected model instance and model type
        """
        text_length = len(text.strip())
        if text_length <= self.short_text_threshold:
            return self.short_text_model, "short_text"
        else:
            return self.long_text_model, "long_text"
    
    def _save_analysis_result(self, result: Dict[str, Any], user, submission, text: str, processing_time_ms: float):
        """
        Save analysis result to database for registered users.

        :param result: Analysis result
        :param user: User instance
        :param submission: Related submission object
        :param text: Analysed text
        :param processing_time_ms: Processing time in milliseconds
        :return: Created TextAnalysisResult instance or None
        """
        analysis = None
        try:
            # Create submission if it doesn't exist.
            if submission is None and self.claude_service is not None:
                # Generate a smart name using Claude.
                try:
                    submission_name = self.claude_service.create_text_submission_name(text, max_length=50)
                except Exception:
                    # Fallback to date-based name if Claude fails
                    submission_name = f"Text Analysis {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"

                # Create a new TextSubmission for this analysis.
                submission = TextSubmission.objects.create(
                    name=submission_name,
                    content=text,
                    user=user
                )

            # Get content type for the submission.
            content_type = ContentType.objects.get_for_model(submission)
            
            # Create initial TextAnalysisResult instance with PENDING status initially.
            analysis = TextAnalysisResult(
                content_type=content_type,
                object_id=submission.id,
                status=TextAnalysisResult.Status.PENDING
            )
            analysis.save()
            
            # Save the analysis result with a COMPLETED status.
            analysis.save_analysis_result(result)
            analysis.save()
            
            print(f"Saved analysis result {analysis.id} for user {user.email} (processed in {processing_time_ms:.2f}ms)")
            return analysis
        
        except Exception as e:
            # Log error but don't fail the analysis
            print(f"Failed to save analysis result: {e}")

            # If we created an analysis object, mark it as failed.
            if analysis is not None:
                try:
                    analysis.status = TextAnalysisResult.Status.FAILED
                    analysis.completed_at = timezone.now()
                    analysis.calculate_processing_time()
                    analysis.save()
                except Exception as save_error:
                    print(f"Failed to mark analysis as failed: {save_error}")

            return None

    def preprocess(self, raw_input: Any = None, image_path: Any = None) -> Any:
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
    
    def calculate_statistics(self, text: str, enhanced_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate basic text statistics for analysis.

        :param text: The text to analyse.
        :return: Dictionary containing text statistics.
        """
        if not text or not text.strip():
            return {
                'total_words': 0,
                'sentences': 0,
                'avg_sentence_length': 0,
                'ai_keywords_count': 0,
                'transition_words_count': 0,
                'corporate_jargon_count': 0,
                'buzzwords_count': 0,
                'suspicious_patterns_count': 0,
                'human_indicators_count': 0
            }

        # Basic text processing
        words = [word for word in re.split(r'\s+', text) if len(word) > 0]
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
        # Calculate basic statistics
        total_words = len(words)
        sentence_count = len(sentences)
        avg_sentence_length = total_words / sentence_count if sentence_count > 0 else 0

        # Extract counts from enhanced analysis 
        ai_keywords_count = 0
        transition_words_count = 0
        corporate_jargon_count = 0
        buzzwords_count = 0
        suspicious_patterns_count = 0
        human_indicators_count = 0

        if enhanced_analysis and enhanced_analysis.get('analysis_details'):
            analysis_details = enhanced_analysis['analysis_details']
            
            # Count items from Claude's analysis
            ai_keywords_count = len(analysis_details.get('found_keywords', []))
            transition_words_count = len(analysis_details.get('found_transitions', []))
            corporate_jargon_count = len(analysis_details.get('found_jargon', []))
            buzzwords_count = len(analysis_details.get('found_buzzwords', []))
            suspicious_patterns_count = len(analysis_details.get('found_patterns', []))
            human_indicators_count = len(analysis_details.get('found_human_indicators', []))

        # Calculate statistics
        total_words = len(words)
        sentence_count = len(sentences)

        # Calculate averages (handle division by zero)
        avg_sentence_length = total_words / sentence_count if sentence_count > 0 else 0

        return {
            'total_words': total_words,
            'sentences': sentence_count,
            'avg_sentence_length': round(avg_sentence_length, 2),
            'ai_keywords_count': ai_keywords_count,
            'transition_words_count': transition_words_count,
            'corporate_jargon_count': corporate_jargon_count,
            'buzzwords_count': buzzwords_count,
            'suspicious_patterns_count': suspicious_patterns_count,
            'human_indicators_count': human_indicators_count
        }