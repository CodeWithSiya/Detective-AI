from django.db import models
from .submission import Submission

class TextSubmission(Submission):
    """
    Class which represents a user's text submission for AI content detection.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025
    """
    # Definining fields for the text submission.
    content = models.TextField(
        max_length=5000,
        help_text="The text content submitted for AI detection analysis."
    )
    character_count = models.PositiveIntegerField(
        null = True,
        blank= True,
        help_text="Number of characters in the submission."
    )

    # Defining metadata for the text submission table.
    class Meta(Submission.Meta):
        db_table = "text_submissions"
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

    def save(self, *args, **kwargs) -> None:
        """
        Auto-calculate metadata when saving.
        """
        if self.content:
            # Get the character count.
            self.character_count = len(self.content)
        
        # Save the text submission.
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Obtain a string representation of this Text Submission.
        """
        return f"{self.name} | {self.user.email} | {self.character_count}"