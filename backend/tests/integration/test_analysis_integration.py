# type: ignore
from unittest.mock import Mock, patch, MagicMock
import pytest
import tempfile
import os
import uuid
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from app.views.analysis_views import analyse_text, analyse_image

class TestAnalysisWorkflowsIntegration:
    """
    Integration tests for Text and Image Analysis Workflows.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 28/09/2025
    """

    @pytest.fixture
    def api_factory(self):
        """Create APIRequestFactory instance."""
        return APIRequestFactory()

    @pytest.fixture
    def authenticated_user(self):
        """Create a mock authenticated user."""
        user = Mock()
        user.id = uuid.uuid4()
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
    def valid_image_file(self):
        """Create a valid test image file."""
        return SimpleUploadedFile(
            "test_image.jpg",
            b"fake_image_content",
            content_type="image/jpeg"
        )

    # Text Analysis Workflow Integration Tests
    @patch('app.views.analysis_views.TextSubmission.objects.create')
    @patch('app.views.analysis_views.AiTextAnalyser')
    def test_text_analysis_complete_workflow_authenticated_user(
        self, mock_analyser_class, mock_submission_create, api_factory, authenticated_user
    ):
        """Test complete text analysis workflow for authenticated user."""
        # Setup submission mock
        mock_submission = Mock()
        mock_submission.id = uuid.uuid4()
        mock_submission.created_at.isoformat.return_value = "2025-09-28T10:00:00Z"
        mock_submission_create.return_value = mock_submission
        
        # Setup analysis result mock
        mock_analysis_result = {
            'prediction': {
                'is_ai_generated': True,
                'probability': 0.85,
                'confidence': 0.92
            },
            'analysis': {
                'detection_reasons': [
                    {'type': 'critical', 'title': 'AI Detected', 'description': 'High confidence AI content'}
                ]
            },
            'analysis_id': str(uuid.uuid4())
        }
        
        # Setup analyser mock
        mock_analyser = Mock()
        mock_analyser.analyse.return_value = mock_analysis_result
        mock_analyser_class.return_value = mock_analyser
        
        # Create request
        request_data = {
            'text': 'This is a sample text for AI detection analysis.',
            'name': 'Test Analysis'
        }
        request = api_factory.post('/api/analysis/text/', request_data)
        force_authenticate(request, user=authenticated_user)
        
        # Execute workflow
        response = analyse_text(request)
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'data' in response.data
        
        # Verify analyser was created and used
        mock_analyser_class.assert_called_once()
        mock_analyser.analyse.assert_called_once_with(
            request_data['text'], 
            user=authenticated_user, 
            submission=mock_submission
        )
        
        # Verify submission was created
        mock_submission_create.assert_called_once()
        
        # Verify response includes submission data
        assert 'submission' in response.data['data']

    @patch('app.views.analysis_views.AiTextAnalyser')
    def test_text_analysis_complete_workflow_anonymous_user(
        self, mock_analyser_class, api_factory, anonymous_user
    ):
        """Test complete text analysis workflow for anonymous user."""
        # Setup analysis result mock
        mock_analysis_result = {
            'prediction': {
                'is_ai_generated': False,
                'probability': 0.25,
                'confidence': 0.88
            },
            'analysis': {
                'detection_reasons': [
                    {'type': 'success', 'title': 'Human Content', 'description': 'Appears human-written'}
                ]
            }
        }
        
        # Setup analyser mock
        mock_analyser = Mock()
        mock_analyser.analyse.return_value = mock_analysis_result
        mock_analyser_class.return_value = mock_analyser
        
        # Create request
        request_data = {'text': 'This is human-written content for testing.'}
        request = api_factory.post('/api/analysis/text/', request_data)
        force_authenticate(request, user=anonymous_user)
        
        # Execute workflow
        response = analyse_text(request)
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        
        # Verify no submission data for anonymous user
        assert 'submission' not in response.data['data']
        
        # Verify analysis was performed
        mock_analyser.analyse.assert_called_once_with(
            request_data['text'], 
            user=anonymous_user, 
            submission=None
        )

    # Image Analysis Workflow Integration Tests
    @patch('app.views.analysis_views.AiImageAnalyser')
    def test_image_analysis_complete_workflow_authenticated_user(
        self, mock_analyser_class, api_factory, authenticated_user, valid_image_file
    ):
        """Test complete image analysis workflow for authenticated user."""
        # Setup analysis result mock
        mock_analysis_result = {
            'prediction': {
                'is_ai_generated': True,
                'probability': 0.78,
                'confidence': 0.85
            },
            'analysis': {
                'detection_reasons': [
                    {'type': 'warning', 'title': 'AI Patterns Detected', 'description': 'Image shows AI characteristics'}
                ]
            },
            'analysis_id': str(uuid.uuid4())
        }
        
        # Setup analyser mock
        mock_analyser = Mock()
        mock_analyser.analyse.return_value = mock_analysis_result
        mock_analyser_class.return_value = mock_analyser
        
        # Create request
        request_data = {
            'image': valid_image_file,
            'name': 'Test Image Analysis'
        }
        request = api_factory.post('/api/analysis/image/', request_data)
        force_authenticate(request, user=authenticated_user)
        
        # Mock the ImageSubmission creation within the view
        with patch('app.views.analysis_views.ImageSubmission') as mock_submission_class:
            mock_submission_instance = mock_submission_class.return_value
            mock_submission_instance.id = uuid.uuid4()
            mock_submission_instance.name = 'Test Image Analysis'
            mock_submission_instance.image.url = 'https://storage.url/image.jpg'
            mock_submission_instance.file_size_mb = 2.5
            mock_submission_instance.dimensions = '1920x1080'
            mock_submission_instance.created_at.isoformat.return_value = "2025-09-28T10:00:00Z"
            
            # Execute workflow
            response = analyse_image(request)
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        
        # Verify analyser integration
        mock_analyser_class.assert_called_once()
        mock_analyser.analyse.assert_called_once()

    @patch('app.views.analysis_views.ClaudeService')
    @patch('app.views.analysis_views.AiImageAnalyser')
    def test_image_analysis_with_auto_naming_workflow(
        self, mock_analyser_class, mock_claude_service_class, 
        api_factory, authenticated_user, valid_image_file
    ):
        """Test image analysis workflow with automatic submission naming."""
        # Setup Claude service for auto-naming
        mock_claude_service = Mock()
        mock_claude_service.create_image_submission_name.return_value = "AI-Generated Landscape"
        mock_claude_service_class.return_value = mock_claude_service
        
        # Setup analysis result
        mock_analysis_result = {
            'prediction': {
                'is_ai_generated': True,
                'probability': 0.82,
                'confidence': 0.79
            },
            'analysis': {
                'detection_reasons': []
            }
        }
        
        # Setup analyser mock
        mock_analyser = Mock()
        mock_analyser.analyse.return_value = mock_analysis_result
        mock_analyser_class.return_value = mock_analyser
        
        # Create request without name
        request_data = {'image': valid_image_file}
        request = api_factory.post('/api/analysis/image/', request_data)
        force_authenticate(request, user=authenticated_user)
        
        # Mock submission creation within the view
        with patch('app.views.analysis_views.ImageSubmission') as mock_submission_class:
            mock_submission_instance = mock_submission_class.return_value
            mock_submission_instance.id = uuid.uuid4()
            mock_submission_instance.name = "AI-Generated Landscape"
            
            # Mock the temporary file creation
            with patch('tempfile.NamedTemporaryFile') as mock_temp_file:
                mock_temp = Mock()
                mock_temp.name = '/tmp/test_image.jpg'
                mock_temp_file.return_value.__enter__.return_value = mock_temp
                mock_temp_file.return_value.__exit__.return_value = None
                
                # Execute workflow
                response = analyse_image(request)
        
        # Verify Claude service was used for naming
        mock_claude_service.create_image_submission_name.assert_called_once_with(
            '/tmp/test_image.jpg', max_length=50
        )
        
        # Verify response success
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True

    @patch('app.views.analysis_views.AiImageAnalyser')
    def test_image_analysis_anonymous_user_workflow(
        self, mock_analyser_class, api_factory, anonymous_user, valid_image_file
    ):
        """Test image analysis workflow for anonymous user."""
        mock_analysis_result = {
            'prediction': {
                'is_ai_generated': False,
                'probability': 0.15,
                'confidence': 0.91
            },
            'analysis': {
                'detection_reasons': [
                    {'type': 'success', 'title': 'Human Content', 'description': 'Appears human-created'}
                ]
            }
        }
        
        mock_analyser = Mock()
        mock_analyser.analyse.return_value = mock_analysis_result
        mock_analyser_class.return_value = mock_analyser
        
        # Create request
        request = api_factory.post('/api/analysis/image/', {'image': valid_image_file})
        force_authenticate(request, user=anonymous_user)
        
        # Execute workflow
        response = analyse_image(request)
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        
        # Verify no submission for anonymous user
        assert 'submission' not in response.data['data']
        
        # Verify analysis was performed without submission
        mock_analyser.analyse.assert_called_once()

    # Error Handling Integration Tests
    @patch('app.views.analysis_views.AiTextAnalyser')
    def test_text_analysis_analyser_failure_workflow(
        self, mock_analyser_class, api_factory, authenticated_user
    ):
        """Test text analysis workflow when analyser fails."""
        # Make analyser initialization or analysis fail
        mock_analyser = Mock()
        mock_analyser.analyse.side_effect = Exception("Analysis failed")
        mock_analyser_class.return_value = mock_analyser
        
        request_data = {'text': 'Test text for analysis'}
        request = api_factory.post('/api/analysis/text/', request_data)
        force_authenticate(request, user=authenticated_user)
        
        # Execute workflow
        response = analyse_text(request)
        
        # Verify error response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False

    @patch('app.views.analysis_views.AiImageAnalyser')
    def test_image_analysis_processing_failure_workflow(
        self, mock_analyser_class, api_factory, authenticated_user, valid_image_file
    ):
        """Test image analysis workflow when image processing fails."""
        # Make analyser fail
        mock_analyser = Mock()
        mock_analyser.analyse.side_effect = Exception("Image processing failed")
        mock_analyser_class.return_value = mock_analyser
        
        request = api_factory.post('/api/analysis/image/', {'image': valid_image_file})
        force_authenticate(request, user=authenticated_user)
        
        # Execute workflow
        response = analyse_image(request)
        
        # Verify error response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False

    # Validation Integration Tests
    def test_text_analysis_validation_workflow(self, api_factory, authenticated_user):
        """Test text analysis workflow with validation errors."""
        # Test missing text field
        request = api_factory.post('/api/analysis/text/', {'name': 'Test'})
        force_authenticate(request, user=authenticated_user)
        
        response = analyse_text(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert 'required' in response.data['error'].lower()

    def test_image_analysis_validation_workflow(self, api_factory, authenticated_user):
        """Test image analysis workflow with validation errors."""
        # Test missing image field
        request = api_factory.post('/api/analysis/image/', {'name': 'Test'})
        force_authenticate(request, user=authenticated_user)
        
        response = analyse_image(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert 'Image file is required' in response.data['error']

    def test_image_analysis_file_size_validation_workflow(self, api_factory, authenticated_user):
        """Test image analysis workflow with file size validation."""
        # Create oversized file
        large_file = SimpleUploadedFile(
            "large_image.jpg",
            b"x" * (11 * 1024 * 1024),  # 11MB
            content_type="image/jpeg"
        )
        
        request = api_factory.post('/api/analysis/image/', {'image': large_file})
        force_authenticate(request, user=authenticated_user)
        
        response = analyse_image(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'too large' in response.data['error'].lower()

    # Service Integration Tests
    @patch('app.views.analysis_views.TextSubmission.objects.create')
    @patch('app.views.analysis_views.AiTextAnalyser')
    @patch('app.views.analysis_views.AiImageAnalyser')
    def test_concurrent_text_and_image_analysis_workflow(
        self, mock_image_analyser_class, mock_text_analyser_class, mock_text_submission_create, 
        api_factory, authenticated_user, valid_image_file
    ):
        """Test that text and image analysis can work independently and concurrently."""
        # Setup text analysis mocks
        mock_text_submission = Mock(id=uuid.uuid4())
        mock_text_submission.created_at.isoformat.return_value = "2025-09-28T10:00:00Z"
        mock_text_submission_create.return_value = mock_text_submission
        
        mock_text_result = {
            'prediction': {'is_ai_generated': True, 'probability': 0.8, 'confidence': 0.85},
            'analysis': {'detection_reasons': []},
            'analysis_id': str(uuid.uuid4())
        }
        mock_text_analyser = Mock()
        mock_text_analyser.analyse.return_value = mock_text_result
        mock_text_analyser_class.return_value = mock_text_analyser
        
        # Setup image analysis mocks
        mock_image_result = {
            'prediction': {'is_ai_generated': False, 'probability': 0.3, 'confidence': 0.78},
            'analysis': {'detection_reasons': []},
            'analysis_id': str(uuid.uuid4())
        }
        mock_image_analyser = Mock()
        mock_image_analyser.analyse.return_value = mock_image_result
        mock_image_analyser_class.return_value = mock_image_analyser
        
        # Execute text analysis
        text_request = api_factory.post('/api/analysis/text/', {
            'text': 'Sample text for analysis',
            'name': 'Text Analysis'
        })
        force_authenticate(text_request, user=authenticated_user)
        text_response = analyse_text(text_request)
        
        # Execute image analysis
        image_request = api_factory.post('/api/analysis/image/', {
            'image': valid_image_file,
            'name': 'Image Analysis'
        })
        force_authenticate(image_request, user=authenticated_user)
        
        with patch('app.views.analysis_views.ImageSubmission') as mock_submission_class:
            mock_submission_instance = mock_submission_class.return_value
            mock_submission_instance.id = uuid.uuid4()
            mock_submission_instance.name = 'Image Analysis'
            mock_submission_instance.image.url = 'https://storage.url/image.jpg'
            mock_submission_instance.file_size_mb = 2.5
            mock_submission_instance.dimensions = '1920x1080'
            mock_submission_instance.created_at.isoformat.return_value = "2025-09-28T10:00:00Z"
            
            image_response = analyse_image(image_request)
        
        # Verify both analyses succeeded independently
        assert text_response.status_code == status.HTTP_200_OK
        assert text_response.data['success'] is True
        assert image_response.status_code == status.HTTP_200_OK
        assert image_response.data['success'] is True
        
        # Verify both analysers were used
        mock_text_analyser_class.assert_called_once()
        mock_image_analyser_class.assert_called_once()
        
        # Verify both analyses were performed
        mock_text_analyser.analyse.assert_called_once()
        mock_image_analyser.analyse.assert_called_once()

    # Database Integration Test
    @patch('app.views.analysis_views.TextSubmission.objects.create')
    @patch('app.views.analysis_views.AiTextAnalyser')
    def test_database_persistence_workflow(
        self, mock_analyser_class, mock_submission_create, api_factory, authenticated_user
    ):
        """Test that analysis results are properly persisted to database."""
        # Setup submission mock
        mock_submission = Mock()
        mock_submission.id = uuid.uuid4()
        mock_submission.name = 'Database Test'
        mock_submission.created_at.isoformat.return_value = "2025-09-28T10:00:00Z"
        mock_submission_create.return_value = mock_submission
        
        # Setup analysis result with database ID
        analysis_id = str(uuid.uuid4())
        mock_analysis_result = {
            'prediction': {
                'is_ai_generated': True,
                'probability': 0.89,
                'confidence': 0.94
            },
            'analysis': {
                'detection_reasons': [
                    {'type': 'critical', 'title': 'Strong AI Indicators', 'description': 'Multiple AI patterns detected'}
                ]
            },
            'analysis_id': analysis_id  # This indicates successful database save
        }
        
        mock_analyser = Mock()
        mock_analyser.analyse.return_value = mock_analysis_result
        mock_analyser_class.return_value = mock_analyser
        
        # Create request
        request_data = {
            'text': 'Test text for database persistence',
            'name': 'Database Test'
        }
        request = api_factory.post('/api/analysis/text/', request_data)
        force_authenticate(request, user=authenticated_user)
        
        # Execute workflow
        response = analyse_text(request)
        
        # Verify response includes analysis ID (indicating database save)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'analysis_id' in response.data['data']['analysis_result']
        assert response.data['data']['analysis_result']['analysis_id'] == analysis_id
        
        # Verify submission was created with correct data
        mock_submission_create.assert_called_once_with(
            name='Database Test',
            content='Test text for database persistence',
            user=authenticated_user
        )