# type: ignore
from unittest.mock import Mock, patch, mock_open, MagicMock
import pytest
from django.core.files.base import ContentFile
from django.test import override_settings
from app.services.supabase_storage_service import SupabaseStorage, SupabaseStorageService
import os
import uuid
import requests

class TestSupabaseStorage:
    """
    Unit tests for Supabase Storage (Django Storage Backend).

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 28/09/2025
    """

    @pytest.fixture
    def mock_supabase_client(self):
        """Create mock Supabase client."""
        with patch('app.services.supabase_storage_service.create_client') as mock_create:
            mock_client = Mock()
            mock_create.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def storage_instance(self, mock_supabase_client):
        """Create storage instance with mocked client."""
        with override_settings(
            SUPABASE_URL='https://test.supabase.co',
            SUPABASE_SERVICE_ROLE_KEY='test-key',
            SUPABASE_BUCKET_NAME='test-bucket'
        ):
            return SupabaseStorage()

    @pytest.fixture
    def mock_content_file(self):
        """Create mock content file."""
        content = b"test image content"
        return ContentFile(content, name="test.jpg")

    # Save Method Tests
    def test_save_success(self, storage_instance, mock_supabase_client, mock_content_file):
        """Test successful file save."""
        # Mock successful upload
        mock_supabase_client.storage.from_.return_value.upload.return_value = {'path': 'test.jpg'}
        
        result = storage_instance._save('test.jpg', mock_content_file)
        
        assert result == 'test.jpg'
        mock_supabase_client.storage.from_.assert_called_with('test-bucket')

    def test_save_file_exists_update_success(self, storage_instance, mock_supabase_client, mock_content_file):
        """Test save when file exists, update succeeds."""
        # Mock upload failure (file exists), then successful update
        mock_supabase_client.storage.from_.return_value.upload.side_effect = Exception("already exists")
        mock_supabase_client.storage.from_.return_value.update.return_value = {'path': 'test.jpg'}
        
        result = storage_instance._save('test.jpg', mock_content_file)
        
        assert result == 'test.jpg'
        # Verify update was called after upload failed
        mock_supabase_client.storage.from_.return_value.update.assert_called_once()

    def test_save_file_exists_generate_unique_name(self, storage_instance, mock_supabase_client, mock_content_file):
        """Test save when file exists and update fails, generates unique name."""
        # Mock upload and update failures
        mock_supabase_client.storage.from_.return_value.upload.side_effect = [
            Exception("already exists"),  # First upload fails
            {'path': 'test_12345678.jpg'}  # Second upload with unique name succeeds
        ]
        mock_supabase_client.storage.from_.return_value.update.side_effect = Exception("update failed")
        
        with patch('app.services.supabase_storage_service.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = Mock()
            mock_uuid.return_value.__str__ = Mock(return_value='12345678-1234-1234-1234-123456789012')
            
            result = storage_instance._save('test.jpg', mock_content_file)
            
            # Should return unique filename
            assert 'test_' in result
            assert result.endswith('.jpg')

    def test_save_exception_handling(self, storage_instance, mock_supabase_client, mock_content_file):
        """Test save with unhandled exception."""
        mock_supabase_client.storage.from_.return_value.upload.side_effect = Exception("Network error")
        
        with pytest.raises(Exception, match="Failed to save file to Supabase: Network error"):
            storage_instance._save('test.jpg', mock_content_file)

    # Open Method Tests
    @patch('app.services.supabase_storage_service.requests.get')
    def test_open_success(self, mock_get, storage_instance, mock_supabase_client):
        """Test successful file open."""
        # Mock URL generation and HTTP response
        mock_supabase_client.storage.from_.return_value.get_public_url.return_value = 'https://example.com/test.jpg'
        
        mock_response = Mock()
        mock_response.content = b"test image content"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        file_obj = storage_instance._open('test.jpg')
        
        assert isinstance(file_obj, ContentFile)
        assert file_obj.read() == b"test image content"
        mock_get.assert_called_once_with('https://example.com/test.jpg')

    @patch('app.services.supabase_storage_service.requests.get')
    def test_open_http_error(self, mock_get, storage_instance, mock_supabase_client):
        """Test file open with HTTP error."""
        mock_supabase_client.storage.from_.return_value.get_public_url.return_value = 'https://example.com/test.jpg'
        mock_get.side_effect = requests.RequestException("File not found")
        
        with pytest.raises(Exception, match="Failed to open file test.jpg"):
            storage_instance._open('test.jpg')

    # URL Method Tests
    def test_url_success(self, storage_instance, mock_supabase_client):
        """Test successful URL generation."""
        mock_supabase_client.storage.from_.return_value.get_public_url.return_value = 'https://example.com/test.jpg'
        
        url = storage_instance.url('test.jpg')
        
        assert url == 'https://example.com/test.jpg'

    def test_url_empty_name(self, storage_instance):
        """Test URL with empty name."""
        url = storage_instance.url('')
        assert url == ""

    def test_url_fallback(self, storage_instance, mock_supabase_client):
        """Test URL fallback when Supabase method fails."""
        mock_supabase_client.storage.from_.return_value.get_public_url.side_effect = Exception("API error")
        
        with override_settings(SUPABASE_URL='https://test.supabase.co', SUPABASE_BUCKET_NAME='test-bucket'):
            url = storage_instance.url('test.jpg')
            
            assert url == 'https://test.supabase.co/storage/v1/object/public/test-bucket/test.jpg'

    # Exists Method Tests
    def test_exists_true(self, storage_instance, mock_supabase_client):
        """Test file exists check returns True."""
        mock_supabase_client.storage.from_.return_value.list.return_value = [
            {'name': 'test.jpg', 'size': 1024}
        ]
        
        exists = storage_instance.exists('test.jpg')
        assert exists is True

    def test_exists_false(self, storage_instance, mock_supabase_client):
        """Test file exists check returns False."""
        mock_supabase_client.storage.from_.return_value.list.return_value = [
            {'name': 'other.jpg', 'size': 1024}
        ]
        
        exists = storage_instance.exists('test.jpg')
        assert exists is False

    def test_exists_exception_handling(self, storage_instance, mock_supabase_client):
        """Test exists with exception returns False."""
        mock_supabase_client.storage.from_.return_value.list.side_effect = Exception("API error")
        
        exists = storage_instance.exists('test.jpg')
        assert exists is False

    # Size Method Tests
    def test_size_success(self, storage_instance, mock_supabase_client):
        """Test successful file size retrieval."""
        mock_supabase_client.storage.from_.return_value.list.return_value = [
            {'name': 'test.jpg', 'metadata': {'size': 2048}}
        ]
        
        size = storage_instance.size('test.jpg')
        assert size == 2048

    def test_size_file_not_found(self, storage_instance, mock_supabase_client):
        """Test size when file not found returns 0."""
        mock_supabase_client.storage.from_.return_value.list.return_value = []
        
        size = storage_instance.size('test.jpg')
        assert size == 0

    def test_size_exception_handling(self, storage_instance, mock_supabase_client):
        """Test size with exception returns 0."""
        mock_supabase_client.storage.from_.return_value.list.side_effect = Exception("API error")
        
        size = storage_instance.size('test.jpg')
        assert size == 0

    # Delete Method Tests
    def test_delete_success(self, storage_instance, mock_supabase_client):
        """Test successful file deletion."""
        mock_supabase_client.storage.from_.return_value.remove.return_value = True
        
        # Should not raise exception
        storage_instance.delete('test.jpg')
        
        mock_supabase_client.storage.from_.return_value.remove.assert_called_once_with(['test.jpg'])

    def test_delete_exception_handling(self, storage_instance, mock_supabase_client):
        """Test delete with exception (should pass silently)."""
        mock_supabase_client.storage.from_.return_value.remove.side_effect = Exception("API error")
        
        # Should not raise exception
        storage_instance.delete('test.jpg')

    # Content Type Tests
    def test_get_content_type_jpg(self, storage_instance):
        """Test content type detection for JPG."""
        content_type = storage_instance._get_content_type('test.jpg')
        assert content_type == 'image/jpeg'

    def test_get_content_type_png(self, storage_instance):
        """Test content type detection for PNG."""
        content_type = storage_instance._get_content_type('test.png')
        assert content_type == 'image/png'

    def test_get_content_type_unknown(self, storage_instance):
        """Test content type for unknown extension."""
        content_type = storage_instance._get_content_type('test.xyz')
        assert content_type == 'application/octet-stream'

    # Unique Name Generation Tests
    def test_get_unique_name(self, storage_instance):
        """Test unique name generation."""
        with patch('app.services.supabase_storage_service.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = Mock()
            mock_uuid.return_value.__str__ = Mock(return_value='12345678-1234-1234-1234-123456789012')
            
            unique_name = storage_instance._get_unique_name('test.jpg')
            
            assert unique_name.startswith('test_12345678')
            assert unique_name.endswith('.jpg')


class TestSupabaseStorageService:
    """
    Unit tests for Supabase Storage Service (Direct Operations).

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 28/09/2025
    """

    @pytest.fixture
    def mock_supabase_client(self):
        """Create mock Supabase client."""
        with patch('app.services.supabase_storage_service.create_client') as mock_create:
            mock_client = Mock()
            mock_create.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def service_instance(self, mock_supabase_client):
        """Create service instance with mocked client."""
        with override_settings(
            SUPABASE_URL='https://test.supabase.co',
            SUPABASE_SERVICE_ROLE_KEY='test-key',
            SUPABASE_BUCKET_NAME='test-bucket'
        ):
            return SupabaseStorageService()

    # Upload Image Tests
    @patch('builtins.open', new_callable=mock_open, read_data=b"test image data")
    def test_upload_image_success(self, mock_file, service_instance, mock_supabase_client):
        """Test successful image upload."""
        mock_supabase_client.storage.from_.return_value.upload.return_value = {'path': 'images/test.jpg'}
        
        with override_settings(SUPABASE_URL='https://test.supabase.co', SUPABASE_BUCKET_NAME='test-bucket'):
            url = service_instance.upload_image('/local/test.jpg', 'images/test.jpg')
            
            expected_url = 'https://test.supabase.co/storage/v1/object/public/test-bucket/images/test.jpg'
            assert url == expected_url
            
            # Verify upload was called
            mock_supabase_client.storage.from_.assert_called_with('test-bucket')

    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    def test_upload_image_file_not_found(self, mock_file, service_instance):
        """Test upload when local file not found."""
        with pytest.raises(Exception, match="Failed to upload image"):
            service_instance.upload_image('/nonexistent/test.jpg', 'images/test.jpg')

    @patch('builtins.open', new_callable=mock_open, read_data=b"test image data")
    def test_upload_image_upload_failure(self, mock_file, service_instance, mock_supabase_client):
        """Test upload when Supabase upload fails."""
        mock_supabase_client.storage.from_.return_value.upload.side_effect = Exception("Upload failed")
        
        with pytest.raises(Exception, match="Failed to upload image: Upload failed"):
            service_instance.upload_image('/local/test.jpg', 'images/test.jpg')

    @patch('builtins.open', new_callable=mock_open, read_data=b"test image data")
    def test_upload_image_no_response(self, mock_file, service_instance, mock_supabase_client):
        """Test upload when no response received."""
        mock_supabase_client.storage.from_.return_value.upload.return_value = None
        
        with pytest.raises(Exception, match="Upload failed: No response received"):
            service_instance.upload_image('/local/test.jpg', 'images/test.jpg')

    # Get Public URL Tests
    def test_get_public_url(self, service_instance):
        """Test public URL generation."""
        with override_settings(SUPABASE_URL='https://test.supabase.co', SUPABASE_BUCKET_NAME='test-bucket'):
            url = service_instance.get_public_url('images/test.jpg')
            
            expected_url = 'https://test.supabase.co/storage/v1/object/public/test-bucket/images/test.jpg'
            assert url == expected_url

    # Delete File Tests
    def test_delete_file_success(self, service_instance, mock_supabase_client):
        """Test successful file deletion."""
        mock_supabase_client.storage.from_.return_value.remove.return_value = {'success': True}
        
        result = service_instance.delete_file('images/test.jpg')
        
        assert result is True
        mock_supabase_client.storage.from_.return_value.remove.assert_called_once_with(['images/test.jpg'])

    def test_delete_file_failure(self, service_instance, mock_supabase_client):
        """Test file deletion failure."""
        mock_supabase_client.storage.from_.return_value.remove.side_effect = Exception("Delete failed")
        
        result = service_instance.delete_file('images/test.jpg')
        
        assert result is False

    def test_delete_file_none_response(self, service_instance, mock_supabase_client):
        """Test file deletion with None response."""
        mock_supabase_client.storage.from_.return_value.remove.return_value = None
        
        result = service_instance.delete_file('images/test.jpg')
        
        assert result is False

    # Content Type Tests
    def test_get_content_type_service_jpg(self, service_instance):
        """Test service content type detection for JPG."""
        content_type = service_instance._get_content_type('/path/to/test.jpg')
        assert content_type == 'image/jpeg'

    def test_get_content_type_service_webp(self, service_instance):
        """Test service content type detection for WebP."""
        content_type = service_instance._get_content_type('/path/to/test.webp')
        assert content_type == 'image/webp'

    def test_get_content_type_service_unknown(self, service_instance):
        """Test service content type for unknown extension."""
        content_type = service_instance._get_content_type('/path/to/test.xyz')
        assert content_type == 'application/octet-stream'