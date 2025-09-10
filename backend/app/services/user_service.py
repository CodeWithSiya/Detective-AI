from django.utils import timezone
from django.db import transaction
from rest_framework.authtoken.models import Token
from app.models.user import User
from datetime import timedelta
from typing import Any, Dict
import logging
import secrets

logger = logging.getLogger(__name__)

class UserService:
    """
    Service class for user account management.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 10/09/2025
    """

    @staticmethod
    def generate_verification_code() -> str:
        """
        Generate a 6-digit verification code.
        """
        return str(secrets.randbelow(900000) + 100000)

    @staticmethod
    @transaction.atomic
    def create_user_with_verification(username: str, email: str, password: str, first_name: str, last_name: str, user_type: str = "REGISTERED"):
        """
        Create a new user account that requires email verification.

        :param username: Unique username for the user.
        :param email: Unique email for the user.
        :param password: User's password.
        :param first_name: First name of the user.
        :param last_name: Last name of the user.
        :param user_type: Type of user (default is "REGISTERED").
        :returns: Tuple of (User instance, verification_code)
        """
        # Check for existing users.
        if User.objects.filter(email=email).exists():
            raise ValueError("A user with this email already exists.")
        
        if User.objects.filter(username=username).exists():
            raise ValueError("A user with this username already exists.")
        
        # Generate verification code that expires in 15 minutes from creation.
        verification_code = UserService.generate_verification_code()
        expires_at = timezone.now() + timedelta(minutes=15)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            is_active=False,    # Inactive until verified.
            is_email_verified=False,
            verification_code_expires_at=expires_at
        )

        # Hash and store the verification code.
        user.set_verification_code(verification_code)
        user.save(update_fields=['email_verification_code_hash'])

        logger.info(f"User created with verification required: {user.pk} ({user.email})")
        
        # Return plain verification code for email.
        return user, verification_code
    
    @staticmethod
    @transaction.atomic
    def verify_email(email: str, verification_code: str) -> dict:
        """
        Verify user's email with verification code.

        :param email: User's email address.
        :param verification_code: 6 digit verification code.
        :return: Dictionary with success status, user, and token if successful.
        """
        try:
            user = User.objects.get(email=email)

            # Check if already verified.
            if user.is_email_verified:
                return {
                    'success': False,
                    'error': 'Email is already verified'
                }
            
            # Check if code has expired.
            if user.verification_code_expires_at is not None and user.verification_code_expires_at < timezone.now():
                return {
                    'success': False,
                    'error': 'Verification code has expired'
                }
            
            # Check if code matches using hash comparison
            if not user.check_verification_code(verification_code):
                return {
                    'success': False,
                    'error': 'Invalid verification code'
                }
            
            # Verify the user.
            user.is_email_verified = True
            user.is_active = True
            user.clear_verification_code()  # Clear sensitive data
            user.save(update_fields=[
                'is_email_verified', 'is_active',
                'email_verification_code_hash', 'verification_code_expires_at'
            ])

            # Create authentication token.
            token, created = Token.objects.get_or_create(user=user)

            return {
                'success': True,
                'user': user,
                'token': token.key
            }
            
        except User.DoesNotExist:
            return {
                'success': False,
                'error': 'User not found'
            }
        
    @staticmethod
    @transaction.atomic
    def resend_verification_code(email: str) -> dict:
        """
        Resend verification code to user.
        
        :param email: User's email address.
        :return: Dictionary with success status, user, and new verification code.
        """
        try:
            user = User.objects.get(email=email)
            
            if user.is_email_verified:
                return {
                    'success': False,
                    'error': 'Email is already verified'
                }
            
            # Generate new code.
            verification_code = UserService.generate_verification_code()
            expires_at = timezone.now() + timedelta(minutes=15)
            
            user.verification_code_expires_at = expires_at
            user.set_verification_code(verification_code)  # Hash the new code
            user.save(update_fields=['email_verification_code_hash', 'verification_code_expires_at'])
            
            logger.info(f"Verification code resent for user: {user.pk} ({user.email})")
            
            return {
                'success': True,
                'user': user,
                'verification_code': verification_code  # Return plain code for email
            }
            
        except User.DoesNotExist:
            return {
                'success': False,
                'error': 'User not found'
            }
    
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

            # Check if email is verified.
            if not user.is_email_verified:
                return None, None
            
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