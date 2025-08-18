from django.db import models
from django.core.validators import FileExtensionValidator
from typing import Optional
from PIL import Image
from .submission import Submission
import os

def image_upload_path(instance: models.Model, filename: str) -> str:
    """
    Generate upload path for image submissions.

    :param instance: The ImageSubmission model instance.
    :param filename: Filename of the uploaded file.
    :return:
    """
    return f""

class ImageSubmission(Submission):
    """
    Class which represents a user's image submission for AI content detection.
    - Accepted Formats: .jpeg, .jpg, .png

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025
    """ 
    # Initialising the file extention validator.
    file_extension_validator = FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])

    # Storing the image file.
    image = models.ImageField(
        upload_to=image_upload_path,
        validators=[file_extension_validator],
        help_text="Image file for AI detection analysis. Supported formats: JPG, JPEG, PNG."
    )

    # Defining the Image's metadata.
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes."
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

    # Defining metadata for the Iimage submission table.
    class Meta(Submission.Meta):
        db_table = "image_submissions"
        indexes = [
            models.Index(fields=["user", "created_at"])
        ]

    def save(self, *args, **kwargs):
        """
        Auto-calculate and save the metadata.
        """
        if self.image:
            try:
                # Get file size.
                self.file_size = self.image.size

                # Get image dimensions.
                with Image.open(self.image) as img:
                    self.width, self.height = img.size

            except Exception as e:
                # Handle corrupted files.
                self.file_size = None
                self.width = None
                self.height = None
        
        # Save the image submission.
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        """
        Delete the associated image when model is deleted.
        """
        if self.image:
            # Delete the image from storage.
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)

        return super().delete(*args, **kwargs)

    @property
    def image_url(self) -> Optional[str]:
        """
        Get the URL of the uploaded image.
        """
        if self.image:
            return self.image.url
        return None

    def __str__(self) -> str:
        """
        Obtain a string representation of this Image Submission.
        """
        dimensions = f"{self.width}x{self.height}" if self.width and self.height else "Unknown"
        return f"{self.name} | {self.user.email} ({dimensions})"