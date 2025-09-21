from django.db import models
from django.utils import timezone
from .analysis_result import AnalysisResult

class ImageAnalysisResult(AnalysisResult):
    """
    Class which represents the result of an detection analysis on a user’s image submission.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025
    """ 

    # Enhanced analysis metadata.
    enhanced_analysis_used = models.BooleanField(
        default=False,
        help_text="Whether enhanced visual analysis (Claude) was used"
    )

    analysis_details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detailed analysis including detection reasons and Claude explanation"
    )

    # Defining metadata for the image analysis table.
    class Meta(AnalysisResult.Meta):
        db_table = "image_analysis_results"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["detection_result"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["enhanced_analysis_used"]),
        ]

    def __str__(self) -> str:
        """
        Returns a string representation of this image analysis result.
        """
        return f"Image Analysis {self.id} | {self.status} | {self.detection_result} | {self.probability:.3f}"
    
    @property
    def has_claude_explanation(self) -> bool:
        """
        Check if Claude provided an explanation.
        """
        return bool(self.analysis_details.get('explanation', '').strip())
    
    @property
    def explanation(self) -> str:
        """
        Get the Claude explanation from analysis details.
        """
        return self.analysis_details.get('explanation', '')
    
    def save_analysis_result(self, analysis_result: dict) -> None:
        """
        Save the complete analysis result to the model.

        :param analysis_result: The result from AiImageAnalyser.analyse()
        """
        if not analysis_result:
            raise ValueError("Analysis result cannot be empty")

        try:
            # Save prediction data
            prediction = analysis_result.get('prediction', {})
            self.probability = prediction.get('probability', 0.0) 
            self.confidence = prediction.get('confidence', 0.0)
            
            # Map is_ai_generated to detection_result choices
            is_ai_generated = prediction.get('is_ai_generated', False)
            if is_ai_generated:
                self.detection_result = self.DetectionResult.AI_GENERATED
            else:
                self.detection_result = self.DetectionResult.HUMAN_WRITTEN
            
            # Save analysis data (simplified for image analysis)
            analysis = analysis_result.get('analysis', {})
            self.analysis_details = {
                'explanation': analysis.get('explanation', '')
            }
            
            # Save metadata and processing time
            metadata = analysis_result.get('metadata', {})
            self.enhanced_analysis_used = metadata.get('enhanced_analysis_used', False)
            self.processing_time_ms = metadata.get('processing_time_ms')

            # Set status to completed
            self.status = self.Status.COMPLETED
            self.completed_at = timezone.now()
            
        except Exception as e:
            # If something goes wrong, mark as failed
            self.status = self.Status.FAILED
            self.completed_at = timezone.now()
            print(f"Error saving image analysis result: {e}")
            raise