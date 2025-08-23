from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from app.services.user_service import UserService

User = get_user_model()

class UserServiceTestCase(TestCase):
    """
    Unit tests for UserService with mocked database.
    """

    def setUp(self):
        """Set up test data."""
        self.test_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    @patch('app.services.user_service.User')
    def test_create_user_success(self, mock_user_model):
        """Test successful user creation."""
        # Mock the filter and exists methods
        mock_user_model.objects.filter.return_value.exists.return_value = False
        
        # Mock the created user
        mock_user = Mock()
        mock_user.username = self.test_user_data['username']
        mock_user.email = self.test_user_data['email']
        mock_user.first_name = self.test_user_data['first_name']
        mock_user.last_name = self.test_user_data['last_name']
        
        mock_user_model.objects.create_user.return_value = mock_user
        
        # Call the service
        user = UserService.create_user(**self.test_user_data)
        
        # Assertions
        mock_user_model.objects.create_user.assert_called_once_with(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User',
            user_type='REGISTERED'
        )
        self.assertEqual(user, mock_user)

    @patch('app.services.user_service.User')
    def test_create_user_duplicate_email(self, mock_user_model):
        """Test user creation with duplicate email raises ValueError."""
        # Mock email exists but username doesn't
        def mock_filter_side_effect(**kwargs):
            mock_queryset = Mock()
            if 'email' in kwargs:
                mock_queryset.exists.return_value = True
            else:
                mock_queryset.exists.return_value = False
            return mock_queryset
        
        mock_user_model.objects.filter.side_effect = mock_filter_side_effect
        
        with self.assertRaises(ValueError) as context:
            UserService.create_user(**self.test_user_data)
        
        self.assertIn("email already exists", str(context.exception))

    @patch('app.services.user_service.User')
    def test_create_user_duplicate_username(self, mock_user_model):
        """Test user creation with duplicate username raises ValueError."""
        # Mock username exists but email doesn't
        def mock_filter_side_effect(**kwargs):
            mock_queryset = Mock()
            if 'username' in kwargs:
                mock_queryset.exists.return_value = True
            else:
                mock_queryset.exists.return_value = False
            return mock_queryset
        
        mock_user_model.objects.filter.side_effect = mock_filter_side_effect
        
        with self.assertRaises(ValueError) as context:
            UserService.create_user(**self.test_user_data)
        
        self.assertIn("username already exists", str(context.exception))

    @patch('app.services.user_service.User')
    def test_delete_user_success(self, mock_user_model):
        """Test successful user deletion."""
        mock_user = Mock()
        mock_user_model.objects.get.return_value = mock_user
        
        result = UserService.delete_user("123")
        
        mock_user_model.objects.get.assert_called_once_with(id="123")
        mock_user.delete.assert_called_once()
        self.assertTrue(result)