from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Submission(models.Model):
    """
    Class which represents a general user submission for AI content detection.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025
    """
    # Definining fields for the submission.
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the user."
    )
    name = models.CharField(
      max_length=150,
      blank=True, 
      help_text="Name for the submission"
    )
    user = models.ForeignKey(
       User,
       on_delete=models.CASCADE,
       related_name="submissions",
       help_text="User who made this submission."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the submission was "
    )
    
    class Meta:
        abstract = True

    def __str__(self) -> str:
        """
        Returns a String representation of this submission.
        """
        return f"{self.name} | {self.user.email} | {self.created_at}"