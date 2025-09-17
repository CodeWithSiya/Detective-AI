# type: ignore
from unittest.mock import Mock, patch
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from datetime import datetime
from app.views.analysis_views import analyse_text
import pytest
import uuid

class TestAnalysisViews:
    """
    Unit tests for the Text Analysis View.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose 
    :version: 16/09/2025
    """

    @pytest.fixture
    def authenticated_user(self):
        """
        Create a mock authenticated user.
        """
        user = Mock()
        user.id = uuid.uuid4()
        user.username = 'testuser'
        user.email = 'test@example.com'
        user.is_authenticated = True
        return user

    @pytest.fixture
    def anonymous_user(self):
        """
        Create a mock anonymous user.
        """
        user = Mock()
        user.is_authenticated = False
        return user

    @pytest.fixture
    def api_factory(self):
        """
        Create APIRequestFactory instance.
        """
        return APIRequestFactory()

    @pytest.fixture
    def valid_text_data(self):
        """
        Create valid text analysis request data.
        """
        return {
            'text': 'This is a sample text for AI detection analysis.',
            'name': 'Sample Analysis'
        }

    @pytest.fixture
    def mock_analysis_result(self):
        """
        Create mock analysis result from AiTextAnalyser.
        """
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
    def mock_submission(self):
        """Create mock TextSubmission instance."""
        submission = Mock()
        submission.id = uuid.uuid4()
        submission.name = 'Test Submission'
        submission.created_at = datetime.now()
        return submission
    
    @patch('app.views.analysis_views.TextSubmission')
    @patch('app.views.analysis_views.AiTextAnalyser')
    @patch('app.views.analysis_views.AiTextModel')
    def test_analyse_text_success_authenticated_user(
        self, mock_model_class, mock_analyser_class, mock_submission_class,
        api_factory, authenticated_user, valid_text_data, mock_analysis_result, mock_submission
    ):
        """
        Test successful text analysis for authenticated user.
        """
        # Setup mocks.
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        mock_analyser = Mock()
        mock_analyser.analyse.return_value = mock_analysis_result
        mock_analyser_class.return_value = mock_analyser

        mock_submission_class.objects.create.return_value = mock_submission

        # Create authenticated request.
        request = api_factory.post('/api/analysis/text/', valid_text_data, format='json')
        force_authenticate(request, user=authenticated_user)

        # Call view.
        response = analyse_text(request)

        # Assertions.
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Text analysis completed successfully'
        assert response.data['data']['analysis_result'] == mock_analysis_result
        assert 'submission' in response.data['data']

        # Verify service calls.
        mock_analyser.analyse.assert_called_once_with(
            valid_text_data['text'], 
            user=authenticated_user, 
            submission=mock_submission
        )
    
    @patch('app.views.analysis_views.AiTextAnalyser')
    @patch('app.views.analysis_views.AiTextModel')
    def test_analyse_text_success_anonymous_user(
        self, mock_model_class, mock_analyser_class,
        api_factory, anonymous_user, valid_text_data, mock_analysis_result
    ):
        """
        Test successful text analysis for anonymous user.
        """
        # Setup mocks.
        mock_model = Mock()
        mock_model_class.return_value = mock_model
        
        mock_analyser = Mock()
        mock_analyser.analyse.return_value = mock_analysis_result
        mock_analyser_class.return_value = mock_analyser

        # Create anonymous request.
        request = api_factory.post('/api/analysis/text/', valid_text_data, format='json')
        force_authenticate(request, user=anonymous_user)

        # Call view.
        response = analyse_text(request)

        # Assertions.
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
        """
        Test validation error when text field is missing.
        """
        # Create authenticated request.
        request = api_factory.post('/api/analysis/text/', {'name': 'Test'}, format='json')
        force_authenticate(request, user=authenticated_user)

        # Create anonymous request.
        response = analyse_text(request)

        # Verify analyser called with None submission.
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert response.data['error'] == 'Text field is required'

    @pytest.mark.parametrize("invalid_text", [None, '', '   '])
    def test_analyse_text_invalid_text_values(self, api_factory, authenticated_user, invalid_text):
        """
        Test validation with various invalid text values.
        """
        # Create authenticated request.
        request = api_factory.post('/api/analysis/text/', {'text': invalid_text}, format='json')
        force_authenticate(request, user=authenticated_user)

        # Create anonymous request.
        response = analyse_text(request)

        # Verify analyser called with None submission.
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Text field is required'

    @patch('app.views.analysis_views.ClaudeService')
    @patch('app.views.analysis_views.TextSubmission')
    @patch('app.views.analysis_views.AiTextAnalyser')
    @patch('app.views.analysis_views.AiTextModel')
    def test_analyse_text_auto_generate_submission_name(
        self, mock_model_class, mock_analyser_class, mock_submission_class,
        mock_claude_service_class, api_factory, authenticated_user, mock_analysis_result, mock_submission
    ):
        """
        Test automatic submission name generation when name is not provided.
        """
        # Setup mocks.
        mock_model_class.return_value = Mock()
        mock_analyser = Mock()
        mock_analyser.analyse.return_value = mock_analysis_result
        mock_analyser_class.return_value = mock_analyser

        mock_claude_service = Mock()
        mock_claude_service.create_submission_name.return_value = "AI-Generated Title"
        mock_claude_service_class.return_value = mock_claude_service

        mock_submission_class.objects.create.return_value = mock_submission

        # Create request without name.
        request = api_factory.post('/api/analysis/text/', {'text': 'Sample text'}, format='json')
        force_authenticate(request, user=authenticated_user)

        # Call view.
        response = analyse_text(request)

        # Assertions.
        assert response.status_code == status.HTTP_200_OK
        mock_claude_service.create_submission_name.assert_called_once_with('Sample text', max_length=50)

    @patch('app.views.analysis_views.ClaudeService')
    @patch('app.views.analysis_views.TextSubmission')
    @patch('app.views.analysis_views.AiTextAnalyser')
    @patch('app.views.analysis_views.AiTextModel')
    def test_analyse_text_claude_service_fallback(
        self, mock_model_class, mock_analyser_class, mock_submission_class,
        mock_claude_service_class, api_factory, authenticated_user, mock_analysis_result, mock_submission
    ):
        """
        Test fallback name generation when Claude service fails.
        """
        # Setup mocks.
        mock_model_class.return_value = Mock()
        mock_analyser = Mock()
        mock_analyser.analyse.return_value = mock_analysis_result
        mock_analyser_class.return_value = mock_analyser

        # Mock Claude service to raise exception.
        mock_claude_service = Mock()
        mock_claude_service.create_submission_name.side_effect = Exception("Claude API timeout")
        mock_claude_service_class.return_value = mock_claude_service

        mock_submission_class.objects.create.return_value = mock_submission

        # Create request without name.
        request = api_factory.post('/api/analysis/text/', {'text': 'Sample text'}, format='json')
        force_authenticate(request, user=authenticated_user)

        # Call view.
        response = analyse_text(request)

        # Assertions.
        assert response.status_code == status.HTTP_200_OK
        
        # Verify fallback name was used.
        call_args = mock_submission_class.objects.create.call_args
        created_name = call_args[1]['name']
        assert 'Text Analysis' in created_name

    @patch('app.views.analysis_views.AiTextAnalyser')
    @patch('app.views.analysis_views.AiTextModel')
    def test_analyse_text_model_initialisation_failure(
        self, mock_model_class, mock_analyser_class,
        api_factory, authenticated_user, valid_text_data
    ):
        """
        Test handling of model initialization failure.
        """
        # Setup model to raise exception during initialization
        mock_model_class.side_effect = Exception("Model loading failed")

        # Create request
        request = api_factory.post('/api/analysis/text/', valid_text_data, format='json')
        force_authenticate(request, user=authenticated_user)

        # Call view
        response = analyse_text(request)

        # Assertions
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False
        assert "Analysis failed: Model loading failed" in response.data['error']

    @patch('app.views.analysis_views.TextSubmission')
    @patch('app.views.analysis_views.AiTextAnalyser')
    @patch('app.views.analysis_views.AiTextModel')
    def test_analyse_text_analysis_execution_failure(
        self, mock_model_class, mock_analyser_class, mock_submission_class,
        api_factory, authenticated_user, valid_text_data
    ):
        """
        Test handling of analysis execution failure.
        """
        # Setup mocks - analyser fails during analysis.
        mock_model_class.return_value = Mock()
        mock_analyser = Mock()
        mock_analyser.analyse.side_effect = Exception("Text processing failed")
        mock_analyser_class.return_value = mock_analyser

        # Prevent actual DB call.
        mock_submission_class.objects.create.return_value = Mock()

        # Create request.
        request = api_factory.post('/api/analysis/text/', valid_text_data, format='json')
        force_authenticate(request, user=authenticated_user)

        # Call view.
        response = analyse_text(request)

        # Assertions.
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False
        assert "Analysis failed: Text processing failed" in response.data['error']

    @patch('app.views.analysis_views.TextSubmission')
    @patch('app.views.analysis_views.AiTextAnalyser')
    @patch('app.views.analysis_views.AiTextModel')
    def test_analyse_text_submission_creation_failure(
        self, mock_model_class, mock_analyser_class, mock_submission_class,
        api_factory, authenticated_user, valid_text_data
    ):
        """
        Test handling of submission creation failure for authenticated users.
        """
        # Setup mocks.
        mock_model_class.return_value = Mock()
        mock_analyser = Mock()
        mock_analyser_class.return_value = mock_analyser

        # Mock submission creation to fail.
        mock_submission_class.objects.create.side_effect = Exception("Database constraint violation")

        # Create request.
        request = api_factory.post('/api/analysis/text/', valid_text_data, format='json')
        force_authenticate(request, user=authenticated_user)

        # Call view.
        response = analyse_text(request)

        # Assertions.
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False
        assert "Analysis failed: Database constraint violation" in response.data['error']

    def test_analyse_text_http_methods(self, api_factory, authenticated_user):
        """
        Test that only POST method is allowed.
        """
        # Create request.
        request = api_factory.get('/api/analysis/text/')
        force_authenticate(request, user=authenticated_user)

        # Call view.
        response = analyse_text(request)

        # Assertions.
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_analyse_text_allows_anonymous_access(self, api_factory, valid_text_data):
        """
        Test that the view allows anonymous access.
        """
        with patch('app.views.analysis_views.AiTextModel'), \
             patch('app.views.analysis_views.AiTextAnalyser'):
            request = api_factory.post('/api/analysis/text/', valid_text_data, format='json')
            response = analyse_text(request)
            
            # Should not be permission denied.
            assert response.status_code != status.HTTP_401_UNAUTHORIZED
            assert response.status_code != status.HTTP_403_FORBIDDEN

    @patch('app.views.analysis_views.ClaudeService')
    @patch('app.views.analysis_views.TextSubmission')
    @patch('app.views.analysis_views.AiTextAnalyser')
    @patch('app.views.analysis_views.AiTextModel')
    def test_analyse_text_partial_failure_continues_analysis(
        self, mock_model_class, mock_analyser_class, mock_submission_class,
        mock_claude_service_class, api_factory, authenticated_user, mock_analysis_result
    ):
        """
        Test that analysis continues even if Claude service fails.
        """
        # Setup mocks - Claude fails but analysis should continue.
        mock_model_class.return_value = Mock()
        mock_analyser = Mock()
        mock_analyser.analyse.return_value = mock_analysis_result  # Analysis still succeeds.
        mock_analyser_class.return_value = mock_analyser

        mock_claude_service_class.side_effect = Exception("Claude service unavailable")
        mock_submission_class.objects.create.side_effect = Exception("DB error")

        # Create request without name (would trigger Claude usage).
        request = api_factory.post('/api/analysis/text/', {'text': 'Sample text'}, format='json')
        force_authenticate(request, user=authenticated_user)

        # Call view.
        response = analyse_text(request)

        # Assertions - should fail because submission creation failed.
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False

    def test_analyse_text_invalid_json_request(self, api_factory, authenticated_user):
        """
        Test handling of invalid request data.
        """
        # Create request with invalid data structure.
        request = api_factory.post('/api/analysis/text/', 'invalid json', content_type='application/json')
        force_authenticate(request, user=authenticated_user)

        # Call view.
        response = analyse_text(request)

        # Assertions.
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'JSON parse error' in response.data['detail']