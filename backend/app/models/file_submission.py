from django.db import models
from django.core.validators import FileExtensionValidator
from typing import Optional
from .submission import Submission
from app.services.TextExtractor import TextExtractor
import os

def file_upload_path(instance: 'FileSubmission', filename: str) -> str:
    """
    Generate upload path for file submissions.

    :param instance: The FileSubmission model instance.
    :param filename: Filename of the uploaded file.
    :return: The file upload path as a string.
    """
    return f"submissions/files/{instance.user.pk}/{filename}"

class FileSubmission(Submission):
    """
    Class which represents a user's file submission for AI content detection.
    - Accepted Formats: .pdf, .txt, .docx

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025
    """
    # Initialising the file extention validator.
    file_extension_validator = FileExtensionValidator(allowed_extensions=["pdf", "txt", "docx"])

    # Storing the image file.
    file = models.FileField(
        upload_to=file_upload_path,
        validators=[file_extension_validator],
        help_text="Document file for AI detection analysis. Supported formats: PDF, TXT, DOCX."
    )

    # Defining the file's metadata.
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes."
    )
    file_type = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="File extension (pdf, txt, docx)."
    )
    extracted_text = models.TextField(
        null=True,
        blank=True,
        help_text="Text content extracted from the file."
    )
    character_count = models.PositiveIntegerField(
        null = True,
        blank= True,
        help_text="Number of characters in the submission."
    )

    # Defining metadata for the file submission table.
    class Meta(Submission.Meta):
        db_table = 'file_submissions'
        indexes = [
            models.Index(fields=["user", "created_at"])
        ]

    def save(self, *args, **kwargs) -> None:
        """
        Auto-calculate metadata when saving.
        """
        if self.file:
            try:
                # Get file size.
                self.file_size = self.file.size

                # Extract file type.
                self.file_type = self.file.name.split('.')[-1].lower()

                # Extract text content based on file type.
                self.extracted_text = self.extract_text_content()

                # Calculate character count.
                if self.extracted_text:
                    self.character_count = len(self.extracted_text)

            except Exception:
                # Handle corrupted files.
                self.file_size = None
                self.file_type = None
                self.extracted_text = None
                self.character_count = None

        # Save the file submission.
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        """
        Delete the associated file when model is deleted.
        """
        if self.file:
            # Delete the image from storage.
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)

        return super().delete(*args, **kwargs)
    
    def extract_text_content(self) -> Optional[str]:
        """
        Extract text content from the uploaded file.

        :returns: Extracted text content from the uploaded file.
        """
        if not self.file or not self.file_type:
            return None
        
        try:
            file_path = self.file.path
            file_type = self.file_type
            return TextExtractor.extract_text(file_path, file_type)
        
        except Exception:
            return None
    
    def __str__(self) -> str:
        """
        Obtain a string representation of this File Submission.
        """
        return f"{self.name} | {self.user.email} | {self.file_type} | {self.character_count}"