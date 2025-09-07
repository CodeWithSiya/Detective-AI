from django.db import models
from django.utils import timezone
from .analysis_result import AnalysisResult

class TextAnalysisResult(AnalysisResult):
    """
    Class which represents the result of an detection analysis on a user’s text submission.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025
    """    
    # Enhanced analysis results
    detection_reasons = models.JSONField(
        default=list,
        blank=True,
        help_text="List of detection reasons from Claude analysis"
    )

    # Enhanced analysis metadata
    enhanced_analysis_used = models.BooleanField(
        default=False,
        help_text="Whether Claude enhanced analysis was used"
    )

    analysis_details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detailed analysis including found patterns, keywords, etc."
    )
    
    # Text statistics
    statistics = models.JSONField(
        default=dict,
        blank=True,
        help_text="Text statistics (word count, sentences, AI patterns, etc.)"
    )

    # Defining metadata for the text analysis table.
    class Meta(AnalysisResult.Meta):
        db_table = "text_analysis_results" 
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["detection_result"]),
            models.Index(fields=["probability"]),
            models.Index(fields=["enhanced_analysis_used"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        """
        Returns a string representation of this text analysis result.
        """
        return f"Text Analysis {self.id} | {self.status} | {self.detection_result} | {self.probability:.3f}"
    
    @property
    def has_flagged_content(self) -> bool:
        """
        Check if any content was flagged for being potentially AI-generated.
        """
        return len(self.detection_reasons) > 0
    
    @property
    def ai_indicators_count(self) -> int:
        """
        Get total count of AI indicators found.
        """
        if not self.statistics:
            return 0
        return (
            self.statistics.get('ai_keywords_count', 0) +
            self.statistics.get('transition_words_count', 0) +
            self.statistics.get('corporate_jargon_count', 0) +
            self.statistics.get('buzzwords_count', 0) +
            self.statistics.get('suspicious_patterns_count', 0)
        )
    
    def save_analysis_result(self, analysis_result: dict) -> None:
        """
        Save the complete analysis result to the model.

        :param analysis_result: The result from AiTextAnalyser.analyse()
        """
        if not analysis_result:
            raise ValueError("Analysis result cannot be empty")

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
        
        # Save analysis data
        analysis = analysis_result.get('analysis', {})
        self.detection_reasons = analysis.get('detection_reasons', [])
        self.analysis_details = analysis.get('analysis_details', {})
        
        # Save statistics
        self.statistics = analysis_result.get('statistics', {})
        
        # Save metadata and processing time
        metadata = analysis_result.get('metadata', {})
        self.enhanced_analysis_used = metadata.get('enhanced_analysis_used', False)
        self.processing_time_ms = metadata.get('processing_time_ms')

        # Set status to completed
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()