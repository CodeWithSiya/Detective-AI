# type: ignore
from unittest.mock import Mock, patch, MagicMock
import pytest
import torch
import torch.nn as nn
from transformers import PretrainedConfig
from app.ai.ai_text_model import AiTextModel, DetectionModel
import hashlib

class TestDetectionModel:
    """
    Unit tests for DetectionModel.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 28/09/2025
    """

    @pytest.fixture
    def mock_config(self):
        """Create mock config with proper base class."""
        config = PretrainedConfig()
        config.hidden_size = 768
        return config

    def test_model_initialization(self, mock_config):
        """Test model initialization."""
        with patch('app.ai.ai_text_model.AutoModel.from_config') as mock_auto_model:
            with patch.object(DetectionModel, 'init_weights') as mock_init_weights:
                model = DetectionModel(mock_config)
                
                mock_auto_model.assert_called_once_with(mock_config)
                mock_init_weights.assert_called_once()
                assert hasattr(model, 'classifier')
                assert isinstance(model.classifier, nn.Linear)

    def test_forward_pass_without_labels(self, mock_config):
        """Test forward pass without labels."""
        with patch('app.ai.ai_text_model.AutoModel.from_config') as mock_auto_model:
            with patch.object(DetectionModel, 'init_weights'):
                # Create the model
                model = DetectionModel(mock_config)
                
                # Mock the transformer model's output
                mock_transformer = Mock()
                mock_hidden_state = torch.randn(1, 4, 768)
                mock_transformer.return_value = [mock_hidden_state]
                model.model = mock_transformer
                
                # Mock the classifier forward pass
                with patch.object(model.classifier, 'forward', return_value=torch.tensor([[0.5]])):
                    # Test inputs
                    input_ids = torch.tensor([[1, 2, 3, 0]])
                    attention_mask = torch.tensor([[1, 1, 1, 0]])
                    
                    result = model.forward(input_ids, attention_mask)
                    
                    assert 'logits' in result
                    assert 'loss' not in result
                    assert result['logits'].shape == torch.Size([1, 1])

    def test_forward_pass_with_labels(self, mock_config):
        """Test forward pass with labels."""
        with patch('app.ai.ai_text_model.AutoModel.from_config') as mock_auto_model:
            with patch.object(DetectionModel, 'init_weights'):
                # Create the model
                model = DetectionModel(mock_config)
                
                # Mock the transformer model's output
                mock_transformer = Mock()
                mock_hidden_state = torch.randn(1, 4, 768)
                mock_transformer.return_value = [mock_hidden_state]
                model.model = mock_transformer
                
                # Mock the classifier forward pass
                with patch.object(model.classifier, 'forward', return_value=torch.tensor([[0.5]])):
                    # Test inputs
                    input_ids = torch.tensor([[1, 2, 3, 0]])
                    attention_mask = torch.tensor([[1, 1, 1, 0]])
                    labels = torch.tensor([1.0])
                    
                    result = model.forward(input_ids, attention_mask, labels)
                    
                    assert 'logits' in result
                    assert 'loss' in result
                    assert result['logits'].shape == torch.Size([1, 1])
                    assert isinstance(result['loss'], torch.Tensor)


class TestAiTextModel:
    """
    Unit tests for AiTextModel.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 28/09/2025
    """

    def setup_method(self):
        """Reset singleton before each test."""
        AiTextModel.reset_instance()

    def teardown_method(self):
        """Clean up after each test."""
        AiTextModel.reset_instance()

    # Singleton Pattern Tests
    def test_singleton_pattern(self):
        """Test singleton pattern implementation."""
        instance1 = AiTextModel()
        instance2 = AiTextModel()
        
        assert instance1 is instance2

    def test_get_instance_method(self):
        """Test get_instance class method."""
        instance1 = AiTextModel.get_instance()
        instance2 = AiTextModel()
        
        assert instance1 is instance2

    def test_reset_instance(self):
        """Test instance reset functionality."""
        instance1 = AiTextModel()
        AiTextModel.reset_instance()
        instance2 = AiTextModel()
        
        assert instance1 is not instance2

    # Initialization Tests
    @patch('torch.cuda.is_available', return_value=False)
    def test_initialization_cpu_default(self, mock_cuda):
        """Test initialization defaults to CPU when CUDA unavailable."""
        model = AiTextModel()
        
        assert model.device == "cpu"
        assert model.threshold == 0.5

    @patch('torch.cuda.is_available', return_value=True)
    def test_initialization_gpu_default(self, mock_cuda):
        """Test initialization defaults to GPU when CUDA available."""
        model = AiTextModel()
        
        assert model.device == "cuda"

    def test_initialization_custom_device(self):
        """Test initialization with custom device."""
        model = AiTextModel(device="cpu")
        
        assert model.device == "cpu"

    def test_initialization_custom_model_name(self):
        """Test initialization with custom model name."""
        custom_name = "custom/model-name"
        model = AiTextModel(model_name=custom_name)
        
        assert model.model_name == custom_name

    # Model Loading Tests
    @patch('app.ai.ai_text_model.AutoTokenizer.from_pretrained')
    @patch('app.ai.ai_text_model.DetectionModel.from_pretrained')
    def test_load_success(self, mock_model, mock_tokenizer):
        """Test successful model loading."""
        mock_tokenizer_instance = Mock()
        mock_model_instance = Mock()
        
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_model.return_value = mock_model_instance
        
        model = AiTextModel()
        model.load()
        
        assert model.tokenizer == mock_tokenizer_instance
        assert model.model == mock_model_instance
        assert model.max_length == 1024
        mock_model_instance.to.assert_called_once()
        mock_model_instance.eval.assert_called_once()

    @patch('app.ai.ai_text_model.AutoTokenizer.from_pretrained')
    def test_load_failure(self, mock_tokenizer):
        """Test model loading failure."""
        mock_tokenizer.side_effect = Exception("Model not found")
        
        model = AiTextModel()
        
        with pytest.raises(RuntimeError, match="Failed to load model"):
            model.load()

    # Text Normalization Tests
    def test_normalize_text_basic(self):
        """Test basic text normalization."""
        model = AiTextModel()
        
        result = model._normalize_text("  Hello World  \n")
        
        assert result == "Hello World"

    def test_normalize_text_newlines(self):
        """Test newline normalization."""
        model = AiTextModel()
        
        text = "Line 1\r\nLine 2\rLine 3"
        result = model._normalize_text(text)
        
        assert result == "Line 1\nLine 2\nLine 3"

    # Prediction Tests
    @patch.object(AiTextModel, 'is_loaded', return_value=True)
    def test_predict_success(self, mock_is_loaded):
        """Test successful prediction."""
        model = AiTextModel()
        
        # Mock tokenizer and model
        mock_tokenizer = Mock()
        mock_model = Mock()
        
        # Mock tokenization
        mock_encoded = {
            'input_ids': torch.tensor([[1, 2, 3]]),
            'attention_mask': torch.tensor([[1, 1, 1]])
        }
        mock_tokenizer.return_value = mock_encoded
        
        # Mock model output
        mock_outputs = {'logits': torch.tensor([[0.8]])}
        mock_model.return_value = mock_outputs
        
        model.tokenizer = mock_tokenizer
        model.model = mock_model
        model.device = "cpu"
        model.max_length = 1024
        
        with patch('torch.sigmoid', return_value=torch.tensor([0.7])):
            result = model.predict("This is test text")
        
        assert 'probability' in result
        assert 'is_ai_generated' in result
        assert 'confidence' in result
        assert isinstance(result['is_ai_generated'], bool)

    def test_predict_model_not_loaded(self):
        """Test prediction when model not loaded."""
        model = AiTextModel()
        
        with patch.object(model, 'is_loaded', return_value=False):
            with pytest.raises(RuntimeError, match="Model not loaded"):
                model.predict("test text")

    def test_predict_ai_generated_high_probability(self):
        """Test prediction classifying text as AI-generated."""
        model = AiTextModel()
        model.threshold = 0.5
        
        # Mock the cached predict method
        with patch.object(model, '_cached_predict', return_value=(0.8, True, 0.8)):
            result = model.predict("test text")
            
            assert result['is_ai_generated'] is True
            assert result['probability'] == 0.8
            assert result['confidence'] == 0.8

    def test_predict_human_generated_low_probability(self):
        """Test prediction classifying text as human-generated."""
        model = AiTextModel()
        model.threshold = 0.5
        
        # Mock the cached predict method
        with patch.object(model, '_cached_predict', return_value=(0.3, False, 0.7)):
            result = model.predict("test text")
            
            assert result['is_ai_generated'] is False
            assert result['probability'] == 0.3
            assert result['confidence'] == 0.7

    # Cache Tests
    def test_cache_same_text_multiple_calls(self):
        """Test caching behavior with same text."""
        model = AiTextModel()
        
        with patch.object(model, '_cached_predict') as mock_cached:
            mock_cached.return_value = (0.7, True, 0.7)
            
            # Call predict multiple times with same text
            text = "This is test text"
            result1 = model.predict(text)
            result2 = model.predict(text)
            
            # Should use same hash and call cached method once
            expected_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
            mock_cached.assert_called_with(expected_hash, text)
            
            assert result1 == result2

    def test_clear_cache(self):
        """Test cache clearing functionality."""
        model = AiTextModel()
        
        # Mock the cached method
        model._cached_predict = Mock()
        model._cached_predict.cache_clear = Mock()
        
        model.clear_cache()
        
        model._cached_predict.cache_clear.assert_called_once()

    def test_get_cache_info_with_cache(self):
        """Test getting cache information."""
        model = AiTextModel()
        
        # Mock cache info
        mock_cache_info = Mock()
        mock_cache_info.hits = 10
        mock_cache_info.misses = 5
        mock_cache_info.currsize = 8
        mock_cache_info.maxsize = 512
        
        model._cached_predict = Mock()
        model._cached_predict.cache_info.return_value = mock_cache_info
        
        info = model.get_cache_info()
        
        assert info['hits'] == 10
        assert info['misses'] == 5
        assert info['current_size'] == 8
        assert info['max_size'] == 512
        assert info['hit_rate'] == 10 / 15  # 10 hits / (10 hits + 5 misses)

    def test_get_cache_info_default_values(self):
        """Test getting cache info returns default values when not initialized."""
        model = AiTextModel()
        
        info = model.get_cache_info()
        
        # The actual implementation returns default values, not an error
        assert info['hits'] == 0
        assert info['misses'] == 0
        assert info['current_size'] == 0
        assert info['hit_rate'] == 0.0

    # Edge Cases Tests
    def test_predict_empty_text(self):
        """Test prediction with empty text."""
        model = AiTextModel()
        
        with patch.object(model, '_cached_predict', return_value=(0.5, True, 0.5)):
            result = model.predict("")
            
            assert 'probability' in result
            assert 'is_ai_generated' in result
            assert 'confidence' in result

    def test_predict_very_long_text(self):
        """Test prediction with text longer than max_length."""
        model = AiTextModel()
        
        long_text = "word " * 2000  # Very long text
        
        with patch.object(model, '_cached_predict', return_value=(0.6, True, 0.6)):
            result = model.predict(long_text)
            
            assert 'probability' in result
            # Text should be normalized and truncated during tokenization

    def test_cached_predict_hash_consistency(self):
        """Test that same text produces same hash."""
        model = AiTextModel()
        
        text1 = "  Hello World  \n"
        text2 = "Hello World"
        
        # Both should normalize to same text and produce same hash
        normalized1 = model._normalize_text(text1)
        normalized2 = model._normalize_text(text2)
        
        assert normalized1 == normalized2
        
        hash1 = hashlib.sha256(normalized1.encode('utf-8')).hexdigest()
        hash2 = hashlib.sha256(normalized2.encode('utf-8')).hexdigest()
        
        assert hash1 == hash2

    def test_threshold_boundary_conditions(self):
        """Test predictions at threshold boundary."""
        model = AiTextModel()
        model.threshold = 0.5
        
        # Test exactly at threshold
        with patch.object(model, '_cached_predict', return_value=(0.5, True, 0.5)):
            result = model.predict("test")
            assert result['is_ai_generated'] is True
        
        # Test just below threshold
        with patch.object(model, '_cached_predict', return_value=(0.49, False, 0.51)):
            result = model.predict("test")
            assert result['is_ai_generated'] is False

    def test_device_configuration(self):
        """Test device configuration affects model loading."""
        model = AiTextModel(device="cpu")
        
        mock_model_instance = Mock()
        
        with patch('app.ai.ai_text_model.AutoTokenizer.from_pretrained'):
            with patch('app.ai.ai_text_model.DetectionModel.from_pretrained') as mock_model:
                mock_model.return_value = mock_model_instance
                
                model.load()
                
                # Verify model is moved to correct device
                mock_model_instance.to.assert_called_once_with(torch.device("cpu"))

    # Model State Tests
    def test_is_loaded_true_when_model_and_tokenizer_exist(self):
        """Test is_loaded returns True when both model and tokenizer are loaded."""
        model = AiTextModel()
        model.model = Mock()
        model.tokenizer = Mock()
        
        assert model.is_loaded() is True

    def test_is_loaded_false_when_model_missing(self):
        """Test is_loaded returns False when model is missing."""
        model = AiTextModel()
        model.model = None
        model.tokenizer = Mock()
        
        assert model.is_loaded() is False

    def test_is_loaded_false_when_tokenizer_missing(self):
        """Test is_loaded returns False when tokenizer is missing."""
        model = AiTextModel()
        model.model = Mock()
        model.tokenizer = None
        
        assert model.is_loaded() is False