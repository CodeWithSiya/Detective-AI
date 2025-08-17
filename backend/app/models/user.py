from django.contrib.auth.models import AbstractUser
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

    # Adding the field to differentiate between different user types.
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='REGISTERED',
        help_text="Defines the user's role and access level in the system."
    )

    # Use email instead of username for authentication.
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

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