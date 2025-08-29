from django.db import models
from .analysis_result import AnalysisResult

class ImageAnalysisResult(AnalysisResult):
    """
    Class which represents the result of an detection analysis on a user’s image submission.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025
    """ 
    # Defining metadata for the image analysis table.
    class Meta(AnalysisResult.Meta):
        db_table = "image_analysis_results"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["detection_result"]),
            models.Index(fields=["created_at"])
        ]

    def __str__(self) -> str:
        """
        Returns a string representation of this image analysis result.
        """
        return f"Image Analysis {self.id} | {self.status} | {self.detection_result}"