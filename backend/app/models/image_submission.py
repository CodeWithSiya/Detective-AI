from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.module_loading import import_string
from django.core.files.storage import default_storage
from django.contrib.auth import get_user_model
from typing import Optional
from PIL import Image
from .submission import Submission
from django.utils import timezone
import os

User = get_user_model()

def image_upload_path(instance, filename: str) -> str:
    """
    Generate upload path for image submissions.
    
    :param instance: The ImageSubmission model instance.
    :param filename: Filename of the uploaded file.
    :return: Upload path string
    """
    # Clean filename and get extension
    name, ext = os.path.splitext(filename)
    clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    
    # Use current time if created_at is not set yet.
    timestamp = instance.created_at if instance.created_at else timezone.now()
    
    return f"submissions/images/{instance.user.id}/{timestamp.strftime('%Y/%m')}/{clean_name}{ext}"

class ImageSubmission(Submission):
    """
    Class which represents a user's image submission for AI content detection.
    - Accepted Formats: .jpeg, .jpg, .png

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025
    """ 
    # File extension validator
    file_extension_validator = FileExtensionValidator(
        allowed_extensions=["jpg", "jpeg", "png"]
    )

    # Image file field
    image = models.ImageField(
        upload_to=image_upload_path,
        validators=[file_extension_validator],
        help_text="Image file for AI detection analysis. Supported formats: JPG, JPEG, PNG."
    )

    # Image-specific metadata
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes."
    )
    user = models.ForeignKey(
       User,
       on_delete=models.CASCADE,
       related_name="image_submissions",
       help_text="User who made this submission."
    )
    width = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Image width in pixels."
    )
    height = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Image height in pixels."
    )
    image_format = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Image format (jpg, png, etc.)"
    )

    # Defining metadata for the image submission table
    class Meta(Submission.Meta):
        db_table = "image_submissions"
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["image_format"]),
        ]

    def save(self, *args, **kwargs):
        """
        Auto-calculate and save the metadata.
        """
        if self.image:
            try:
                # Get file size
                self.file_size = self.image.size
                
                # Extract image format
                self.image_format = self.image.name.split('.')[-1].lower()

                # Get image dimensions
                with Image.open(self.image) as img:
                    self.width, self.height = img.size

            except Exception as e:
                print(f"Error processing image metadata: {e}")
                # Handle corrupted files
                self.file_size = None
                self.width = None
                self.height = None
                self.image_format = None
        
        # Save the image submission
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        """
        Delete the ImageSubmission database entry.
        """
        return super().delete(*args, **kwargs)

    @property
    def image_url(self) -> Optional[str]:
        """
        Get the public URL for the stored image.
        """
        if self.image:
            return self.image.url
        return None

    @property
    def file_size_mb(self) -> Optional[float]:
        """
        Get file size in megabytes.
        """
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None

    @property
    def dimensions(self) -> str:
        """
        Get formatted dimensions string.
        """
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        return "Unknown"

    def __str__(self) -> str:
        """
        Obtain a string representation of this Image Submission.
        """
        return f"{self.name} | {self.user.email} | {self.dimensions}"