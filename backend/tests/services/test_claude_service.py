# type: ignore
from unittest.mock import Mock, patch, MagicMock, mock_open
import pytest
import json
import os
import tempfile
from app.services.claude_service import ClaudeService, DetectionReason, AnalysisDetails

class TestClaudeService:
    """
    Unit tests for Claude Service.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 28/09/2025
    """

    @pytest.fixture
    def mock_anthropic_client(self):
        """Create a mock Anthropic client."""
        client = Mock()
        
        # Mock successful text response
        text_response = Mock()
        text_response.content = [Mock()]
        text_response.content[0].text = json.dumps({
            "detection_reasons": [
                {
                    "type": "critical",
                    "title": "AI Keywords Detected",
                    "description": "Found typical AI-generated patterns",
                    "impact": "High"
                }
            ],
            "analysis_details": {
                "found_keywords": ["optimize", "streamline"],
                "found_patterns": ["repetitive structure"],
                "found_transitions": ["furthermore", "moreover"],
                "found_jargon": ["synergy"],
                "found_buzzwords": ["innovative"],
                "found_human_indicators": ["personal story"]
            }
        })
        
        client.messages.create.return_value = text_response
        return client

    @pytest.fixture
    def mock_base_prediction(self):
        """Create a mock base prediction from AI model."""
        return {
            'probability': 0.85,
            'is_ai_generated': True,
            'confidence': 0.92
        }

    @pytest.fixture
    def temp_image_path(self):
        """Create a temporary image file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_file.write(b'fake image data')
            yield temp_file.name
        
        # Cleanup
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

    # Initialization Tests
    @patch('app.services.claude_service.anthropic.Anthropic')
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-api-key'})
    def test_init_with_env_api_key(self, mock_anthropic):
        """Test initialization with API key from environment."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        
        service = ClaudeService()
        
        assert service.api_key == 'test-api-key'
        assert service.client == mock_client
        assert service.model == "claude-sonnet-4-20250514"
        mock_anthropic.assert_called_once_with(api_key='test-api-key')

    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_init_with_provided_api_key(self, mock_anthropic):
        """Test initialization with provided API key."""
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        
        service = ClaudeService(api_key='provided-key', model='claude-3-opus')
        
        assert service.api_key == 'provided-key'
        assert service.model == 'claude-3-opus'
        mock_anthropic.assert_called_once_with(api_key='provided-key')

    def test_init_no_api_key_raises_error(self):
        """Test initialization without API key raises ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Anthropic API key is required"):
                ClaudeService()

    # Text Analysis Tests
    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_analyse_text_patterns_success(self, mock_anthropic, mock_anthropic_client, mock_base_prediction):
        """Test successful text pattern analysis."""
        mock_anthropic.return_value = mock_anthropic_client
        
        service = ClaudeService(api_key='test-key')
        text = "This text demonstrates various optimization strategies for streamlining processes."
        
        result = service.analyse_text_patterns(text, mock_base_prediction)
        
        # Verify API was called
        mock_anthropic_client.messages.create.assert_called_once()
        call_args = mock_anthropic_client.messages.create.call_args
        
        assert call_args[1]['model'] == service.model
        assert call_args[1]['max_tokens'] == 2000
        assert call_args[1]['temperature'] == 0.1
        assert text in call_args[1]['messages'][0]['content']
        
        # Verify response structure
        assert 'detection_reasons' in result
        assert 'analysis_details' in result
        assert len(result['detection_reasons']) == 1
        assert result['detection_reasons'][0]['type'] == 'critical'
        assert result['analysis_details']['found_keywords'] == ['optimize', 'streamline']

    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_analyse_text_patterns_api_failure(self, mock_anthropic):
        """Test text analysis with API failure returns fallback."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API connection failed")
        mock_anthropic.return_value = mock_client
        
        service = ClaudeService(api_key='test-key')
        
        result = service.analyse_text_patterns("test text", {'probability': 0.5})
        
        # Should return fallback analysis
        assert result['detection_reasons'][0]['type'] == 'warning'
        assert result['detection_reasons'][0]['title'] == 'Claude Analysis Unavailable'
        assert 'API connection failed' in result['detection_reasons'][0]['description']
        assert all(isinstance(v, list) for v in result['analysis_details'].values())

    # Image Analysis Tests
    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_analyse_image_patterns_success(self, mock_anthropic, mock_base_prediction, temp_image_path):
        """Test successful image pattern analysis."""
        # Mock successful image response
        mock_client = Mock()
        image_response = Mock()
        image_response.content = [Mock()]
        image_response.content[0].text = json.dumps({
            "detection_reasons": [
                {
                    "type": "critical",
                    "title": "AI Artifacts Detected",
                    "description": "Found artificial generation patterns",
                    "impact": "High"
                }
            ]
        })
        mock_client.messages.create.return_value = image_response
        mock_anthropic.return_value = mock_client
        
        service = ClaudeService(api_key='test-key')
        
        result = service.analyse_image_patterns(temp_image_path, mock_base_prediction)
        
        # Verify API was called with image data
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args
        
        assert call_args[1]['model'] == service.model
        assert call_args[1]['max_tokens'] == 1000
        
        # Verify image was included in the request
        content = call_args[1]['messages'][0]['content']
        assert any(item['type'] == 'image' for item in content)
        assert any(item['type'] == 'text' for item in content)
        
        # Verify response structure
        assert 'detection_reasons' in result
        assert len(result['detection_reasons']) == 1
        assert result['detection_reasons'][0]['type'] == 'critical'

    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_analyse_image_patterns_file_not_found(self, mock_anthropic, mock_base_prediction):
        """Test image analysis with non-existent file."""
        mock_anthropic.return_value = Mock()
        
        service = ClaudeService(api_key='test-key')
        
        result = service.analyse_image_patterns("/non/existent/path.jpg", mock_base_prediction)
        
        # Should return fallback analysis
        assert result['detection_reasons'][0]['type'] == 'warning'
        assert result['detection_reasons'][0]['title'] == 'Enhanced Analysis Unavailable'

    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_analyse_image_patterns_different_formats(self, mock_anthropic, mock_base_prediction):
        """Test image analysis with different image formats."""
        mock_client = Mock()
        mock_client.messages.create.return_value = Mock()
        mock_client.messages.create.return_value.content = [Mock()]
        mock_client.messages.create.return_value.content[0].text = '{"detection_reasons": []}'
        mock_anthropic.return_value = mock_client
        
        service = ClaudeService(api_key='test-key')
        
        # Test PNG format
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(b'fake png data')
            temp_file.flush()
            
            service.analyse_image_patterns(temp_file.name, mock_base_prediction)
            
            # Verify PNG media type was used
            call_args = mock_client.messages.create.call_args
            image_content = next(item for item in call_args[1]['messages'][0]['content'] if item['type'] == 'image')
            assert image_content['source']['media_type'] == 'image/png'
            
            os.unlink(temp_file.name)

    # Response Parsing Tests
    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_parse_text_response_valid_json(self, mock_anthropic):
        """Test parsing valid JSON response."""
        mock_anthropic.return_value = Mock()
        service = ClaudeService(api_key='test-key')
        
        valid_json = json.dumps({
            "detection_reasons": [{"type": "info", "title": "Test", "description": "Test desc", "impact": "Low"}],
            "analysis_details": {"found_keywords": ["test"]}
        })
        
        result = service.parse_text_reponse(valid_json)
        
        assert 'detection_reasons' in result
        assert 'analysis_details' in result
        assert result['detection_reasons'][0]['type'] == 'info'
        assert result['analysis_details']['found_keywords'] == ['test']

    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_parse_text_response_with_markdown_formatting(self, mock_anthropic):
        """Test parsing JSON response wrapped in markdown code blocks."""
        mock_anthropic.return_value = Mock()
        service = ClaudeService(api_key='test-key')
        
        markdown_json = '```json\n{"detection_reasons": [], "analysis_details": {}}\n```'
        
        result = service.parse_text_reponse(markdown_json)
        
        assert 'detection_reasons' in result
        assert 'analysis_details' in result

    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_parse_text_response_invalid_json(self, mock_anthropic):
        """Test parsing invalid JSON returns fallback."""
        mock_anthropic.return_value = Mock()
        service = ClaudeService(api_key='test-key')
        
        invalid_json = "This is not valid JSON at all"
        
        result = service.parse_text_reponse(invalid_json)
        
        # Should return fallback structure
        assert result['detection_reasons'][0]['type'] == 'warning'
        assert 'JSON parsing error' in result['detection_reasons'][0]['description']

    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_parse_image_response_success(self, mock_anthropic):
        """Test parsing image analysis response."""
        mock_anthropic.return_value = Mock()
        service = ClaudeService(api_key='test-key')
        
        valid_response = json.dumps({
            "detection_reasons": [
                {"type": "success", "title": "Natural Image", "description": "Shows human creativity", "impact": "Positive"}
            ]
        })
        
        result = service.parse_image_response(valid_response)
        
        assert 'detection_reasons' in result
        assert len(result['detection_reasons']) == 1
        assert result['detection_reasons'][0]['type'] == 'success'

    # Submission Name Creation Tests
    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_create_text_submission_name_success(self, mock_anthropic):
        """Test successful text submission name creation."""
        mock_client = Mock()
        name_response = Mock()
        name_response.content = [Mock()]
        name_response.content[0].text = "Climate Change Analysis"
        mock_client.messages.create.return_value = name_response
        mock_anthropic.return_value = mock_client
        
        service = ClaudeService(api_key='test-key')
        
        text = "Global warming is affecting polar ice caps and sea levels worldwide."
        name = service.create_text_submission_name(text, max_length=30)
        
        assert name == "Climate Change Analysis"
        mock_client.messages.create.assert_called_once()
        
        # Verify prompt parameters
        call_args = mock_client.messages.create.call_args
        assert call_args[1]['max_tokens'] == 20
        assert call_args[1]['temperature'] == 0.3

    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_create_text_submission_name_empty_text(self, mock_anthropic):
        """Test text submission name creation with empty text."""
        mock_anthropic.return_value = Mock()
        service = ClaudeService(api_key='test-key')
        
        name = service.create_text_submission_name("   ", max_length=20)
        
        assert name == "Empty Submission"

    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_create_text_submission_name_removes_quotes(self, mock_anthropic):
        """Test that quotes are removed from submission names."""
        mock_client = Mock()
        name_response = Mock()
        name_response.content = [Mock()]
        name_response.content[0].text = '"Product Review Analysis"'
        mock_client.messages.create.return_value = name_response
        mock_anthropic.return_value = mock_client
        
        service = ClaudeService(api_key='test-key')
        
        name = service.create_text_submission_name("This product is great!", max_length=30)
        
        assert name == "Product Review Analysis"  # Quotes should be removed

    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_create_image_submission_name_success(self, mock_anthropic, temp_image_path):
        """Test successful image submission name creation."""
        mock_client = Mock()
        name_response = Mock()
        name_response.content = [Mock()]
        name_response.content[0].text = "Portrait Analysis"
        mock_client.messages.create.return_value = name_response
        mock_anthropic.return_value = mock_client
        
        service = ClaudeService(api_key='test-key')
        
        name = service.create_image_submission_name(temp_image_path, max_length=50)
        
        assert name == "Portrait Analysis"
        mock_client.messages.create.assert_called_once()
        
        # Verify image was included in request
        call_args = mock_client.messages.create.call_args
        content = call_args[1]['messages'][0]['content']
        assert any(item['type'] == 'image' for item in content)
        assert any(item['type'] == 'text' for item in content)

    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_create_image_submission_name_api_failure_fallback(self, mock_anthropic, temp_image_path):
        """Test image submission name creation with API failure uses fallback."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API failed")
        mock_anthropic.return_value = mock_client
        
        service = ClaudeService(api_key='test-key')
        
        name = service.create_image_submission_name(temp_image_path, max_length=50)
        
        # Should fall back to filename-based name
        filename = os.path.basename(temp_image_path)
        expected_name = f"{os.path.splitext(filename)[0][:41]} Analysis"  # 50-9 = 41
        assert name == expected_name

    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_create_image_submission_name_truncates_long_names(self, mock_anthropic, temp_image_path):
        """Test that long image names are truncated."""
        mock_client = Mock()
        name_response = Mock()
        name_response.content = [Mock()]
        name_response.content[0].text = "Very Long Detailed Portrait Analysis With Extra Details"
        mock_client.messages.create.return_value = name_response
        mock_anthropic.return_value = mock_client
        
        service = ClaudeService(api_key='test-key')
        
        name = service.create_image_submission_name(temp_image_path, max_length=20)
        
        # Should be truncated to max_length
        assert len(name) <= 20
        assert name.endswith("...")

    # Prompt Building Tests
    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_build_text_analysis_prompt_includes_prediction_data(self, mock_anthropic):
        """Test that text analysis prompt includes prediction data."""
        mock_anthropic.return_value = Mock()
        service = ClaudeService(api_key='test-key')
        
        text = "Sample text for analysis"
        prediction = {'probability': 0.75, 'is_ai_generated': True, 'confidence': 0.88}
        
        prompt = service.build_text_analysis_prompt(text, prediction)
        
        assert text in prompt
        assert '0.750' in prompt  # Probability formatted to 3 decimals
        assert 'True' in prompt   # is_ai_generated
        assert '0.880' in prompt  # Confidence formatted to 3 decimals
        assert 'JSON' in prompt   # Requesting JSON output

    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_build_image_analysis_prompt_includes_prediction_data(self, mock_anthropic):
        """Test that image analysis prompt includes prediction data."""
        mock_anthropic.return_value = Mock()
        service = ClaudeService(api_key='test-key')
        
        prediction = {'probability': 0.65, 'is_ai_generated': False, 'confidence': 0.92}
        
        prompt = service.build_image_analysis_prompt(prediction)
        
        assert '0.650' in prompt  # Probability formatted to 3 decimals
        assert 'False' in prompt  # is_ai_generated
        assert '0.920' in prompt  # Confidence formatted to 3 decimals
        assert 'JSON' in prompt   # Requesting JSON output

    # Fallback Analysis Tests
    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_fallback_text_analysis_structure(self, mock_anthropic):
        """Test fallback text analysis returns correct structure."""
        mock_anthropic.return_value = Mock()
        service = ClaudeService(api_key='test-key')
        
        result = service.fallback_text_analysis("Test error message")
        
        # Verify structure
        assert 'detection_reasons' in result
        assert 'analysis_details' in result
        assert len(result['detection_reasons']) == 1
        assert result['detection_reasons'][0]['type'] == 'warning'
        assert 'Test error message' in result['detection_reasons'][0]['description']
        
        # Verify all analysis_details fields are present and are lists
        expected_fields = ['found_keywords', 'found_patterns', 'found_transitions', 
                          'found_jargon', 'found_buzzwords', 'found_human_indicators']
        for field in expected_fields:
            assert field in result['analysis_details']
            assert isinstance(result['analysis_details'][field], list)
            assert result['analysis_details'][field] == []

    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_fallback_image_analysis_structure(self, mock_anthropic):
        """Test fallback image analysis returns correct structure."""
        mock_anthropic.return_value = Mock()
        service = ClaudeService(api_key='test-key')
        
        result = service.fallback_image_analysis("Image processing failed")
        
        # Verify structure
        assert 'detection_reasons' in result
        assert len(result['detection_reasons']) == 1
        assert result['detection_reasons'][0]['type'] == 'warning'
        assert result['detection_reasons'][0]['title'] == 'Enhanced Analysis Unavailable'
        assert 'Image processing failed' in result['detection_reasons'][0]['description']

    # Edge Cases
    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_handles_missing_prediction_values(self, mock_anthropic, mock_anthropic_client):
        """Test that missing prediction values are handled gracefully."""
        mock_anthropic.return_value = mock_anthropic_client
        service = ClaudeService(api_key='test-key')
        
        # Prediction with missing values
        incomplete_prediction = {}
        
        result = service.analyse_text_patterns("test", incomplete_prediction)
        
        # Should not crash and should call API
        mock_anthropic_client.messages.create.assert_called_once()
        assert 'detection_reasons' in result

    @patch('app.services.claude_service.anthropic.Anthropic')
    def test_long_text_truncation_in_naming(self, mock_anthropic):
        """Test that very long text is truncated for naming."""
        mock_client = Mock()
        name_response = Mock()
        name_response.content = [Mock()]
        name_response.content[0].text = "Long Text Analysis"
        mock_client.messages.create.return_value = name_response
        mock_anthropic.return_value = mock_client
        
        service = ClaudeService(api_key='test-key')
        
        # Text longer than 500 characters
        long_text = "A" * 1000
        
        name = service.create_text_submission_name(long_text, max_length=30)
        
        # Should still work
        assert name == "Long Text Analysis"
        
        # Verify that text was truncated in the prompt
        call_args = mock_client.messages.create.call_args
        prompt_content = call_args[1]['messages'][0]['content']
        # The prompt should contain truncated text (first 500 chars)
        assert "A" * 500 in prompt_content