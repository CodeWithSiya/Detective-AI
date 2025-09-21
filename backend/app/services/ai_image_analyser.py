from typing import Any, Dict, Optional
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.utils import timezone
from app.models.image_submission import ImageSubmission
from app.models.image_analysis_result import ImageAnalysisResult
from app.ai.ai_image_model import AiImageModel
from app.services.claude_service import ClaudeService
from .ai_analyser import AiAnalyser
import os
import time
from PIL import Image

class AiImageAnalyser(AiAnalyser):
    """
    Service class for AI text analysis logic.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025 
    """ 

    def __init__(self, ai_model: AiImageModel, use_claude: bool = True):
        """
        Create an instance of the AI Image Analyser.

        :param ai_model: The image model used to analyse.
        :param use_claude: Whether to use Claude for enhanced analysis.
        """
        super().__init__(ai_model)
        self.ai_model: AiImageModel = ai_model
        self.use_claude = use_claude

        # Initialise Claude service if API key is available.
        self.claude_service = None
        if use_claude:
            try:
                self.claude_service = ClaudeService()
            except ValueError:
                print("Warning: Claude API key not found. Enhanced analysis disabled.")
                self.use_claude = False

        if not ai_model.is_loaded():
            ai_model.load()

    def analyse(self, input_data: str, user: Optional[User] = None, submission: Optional[ImageSubmission] = None) -> Dict[str, Any]:
        """
        Perform analysis using the AI model to detect AI generated content.

        :param input_data: Path to image file to analyze
        :param user: Optional authenticated user
        :param submission: Optional submission record
        :return: Analysis results
        """
        # Start timing
        start_time = time.time()
        analysis_result = None

        try:
            # Ensure model is loaded.
            if not self.ai_model.is_loaded():
                self.ai_model.load()

            # Preprocess input.
            processed_path = self.preprocess(image_path=input_data)  # Fixed: was "input"

            # Perform AI detection.
            base_prediction = self.ai_model.predict(processed_path)

            # Enhanced analysis with Claude if available
            enhanced_analysis = None
            if self.use_claude and self.claude_service:
                try:
                    enhanced_analysis = self.claude_service.analyse_image_patterns(
                        processed_path, base_prediction
                    )
                except Exception as e:
                    print(f"Claude image analysis failed: {e}")

            # Post-process results.
            final_result = self.postprocess(base_prediction, enhanced_analysis)

            # Calculate and add processing time.
            end_time = time.time()
            processing_time_ms = (end_time - start_time) * 1000
            final_result['metadata']['processing_time_ms'] = round(processing_time_ms, 2)

            # Save analysis result for registered users.
            if user and user.is_authenticated:
                print("User is authenticated so we are saving their result!")
                analysis_result = self._save_analysis_result(final_result, user, submission, processed_path, processing_time_ms)

            # Add analysis info to result if saved successfully
            if analysis_result:
                final_result['analysis_id'] = str(analysis_result.id)

            return final_result
        
        except Exception as e:
            # Handle analysis failure
            print(f"Image analysis failed: {e}")
            
            # If we have a user and started creating an analysis, mark it as failed
            if user and user.is_authenticated and analysis_result:
                try:
                    analysis_result.status = ImageAnalysisResult.Status.FAILED
                    analysis_result.completed_at = timezone.now()
                    analysis_result.save()
                except Exception as save_error:
                    print(f"Failed to mark analysis as failed: {save_error}")
            
            # Re-raise the exception so the view can handle it
            raise

    def _save_analysis_result(self, result: Dict[str, Any], user, submission, image_path: str, processing_time_ms: float):
        """
        Save analysis result to database for registered users.

        :param result: Analysis result
        :param user: User instance
        :param submission: Related submission object
        :param image_path: Path to analyzed image
        :param processing_time_ms: Processing time in milliseconds
        :return: Created ImageAnalysisResult instance or None
        """
        analysis = None
        try:
            # Create submission if it doesn't exist
            if submission is None and self.claude_service is not None:
                # Generate a smart name using Claude or fallback
                try:
                    submission_name = self.claude_service.create_image_submission_name(image_path, max_length=50)
                except Exception:
                    # Fallback to filename-based name
                    filename = os.path.basename(image_path)
                    submission_name = f"Image Analysis - {filename}"

                # Create a new ImageSubmission for this analysis
                submission = ImageSubmission.objects.create(
                    name=submission_name,
                    user=user
                )

                # Save the image file to Supabase storage.
                with open(image_path, 'rb') as f:
                    filename = os.path.basename(image_path)
                    submission.image.save(filename, File(f), save=True)

            # Get content type for the submission
            content_type = ContentType.objects.get_for_model(submission)
            
            # Create initial ImageAnalysisResult instance
            analysis = ImageAnalysisResult(
                content_type=content_type,
                object_id=submission.id,
                status=ImageAnalysisResult.Status.PENDING
            )
            analysis.save()
            
            # Save the analysis result
            analysis.save_analysis_result(result)
            analysis.save()
            
            print(f"Saved image analysis result {analysis.id} for user {user.email} (processed in {processing_time_ms:.2f}ms)")
            print(f"Image stored at: {submission.image.url}")
            return analysis
        
        except Exception as e:
            print(f"Failed to save image analysis result: {e}")

            # If we created an analysis object, mark it as failed
            if analysis is not None:
                try:
                    analysis.status = ImageAnalysisResult.Status.FAILED
                    analysis.completed_at = timezone.now()
                    analysis.save()
                except Exception as save_error:
                    print(f"Failed to mark analysis as failed: {save_error}")

            return None
    
    def preprocess(self, raw_input: Any = None, image_path: Any = None) -> str:
        """
        Preprocess image input for analysis.
        
        :param image_path: Path to image file
        :return: Processed image path or processed image data
        """
        # Validate image exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Validate image format
        try:
            with Image.open(image_path) as img:
                # Ensure image is in supported format
                if img is not None and img.format and img.format.lower() not in ['jpeg', 'jpg', 'png']:
                    raise ValueError(f"Unsupported image format: {img.format}")
                
        except Exception as e:
            raise ValueError(f"Invalid image file: {e}")
        
        return image_path
    
    def postprocess(self, model_output: Any, enhanced_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format image analysis results into structured JSON.
        
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
                'explanation': '' 
            },
            'metadata': {
                'enhanced_analysis_used': bool(enhanced_analysis and enhanced_analysis.get('explanation')),
                'model_threshold': 0.5
            }
        }

        # Add Claude's explanation if available
        if enhanced_analysis and enhanced_analysis.get('explanation'):
            result['analysis']['explanation'] = enhanced_analysis.get('explanation')
        else:
            # Provide basic explanation based on model output
            if is_ai_generated:
                result['analysis']['explanation'] = f"The model detected this image as AI-generated with {probability:.1%} confidence. This suggests the image may have been created using artificial intelligence tools."
            else:
                result['analysis']['explanation'] = f"The model indicates this image appears to be human-created with {1 - probability:.1%} confidence. The image shows characteristics typical of traditional photography or artwork."
        
        return result