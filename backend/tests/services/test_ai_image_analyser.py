# type: ignore
from unittest.mock import Mock, patch, MagicMock, mock_open
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image
from app.services.ai_image_analyser import AiImageAnalyser
from app.models.image_submission import ImageSubmission
from app.models.image_analysis_result import ImageAnalysisResult
import pytest
import os
import tempfile
import uuid

class TestAiImageAnalyser:
    """
    Unit tests for AI Image Analyser Service.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 28/09/2025
    """

    @pytest.fixture
    def mock_ai_model(self):
        """Create a mock AI image model."""
        model = Mock()
        model.is_loaded.return_value = True
        model.predict.return_value = {
            'probability': 0.85,
            'is_ai_generated': True,
            'confidence': 0.92
        }
        return model

    @pytest.fixture
    def mock_claude_service(self):
        """Create a mock Claude service."""
        service = Mock()
        service.analyse_image_patterns.return_value = {
            'detection_reasons': [
                {
                    'type': 'critical',
                    'title': 'AI Artifacts Detected',
                    'description': 'Enhanced analysis found typical AI generation patterns',
                    'impact': 'High'
                }
            ]
        }
        service.create_image_submission_name.return_value = "AI Generated Landscape"
        return service

    @pytest.fixture
    def mock_user(self):
        """Create a mock authenticated user."""
        user = Mock()
        user.id = uuid.uuid4()
        user.email = 'test@example.com'
        user.is_authenticated = True
        return user

    @pytest.fixture
    def mock_submission(self):
        """Create a mock image submission."""
        submission = Mock()
        submission.id = uuid.uuid4()
        submission.name = 'Test Image'
        submission.image.url = 'https://example.com/image.jpg'
        return submission

    @pytest.fixture
    def temp_image_path(self):
        """Create a temporary image file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            # Create a simple test image
            test_image = Image.new('RGB', (100, 100), color='red')
            test_image.save(temp_file.name, 'JPEG')
            yield temp_file.name
        
        # Cleanup
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

    # Initialization Tests
    @patch('app.services.ai_image_analyser.ClaudeService')
    def test_init_with_claude_success(self, mock_claude_class, mock_ai_model):
        """Test successful initialization with Claude service."""
        mock_claude_instance = Mock()
        mock_claude_class.return_value = mock_claude_instance
        
        mock_ai_model.is_loaded.return_value = False
        
        analyser = AiImageAnalyser(mock_ai_model, use_claude=True)
        
        assert analyser.ai_model == mock_ai_model
        assert analyser.use_claude is True
        assert analyser.claude_service == mock_claude_instance
        mock_ai_model.load.assert_called_once()

    @patch('app.services.ai_image_analyser.ClaudeService')
    def test_init_claude_api_key_missing(self, mock_claude_class, mock_ai_model):
        """Test initialization when Claude API key is missing."""
        mock_claude_class.side_effect = ValueError("API key not found")
        
        analyser = AiImageAnalyser(mock_ai_model, use_claude=True)
        
        assert analyser.use_claude is False
        assert analyser.claude_service is None

    def test_init_without_claude(self, mock_ai_model):
        """Test initialization without Claude service."""
        analyser = AiImageAnalyser(mock_ai_model, use_claude=False)
        
        assert analyser.use_claude is False
        assert analyser.claude_service is None

    def test_init_loads_model_if_not_loaded(self, mock_ai_model):
        """Test that model is loaded during initialization if not already loaded."""
        mock_ai_model.is_loaded.return_value = False
        
        analyser = AiImageAnalyser(mock_ai_model)
        
        mock_ai_model.load.assert_called_once()
    
    def test_init_skips_loading_if_already_loaded(self, mock_ai_model):
        """Test that model loading is skipped if already loaded."""
        # New test: model already loaded, so loading should be skipped
        mock_ai_model.is_loaded.return_value = True
        
        analyser = AiImageAnalyser(mock_ai_model)
        
        mock_ai_model.load.assert_not_called()

    # Analysis Tests
    @patch('app.services.ai_image_analyser.time.time')
    @patch('app.services.ai_image_analyser.ClaudeService')
    def test_analyse_success_with_claude(self, mock_claude_class, mock_time, mock_ai_model, 
                                        temp_image_path, mock_user, mock_submission, mock_claude_service):
        """Test successful analysis with Claude enhancement."""
        # Setup mocks
        mock_claude_class.return_value = mock_claude_service
        mock_time.side_effect = [1000.0, 1001.5]  # Start and end times
        
        analyser = AiImageAnalyser(mock_ai_model, use_claude=True)
        
        with patch.object(analyser, '_save_analysis_result') as mock_save:
            mock_analysis = Mock()
            mock_analysis.id = uuid.uuid4()
            mock_save.return_value = mock_analysis
            
            result = analyser.analyse(temp_image_path, user=mock_user, submission=mock_submission)
            
            # Verify results
            assert result['prediction']['is_ai_generated'] is True
            assert result['prediction']['probability'] == 0.85
            assert result['metadata']['enhanced_analysis_used'] is True
            assert result['metadata']['processing_time_ms'] == 1500.0
            assert result['analysis_id'] == str(mock_analysis.id)
            
            # Verify Claude was called
            mock_claude_service.analyse_image_patterns.assert_called_once_with(temp_image_path, mock_ai_model.predict.return_value)

    @patch('app.services.ai_image_analyser.time.time')
    def test_analyse_success_without_claude(self, mock_time, mock_ai_model, temp_image_path):
        """Test successful analysis without Claude enhancement."""
        mock_time.side_effect = [1000.0, 1001.0]  # Start and end times
        
        analyser = AiImageAnalyser(mock_ai_model, use_claude=False)
        
        result = analyser.analyse(temp_image_path)
        
        # Verify results
        assert result['prediction']['is_ai_generated'] is True
        assert result['prediction']['probability'] == 0.85
        assert result['metadata']['enhanced_analysis_used'] is False
        assert result['metadata']['processing_time_ms'] == 1000.0
        assert 'analysis_id' not in result  # No user, so no saving

    def test_analyse_file_not_found(self, mock_ai_model):
        """Test analysis with non-existent file."""
        analyser = AiImageAnalyser(mock_ai_model)
        
        with pytest.raises(FileNotFoundError, match="Image file not found"):
            analyser.analyse("/non/existent/path.jpg")

    @patch('app.services.ai_image_analyser.Image.open')
    def test_analyse_invalid_image_format(self, mock_image_open, mock_ai_model, temp_image_path):
        """Test analysis with invalid image format."""
        # Mock PIL to raise an exception
        mock_image_open.side_effect = Exception("Cannot identify image file")
        
        analyser = AiImageAnalyser(mock_ai_model)
        
        with pytest.raises(ValueError, match="Invalid image file"):
            analyser.analyse(temp_image_path)

    @patch('app.services.ai_image_analyser.ClaudeService')
    def test_analyse_claude_failure_fallback(self, mock_claude_class, mock_ai_model, 
                                           temp_image_path, mock_claude_service):
        """Test that Claude failures don't break analysis."""
        mock_claude_class.return_value = mock_claude_service
        mock_claude_service.analyse_image_patterns.side_effect = Exception("Claude API error")
        
        analyser = AiImageAnalyser(mock_ai_model, use_claude=True)
        
        result = analyser.analyse(temp_image_path)
        
        # Should still work without Claude
        assert result['prediction']['is_ai_generated'] is True
        assert result['metadata']['enhanced_analysis_used'] is False

    @patch('app.services.ai_image_analyser.timezone.now')
    def test_analyse_failure_marks_result_as_failed(self, mock_now, mock_ai_model, temp_image_path, mock_user):
        """Test that analysis failure marks result as failed."""
        mock_ai_model.predict.side_effect = Exception("Model prediction failed")
        
        analyser = AiImageAnalyser(mock_ai_model)
        
        with pytest.raises(Exception, match="Model prediction failed"):
            analyser.analyse(temp_image_path, user=mock_user)

    # Save Analysis Result Tests
    @patch('app.services.ai_image_analyser.ContentType.objects.get_for_model')
    @patch('app.services.ai_image_analyser.ImageSubmission.objects.create')
    @patch('app.services.ai_image_analyser.ClaudeService')
    def test_save_analysis_result_creates_submission(self, mock_claude_class, mock_create_submission,
                                                   mock_content_type, mock_ai_model, mock_user, 
                                                   temp_image_path, mock_claude_service):
        """Test saving analysis result creates submission when none provided."""
        mock_claude_class.return_value = mock_claude_service
        mock_submission = Mock()
        mock_submission.id = uuid.uuid4()
        mock_create_submission.return_value = mock_submission
        
        mock_content_type_obj = Mock()
        mock_content_type.return_value = mock_content_type_obj
        
        analyser = AiImageAnalyser(mock_ai_model, use_claude=True)
        
        result = {'prediction': {'is_ai_generated': True}}
        
        with patch('builtins.open', mock_open(read_data=b'fake image data')):
            analysis_result = analyser._save_analysis_result(result, mock_user, None, temp_image_path, 1500.0)
            
            # Verify submission was created
            mock_create_submission.assert_called_once()
            mock_claude_service.create_image_submission_name.assert_called_once_with(temp_image_path, max_length=50)

    @patch('app.services.ai_image_analyser.ContentType.objects.get_for_model')
    def test_save_analysis_result_with_existing_submission(self, mock_content_type, mock_ai_model, 
                                                         mock_user, mock_submission, temp_image_path):
        """Test saving analysis result with existing submission."""
        mock_content_type_obj = Mock()
        mock_content_type.return_value = mock_content_type_obj
        
        analyser = AiImageAnalyser(mock_ai_model, use_claude=False)
        
        result = {'prediction': {'is_ai_generated': True}}
        
        with patch('app.services.ai_image_analyser.ImageAnalysisResult') as mock_analysis_class:
            mock_analysis = Mock()
            mock_analysis.id = uuid.uuid4()
            mock_analysis_class.return_value = mock_analysis
            
            analysis_result = analyser._save_analysis_result(result, mock_user, mock_submission, temp_image_path, 1000.0)
            
            # Verify analysis was created and saved
            assert analysis_result == mock_analysis
            mock_analysis.save_analysis_result.assert_called_once_with(result)
            mock_analysis.save.assert_called()

    def test_save_analysis_result_handles_exceptions(self, mock_ai_model, mock_user, temp_image_path):
        """Test that save analysis result handles exceptions gracefully."""
        analyser = AiImageAnalyser(mock_ai_model, use_claude=False)
        
        result = {'prediction': {'is_ai_generated': True}}
        
        with patch('app.services.ai_image_analyser.ContentType.objects.get_for_model') as mock_content_type:
            mock_content_type.side_effect = Exception("Database error")
            
            analysis_result = analyser._save_analysis_result(result, mock_user, None, temp_image_path, 1000.0)
            
            # Should return None on failure
            assert analysis_result is None

    # Preprocessing Tests
    def test_preprocess_valid_image(self, mock_ai_model, temp_image_path):
        """Test preprocessing with valid image."""
        analyser = AiImageAnalyser(mock_ai_model)
        
        result = analyser.preprocess(image_path=temp_image_path)
        
        assert result == temp_image_path

    def test_preprocess_file_not_found(self, mock_ai_model):
        """Test preprocessing with non-existent file."""
        analyser = AiImageAnalyser(mock_ai_model)
        
        with pytest.raises(FileNotFoundError, match="Image file not found"):
            analyser.preprocess(image_path="/non/existent/path.jpg")

    @patch('app.services.ai_image_analyser.Image.open')
    def test_preprocess_unsupported_format(self, mock_image_open, mock_ai_model, temp_image_path):
        """Test preprocessing with unsupported image format."""
        mock_img = Mock()
        mock_img.format = 'BMP'
        mock_image_open.return_value.__enter__.return_value = mock_img
        
        analyser = AiImageAnalyser(mock_ai_model)
        
        with pytest.raises(ValueError, match="Unsupported image format"):
            analyser.preprocess(image_path=temp_image_path)

    # Postprocessing Tests
    def test_postprocess_ai_generated_without_claude(self, mock_ai_model):
        """Test postprocessing AI-generated result without Claude."""
        analyser = AiImageAnalyser(mock_ai_model)
        
        model_output = {
            'probability': 0.85,
            'is_ai_generated': True,
            'confidence': 0.92
        }
        
        result = analyser.postprocess(model_output)
        
        assert result['prediction']['is_ai_generated'] is True
        assert result['prediction']['probability'] == 0.85
        assert result['metadata']['enhanced_analysis_used'] is False
        assert len(result['analysis']['detection_reasons']) == 1
        assert result['analysis']['detection_reasons'][0]['type'] == 'critical'

    def test_postprocess_human_generated_without_claude(self, mock_ai_model):
        """Test postprocessing human-generated result without Claude."""
        analyser = AiImageAnalyser(mock_ai_model)
        
        model_output = {
            'probability': 0.25,
            'is_ai_generated': False,
            'confidence': 0.88
        }
        
        result = analyser.postprocess(model_output)
        
        assert result['prediction']['is_ai_generated'] is False
        assert result['prediction']['probability'] == 0.25
        assert result['analysis']['detection_reasons'][0]['type'] == 'success'
        assert 'Human Content Detected' in result['analysis']['detection_reasons'][0]['title']

    def test_postprocess_with_claude_enhancement(self, mock_ai_model):
        """Test postprocessing with Claude enhanced analysis."""
        analyser = AiImageAnalyser(mock_ai_model)
        
        model_output = {
            'probability': 0.85,
            'is_ai_generated': True,
            'confidence': 0.92
        }
        
        enhanced_analysis = {
            'detection_reasons': [
                {
                    'type': 'critical',
                    'title': 'AI Artifacts Detected',
                    'description': 'Enhanced Claude analysis found typical patterns',
                    'impact': 'High'
                }
            ]
        }
        
        result = analyser.postprocess(model_output, enhanced_analysis)
        
        assert result['metadata']['enhanced_analysis_used'] is True
        assert result['analysis']['detection_reasons'] == enhanced_analysis['detection_reasons']

    def test_postprocess_handles_missing_values(self, mock_ai_model):
        """Test postprocessing handles missing values gracefully."""
        analyser = AiImageAnalyser(mock_ai_model)
        
        model_output = {}  # Empty output
        
        result = analyser.postprocess(model_output)
        
        assert result['prediction']['probability'] == 0.0
        assert result['prediction']['is_ai_generated'] is False
        assert result['prediction']['confidence'] == 0.0
        assert len(result['analysis']['detection_reasons']) == 1

    # Edge Cases
    def test_model_loading_during_analysis(self, mock_ai_model, temp_image_path):
        """Test that model is loaded during analysis if not already loaded."""
        mock_ai_model.is_loaded.return_value = False
        
        analyser = AiImageAnalyser(mock_ai_model)
        
        result = analyser.analyse(temp_image_path)
        
        # Model should be loaded during analysis
        assert mock_ai_model.load.call_count >= 2  # Once in init, once in analyse

    def test_rounding_precision(self, mock_ai_model):
        """Test that probabilities are rounded correctly."""
        analyser = AiImageAnalyser(mock_ai_model)
        
        model_output = {
            'probability': 0.123456789,
            'is_ai_generated': True,
            'confidence': 0.987654321
        }
        
        result = analyser.postprocess(model_output)
        
        assert result['prediction']['probability'] == 0.123
        assert result['prediction']['confidence'] == 0.988