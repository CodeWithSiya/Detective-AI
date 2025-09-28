# type: ignore
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from app.services.ai_text_analyser import AiTextAnalyser
from app.models.text_submission import TextSubmission
from app.models.text_analysis_result import TextAnalysisResult
from app.ai.ai_text_model import AiTextModel
from app.ai.ai_short_text_model import AiShortTextModel
import pytest
import uuid

class TestAiTextAnalyser:
    """
    Unit tests for AI Text Analyser Service.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 28/09/2025
    """

    @pytest.fixture
    def mock_long_text_model(self):
        """Create a mock long text AI model."""
        model = Mock(spec=AiTextModel)
        model.is_loaded.return_value = True
        model.predict.return_value = {
            'probability': 0.85,
            'is_ai_generated': True,
            'confidence': 0.92
        }
        return model

    @pytest.fixture
    def mock_short_text_model(self):
        """Create a mock short text AI model."""
        model = Mock(spec=AiShortTextModel)
        model.is_loaded.return_value = True
        model.predict.return_value = {
            'probability': 0.65,
            'is_ai_generated': True,
            'confidence': 0.78
        }
        return model

    @pytest.fixture
    def mock_claude_service(self):
        """Create a mock Claude service."""
        service = Mock()
        service.analyse_text_patterns.return_value = {
            'detection_reasons': [
                {
                    'type': 'critical',
                    'title': 'AI Keywords Detected',
                    'description': 'Found typical AI-generated patterns',
                    'impact': 'High'
                }
            ],
            'analysis_details': {
                'found_keywords': ['optimize', 'streamline'],
                'found_patterns': ['repetitive structure'],
                'found_transitions': ['furthermore', 'moreover']
            }
        }
        service.create_text_submission_name.return_value = "AI Analysis Sample"
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
        """Create a mock text submission."""
        submission = Mock()
        submission.id = uuid.uuid4()
        submission.name = 'Test Text'
        submission.content = 'Sample text content'
        return submission

    # Initialization Tests
    @patch('app.services.ai_text_analyser.AiShortTextModel')
    @patch('app.services.ai_text_analyser.ClaudeService')
    def test_init_with_provided_model_and_claude(self, mock_claude_class, mock_short_class, mock_long_text_model):
        """Test initialization with provided model and Claude."""
        mock_claude_instance = Mock()
        mock_claude_class.return_value = mock_claude_instance
        mock_short_instance = Mock()
        mock_short_class.return_value = mock_short_instance
        
        analyser = AiTextAnalyser(ai_model=mock_long_text_model, use_claude=True)
        
        assert analyser.long_text_model == mock_long_text_model
        assert analyser.short_text_model == mock_short_instance
        assert analyser.use_claude is True
        assert analyser.claude_service == mock_claude_instance
        assert analyser.short_text_threshold == 50

    @patch('app.services.ai_text_analyser.AiTextModel')
    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_init_without_provided_model(self, mock_short_class, mock_long_class):
        """Test initialization without providing a model (backward compatibility)."""
        mock_long_instance = Mock()
        mock_long_class.return_value = mock_long_instance
        mock_short_instance = Mock()
        mock_short_class.return_value = mock_short_instance
        
        analyser = AiTextAnalyser(use_claude=False)
        
        assert analyser.long_text_model == mock_long_instance
        assert analyser.short_text_model == mock_short_instance
        assert analyser.use_claude is False
        assert analyser.claude_service is None

    @patch('app.services.ai_text_analyser.AiShortTextModel')
    @patch('app.services.ai_text_analyser.ClaudeService')
    def test_init_claude_api_key_missing(self, mock_claude_class, mock_short_class, mock_long_text_model):
        """Test initialization when Claude API key is missing."""
        mock_claude_class.side_effect = ValueError("API key not found")
        mock_short_class.return_value = Mock()
        
        analyser = AiTextAnalyser(ai_model=mock_long_text_model, use_claude=True)
        
        assert analyser.use_claude is False
        assert analyser.claude_service is None

    # Model Selection Tests
    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_select_model_short_text(self, mock_short_class, mock_long_text_model):
        """Test model selection for short text."""
        mock_short_instance = Mock()
        mock_short_class.return_value = mock_short_instance
        
        analyser = AiTextAnalyser(ai_model=mock_long_text_model, use_claude=False)
        
        # Text with 30 characters (below threshold of 50)
        short_text = "This is a short text sample."
        selected_model, model_type = analyser._select_model(short_text)
        
        assert selected_model == mock_short_instance
        assert model_type == "short_text"

    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_select_model_long_text(self, mock_short_class, mock_long_text_model):
        """Test model selection for long text."""
        mock_short_class.return_value = Mock()
        
        analyser = AiTextAnalyser(ai_model=mock_long_text_model, use_claude=False)
        
        # Text with more than 50 characters
        long_text = "This is a much longer text sample that exceeds the threshold for short text analysis."
        selected_model, model_type = analyser._select_model(long_text)
        
        assert selected_model == mock_long_text_model
        assert model_type == "long_text"

    # Analysis Tests
    @patch('app.services.ai_text_analyser.time.time')
    @patch('app.services.ai_text_analyser.AiShortTextModel')
    @patch('app.services.ai_text_analyser.ClaudeService')
    def test_analyse_success_with_claude_long_text(self, mock_claude_class, mock_short_class, 
                                                  mock_time, mock_long_text_model, mock_claude_service):
        """Test successful analysis with Claude for long text."""
        # Setup mocks
        mock_claude_class.return_value = mock_claude_service
        mock_short_class.return_value = Mock()
        mock_time.side_effect = [1000.0, 1001.5]  # Start and end times
        
        analyser = AiTextAnalyser(ai_model=mock_long_text_model, use_claude=True)
        
        long_text = "This is a comprehensive analysis of artificial intelligence and machine learning technologies."
        
        result = analyser.analyse(long_text)
        
        # Verify results
        assert result['prediction']['is_ai_generated'] is True
        assert result['prediction']['probability'] == 0.85
        assert result['metadata']['enhanced_analysis_used'] is True
        assert result['metadata']['model_used'] == 'long_text'
        assert result['metadata']['processing_time_ms'] == 1500.0
        assert 'statistics' in result
        
        # Verify Claude was called
        mock_claude_service.analyse_text_patterns.assert_called_once()

    @patch('app.services.ai_text_analyser.time.time')
    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_analyse_success_short_text_without_claude(self, mock_short_class, mock_time, mock_long_text_model):
        """Test successful analysis for short text without Claude."""
        mock_short_instance = Mock()
        mock_short_instance.is_loaded.return_value = True
        mock_short_instance.predict.return_value = {
            'probability': 0.65,
            'is_ai_generated': True,
            'confidence': 0.78
        }
        mock_short_class.return_value = mock_short_instance
        mock_time.side_effect = [1000.0, 1001.0]
        
        analyser = AiTextAnalyser(ai_model=mock_long_text_model, use_claude=False)
        
        short_text = "Short sample text."
        result = analyser.analyse(short_text)
        
        # Verify results
        assert result['prediction']['is_ai_generated'] is True
        assert result['prediction']['probability'] == 0.65
        assert result['metadata']['enhanced_analysis_used'] is False
        assert result['metadata']['model_used'] == 'short_text'
        assert result['metadata']['text_length'] == len(short_text.strip())

    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_analyse_model_loading_if_not_loaded(self, mock_short_class, mock_long_text_model):
        """Test that model is loaded if not already loaded during analysis."""
        mock_short_instance = Mock()
        mock_short_instance.is_loaded.return_value = False  # Not loaded
        mock_short_instance.predict.return_value = {'probability': 0.5, 'is_ai_generated': False, 'confidence': 0.6}
        mock_short_class.return_value = mock_short_instance
        
        analyser = AiTextAnalyser(ai_model=mock_long_text_model, use_claude=False)
        
        result = analyser.analyse("Short text")
        
        # Verify model was loaded
        mock_short_instance.load.assert_called_once()

    @patch('app.services.ai_text_analyser.AiShortTextModel')
    @patch('app.services.ai_text_analyser.ClaudeService')
    def test_analyse_claude_failure_fallback(self, mock_claude_class, mock_short_class, 
                                           mock_long_text_model, mock_claude_service):
        """Test that Claude failures don't break analysis."""
        # Mocks
        mock_claude_class.return_value = mock_claude_service
        mock_claude_service.analyse_text_patterns.side_effect = Exception("Claude API error")
        mock_short_instance = Mock()
        mock_short_instance.is_loaded.return_value = True
        mock_short_instance.predict.return_value = {
            'probability': 0.75,
            'is_ai_generated': True,
            'confidence': 0.85
        }
        mock_short_class.return_value = mock_short_instance
        
        analyser = AiTextAnalyser(ai_model=mock_long_text_model, use_claude=True)
        
        result = analyser.analyse("Test text for analysis")
        
        # Should still work without Claude
        assert result['prediction']['is_ai_generated'] is True
        assert result['metadata']['enhanced_analysis_used'] is False

    @patch('app.services.ai_text_analyser.AiShortTextModel')
    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_analyse_with_authenticated_user(self, mock_short_class, mock_long_text_model, mock_user):
        """Test analysis with authenticated user saves result."""
        # Mocks
        mock_short_instance = Mock()
        mock_short_instance.is_loaded.return_value = True
        mock_short_instance.predict.return_value = {
            'probability': 0.65,
            'is_ai_generated': True,
            'confidence': 0.78
        }
        mock_short_class.return_value = mock_short_instance
        
        analyser = AiTextAnalyser(ai_model=mock_long_text_model, use_claude=False)
        
        with patch.object(analyser, '_save_analysis_result') as mock_save:
            mock_analysis = Mock()
            mock_analysis.id = uuid.uuid4()
            mock_save.return_value = mock_analysis
            
            result = analyser.analyse("Test text", user=mock_user)
            
            # Verify result was saved
            assert result['analysis_id'] == str(mock_analysis.id)
            mock_save.assert_called_once()

    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_analyse_exception_handling(self, mock_short_class, mock_long_text_model):
        """Test analysis exception handling."""
        mock_short_instance = Mock()
        mock_short_instance.predict.side_effect = Exception("Model prediction failed")
        mock_short_class.return_value = mock_short_instance
        
        analyser = AiTextAnalyser(ai_model=mock_long_text_model, use_claude=False)
        
        with pytest.raises(Exception, match="Model prediction failed"):
            analyser.analyse("Test text")

    # Save Analysis Result Tests
    @patch('app.services.ai_text_analyser.ContentType.objects.get_for_model')
    @patch('app.services.ai_text_analyser.TextSubmission.objects.create')
    @patch('app.services.ai_text_analyser.ClaudeService')
    def test_save_analysis_result_creates_submission(self, mock_claude_class, mock_create_submission,
                                                   mock_content_type, mock_long_text_model, mock_user, 
                                                   mock_claude_service):
        """Test saving analysis result creates submission when none provided."""
        mock_claude_class.return_value = mock_claude_service
        mock_submission = Mock()
        mock_submission.id = uuid.uuid4()
        mock_create_submission.return_value = mock_submission
        
        mock_content_type_obj = Mock()
        mock_content_type.return_value = mock_content_type_obj
        
        analyser = AiTextAnalyser(ai_model=mock_long_text_model, use_claude=True)
        
        result = {'prediction': {'is_ai_generated': True}}
        text = "Sample text for analysis"
        
        with patch('app.services.ai_text_analyser.TextAnalysisResult') as mock_analysis_class:
            mock_analysis = Mock()
            mock_analysis.id = uuid.uuid4()
            mock_analysis_class.return_value = mock_analysis
            
            analysis_result = analyser._save_analysis_result(result, mock_user, None, text, 1500.0)
            
            # Verify submission was created
            mock_create_submission.assert_called_once()
            mock_claude_service.create_text_submission_name.assert_called_once_with(text, max_length=50)

    @patch('app.services.ai_text_analyser.ContentType.objects.get_for_model')
    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_save_analysis_result_with_existing_submission(self, mock_short_class, mock_content_type, 
                                                         mock_long_text_model, mock_user, mock_submission):
        """Test saving analysis result with existing submission."""
        mock_short_class.return_value = Mock()
        mock_content_type_obj = Mock()
        mock_content_type.return_value = mock_content_type_obj
        
        analyser = AiTextAnalyser(ai_model=mock_long_text_model, use_claude=False)
        
        result = {'prediction': {'is_ai_generated': True}}
        
        with patch('app.services.ai_text_analyser.TextAnalysisResult') as mock_analysis_class:
            mock_analysis = Mock()
            mock_analysis.id = uuid.uuid4()
            mock_analysis_class.return_value = mock_analysis
            
            analysis_result = analyser._save_analysis_result(result, mock_user, mock_submission, "text", 1000.0)
            
            # Verify analysis was created and saved
            assert analysis_result == mock_analysis
            mock_analysis.save_analysis_result.assert_called_once_with(result)
            mock_analysis.save.assert_called()

    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_save_analysis_result_handles_exceptions(self, mock_short_class, mock_long_text_model, mock_user):
        """Test that save analysis result handles exceptions gracefully."""
        mock_short_class.return_value = Mock()
        analyser = AiTextAnalyser(ai_model=mock_long_text_model, use_claude=False)
        
        result = {'prediction': {'is_ai_generated': True}}
        
        with patch('app.services.ai_text_analyser.ContentType.objects.get_for_model') as mock_content_type:
            mock_content_type.side_effect = Exception("Database error")
            
            analysis_result = analyser._save_analysis_result(result, mock_user, None, "text", 1000.0)
            
            # Should return None on failure
            assert analysis_result is None

    # Preprocessing Tests
    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_preprocess_cleans_text(self, mock_short_class, mock_long_text_model):
        """Test text preprocessing removes extra whitespace."""
        mock_short_class.return_value = Mock()
        analyser = AiTextAnalyser(ai_model=mock_long_text_model)
        
        messy_text = "  This   has    lots of    spaces   "
        cleaned = analyser.preprocess(messy_text)
        
        assert cleaned == "This has lots of spaces"

    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_preprocess_strips_text(self, mock_short_class, mock_long_text_model):
        """Test text preprocessing strips leading/trailing whitespace."""
        mock_short_class.return_value = Mock()
        analyser = AiTextAnalyser(ai_model=mock_long_text_model)
        
        text_with_spaces = "\n\t  Clean text here  \n\t"
        cleaned = analyser.preprocess(text_with_spaces)
        
        assert cleaned == "Clean text here"

    # Postprocessing Tests
    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_postprocess_ai_generated_without_claude(self, mock_short_class, mock_long_text_model):
        """Test postprocessing AI-generated result without Claude."""
        mock_short_class.return_value = Mock()
        analyser = AiTextAnalyser(ai_model=mock_long_text_model)
        
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

    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_postprocess_human_generated_without_claude(self, mock_short_class, mock_long_text_model):
        """Test postprocessing human-generated result without Claude."""
        mock_short_class.return_value = Mock()
        analyser = AiTextAnalyser(ai_model=mock_long_text_model)
        
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

    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_postprocess_with_claude_enhancement(self, mock_short_class, mock_long_text_model):
        """Test postprocessing with Claude enhanced analysis."""
        mock_short_class.return_value = Mock()
        analyser = AiTextAnalyser(ai_model=mock_long_text_model)
        
        model_output = {
            'probability': 0.85,
            'is_ai_generated': True,
            'confidence': 0.92
        }
        
        enhanced_analysis = {
            'detection_reasons': [
                {
                    'type': 'critical',
                    'title': 'AI Keywords Detected',
                    'description': 'Enhanced Claude analysis found patterns',
                    'impact': 'High'
                }
            ],
            'analysis_details': {
                'found_keywords': ['optimize', 'streamline']
            }
        }
        
        result = analyser.postprocess(model_output, enhanced_analysis)
        
        assert result['metadata']['enhanced_analysis_used'] is True
        assert result['analysis']['detection_reasons'] == enhanced_analysis['detection_reasons']
        assert result['analysis']['analysis_details']['found_keywords'] == ['optimize', 'streamline']

    # Statistics Tests
    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_calculate_statistics_basic_text(self, mock_short_class, mock_long_text_model):
        """Test calculating statistics for basic text."""
        mock_short_class.return_value = Mock()
        analyser = AiTextAnalyser(ai_model=mock_long_text_model)
        
        text = "This is a sample text with exactly ten words total."
        stats = analyser.calculate_statistics(text)
        
        assert stats['total_words'] == 10
        assert stats['sentences'] == 1
        assert stats['avg_sentence_length'] == 10.0
        assert stats['ai_keywords_count'] == 0  # No enhanced analysis

    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_calculate_statistics_with_enhanced_analysis(self, mock_short_class, mock_long_text_model):
        """Test calculating statistics with Claude enhanced analysis."""
        mock_short_class.return_value = Mock()
        analyser = AiTextAnalyser(ai_model=mock_long_text_model)
        
        text = "Sample text for analysis."
        enhanced_analysis = {
            'analysis_details': {
                'found_keywords': ['optimize', 'streamline'],
                'found_transitions': ['furthermore'],
                'found_jargon': ['synergy'],
                'found_buzzwords': ['innovative'],
                'found_patterns': ['repetitive'],
                'found_human_indicators': ['personal story']
            }
        }
        
        stats = analyser.calculate_statistics(text, enhanced_analysis)
        
        assert stats['ai_keywords_count'] == 2
        assert stats['transition_words_count'] == 1
        assert stats['corporate_jargon_count'] == 1
        assert stats['buzzwords_count'] == 1
        assert stats['suspicious_patterns_count'] == 1
        assert stats['human_indicators_count'] == 1

    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_calculate_statistics_empty_text(self, mock_short_class, mock_long_text_model):
        """Test calculating statistics for empty text."""
        mock_short_class.return_value = Mock()
        analyser = AiTextAnalyser(ai_model=mock_long_text_model)
        
        stats = analyser.calculate_statistics("")
        
        assert stats['total_words'] == 0
        assert stats['sentences'] == 0
        assert stats['avg_sentence_length'] == 0
        assert stats['ai_keywords_count'] == 0

    # Edge Cases
    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_postprocess_handles_missing_values(self, mock_short_class, mock_long_text_model):
        """Test postprocessing handles missing values gracefully."""
        mock_short_class.return_value = Mock()
        analyser = AiTextAnalyser(ai_model=mock_long_text_model)
        
        model_output = {}  # Empty output
        
        result = analyser.postprocess(model_output)
        
        assert result['prediction']['probability'] == 0.0
        assert result['prediction']['is_ai_generated'] is False
        assert result['prediction']['confidence'] == 0.0
        assert len(result['analysis']['detection_reasons']) == 1

    @patch('app.services.ai_text_analyser.AiShortTextModel')
    def test_threshold_boundary_case(self, mock_short_class, mock_long_text_model):
        """Test model selection at the exact threshold boundary."""
        mock_short_instance = Mock()
        mock_short_class.return_value = mock_short_instance
        
        analyser = AiTextAnalyser(ai_model=mock_long_text_model, use_claude=False)
    
        boundary_text = "This text has exactly fifty characters here......."
        # Verify it's exactly 50 characters
        assert len(boundary_text.strip()) == 50
        
        selected_model, model_type = analyser._select_model(boundary_text)
        
        # Should use short text model (<=50)
        assert selected_model == mock_short_instance
        assert model_type == "short_text"