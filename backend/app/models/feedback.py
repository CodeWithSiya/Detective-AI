from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import uuid

User = get_user_model()

class Feedback(models.Model):
    """
    Class which represents user feedback for an analysis.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025
    """ 
    # Feedback Rating Choices.
    class FeedbackRating(models.TextChoices):
        THUMBS_UP = "THUMBS_UP", "Thumbs Up"
        THUMBS_DOWN = "THUMBS_DOWN", "Thumbs Down"

    # Feedback Status Choices.
    class FeedbackStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        REVIEWED = 'REVIEWED', 'Reviewed' 
        RESOLVED = 'RESOLVED', 'Resolved'

    # Defining fields for the feedback.
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the feedback."
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='feedback',
        help_text="User who provided the feedback."
    )
    rating = models.CharField(
        max_length=15,
        choices=FeedbackRating.choices,
        help_text="User's rating for the AI analysis result."
    )
    comment = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Optional comment about the analysis result."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the feedback was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the feedback was last updated."
    )

    # Admin fields.
    status = models.CharField(
        max_length=20,
        choices=FeedbackStatus.choices,
        default=FeedbackStatus.PENDING
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Generic relation to any submission type.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    analysis_result = GenericForeignKey('content_type', 'object_id')

    # Defining metadata for the feedback table.
    class Meta:
        db_table = 'feedback'
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["rating"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["status"]), 
        ]
        # Ensure one feedback per user per analysis result.
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"],
                name="unique_feedback_per_user_analysis"
            )
        ]

    def mark_as_resolved(self) -> None:
        """
        Mark feedback as resolved by an admin user.
        """
        self.status = self.FeedbackStatus.RESOLVED
        self.resolved_at = timezone.now()
        self.save(update_fields=['status', 'resolved_at'])

    def mark_as_reviewed(self) -> None:
        """
        Mark feedback as reviewed by an admin user.
        """
        self.status = self.FeedbackStatus.REVIEWED
        self.save(update_fields=['status'])

    @property
    def is_reviewed(self) -> bool:
        """Check if feedback is reviewed."""
        return self.status == self.FeedbackStatus.REVIEWED

    @property
    def is_resolved(self) -> bool:
        """Check if feedback is resolved."""
        return self.status == self.FeedbackStatus.RESOLVED

    @property
    def is_pending(self) -> bool:
        """Check if feedback is pending."""
        return self.status == self.FeedbackStatus.PENDING

    def __str__(self) -> str:
        """
        Returns a string representation of this feedback.
        """
        return f"{self.user.username} | {self.rating} | {self.created_at}"