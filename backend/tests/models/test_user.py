# type: ignore
from unittest.mock import Mock, patch
import pytest
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
from app.models.user import User
import uuid

class TestUserModel:
    """
    Unit tests for User model.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 28/09/2025
    """

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        user = Mock(spec=User)
        user.id = uuid.uuid4()
        user.username = 'testuser'
        user.email = 'test@example.com'
        user.first_name = 'Test'
        user.last_name = 'User'
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False
        user.is_email_verified = True
        user.email_verification_code_hash = None
        user.verification_code_expires_at = None
        user.last_login = None
        return user

    # Model Configuration Tests
    def test_uuid_field_generates_valid_uuid(self):
        """Test that the UUID field generates valid UUIDs."""
        field = User._meta.get_field('id')
        generated_uuid = field.default()
        
        assert isinstance(generated_uuid, uuid.UUID)
        assert generated_uuid.version == 4

    def test_model_meta_configuration(self):
        """Test model Meta configuration."""
        meta = User._meta
        
        assert meta.db_table == 'users'
        assert len(meta.indexes) == 6  # Check number of indexes

    def test_username_field_configuration(self):
        """Test USERNAME_FIELD is set to email."""
        assert User.USERNAME_FIELD == "email"

    def test_required_fields_configuration(self):
        """Test REQUIRED_FIELDS configuration."""
        expected_fields = ["username", "first_name", "last_name"]
        assert User.REQUIRED_FIELDS == expected_fields

    # String Representation Tests
    def test_str_representation_regular_user(self):
        """Test string representation for regular user."""
        user = User(username="testuser", email="test@example.com", is_staff=False)
        expected = "testuser | test@example.com | User"
        assert str(user) == expected

    def test_str_representation_admin_user(self):
        """Test string representation for admin user."""
        user = User(username="admin", email="admin@example.com", is_staff=True)
        expected = "admin | admin@example.com | Admin"
        assert str(user) == expected

    # Property Tests
    def test_full_name_property(self):
        """Test full_name property."""
        user = User(first_name="John", last_name="Doe")
        assert user.full_name == "John Doe"

    def test_full_name_property_with_spaces(self):
        """Test full_name property handles extra spaces."""
        user = User(first_name="  John  ", last_name="  Doe  ")
        assert user.full_name.strip() == "John     Doe"

    def test_full_name_property_empty_names(self):
        """Test full_name property with empty names."""
        user = User(first_name="", last_name="")
        assert user.full_name == ""

    # User Role Tests
    def test_is_admin_user_true(self):
        """Test is_admin_user returns True for staff users."""
        user = User(is_staff=True)
        assert user.is_admin_user() is True

    def test_is_admin_user_false(self):
        """Test is_admin_user returns False for non-staff users."""
        user = User(is_staff=False)
        assert user.is_admin_user() is False

    def test_is_regular_user_true(self):
        """Test is_regular_user returns True for active non-staff users."""
        user = User(is_staff=False, is_active=True)
        assert user.is_regular_user() is True

    def test_is_regular_user_false_inactive(self):
        """Test is_regular_user returns False for inactive users."""
        user = User(is_staff=False, is_active=False)
        assert user.is_regular_user() is False

    def test_is_regular_user_false_admin(self):
        """Test is_regular_user returns False for admin users."""
        user = User(is_staff=True, is_active=True)
        assert user.is_regular_user() is False

    # User Status Management Tests
    @patch.object(User, 'save')
    def test_promote_to_admin(self, mock_save):
        """Test promote_to_admin method."""
        user = User(is_staff=False, is_superuser=False)
        
        user.promote_to_admin()
        
        assert user.is_staff is True
        assert user.is_superuser is True
        mock_save.assert_called_once_with(update_fields=['is_staff', 'is_superuser'])

    @patch.object(User, 'save')
    def test_demote_from_admin(self, mock_save):
        """Test demote_from_admin method."""
        user = User(is_staff=True, is_superuser=True)
        
        user.demote_from_admin()
        
        assert user.is_staff is False
        assert user.is_superuser is False
        mock_save.assert_called_once_with(update_fields=['is_staff', 'is_superuser'])

    @patch.object(User, 'save')
    def test_activate_user(self, mock_save):
        """Test activate_user method."""
        user = User(is_active=False)
        
        user.activate_user()
        
        assert user.is_active is True
        mock_save.assert_called_once_with(update_fields=['is_active'])

    @patch.object(User, 'save')
    def test_deactivate_user(self, mock_save):
        """Test deactivate_user method."""
        user = User(is_active=True)
        
        user.deactivate_user()
        
        assert user.is_active is False
        mock_save.assert_called_once_with(update_fields=['is_active'])

    # Verification Code Tests
    def test_set_verification_code(self):
        """Test set_verification_code method."""
        user = User()
        
        with patch('app.models.user.make_password', return_value='hashed_code') as mock_make_password:
            user.set_verification_code('123456')
            
            mock_make_password.assert_called_once_with('123456')
            assert user.email_verification_code_hash == 'hashed_code'

    def test_check_verification_code_valid(self):
        """Test check_verification_code with valid code."""
        user = User(email_verification_code_hash='hashed_code')
        
        with patch('app.models.user.check_password', return_value=True) as mock_check:
            result = user.check_verification_code('123456')
            
            assert result is True
            mock_check.assert_called_once_with('123456', 'hashed_code')

    def test_check_verification_code_invalid(self):
        """Test check_verification_code with invalid code."""
        user = User(email_verification_code_hash='hashed_code')
        
        with patch('app.models.user.check_password', return_value=False) as mock_check:
            result = user.check_verification_code('wrong_code')
            
            assert result is False
            mock_check.assert_called_once_with('wrong_code', 'hashed_code')

    def test_check_verification_code_no_hash(self):
        """Test check_verification_code when no hash is set."""
        user = User(email_verification_code_hash=None)
        
        result = user.check_verification_code('123456')
        
        assert result is False

    def test_clear_verification_code(self):
        """Test clear_verification_code method."""
        user = User(
            email_verification_code_hash='some_hash',
            verification_code_expires_at=timezone.now()
        )
        
        user.clear_verification_code()
        
        assert user.email_verification_code_hash is None
        assert user.verification_code_expires_at is None

    def test_is_verification_code_expired_no_expiry(self):
        """Test is_verification_code_expired when no expiry is set."""
        user = User(verification_code_expires_at=None)
        
        result = user.is_verification_code_expired()
        
        assert result is True

    def test_is_verification_code_expired_future_time(self):
        """Test is_verification_code_expired with future expiry time."""
        future_time = timezone.now() + timedelta(minutes=10)
        user = User(verification_code_expires_at=future_time)
        
        result = user.is_verification_code_expired()
        
        assert result is False

    def test_is_verification_code_expired_past_time(self):
        """Test is_verification_code_expired with past expiry time."""
        past_time = timezone.now() - timedelta(minutes=10)
        user = User(verification_code_expires_at=past_time)
        
        result = user.is_verification_code_expired()
        
        assert result is True

    # Last Login Tests
    @patch.object(User, 'save')
    @patch('app.models.user.timezone.now')
    def test_update_last_login(self, mock_now, mock_save):
        """Test update_last_login method."""
        fixed_time = timezone.now()
        mock_now.return_value = fixed_time
        
        user = User(last_login=None)
        
        user.update_last_login()
        
        assert user.last_login == fixed_time
        mock_save.assert_called_once_with(update_fields=['last_login'])

    # Field Validation Tests
    def test_email_field_is_unique(self):
        """Test that email field is configured as unique."""
        email_field = User._meta.get_field('email')
        assert email_field.unique is True

    def test_required_fields_not_blank(self):
        """Test that required fields are not blank."""
        first_name_field = User._meta.get_field('first_name')
        last_name_field = User._meta.get_field('last_name')
        email_field = User._meta.get_field('email')
        
        assert first_name_field.blank is False
        assert last_name_field.blank is False
        assert email_field.blank is False

    def test_verification_fields_allow_null(self):
        """Test that verification fields allow null values."""
        hash_field = User._meta.get_field('email_verification_code_hash')
        expiry_field = User._meta.get_field('verification_code_expires_at')
        
        assert hash_field.null is True
        assert expiry_field.null is True

    # Edge Cases Tests
    def test_user_instantiation_minimal_fields(self):
        """Test user can be instantiated with minimal required fields."""
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        # Check defaults are set correctly
        assert user.is_active is True  # Django default
        assert user.is_staff is False  # Django default
        assert user.is_email_verified is False  # Our default
        assert isinstance(user.id, uuid.UUID) or user.id is None  # UUID or None (if not saved)

    def test_verification_code_workflow(self):
        """Test complete verification code workflow."""
        user = User()
        
        # Set verification code
        with patch('app.models.user.make_password', return_value='hashed_123456'):
            user.set_verification_code('123456')
            assert user.email_verification_code_hash == 'hashed_123456'
        
        # Check valid code
        with patch('app.models.user.check_password', return_value=True):
            assert user.check_verification_code('123456') is True
        
        # Clear code
        user.clear_verification_code()
        assert user.email_verification_code_hash is None
        assert user.verification_code_expires_at is None

    def test_admin_promotion_workflow(self):
        """Test complete admin promotion/demotion workflow."""
        user = User(is_staff=False, is_superuser=False)
        
        # Check initial state
        assert user.is_admin_user() is False
        assert user.is_regular_user() is True  # Assuming is_active=True by default
        
        # Promote to admin
        with patch.object(user, 'save'):
            user.promote_to_admin()
            assert user.is_admin_user() is True
            assert user.is_regular_user() is False
        
        # Demote from admin
        with patch.object(user, 'save'):
            user.demote_from_admin()
            assert user.is_admin_user() is False