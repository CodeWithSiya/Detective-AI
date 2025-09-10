from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
import uuid

class User(AbstractUser):
    """
    Model which represents a general user of the application.
    - Extends Django's AbstractUser which defines various fields.
    - Handles both admin and registered user types through the user_type field.

    :authors: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025
    """
    # Configuring user types as constants.
    USER_TYPE_CHOICES = (
        ("ADMIN", "Admin"),
        ("REGISTERED", "Registered User")
    )

    # Overriding the default id with a uuid.
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the user."
    )

    # Overriding inherited fields to make them required.
    first_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name="First Name",
        help_text="User's first name."
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name="Last Name",
        help_text="User's last name."
    )
    email = models.EmailField(
        unique=True,
        blank=False,
        help_text="User's email address. Must be unique."
    )

    # Email verification fields.
    is_email_verified = models.BooleanField(
        default=False,
        help_text="Whether the user's email has been verified"
    )
    email_verification_code_hash = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Hashed 6-digit verification code for email verification"
    )
    verification_code_expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the verification code expires"
    )
    
    # Adding the field to differentiate between different user types.
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='REGISTERED',
        help_text="Defines the user's role and access level in the system."
    )

    # Use email instead of username for authentication.
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    # Defining metadata for the user table.
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email", "user_type"]),
            models.Index(fields=["first_name", "last_name"]),
            models.Index(fields=["user_type"])
        ]

    def __str__(self) -> str:
        """
        Returns a string representation of this user.
        """
        return f"{self.username} | {self.email} | {self.user_type}"

    def is_admin_user(self) -> bool:
        """
        Checks if the user has admin privileges.
        """
        return self.user_type == "ADMIN"
    
    def is_registered_user(self) -> bool:
        """
        Checks if the user is a standard registered user.
        """
        return self.user_type == "REGISTERED"
    
    def set_verification_code(self, code:str) -> None:
        """
        Set and hash the verification code.
        """
        self.email_verification_code_hash = make_password(code)

    def check_verification_code(self, code: str) -> bool:
        """
        Check if the provided code matches the stored hash.
        """
        if not self.email_verification_code_hash:
            return False
        return check_password(code, self.email_verification_code_hash)
    
    def clear_verification_code(self) -> None:
        """
        Clear verification code data after successful verification.
        """
        self.email_verification_code_hash = None
        self.verification_code_expires_at = None