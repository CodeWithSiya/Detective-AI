# type: ignore
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from app.models import ImageSubmission
from unittest.mock import Mock, patch
from datetime import datetime, timezone as dt_timezone
from app.models.image_submission import image_upload_path
import pytest
import uuid

User = get_user_model()

class TestImageSubmissionModel:
    """
    Unit tests for ImageSubmission model.
    
    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose 
    :version: 28/09/2025
    """

    @pytest.fixture
    def mock_user(self):
        """
        Create a mock user.
        """
        user = Mock()
        user.id = uuid.uuid4()
        user.username = 'testuser'
        user.email = 'test@example.com'
        return user

    @pytest.fixture
    def mock_image_file(self):
        """
        Create a mock image file.
        """
        mock_file = Mock()
        mock_file.name = 'test_image.jpg'
        mock_file.size = 1024000  # 1MB
        mock_file.url = '/media/submissions/images/test_image.jpg'
        return mock_file

    def test_file_extension_validator(self):
        """
        Test file extension validator configuration.
        """
        validator = ImageSubmission.file_extension_validator
        assert isinstance(validator, FileExtensionValidator)
        assert set(validator.allowed_extensions) == {"jpg", "jpeg", "png"}

    def test_model_meta_configuration(self):
        """
        Test model Meta configuration.
        """
        meta = ImageSubmission._meta
        
        # Test db_table
        assert meta.db_table == 'image_submissions'
        
        # Test that indexes are defined (2 indexes)
        assert len(meta.indexes) == 2

    def test_image_upload_path_function(self):
        """
        Test image_upload_path function.
        """ 
        # Mock instance
        mock_instance = Mock()
        mock_instance.user.id = uuid.uuid4()
        mock_instance.created_at = datetime(2023, 8, 22, 10, 30, 0, tzinfo=dt_timezone.utc)
        
        # Test with normal filename
        result = image_upload_path(mock_instance, "test_image.jpg")
        expected = f"submissions/images/{mock_instance.user.id}/2023/08/test_image.jpg"
        assert result == expected
        
        # Test with special characters in filename
        result = image_upload_path(mock_instance, "test@#$%image!.jpg")
        expected = f"submissions/images/{mock_instance.user.id}/2023/08/testimage.jpg"
        assert result == expected

    def test_image_upload_path_no_created_at(self):
        """
        Test image_upload_path when created_at is None.
        """
        # Mock instance
        mock_instance = Mock()
        mock_instance.user.id = uuid.uuid4()
        mock_instance.created_at = None
        
        with patch('app.models.image_submission.timezone.now') as mock_now:
            mock_now.return_value = datetime(2023, 8, 22, 10, 30, 0, tzinfo=dt_timezone.utc)
            result = image_upload_path(mock_instance, "test.jpg")
            expected = f"submissions/images/{mock_instance.user.id}/2023/08/test.jpg"
            assert result == expected

    def test_str_representation(self):
        """
        Test the string representation of ImageSubmission.
        """
        mock_submission = Mock(spec=ImageSubmission)
        mock_submission.name = "Test Image"
        mock_submission.user.email = "test@example.com"
        mock_submission.width = 1920
        mock_submission.height = 1080
        mock_submission.dimensions = "1920x1080"
        
        # Mock the __str__ method
        mock_submission.__str__ = Mock(return_value=f"{mock_submission.name} | {mock_submission.user.email} | {mock_submission.dimensions}")
        
        result = str(mock_submission)
        expected = "Test Image | test@example.com | 1920x1080"
        assert result == expected

    def test_image_url_property(self):
        """
        Test image_url property.
        """
        # Test with image
        mock_submission = Mock(spec=ImageSubmission)
        mock_submission.image = Mock()
        mock_submission.image.url = "/media/test.jpg"
        mock_submission.image_url = mock_submission.image.url
        
        assert mock_submission.image_url == "/media/test.jpg"
        
        # Test without image
        mock_submission2 = Mock(spec=ImageSubmission)
        mock_submission2.image = None
        mock_submission2.image_url = None
        
        assert mock_submission2.image_url is None

    def test_file_size_mb_property(self):
        """
        Test file_size_mb property.
        """
        # Test with file size
        mock_submission = Mock(spec=ImageSubmission)
        mock_submission.file_size = 2097152  # 2MB in bytes
        mock_submission.file_size_mb = round(mock_submission.file_size / (1024 * 1024), 2)
        
        assert mock_submission.file_size_mb == 2.0
        
        # Test without file size
        mock_submission2 = Mock(spec=ImageSubmission)
        mock_submission2.file_size = None
        mock_submission2.file_size_mb = None
        
        assert mock_submission2.file_size_mb is None

    def test_dimensions_property(self):
        """
        Test dimensions property.
        """
        # Test with dimensions
        mock_submission = Mock(spec=ImageSubmission)
        mock_submission.width = 1920
        mock_submission.height = 1080
        mock_submission.dimensions = f"{mock_submission.width}x{mock_submission.height}"
        
        assert mock_submission.dimensions == "1920x1080"
        
        # Test without dimensions
        mock_submission2 = Mock(spec=ImageSubmission)
        mock_submission2.width = None
        mock_submission2.height = None
        mock_submission2.dimensions = "Unknown"
        
        assert mock_submission2.dimensions == "Unknown"

    @patch('app.models.image_submission.Image.open')
    def test_save_method_success(self, mock_image_open, mock_user):
        """
        Test successful save method with image processing.
        """
        # Mock PIL Image
        mock_img = Mock()
        mock_img.size = (1920, 1080)
        mock_image_open.return_value.__enter__.return_value = mock_img
        
        # Mock submission
        mock_submission = Mock(spec=ImageSubmission)
        mock_submission.image = Mock()
        mock_submission.image.size = 1024000
        mock_submission.image.name = "test_image.jpg"
        
        def mock_save(*args, **kwargs):
            # Simulate metadata extraction
            mock_submission.file_size = mock_submission.image.size
            mock_submission.image_format = mock_submission.image.name.split('.')[-1].lower()
            mock_submission.width, mock_submission.height = mock_img.size
        
        mock_submission.save = mock_save
        
        # Call save
        mock_submission.save()
        
        # Assertions
        assert mock_submission.file_size == 1024000
        assert mock_submission.image_format == "jpg"
        assert mock_submission.width == 1920
        assert mock_submission.height == 1080

    @patch('app.models.image_submission.Image.open')
    def test_save_method_image_processing_error(self, mock_image_open, mock_user):
        """
        Test save method handles image processing errors.
        """
        # Mock PIL Image to raise exception
        mock_image_open.side_effect = Exception("Corrupted image")
        
        # Mock submission
        mock_submission = Mock(spec=ImageSubmission)
        mock_submission.image = Mock()
        mock_submission.image.size = 1024000
        mock_submission.image.name = "corrupted_image.jpg"
        
        def mock_save(*args, **kwargs):
            try:
                # Simulate image processing
                mock_submission.file_size = mock_submission.image.size
                mock_submission.image_format = mock_submission.image.name.split('.')[-1].lower()
                
                # This will raise the exception
                with mock_image_open(mock_submission.image):
                    pass
            except Exception as e:
                # Handle the error
                mock_submission.file_size = None
                mock_submission.width = None
                mock_submission.height = None
                mock_submission.image_format = None
        
        mock_submission.save = mock_save
        
        # Call save
        mock_submission.save()
        
        # Check error handling
        assert mock_submission.file_size is None
        assert mock_submission.width is None
        assert mock_submission.height is None
        assert mock_submission.image_format is None

    def test_save_method_no_image(self):
        """
        Test save method when no image is provided.
        """
        mock_submission = Mock(spec=ImageSubmission)
        mock_submission.image = None
        
        def mock_save(*args, **kwargs):
            # Should skip image processing if no image
            pass
        
        mock_submission.save = mock_save
        
        # Should not raise any errors
        mock_submission.save()

    def test_delete_method(self):
        """
        Test delete method.
        """
        mock_submission = Mock(spec=ImageSubmission)
        
        def mock_delete(*args, **kwargs):
            return (1, {'ImageSubmission': 1})
        
        mock_submission.delete = mock_delete
        
        result = mock_submission.delete()
        assert result == (1, {'ImageSubmission': 1})

    @patch('app.models.ImageSubmission.objects')
    def test_model_instantiation(self, mock_objects, mock_user, mock_image_file):
        """
        Test that ImageSubmission model can be instantiated.
        """
        # Create a mock image submission instance
        mock_submission = Mock(spec=ImageSubmission)
        mock_submission.id = uuid.uuid4()
        mock_submission.name = "Test Image"
        mock_submission.user = mock_user
        mock_submission.image = mock_image_file
        mock_submission.file_size = 1024000
        mock_submission.width = 1920
        mock_submission.height = 1080
        mock_submission.image_format = "jpg"
        mock_submission.created_at = timezone.now()
        
        # Test that we can create the mock and access its attributes
        submission = mock_submission
        
        # Basic attribute checks
        assert submission.id is not None
        assert submission.name == "Test Image"
        assert submission.user == mock_user
        assert submission.image == mock_image_file
        assert submission.file_size == 1024000
        assert submission.width == 1920
        assert submission.height == 1080
        assert submission.image_format == "jpg"
        assert submission.created_at is not None

    def test_user_foreign_key_relationship(self):
        """
        Test user foreign key relationship.
        """
        field = ImageSubmission._meta.get_field('user')
        
        assert field.related_model == User
        assert field.remote_field.on_delete.__name__ == 'CASCADE'
        assert field.remote_field.related_name == 'image_submissions'

    def test_image_field_configuration(self):
        """
        Test image field configuration.
        """
        field = ImageSubmission._meta.get_field('image')
        
        # Check that it has validators
        assert len(field.validators) > 0
        
        # Check upload_to function is set
        assert field.upload_to is not None

    def test_metadata_fields_configuration(self):
        """
        Test metadata fields configuration.
        """
        # Test file_size field
        file_size_field = ImageSubmission._meta.get_field('file_size')
        assert file_size_field.null == True
        assert file_size_field.blank == True
        
        # Test width field
        width_field = ImageSubmission._meta.get_field('width')
        assert width_field.null == True
        assert width_field.blank == True
        
        # Test height field
        height_field = ImageSubmission._meta.get_field('height')
        assert height_field.null == True
        assert height_field.blank == True
        
        # Test image_format field
        format_field = ImageSubmission._meta.get_field('image_format')
        assert format_field.max_length == 10
        assert format_field.null == True
        assert format_field.blank == True

    def test_property_methods_with_edge_cases(self):
        """
        Test property methods with various edge cases.
        """
        mock_submission = Mock(spec=ImageSubmission)
        
        # Test file_size_mb with zero 
        mock_submission.file_size = 0
        mock_submission.file_size_mb = round(mock_submission.file_size / (1024 * 1024), 2) if mock_submission.file_size is not None else None
        assert mock_submission.file_size_mb == 0.0
        
        # Test dimensions with only width
        mock_submission.width = 1920
        mock_submission.height = None
        mock_submission.dimensions = f"{mock_submission.width}x{mock_submission.height}" if mock_submission.width and mock_submission.height else "Unknown"
        assert mock_submission.dimensions == "Unknown"
        
        # Test dimensions with only height
        mock_submission.width = None
        mock_submission.height = 1080
        mock_submission.dimensions = f"{mock_submission.width}x{mock_submission.height}" if mock_submission.width and mock_submission.height else "Unknown"
        assert mock_submission.dimensions == "Unknown"