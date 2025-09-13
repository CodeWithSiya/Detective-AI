from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.utils import timezone
import uuid

class User(AbstractUser):
    """
    Model which represents a general user of the application.
    - Extends Django's AbstractUser which defines various fields.
    - Uses Django's built-in permission system (is_staff, is_superuser).

    :authors: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 11/09/2025
    """

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

    # Use email instead of username for authentication.
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    # Defining metadata for the user table.
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
            models.Index(fields=["first_name", "last_name"]),
            models.Index(fields=["is_staff"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_email_verified"]),
        ]

    def __str__(self) -> str:
        """
        Returns a string representation of this user.
        """
        role = "Admin" if self.is_staff else "User"
        return f"{self.username} | {self.email} | {role}"
    
    @property
    def full_name(self) -> str:
        """
        Returns the user's full name.
        """
        return f"{self.first_name} {self.last_name}".strip()

    def is_admin_user(self) -> bool:
        """
        Checks if the user has admin privileges.
        """
        return self.is_staff
    
    def is_regular_user(self) -> bool:
        """
        Checks if the user is a regular user (not admin).
        """
        return not self.is_staff and self.is_active
    
    def promote_to_admin(self) -> None:
        """
        Promote user to admin status.
        """
        self.is_staff = True
        self.is_superuser = True
        self.save(update_fields=['is_staff', 'is_superuser'])

    def demote_from_admin(self) -> None:
        """
        Demote user from admin to regular user status.
        """
        self.is_staff = False
        self.is_superuser = False
        self.save(update_fields=['is_staff', 'is_superuser'])

    def activate_user(self) -> None:
        """
        Activate the user account.
        """
        self.is_active = True
        self.save(update_fields=['is_active'])

    def deactivate_user(self) -> None:
        """
        Deactivate the user account.
        """
        self.is_active = False
        self.save(update_fields=['is_active'])
     
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

    def is_verification_code_expired(self) -> bool:
        """
        Check if the verification code has expired.
        """
        if not self.verification_code_expires_at:
            return True
        return timezone.now() > self.verification_code_expires_at

    def update_last_login(self) -> None:
        """
        Update the last login timestamp.
        """
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])