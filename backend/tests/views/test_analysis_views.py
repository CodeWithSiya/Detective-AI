# type: ignore
from unittest.mock import Mock, patch
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime
from app.views.analysis_views import analyse_text, analyse_image, create_json_response
import pytest
import uuid

class TestAnalysisViews:
    """
    Unit tests for the Analysis Views (Text and Image).

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose 
    :version: 28/09/2025
    """

    @pytest.fixture
    def authenticated_user(self):
        """Create a mock authenticated user."""
        user = Mock()
        user.id = uuid.uuid4()
        user.username = 'testuser'
        user.email = 'test@example.com'
        user.is_authenticated = True
        return user

    @pytest.fixture
    def anonymous_user(self):
        """Create a mock anonymous user."""
        user = Mock()
        user.is_authenticated = False
        return user

    @pytest.fixture
    def api_factory(self):
        """Create APIRequestFactory instance."""
        return APIRequestFactory()

    @pytest.fixture
    def valid_text_data(self):
        """Create valid text analysis request data."""
        return {
            'text': 'This is a sample text for AI detection analysis.',
            'name': 'Sample Analysis'
        }

    @pytest.fixture
    def mock_analysis_result(self):
        """Create mock analysis result from AiTextAnalyser."""
        return {
            'prediction': {
                'is_ai_generated': True,
                'probability': 0.75,
                'confidence': 0.89
            },
            'analysis': {
                'detection_reasons': [
                    {'type': 'warning', 'title': 'AI patterns detected'}
                ]
            },
            'statistics': {
                'total_words': 20,
                'sentences': 2
            },
            'metadata': {
                'processing_time_ms': 1230.0
            }
        }

    @pytest.fixture
    def mock_image_analysis_result(self):
        """Create mock analysis result from AiImageAnalyser."""
        return {
            'prediction': {
                'is_ai_generated': False,
                'probability': 0.25,
                'confidence': 0.92
            },
            'analysis': {
                'detection_reasons': [
                    {'type': 'info', 'title': 'Natural image characteristics detected'}
                ]
            },
            'metadata': {
                'processing_time_ms': 850.0,
                'image_dimensions': [1024, 768],
                'file_size_mb': 2.3
            }
        }

    @pytest.fixture
    def mock_submission(self):
        """Create mock TextSubmission instance."""
        submission = Mock()
        submission.id = uuid.uuid4()
        submission.name = 'Test Submission'
        submission.created_at = datetime.now()
        return submission

    @pytest.fixture
    def mock_image_submission(self):
        """Create mock ImageSubmission instance."""
        submission = Mock()
        submission.id = uuid.uuid4()
        submission.name = 'Test Image Submission'
        submission.created_at = datetime.now()
        submission.image = Mock()
        submission.image.url = 'https://example.com/image.jpg'
        submission.file_size_mb = 2.3
        submission.dimensions = {'width': 1024, 'height': 768}
        return submission

    @pytest.fixture
    def valid_image_file(self):
        """Create a valid test image file."""
        return SimpleUploadedFile(
            "image.jpg",
            b"fake_image_content",
            content_type="image/jpeg"
        )

    @patch('app.views.analysis_views.TextSubmission')
    @patch('app.views.analysis_views.AiTextAnalyser')
    def test_analyse_text_success_authenticated_user(
        self, mock_analyser_class, mock_submission_class,
        api_factory, authenticated_user, valid_text_data, mock_analysis_result, mock_submission
    ):
        """Test successful text analysis for authenticated user."""
        # Setup mocks
        mock_analyser = Mock()
        mock_analyser.analyse.return_value = mock_analysis_result
        mock_analyser_class.return_value = mock_analyser
        mock_submission_class.objects.create.return_value = mock_submission

        # Create authenticated request
        request = api_factory.post('/api/analysis/text/', valid_text_data, format='json')
        force_authenticate(request, user=authenticated_user)

        # Call view
        response = analyse_text(request)

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Text analysis completed successfully'
        assert response.data['data']['analysis_result'] == mock_analysis_result
        assert 'submission' in response.data['data']

        # Verify service calls
        mock_analyser.analyse.assert_called_once_with(
            valid_text_data['text'], 
            user=authenticated_user, 
            submission=mock_submission
        )

    @patch('app.views.analysis_views.AiTextAnalyser')
    def test_analyse_text_success_anonymous_user(
        self, mock_analyser_class,
        api_factory, anonymous_user, valid_text_data, mock_analysis_result
    ):
        """Test successful text analysis for anonymous user."""
        # Setup mocks
        mock_analyser = Mock()
        mock_analyser.analyse.return_value = mock_analysis_result
        mock_analyser_class.return_value = mock_analyser

        # Create anonymous request
        request = api_factory.post('/api/analysis/text/', valid_text_data, format='json')
        force_authenticate(request, user=anonymous_user)

        # Call view
        response = analyse_text(request)

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['analysis_result'] == mock_analysis_result
        assert 'submission' not in response.data['data']

        # Verify analyser called with None submission
        mock_analyser.analyse.assert_called_once_with(
            valid_text_data['text'], 
            user=anonymous_user, 
            submission=None
        )

    def test_analyse_text_missing_text_field(self, api_factory, authenticated_user):
        """Test validation error when text field is missing."""
        request = api_factory.post('/api/analysis/text/', {'name': 'Test'}, format='json')
        force_authenticate(request, user=authenticated_user)

        response = analyse_text(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert response.data['error'] == 'Text field is required'

    @pytest.mark.parametrize("invalid_text", [None, '', '   '])
    def test_analyse_text_invalid_text_values(self, api_factory, authenticated_user, invalid_text):
        """Test validation with various invalid text values."""
        request = api_factory.post('/api/analysis/text/', {'text': invalid_text}, format='json')
        force_authenticate(request, user=authenticated_user)

        response = analyse_text(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Text field is required'

    @patch('app.views.analysis_views.ClaudeService')
    @patch('app.views.analysis_views.TextSubmission')
    @patch('app.views.analysis_views.AiTextAnalyser')
    def test_analyse_text_auto_generate_submission_name(
        self, mock_analyser_class, mock_submission_class,
        mock_claude_service_class, api_factory, authenticated_user, mock_analysis_result, mock_submission
    ):
        """Test automatic submission name generation when name is not provided."""
        # Setup mocks
        mock_analyser = Mock()
        mock_analyser.analyse.return_value = mock_analysis_result
        mock_analyser_class.return_value = mock_analyser

        mock_claude_service = Mock()
        mock_claude_service.create_text_submission_name.return_value = "AI-Generated Title"
        mock_claude_service_class.return_value = mock_claude_service

        mock_submission_class.objects.create.return_value = mock_submission

        # Create request without name
        request = api_factory.post('/api/analysis/text/', {'text': 'Sample text'}, format='json')
        force_authenticate(request, user=authenticated_user)

        # Call view
        response = analyse_text(request)

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        mock_claude_service.create_text_submission_name.assert_called_once_with('Sample text', max_length=50)

    @patch('app.views.analysis_views.AiTextAnalyser')
    def test_analyse_text_analysis_execution_failure(
        self, mock_analyser_class, api_factory, authenticated_user, valid_text_data
    ):
        """Test handling of analysis execution failure."""
        # Setup mocks - analyser fails during analysis
        mock_analyser = Mock()
        mock_analyser.analyse.side_effect = Exception("Text processing failed")
        mock_analyser_class.return_value = mock_analyser

        # Create request
        request = api_factory.post('/api/analysis/text/', valid_text_data, format='json')
        force_authenticate(request, user=authenticated_user)

        # Call view
        response = analyse_text(request)

        # Assertions
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False

    def test_analyse_text_http_methods(self, api_factory, authenticated_user):
        """Test that only POST method is allowed."""
        request = api_factory.get('/api/analysis/text/')
        force_authenticate(request, user=authenticated_user)

        response = analyse_text(request)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    # ===== Image Analysis Tests =====

    @patch('app.views.analysis_views.ImageSubmission')
    @patch('app.views.analysis_views.AiImageAnalyser')
    @patch('app.views.analysis_views.AiImageModel')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.unlink')
    def test_analyse_image_success_authenticated_user(
        self, mock_unlink, mock_temp_file, mock_model_class, mock_analyser_class,
        mock_submission_class, api_factory, authenticated_user, valid_image_file,
        mock_image_analysis_result, mock_image_submission
    ):
        """Test successful image analysis for authenticated user."""
        # Setup mocks
        mock_temp = Mock()
        mock_temp.name = '/tmp/test_image.jpg'
        mock_temp_file.return_value.__enter__.return_value = mock_temp
        mock_temp_file.return_value.__exit__.return_value = None

        mock_model = Mock()
        mock_model_class.return_value = mock_model

        mock_analyser = Mock()
        mock_analyser.analyse.return_value = mock_image_analysis_result
        mock_analyser_class.return_value = mock_analyser

        mock_submission_class.return_value = mock_image_submission

        # Create authenticated request
        request = api_factory.post('/api/analysis/image/', {
            'image': valid_image_file,
            'name': 'Test Image'
        })
        force_authenticate(request, user=authenticated_user)

        # Call view
        response = analyse_image(request)

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Image analysis completed successfully'
        assert response.data['data']['analysis_result'] == mock_image_analysis_result
        assert 'submission' in response.data['data']

    @patch('app.views.analysis_views.AiImageAnalyser')
    @patch('app.views.analysis_views.AiImageModel')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.unlink')
    def test_analyse_image_success_anonymous_user(
        self, mock_unlink, mock_temp_file, mock_model_class, mock_analyser_class,
        api_factory, anonymous_user, valid_image_file, mock_image_analysis_result
    ):
        """Test successful image analysis for anonymous user."""
        # Setup mocks
        mock_temp = Mock()
        mock_temp.name = '/tmp/test_image.jpg'
        mock_temp_file.return_value.__enter__.return_value = mock_temp
        mock_temp_file.return_value.__exit__.return_value = None

        mock_model = Mock()
        mock_model_class.return_value = mock_model

        mock_analyser = Mock()
        mock_analyser.analyse.return_value = mock_image_analysis_result
        mock_analyser_class.return_value = mock_analyser

        # Create anonymous request
        request = api_factory.post('/api/analysis/image/', {'image': valid_image_file})
        force_authenticate(request, user=anonymous_user)

        # Call view
        response = analyse_image(request)

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'submission' not in response.data['data']

    def test_analyse_image_missing_image_field(self, api_factory, authenticated_user):
        """Test validation error when image field is missing."""
        request = api_factory.post('/api/analysis/image/', {'name': 'Test'})
        force_authenticate(request, user=authenticated_user)

        response = analyse_image(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert response.data['error'] == 'Image file is required'

    def test_analyse_image_file_too_large(self, api_factory, authenticated_user):
        """Test validation error when image file is too large."""
        # Create a large file mock
        large_file = SimpleUploadedFile(
            "large_image.jpg",
            b"x" * (11 * 1024 * 1024),  # 11MB
            content_type="image/jpeg"
        )
        
        request = api_factory.post('/api/analysis/image/', {'image': large_file})
        force_authenticate(request, user=authenticated_user)

        response = analyse_image(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Image file too large. Maximum size is 10MB.'

    @pytest.mark.parametrize("invalid_extension", ['.gif', '.bmp', '.tiff', '.pdf'])
    def test_analyse_image_invalid_file_format(self, api_factory, authenticated_user, invalid_extension):
        """Test validation error for unsupported file formats."""
        invalid_file = SimpleUploadedFile(
            f"test{invalid_extension}",
            b"fake_content",
            content_type="application/octet-stream"
        )
        
        request = api_factory.post('/api/analysis/image/', {'image': invalid_file})
        force_authenticate(request, user=authenticated_user)

        response = analyse_image(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Unsupported file format' in response.data['error']

    @patch('app.views.analysis_views.AiImageModel')
    def test_analyse_image_model_initialization_failure(
        self, mock_model_class, api_factory, authenticated_user, valid_image_file
    ):
        """Test handling of model initialization failure."""
        mock_model_class.side_effect = Exception("Model loading failed")

        request = api_factory.post('/api/analysis/image/', {'image': valid_image_file})
        force_authenticate(request, user=authenticated_user)

        response = analyse_image(request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Image analysis failed: Model loading failed" in response.data['error']

    @patch('app.views.analysis_views.AiImageAnalyser')
    @patch('app.views.analysis_views.AiImageModel')
    @patch('tempfile.NamedTemporaryFile')
    def test_analyse_image_analysis_execution_failure(
        self, mock_temp_file, mock_model_class, mock_analyser_class,
        api_factory, authenticated_user, valid_image_file
    ):
        """Test handling of analysis execution failure."""
        # Setup mocks
        mock_temp = Mock()
        mock_temp.name = '/tmp/test_image.jpg'
        mock_temp_file.return_value.__enter__.return_value = mock_temp

        mock_model_class.return_value = Mock()
        
        mock_analyser = Mock()
        mock_analyser.analyse.side_effect = Exception("Image processing failed")
        mock_analyser_class.return_value = mock_analyser

        request = api_factory.post('/api/analysis/image/', {'image': valid_image_file})
        force_authenticate(request, user=authenticated_user)

        response = analyse_image(request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False

    def test_analyse_image_http_methods(self, api_factory, authenticated_user):
        """Test that only POST method is allowed for image analysis."""
        request = api_factory.get('/api/analysis/image/')
        force_authenticate(request, user=authenticated_user)

        response = analyse_image(request)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @patch('app.views.analysis_views.ClaudeService')
    @patch('app.views.analysis_views.ImageSubmission')
    @patch('app.views.analysis_views.AiImageAnalyser')
    @patch('app.views.analysis_views.AiImageModel')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.unlink')
    def test_analyse_image_auto_generate_submission_name(
        self, mock_unlink, mock_temp_file, mock_model_class, mock_analyser_class,
        mock_submission_class, mock_claude_service_class, api_factory, authenticated_user,
        valid_image_file, mock_image_analysis_result, mock_image_submission
    ):
        """Test automatic submission name generation for images."""
        # Setup mocks
        mock_temp = Mock()
        mock_temp.name = '/tmp/test_image.jpg'
        mock_temp_file.return_value.__enter__.return_value = mock_temp
        mock_temp_file.return_value.__exit__.return_value = None

        mock_model_class.return_value = Mock()
        
        mock_analyser = Mock()
        mock_analyser.analyse.return_value = mock_image_analysis_result
        mock_analyser_class.return_value = mock_analyser

        mock_claude_service = Mock()
        mock_claude_service.create_image_submission_name.return_value = "AI-Generated Image Title"
        mock_claude_service_class.return_value = mock_claude_service

        mock_submission_class.return_value = mock_image_submission

        # Create request without name
        request = api_factory.post('/api/analysis/image/', {'image': valid_image_file})
        force_authenticate(request, user=authenticated_user)

        response = analyse_image(request)

        assert response.status_code == status.HTTP_200_OK
        mock_claude_service.create_image_submission_name.assert_called_once()