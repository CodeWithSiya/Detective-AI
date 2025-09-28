# type: ignore
from unittest.mock import Mock, patch
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from app.views.user_views import (
    register_user,
    verify_email,
    login_user,
    logout_user,
    get_user_profile,
    get_current_user,
    update_user_profile,
    change_user_password,
    delete_user,
    forgot_password,
    reset_password,
    validate_token,
    create_json_response
)
from app.models.user import User
import pytest
import uuid

class TestUserViews:
    """
    Unit tests for User Views.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose 
    :version: 28/09/2025
    """

    @pytest.fixture
    def mock_user(self):
        """Create a mock authenticated user."""
        user = Mock()
        user.id = uuid.uuid4()
        user.username = 'testuser'
        user.email = 'testuser@example.com'
        user.first_name = 'Test'
        user.last_name = 'User'
        user.is_staff = False
        user.is_email_verified = True
        user.is_authenticated = True
        return user
    
    @pytest.fixture
    def mock_admin_user(self):
        """Create a mock admin user."""
        user = Mock()
        user.id = uuid.uuid4()
        user.username = 'admin'
        user.email = 'admin@example.com'
        user.first_name = 'Admin'
        user.last_name = 'User'
        user.is_staff = True
        user.is_authenticated = True
        return user
    
    @pytest.fixture
    def api_factory(self):
        """Create APIRequestFactory instance for API request testing."""
        return APIRequestFactory()
    
    @pytest.fixture
    def valid_user_data(self):
        """Create valid user registration data."""
        return {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    # JSON Response Helper Tests
    def test_create_json_response_success(self):
        """Test successful JSON response structure."""
        data = {'user': 'test'}
        response = create_json_response(success=True, message='Test message', data=data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Test message'
        assert response.data['data'] == data
        assert 'timestamp' in response.data

    def test_create_json_response_with_kwargs(self):
        """Test JSON response with additional kwargs."""
        response = create_json_response(
            success=True, 
            message='Test', 
            verification_email={'sent': True}
        )
        
        assert response.data['verification_email']['sent'] is True

    # Registration Tests
    @patch('app.views.user_views.EmailService')
    @patch('app.views.user_views.UserService.create_user_with_verification')
    def test_register_user_success(self, mock_user_service, mock_email_service, api_factory, valid_user_data):
        """Test successful user registration."""
        mock_user = Mock()
        mock_user.id = uuid.uuid4()
        mock_user.email = valid_user_data['email']
        mock_user.first_name = valid_user_data['first_name']
        
        mock_user_service.return_value = (mock_user, '123456')
        
        mock_email_instance = Mock()
        mock_email_instance.send_verification_code_email.return_value = {'success': True}
        mock_email_service.return_value = mock_email_instance
        
        request = api_factory.post('/api/users/register/', valid_user_data)
        response = register_user(request)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert 'Please check your email for verification code' in response.data['message']
        assert response.data['data']['requires_verification'] is True
        assert response.data['verification_email']['sent'] is True

    def test_register_user_missing_fields(self, api_factory):
        """Test registration with missing required fields."""
        incomplete_data = {
            'username': 'testuser',
            'email': 'test@example.com'
            # Missing password, first_name, last_name
        }
        
        request = api_factory.post('/api/users/register/', incomplete_data)
        response = register_user(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert 'Missing required fields' in response.data['error']

    @patch('app.views.user_views.UserService.create_user_with_verification')
    def test_register_user_service_error(self, mock_user_service, api_factory, valid_user_data):
        """Test registration with service error."""
        mock_user_service.side_effect = ValueError('Email already exists')
        
        request = api_factory.post('/api/users/register/', valid_user_data)
        response = register_user(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Email already exists'

    # Email Verification Tests
    @patch('app.views.user_views.EmailService')
    @patch('app.views.user_views.UserService.verify_email')
    def test_verify_email_success(self, mock_verify, mock_email_service, api_factory):
        """Test successful email verification."""
        mock_user = Mock()
        mock_user.first_name = 'Test'
        mock_user.id = uuid.uuid4()
        
        # Fix: Mock UserSerializer properly
        with patch('app.views.user_views.UserSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'id': str(mock_user.id),
                'username': 'testuser',
                'email': 'test@example.com',
                'first_name': 'Test'
            }
            mock_serializer.return_value = mock_serializer_instance
            
            mock_verify.return_value = {
                'success': True,
                'user': mock_user,
                'token': 'test_token'
            }
            
            mock_email_instance = Mock()
            mock_email_instance.send_welcome_email.return_value = {'success': True}
            mock_email_service.return_value = mock_email_instance
            
            request_data = {'email': 'test@example.com', 'verification_code': '123456'}
            request = api_factory.post('/api/users/verify-email/', request_data)
            response = verify_email(request)
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['success'] is True
            assert 'Email verified successfully' in response.data['message']

    # Login Tests
    @patch('app.views.user_views.UserSerializer')
    @patch('app.views.user_views.User.objects.get')
    @patch('app.views.user_views.UserService.authenticate_user')
    def test_login_user_success(self, mock_auth, mock_get_user, mock_serializer, api_factory):
        """Test successful user login."""
        mock_user = Mock()
        mock_user.is_email_verified = True
        mock_user.id = uuid.uuid4()
        mock_get_user.return_value = mock_user
        
        # Fix: Mock UserSerializer properly
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = {
            'id': str(mock_user.id),
            'username': 'testuser',
            'email': 'test@example.com'
        }
        mock_serializer.return_value = mock_serializer_instance
        
        mock_auth.return_value = (mock_user, 'test_token')
        
        request_data = {'email': 'test@example.com', 'password': 'password123'}
        request = api_factory.post('/api/users/login/', request_data)
        response = login_user(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Login successful'

    # Profile Tests
    @patch('app.views.user_views.UserSerializer')
    @patch('app.views.user_views.UserService.get_user_by_id')
    def test_get_user_profile_success(self, mock_get_user, mock_serializer, api_factory, mock_user):
        """Test successful profile retrieval."""
        mock_get_user.return_value = mock_user
        
        # Fix: Mock UserSerializer properly
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = {
            'id': str(mock_user.id),
            'username': mock_user.username,
            'email': mock_user.email
        }
        mock_serializer.return_value = mock_serializer_instance
        
        user_id = str(mock_user.id)
        
        request = api_factory.get(f'/api/users/{user_id}/')
        force_authenticate(request, user=mock_user)
        response = get_user_profile(request, user_id)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'User profile retrieved successfully'

    def test_get_user_profile_permission_denied(self, api_factory, mock_user):
        """Test profile access without permission."""
        other_user_id = str(uuid.uuid4())
        
        # FMock to return a user (not None) so permission check is triggered
        with patch('app.views.user_views.UserService.get_user_by_id') as mock_get_user:
            other_user = Mock()
            other_user.id = uuid.uuid4()
            mock_get_user.return_value = other_user  # Return a user, not None
            
            request = api_factory.get(f'/api/users/{other_user_id}/')
            force_authenticate(request, user=mock_user)
            response = get_user_profile(request, other_user_id)
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert response.data['error'] == 'Permission denied'

    @patch('app.views.user_views.UserSerializer')
    def test_get_current_user_success(self, mock_serializer, api_factory, mock_user):
        """Test current user profile retrieval."""
        # Fix: Mock UserSerializer properly
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = {
            'id': str(mock_user.id),
            'username': mock_user.username,
            'email': mock_user.email
        }
        mock_serializer.return_value = mock_serializer_instance
        
        request = api_factory.get('/api/users/me/')
        force_authenticate(request, user=mock_user)
        response = get_current_user(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Current user profile retrieved successfully'

    # Update Profile Tests
    @patch('app.views.user_views.UserSerializer')
    @patch('app.views.user_views.UserService.update_user_profile')
    def test_update_user_profile_success(self, mock_update, mock_serializer, api_factory, mock_user):
        """Test successful profile update."""
        updated_user = Mock()
        updated_user.id = mock_user.id
        mock_update.return_value = {'user': updated_user}
        
        # Fix: Mock UserSerializer properly
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = {
            'id': str(updated_user.id),
            'first_name': 'Updated'
        }
        mock_serializer.return_value = mock_serializer_instance
        
        update_data = {'first_name': 'Updated'}
        user_id = str(mock_user.id)
        
        request = api_factory.put(f'/api/users/{user_id}/update/', update_data)
        force_authenticate(request, user=mock_user)
        response = update_user_profile(request, user_id)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'User profile updated successfully'

    def test_update_user_profile_no_data(self, api_factory, mock_user):
        """Test profile update with no valid data."""
        # Fix: Remove None values that cause encoding issues
        update_data = {'first_name': ''}
        user_id = str(mock_user.id)
        
        request = api_factory.put(f'/api/users/{user_id}/update/', update_data)
        force_authenticate(request, user=mock_user)
        response = update_user_profile(request, user_id)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'No valid data provided for update'

    # Password Reset Tests
    @patch('app.views.user_views.settings')
    @patch('app.views.user_views.default_token_generator.make_token')
    @patch('app.views.user_views.urlsafe_base64_encode')
    @patch('app.views.user_views.force_bytes')
    @patch('app.views.user_views.EmailService')
    @patch('app.views.user_views.User.objects.filter')
    def test_forgot_password_success(self, mock_filter, mock_email_service, mock_force_bytes, 
                                   mock_encode, mock_token, mock_settings, api_factory):
        """Test successful forgot password request."""
        mock_user = Mock()
        mock_user.email = 'test@example.com'
        mock_user.first_name = 'Test'
        mock_user.last_name = 'User'
        mock_user.pk = 1
        
        # Mock settings.FRONTEND_URL
        mock_settings.FRONTEND_URL = 'http://localhost:3000'
        
        # Mock all the encoding functions
        mock_filter.return_value.first.return_value = mock_user
        mock_force_bytes.return_value = b'test_bytes'
        mock_encode.return_value = 'encoded_uid'
        mock_token.return_value = 'reset_token'
        
        mock_email_instance = Mock()
        mock_email_instance.send_forgot_password_email.return_value = {'success': True}
        mock_email_service.return_value = mock_email_instance
        
        request_data = {'email': 'test@example.com'}
        request = api_factory.post('/api/users/forgot-password/', request_data)
        response = forgot_password(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'password reset link has been sent' in response.data['message']

    # Token Validation Tests
    @patch('app.views.user_views.UserSerializer')
    @patch('app.views.user_views.UserService.validate_user_token')
    def test_validate_token_success(self, mock_validate, mock_serializer, api_factory):
        """Test successful token validation."""
        mock_user = Mock()
        mock_user.id = uuid.uuid4()
        
        # Fix: Mock UserSerializer properly
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = {
            'id': str(mock_user.id),
            'username': 'testuser'
        }
        mock_serializer.return_value = mock_serializer_instance
        
        mock_validate.return_value = {
            'valid': True,
            'user': mock_user,
            'token': 'valid_token'
        }
        
        request_data = {'token': 'valid_token'}
        request = api_factory.post('/api/users/validate-token/', request_data)
        response = validate_token(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Token is valid'

    @patch('app.views.user_views.UserService.validate_user_token')
    def test_validate_token_invalid(self, mock_validate, api_factory):
        """Test invalid token validation."""
        mock_validate.return_value = {
            'valid': False,
            'error': 'Token has expired'
        }
        
        request_data = {'token': 'invalid_token'}
        request = api_factory.post('/api/users/validate-token/', request_data)
        response = validate_token(request)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['error'] == 'Token has expired'

    def test_validate_token_missing(self, api_factory):
        """Test token validation without token."""
        request = api_factory.post('/api/users/validate-token/', {})
        response = validate_token(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Token is required'

    # Authentication Tests
    def test_user_views_require_authentication(self, api_factory):
        """Test that protected views require authentication."""
        user_id = str(uuid.uuid4())
        protected_views = [
            (logout_user, api_factory.post('/api/users/logout/')),
            (get_user_profile, api_factory.get(f'/api/users/{user_id}/')),
            (get_current_user, api_factory.get('/api/users/me/')),
            (update_user_profile, api_factory.put(f'/api/users/{user_id}/update/')),
            (change_user_password, api_factory.put(f'/api/users/{user_id}/change-password/')),
            (delete_user, api_factory.delete(f'/api/users/{user_id}/delete/')),
        ]
        
        for view, request in protected_views:
            if 'user_id' in view.__code__.co_varnames:
                response = view(request, user_id)
            else:
                response = view(request)
            assert response.status_code == status.HTTP_403_FORBIDDEN