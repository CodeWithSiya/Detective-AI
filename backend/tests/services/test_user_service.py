# type: ignore
from unittest.mock import Mock, patch
import pytest
from django.utils import timezone
from rest_framework.authtoken.models import Token
from app.services.user_service import UserService
from app.models.user import User
from datetime import timedelta
import uuid

class TestUserService:
    """
    Unit tests for User Service.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 28/09/2025
    """

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        user = Mock(spec=User)
        user.id = uuid.uuid4()
        user.email = 'test@example.com'
        user.username = 'testuser'
        user.is_active = True
        user.is_email_verified = True
        return user

    # Generate Verification Code Tests
    def test_generate_verification_code_format(self):
        """Test verification code generation format."""
        code = UserService.generate_verification_code()
        
        assert isinstance(code, str)
        assert len(code) == 6
        assert code.isdigit()

    # Token Validation Tests
    def test_is_token_valid_fresh_token(self):
        """Test token validation with fresh token."""
        mock_token = Mock()
        mock_token.created = timezone.now() - timedelta(hours=1)  # 1 hour old
        
        assert UserService.is_token_valid(mock_token) is True

    def test_is_token_valid_expired_token(self):
        """Test token validation with expired token."""
        mock_token = Mock()
        mock_token.created = timezone.now() - timedelta(hours=25)  # 25 hours old
        
        assert UserService.is_token_valid(mock_token) is False

    def test_is_token_valid_no_created_date(self):
        """Test token validation with no created date."""
        mock_token = Mock()
        mock_token.created = None
        
        assert UserService.is_token_valid(mock_token) is False

    # Token Refresh Tests
    @patch('app.services.user_service.Token')
    def test_refresh_token_if_needed_refresh_required(self, mock_token_class, mock_user):
        """Test token refresh when refresh is needed."""
        # Token is 23 hours old (within refresh threshold)
        mock_token = Mock()
        mock_token.created = timezone.now() - timedelta(hours=23)
        mock_token.user = mock_user
        
        # Mock new token creation
        new_token = Mock()
        new_token.key = 'new-token-key'
        mock_token_class.objects.create.return_value = new_token
        
        result = UserService.refresh_token_if_needed(mock_token)
        
        # Should refresh token
        assert result == new_token
        mock_token.delete.assert_called_once()

    def test_refresh_token_if_needed_no_refresh_needed(self):
        """Test token refresh when no refresh is needed."""
        mock_token = Mock()
        mock_token.created = timezone.now() - timedelta(hours=1)  # 1 hour old
        
        result = UserService.refresh_token_if_needed(mock_token)
        
        # Should return original token
        assert result == mock_token

    # Create User Tests
    @patch('app.services.user_service.User.objects')
    def test_create_user_with_verification_success(self, mock_user_objects):
        """Test successful user creation with verification."""
        # Mock no existing users
        mock_user_objects.filter.return_value.exists.return_value = False
        
        # Mock user creation
        mock_user = Mock(spec=User)
        mock_user_objects.create_user.return_value = mock_user
        
        user, code = UserService.create_user_with_verification(
            'testuser', 'test@example.com', 'password123', 'Test', 'User'
        )
        
        assert user == mock_user
        assert isinstance(code, str)
        assert len(code) == 6

    @patch('app.services.user_service.User.objects')
    def test_create_user_with_verification_email_exists(self, mock_user_objects):
        """Test user creation when email already exists."""
        mock_user_objects.filter.return_value.exists.side_effect = [True, False]
        
        with pytest.raises(ValueError, match="A user with this email already exists"):
            UserService.create_user_with_verification(
                'testuser', 'test@example.com', 'password123', 'Test', 'User'
            )

    # Email Verification Tests
    @patch('app.services.user_service.User.objects')
    @patch('app.services.user_service.Token')
    def test_verify_email_success(self, mock_token_class, mock_user_objects, mock_user):
        """Test successful email verification."""
        mock_user.is_email_verified = False
        mock_user.verification_code_expires_at = timezone.now() + timedelta(minutes=5)
        mock_user.check_verification_code.return_value = True
        mock_user_objects.get.return_value = mock_user
        
        # Mock token creation
        mock_token = Mock()
        mock_token.key = 'new-token'
        mock_token_class.objects.get_or_create.return_value = (mock_token, True)
        
        result = UserService.verify_email('test@example.com', '123456')
        
        assert result['success'] is True
        assert result['user'] == mock_user
        assert result['token'] == 'new-token'

    @patch('app.services.user_service.User.objects')
    def test_verify_email_invalid_code(self, mock_user_objects, mock_user):
        """Test email verification with invalid code."""
        mock_user.is_email_verified = False
        mock_user.verification_code_expires_at = timezone.now() + timedelta(minutes=5)
        mock_user.check_verification_code.return_value = False
        mock_user_objects.get.return_value = mock_user
        
        result = UserService.verify_email('test@example.com', '123456')
        
        assert result['success'] is False
        assert result['error'] == 'Invalid verification code'

    @patch('app.services.user_service.User.objects')
    def test_verify_email_user_not_found(self, mock_user_objects):
        """Test email verification with non-existent user."""
        mock_user_objects.get.side_effect = User.DoesNotExist()
        
        result = UserService.verify_email('nonexistent@example.com', '123456')
        
        assert result['success'] is False
        assert result['error'] == 'User not found'

    # Authentication Tests
    @patch('app.services.user_service.User.objects')
    @patch('app.services.user_service.Token')
    def test_authenticate_user_success(self, mock_token_class, mock_user_objects, mock_user):
        """Test successful user authentication."""
        mock_user.is_email_verified = True
        mock_user.is_active = True
        mock_user.check_password.return_value = True
        mock_user_objects.get.return_value = mock_user
        
        # Mock token creation
        mock_token = Mock()
        mock_token.key = 'auth-token'
        mock_token.created = timezone.now() - timedelta(hours=1)
        mock_token_class.objects.get_or_create.return_value = (mock_token, False)
        
        # Mock token validation
        with patch.object(UserService, 'is_token_valid', return_value=True):
            with patch.object(UserService, 'refresh_token_if_needed', return_value=mock_token):
                user, token = UserService.authenticate_user('test@example.com', 'password123')
                
                assert user == mock_user
                assert token == 'auth-token'

    @patch('app.services.user_service.User.objects')
    def test_authenticate_user_wrong_password(self, mock_user_objects, mock_user):
        """Test authentication with wrong password."""
        mock_user.check_password.return_value = False
        mock_user_objects.get.return_value = mock_user
        
        user, token = UserService.authenticate_user('test@example.com', 'wrongpassword')
        
        assert user is None
        assert token is None

    # Logout Tests
    @patch('app.services.user_service.Token')
    def test_logout_user_success(self, mock_token_class, mock_user):
        """Test successful user logout."""
        result = UserService.logout_user(mock_user)
        
        assert result is True
        mock_token_class.objects.filter.assert_called_once_with(user=mock_user)

    # Get User Tests
    @patch('app.services.user_service.User.objects')
    def test_get_user_by_email_success(self, mock_user_objects, mock_user):
        """Test successful user retrieval by email."""
        mock_user_objects.get.return_value = mock_user
        
        user = UserService.get_user_by_email('test@example.com')
        
        assert user == mock_user

    @patch('app.services.user_service.User.objects')
    def test_get_user_by_email_not_found(self, mock_user_objects):
        """Test user retrieval by email when not found."""
        mock_user_objects.get.side_effect = User.DoesNotExist()
        
        user = UserService.get_user_by_email('nonexistent@example.com')
        
        assert user is None

    # Update Profile Tests
    @patch('app.services.user_service.User.objects')
    def test_update_user_profile_success(self, mock_user_objects, mock_user):
        """Test successful user profile update."""
        mock_user_objects.get.return_value = mock_user
        
        update_data = {'first_name': 'Updated', 'last_name': 'Name'}
        
        result = UserService.update_user_profile(str(mock_user.id), update_data)
        
        assert result['user'] == mock_user
        assert result['email_changed'] is False

    @patch('app.services.user_service.User.objects')
    def test_update_user_profile_email_change(self, mock_user_objects, mock_user):
        """Test user profile update with email change."""
        mock_user.email = 'old@example.com'
        mock_user_objects.get.return_value = mock_user
        mock_user_objects.filter.return_value.exists.return_value = False
        
        update_data = {'email': 'new@example.com'}
        
        result = UserService.update_user_profile(str(mock_user.id), update_data)
        
        assert result['email_changed'] is True
        assert 'verification_code' in result

    # Change Password Tests
    @patch('app.services.user_service.User.objects')
    @patch('app.services.user_service.Token')
    def test_change_password_success(self, mock_token_class, mock_user_objects, mock_user):
        """Test successful password change."""
        mock_user.check_password.return_value = True
        mock_user_objects.get.return_value = mock_user
        
        result = UserService.change_password(str(mock_user.id), 'oldpassword', 'newpassword')
        
        assert result is True
        mock_user.set_password.assert_called_once_with('newpassword')

    @patch('app.services.user_service.User.objects')
    def test_change_password_wrong_current(self, mock_user_objects, mock_user):
        """Test password change with wrong current password."""
        mock_user.check_password.return_value = False
        mock_user_objects.get.return_value = mock_user
        
        with pytest.raises(ValueError, match="Current password is incorrect"):
            UserService.change_password(str(mock_user.id), 'wrongpassword', 'newpassword')

    # Token Validation Tests
    @patch('app.services.user_service.Token')
    def test_validate_user_token_success(self, mock_token_class, mock_user):
        """Test successful token validation."""
        mock_token = Mock()
        mock_token.user = mock_user
        mock_token.key = 'test-token-key'
        mock_token_class.objects.select_related.return_value.get.return_value = mock_token
        
        with patch.object(UserService, 'is_token_valid', return_value=True):
            with patch.object(UserService, 'refresh_token_if_needed', return_value=mock_token):
                result = UserService.validate_user_token('test-token-key')
                
                assert result['valid'] is True
                assert result['user'] == mock_user

    # Resend Verification Tests
    @patch('app.services.user_service.User.objects')
    def test_resend_verification_code_success(self, mock_user_objects, mock_user):
        """Test successful verification code resend."""
        mock_user.is_email_verified = False
        mock_user_objects.get.return_value = mock_user
        
        result = UserService.resend_verification_code('test@example.com')
        
        assert result['success'] is True
        assert 'verification_code' in result

    @patch('app.services.user_service.User.objects')
    def test_resend_verification_code_already_verified(self, mock_user_objects, mock_user):
        """Test resend verification code when already verified."""
        mock_user.is_email_verified = True
        mock_user_objects.get.return_value = mock_user
        
        result = UserService.resend_verification_code('test@example.com')
        
        assert result['success'] is False
        assert result['error'] == 'Email is already verified'