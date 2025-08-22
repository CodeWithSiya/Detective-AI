from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class UserService:
    """
    Basic user service for account creation and deletion.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 22/08/2025 
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
        :returns: The created User instance
        """
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
        return user
    
    @staticmethod
    def delete_user(user_id: str):
        """
        Delete a user by ID.

        param user_id: The ID of the user to delete.
        :return: True if deleted, False if not found.
        """
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return True
        except User.DoesNotExist:
            return False