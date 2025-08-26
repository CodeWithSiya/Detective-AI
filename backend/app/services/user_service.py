from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.authtoken.models import Token
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class UserService:
    """
    Service class for user account management.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 26/08/2025 
    """

    @staticmethod
    @transaction.atomic
    def create_user(username: str, email: str, password: str, first_name: str, last_name: str, user_type: str = "REGISTERED"):
        """
        Create a new user account.

        :param username: Unique username for the user.
        :param email: Unique email for the user.
        :param password: User's password.
        :param first_name: First name of the user.
        :param last_name: Last name of the user.
        :param user_type: Type of user (default is "REGISTERED").
        :returns: The created User instance.
        """
        # Check for existing users.
        if User.objects.filter(email=email).exists():
            raise ValueError("A user with this email already exists.")
        
        if User.objects.filter(username=username).exists():
            raise ValueError("A user with this username already exists.")
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type
        )
        
        # Create token for the new user.
        Token.objects.create(user=user)

        logger.info(f"User created: {user.pk} ({user.email})")
        return user
    
    @staticmethod
    def authenticate_user(email: str, password: str):
        """
        Authenticate a user with email and password.

        :param email: User's email.
        :param password: User's password.
        :return: Tuple of (User instance, token) if authentication successful, (None, None) otherwise.
        """
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                # Get or create token for the user.
                token, created = Token.objects.get_or_create(user=user)
                logger.info(f"User authenticated: {user.pk} ({user.email})")
                return user, token.key
            return None, None
        
        except User.DoesNotExist:
            return None, None
        
    @staticmethod
    def logout_user(user) -> bool:
        """
        Logout user by deleting their token.

        :param user: User instance.
        :return: True if logout successful.
        """
        try:
            Token.objects.filter(user=user).delete()
            logger.info(f"User logged out: {user.pk} ({user.email})")
            return True
        except Exception as e:
            logger.error(f"Error logging out user {user.pk}: {str(e)}")
            return False
    
    @staticmethod
    def get_user_by_id(user_id: str):
        """
        Retrieve a user by ID.

        :param user_id: The UUID string of the user to retrieve.
        :return: User instance or None if not found.
        """
        try:
            return User.objects.get(id=user_id)
        
        except (User.DoesNotExist, ValueError):
            return None
    
    @staticmethod
    def get_user_by_email(email: str):
        """
        Retrieve a user by email.

        :param email: The email of the user to retrieve.
        :return: User instance or None if not found.
        """
        try:
            return User.objects.get(email=email)
        
        except User.DoesNotExist:
            return None
    
    @staticmethod
    @transaction.atomic
    def update_user_profile(user_id: str, update_data: Dict[str, Any]):
        """
        Update user profile information.

        :param user_id: The ID of the user to update.
        :param update_data: Dictionary containing fields to update.
        :return: Updated User instance or None if not found.
        """
        try:
            user = User.objects.get(id=user_id)

            # Define allowable fields for update.
            allowed_fields = ['first_name', 'last_name', 'email', 'username']

            #TODO: Add validation for other stuff like same first_name and lastname for same user etc.

            # Check for duplicate email if email is being updated.
            if 'email' in update_data and update_data['email'] != user.email:
                if User.objects.filter(email=update_data['email']).exists():
                    raise ValueError("A user with this email already exists.")
                
            # Check for duplicate username if username is being updated.
            if 'username' in update_data and update_data['username'] != user.username:
                if User.objects.filter(username=update_data['username']).exists():
                    raise ValueError("A user with this username already exists.")
                
            # Update allowed fields.
            updated_fields = []
            for field, value in update_data.items():
                if field in allowed_fields and hasattr(user, field):
                    # Only update if value has changed
                    if getattr(user, field) != value:
                        setattr(user, field, value)
                        updated_fields.append(field)
            
            # Save the updated fields to the user's profile.
            if updated_fields:
                user.save(update_fields=updated_fields)
                logger.info(f"User profile updated: {user.pk} ({user.email}) - Fields: {', '.join(updated_fields)}")
            else:
                logger.info(f"No changes made to user profile: {user.pk} ({user.email})")
  
            return user
        
        except User.DoesNotExist:
            return None
        
    @staticmethod
    @transaction.atomic
    def change_password(user_id: str, current_password: str, new_password: str) -> bool:
        """
        Change user password after verifying current password.

        :param user_id: The ID of the user.
        :param current_password: Current password for verification.
        :param new_password: New password to set.
        :return: True if password changed successfully, False otherwise.
        :raises ValueError: If current password is incorrect.
        """
        try:
            user = User.objects.get(id=user_id)
            
            # Verify current password.
            if not user.check_password(current_password):
                raise ValueError("Current password is incorrect.")
            
            # Set new password.
            user.set_password(new_password)
            user.save(update_fields=['password'])
            
            logger.info(f"Password changed for user: {user.pk} ({user.email})")
            return True
        
        except User.DoesNotExist:
            return False

    @staticmethod
    @transaction.atomic
    def delete_user(user_id: str) -> bool:
        """
        Delete a user by ID.

        :param user_id: The ID of the user to delete.
        :return: True if deleted, False if not found.
        """
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            logger.info(f"User deleted: {user.pk} ({user.email})")
            return True
        
        except (User.DoesNotExist, ValueError):
            return False