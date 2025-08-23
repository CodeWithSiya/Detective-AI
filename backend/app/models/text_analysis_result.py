from django.db import models
from .analysis_result import AnalysisResult

class TextAnalysisResult(AnalysisResult):
    """
    Class which represents the result of an detection analysis on a user’s text submission.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025
    """
    # Defining text specific analysis fields.
    flagged_content = models.JSONField(
        default=list,
        blank=True,
        help_text="List of content flagged as potentially AI-generated."
    ) 

    # Defining metadata for the text analysis table.
    class Meta(AnalysisResult.Meta):
        db_table  = "text_analysis_results" 
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["detection_result"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        """
        Returns a string representation of this text analysis result.
        """
        return f"Text Analysis {self.id} | {self.status} | {self.detection_result}"
    
    @property
    def has_flagged_content(self) -> bool:
        """
        Check if any content was flagged for being potentially AI-generated.
        """
        return bool(self.flagged_content)
    
    def add_flagged_content(self, content: str, start_pos: int, end_pos: int, confidence: float, reason: str) -> None:
        """
        Add flagged content to the analysis result.
        """
        flagged_item = {
            "text": content,
            "start_position": start_pos,
            "end_position": end_pos,
            "confidence": confidence,
            "reason": reason
        }
        if not self.flagged_content:
            self.flagged_content = []
        self.flagged_content.append(flagged_item)