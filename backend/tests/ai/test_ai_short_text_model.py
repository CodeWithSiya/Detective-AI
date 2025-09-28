# type: ignore
from unittest.mock import Mock, patch
import pytest
import torch
import torch.nn as nn
from transformers import PretrainedConfig
from app.ai.ai_short_text_model import AiShortTextModel, ShortTextDetectionModel
import hashlib

class TestShortTextDetectionModel:
    """
    Unit tests for ShortTextDetectionModel.

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
        with patch('app.ai.ai_short_text_model.AutoModel.from_pretrained') as mock_auto_model:
            with patch.object(ShortTextDetectionModel, 'init_weights'):
                mock_backbone = Mock()
                mock_backbone.config.hidden_size = 768
                mock_auto_model.return_value = mock_backbone
                
                model = ShortTextDetectionModel(mock_config)
                
                assert hasattr(model, 'attention_pooling')
                assert hasattr(model, 'multi_head_attention')
                assert hasattr(model, 'feature_extractor')
                assert hasattr(model, 'classifier')
                assert isinstance(model.classifier, nn.Linear)

    def test_attention_pool_mechanism(self, mock_config):
        """Test attention pooling mechanism."""
        with patch('app.ai.ai_short_text_model.AutoModel.from_pretrained') as mock_auto_model:
            with patch.object(ShortTextDetectionModel, 'init_weights'):
                # Create proper mock backbone with config
                mock_backbone = Mock()
                mock_backbone.config.hidden_size = 768
                mock_auto_model.return_value = mock_backbone
                
                model = ShortTextDetectionModel(mock_config)
                
                # Mock inputs
                batch_size, seq_len, hidden_size = 2, 4, 768
                hidden_states = torch.randn(batch_size, seq_len, hidden_size)
                attention_mask = torch.tensor([[1, 1, 1, 0], [1, 1, 0, 0]])
                
                # Test attention pooling
                pooled = model.attention_pool(hidden_states, attention_mask)
                
                assert pooled.shape == (batch_size, hidden_size)
                assert not torch.isnan(pooled).any()

    def test_forward_pass_without_labels(self, mock_config):
        """Test forward pass without labels."""
        with patch('app.ai.ai_short_text_model.AutoModel.from_pretrained') as mock_auto_model:
            with patch.object(ShortTextDetectionModel, 'init_weights'):
                # Mock backbone
                mock_backbone = Mock()
                mock_backbone.config.hidden_size = 768
                mock_auto_model.return_value = mock_backbone
                
                model = ShortTextDetectionModel(mock_config)
                
                # Mock backbone output
                batch_size, seq_len, hidden_size = 1, 4, 768
                mock_hidden_states = torch.randn(batch_size, seq_len, hidden_size)
                mock_backbone.return_value.last_hidden_state = mock_hidden_states
                
                # Mock multi-head attention
                with patch.object(model.multi_head_attention, 'forward') as mock_mha:
                    mock_mha.return_value = (mock_hidden_states, None)
                    
                    # Mock classifier
                    with patch.object(model.classifier, 'forward', return_value=torch.tensor([0.5])):
                        input_ids = torch.tensor([[1, 2, 3, 0]])
                        attention_mask = torch.tensor([[1, 1, 1, 0]])
                        
                        result = model.forward(input_ids, attention_mask)
                        
                        assert 'logits' in result
                        assert result['loss'] is None

    def test_forward_pass_with_labels(self, mock_config):
        """Test forward pass with labels."""
        with patch('app.ai.ai_short_text_model.AutoModel.from_pretrained') as mock_auto_model:
            with patch.object(ShortTextDetectionModel, 'init_weights'):
                # Mock backbone
                mock_backbone = Mock()
                mock_backbone.config.hidden_size = 768
                mock_auto_model.return_value = mock_backbone
                
                model = ShortTextDetectionModel(mock_config)
                
                # Mock backbone output
                batch_size, seq_len, hidden_size = 1, 4, 768
                mock_hidden_states = torch.randn(batch_size, seq_len, hidden_size)
                mock_backbone.return_value.last_hidden_state = mock_hidden_states
                
                # Mock multi-head attention
                with patch.object(model.multi_head_attention, 'forward') as mock_mha:
                    mock_mha.return_value = (mock_hidden_states, None)
                    
                    # Mock classifier - return tensor with batch dimension
                    with patch.object(model.classifier, 'forward', return_value=torch.tensor([[0.5]])):
                        input_ids = torch.tensor([[1, 2, 3, 0]])
                        attention_mask = torch.tensor([[1, 1, 1, 0]])
                        labels = torch.tensor([1.0])
                        
                        result = model.forward(input_ids, attention_mask, labels)
                        
                        assert 'logits' in result
                        assert 'loss' in result
                        assert result['loss'] is not None


class TestAiShortTextModel:
    """
    Unit tests for AiShortTextModel.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 28/09/2025
    """

    def setup_method(self):
        """Reset singleton before each test."""
        AiShortTextModel.reset_instance()

    def teardown_method(self):
        """Clean up after each test."""
        AiShortTextModel.reset_instance()

    # Singleton Pattern Tests
    def test_singleton_pattern(self):
        """Test singleton pattern implementation."""
        instance1 = AiShortTextModel()
        instance2 = AiShortTextModel()
        
        assert instance1 is instance2

    def test_reset_instance(self):
        """Test instance reset functionality."""
        instance1 = AiShortTextModel()
        AiShortTextModel.reset_instance()
        instance2 = AiShortTextModel()
        
        assert instance1 is not instance2

    # Initialization Tests
    @patch('torch.cuda.is_available', return_value=False)
    def test_initialization_cpu_default(self, mock_cuda):
        """Test initialization defaults to CPU when CUDA unavailable."""
        model = AiShortTextModel()
        
        assert model.device == "cpu"
        assert model.threshold == 0.5
        assert model.max_length == 128

    @patch('torch.cuda.is_available', return_value=True)
    def test_initialization_gpu_default(self, mock_cuda):
        """Test initialization defaults to GPU when CUDA available."""
        model = AiShortTextModel()
        
        assert model.device == "cuda"

    def test_initialization_custom_device(self):
        """Test initialization with custom device."""
        model = AiShortTextModel(device="cpu")
        
        assert model.device == "cpu"

    def test_initialization_custom_model_name(self):
        """Test initialization with custom model name."""
        custom_name = "custom/short-text-model"
        model = AiShortTextModel(model_name=custom_name)
        
        assert model.model_name == custom_name

    # Model Loading Tests
    @patch('app.ai.ai_short_text_model.AutoTokenizer.from_pretrained')
    @patch('app.ai.ai_short_text_model.ShortTextDetectionModel.from_pretrained')
    def test_load_success(self, mock_model, mock_tokenizer):
        """Test successful model loading."""
        mock_tokenizer_instance = Mock()
        mock_model_instance = Mock()
        
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_model.return_value = mock_model_instance
        
        model = AiShortTextModel()
        model.load()
        
        assert model.tokenizer == mock_tokenizer_instance
        assert model.model == mock_model_instance
        assert model.max_length == 128
        mock_model_instance.to.assert_called_once()
        mock_model_instance.eval.assert_called_once()

    @patch('app.ai.ai_short_text_model.AutoTokenizer.from_pretrained')
    def test_load_failure(self, mock_tokenizer):
        """Test model loading failure."""
        mock_tokenizer.side_effect = Exception("Model not found")
        
        model = AiShortTextModel()
        
        with pytest.raises(RuntimeError, match="Failed to load short text model"):
            model.load()

    # Prediction Tests
    @patch.object(AiShortTextModel, 'is_loaded', return_value=True)
    def test_predict_success(self, mock_is_loaded):
        """Test successful prediction."""
        model = AiShortTextModel()
        
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
        mock_outputs = {'logits': torch.tensor([0.8])}
        mock_model.return_value = mock_outputs
        
        model.tokenizer = mock_tokenizer
        model.model = mock_model
        model.device = "cpu"
        model.max_length = 128
        
        with patch('torch.sigmoid', return_value=torch.tensor([0.7])):
            result = model.predict("This is short test text")
        
        assert 'probability' in result
        assert 'is_ai_generated' in result
        assert 'confidence' in result
        assert isinstance(result['is_ai_generated'], bool)

    def test_predict_model_not_loaded(self):
        """Test prediction when model not loaded."""
        model = AiShortTextModel()
        
        with patch.object(model, 'is_loaded', return_value=False):
            with pytest.raises(RuntimeError, match="Model not loaded"):
                model.predict("test text")

    def test_predict_ai_generated_high_probability(self):
        """Test prediction classifying text as AI-generated."""
        model = AiShortTextModel()
        model.threshold = 0.5
        
        # Mock the cached predict method
        with patch.object(model, '_cached_predict', return_value=(0.8, True, 0.8)):
            result = model.predict("This is short test text")
            
            assert result['is_ai_generated'] is True
            assert result['probability'] == 0.8
            assert result['confidence'] == 0.8

    def test_predict_human_generated_low_probability(self):
        """Test prediction classifying text as human-generated."""
        model = AiShortTextModel()
        model.threshold = 0.5
        
        # Mock the cached predict method
        with patch.object(model, '_cached_predict', return_value=(0.3, False, 0.7)):
            result = model.predict("This is short test text")
            
            assert result['is_ai_generated'] is False
            assert result['probability'] == 0.3
            assert result['confidence'] == 0.7

    # Cache Tests
    def test_cache_same_text_multiple_calls(self):
        """Test caching behavior with same text."""
        model = AiShortTextModel()
        
        with patch.object(model, '_cached_predict') as mock_cached:
            mock_cached.return_value = (0.7, True, 0.7)
            
            # Call predict multiple times with same text
            text = "This is short test text"
            result1 = model.predict(text)
            result2 = model.predict(text)
            
            # Should use same hash and call cached method
            expected_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
            mock_cached.assert_called_with(expected_hash, text)
            
            assert result1 == result2

    def test_clear_cache(self):
        """Test cache clearing functionality."""
        model = AiShortTextModel()
        
        # Mock the cached method
        model._cached_predict = Mock()
        model._cached_predict.cache_clear = Mock()
        
        model.clear_cache()
        
        model._cached_predict.cache_clear.assert_called_once()

    # Text Normalization Tests
    def test_normalize_text_basic(self):
        """Test basic text normalization."""
        model = AiShortTextModel()
        
        result = model._normalize_text("  Hello World  \n")
        
        assert result == "Hello World"

    def test_normalize_text_newlines(self):
        """Test newline normalization."""
        model = AiShortTextModel()
        
        text = "Line 1\r\nLine 2\rLine 3"
        result = model._normalize_text(text)
        
        assert result == "Line 1\nLine 2\nLine 3"

    # Model State Tests
    def test_is_loaded_true_when_model_and_tokenizer_exist(self):
        """Test is_loaded returns True when both model and tokenizer are loaded."""
        model = AiShortTextModel()
        model.model = Mock()
        model.tokenizer = Mock()
        
        assert model.is_loaded() is True

    def test_is_loaded_false_when_model_missing(self):
        """Test is_loaded returns False when model is missing."""
        model = AiShortTextModel()
        model.model = None
        model.tokenizer = Mock()
        
        assert model.is_loaded() is False

    def test_is_loaded_false_when_tokenizer_missing(self):
        """Test is_loaded returns False when tokenizer is missing."""
        model = AiShortTextModel()
        model.model = Mock()
        model.tokenizer = None
        
        assert model.is_loaded() is False

    # Edge Cases Tests
    def test_threshold_boundary_conditions(self):
        """Test predictions at threshold boundary."""
        model = AiShortTextModel()
        model.threshold = 0.6
        
        # Test exactly at threshold
        with patch.object(model, '_cached_predict', return_value=(0.6, True, 0.6)):
            result = model.predict("This is test text")
            assert result['is_ai_generated'] is True
        
        # Test just below threshold
        with patch.object(model, '_cached_predict', return_value=(0.59, False, 0.41)):
            result = model.predict("This is test text")
            assert result['is_ai_generated'] is False

    def test_device_configuration(self):
        """Test device configuration affects model loading."""
        model = AiShortTextModel(device="cpu")
        
        mock_model_instance = Mock()
        
        with patch('app.ai.ai_short_text_model.AutoTokenizer.from_pretrained'):
            with patch('app.ai.ai_short_text_model.ShortTextDetectionModel.from_pretrained') as mock_model:
                mock_model.return_value = mock_model_instance
                
                model.load()
                
                # Verify model is moved to correct device
                mock_model_instance.to.assert_called_once_with(torch.device("cpu"))