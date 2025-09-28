# type: ignore
from unittest.mock import Mock, patch, mock_open
import pytest
import torch
from PIL import Image
from app.ai.ai_image_model import AiImageModel
import os
import tempfile
import hashlib

class TestAiImageModel:
    """
    Unit tests for AiImageModel.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 28/09/2025
    """

    def setup_method(self):
        """Reset singleton before each test."""
        AiImageModel.reset_instance()

    def teardown_method(self):
        """Clean up after each test."""
        AiImageModel.reset_instance()

    # Singleton Pattern Tests
    def test_singleton_pattern(self):
        """Test singleton pattern implementation."""
        instance1 = AiImageModel()
        instance2 = AiImageModel()
        
        assert instance1 is instance2

    def test_get_instance_method(self):
        """Test get_instance class method."""
        instance1 = AiImageModel.get_instance()
        instance2 = AiImageModel()
        
        assert instance1 is instance2

    def test_reset_instance(self):
        """Test instance reset functionality."""
        instance1 = AiImageModel()
        AiImageModel.reset_instance()
        instance2 = AiImageModel()
        
        assert instance1 is not instance2

    # Initialization Tests
    @patch('torch.cuda.is_available', return_value=False)
    def test_initialization_cpu_default(self, mock_cuda):
        """Test initialization defaults to CPU when CUDA unavailable."""
        model = AiImageModel()
        
        assert model.device == "cpu"
        assert model.threshold == 0.5
        assert model.img_size == 380
        assert model.label_mapping == {1: "human", 0: "ai"}

    @patch('torch.cuda.is_available', return_value=True)
    def test_initialization_gpu_default(self, mock_cuda):
        """Test initialization defaults to GPU when CUDA available."""
        model = AiImageModel()
        
        assert model.device == "cuda"

    def test_initialization_custom_device(self):
        """Test initialization with custom device."""
        model = AiImageModel(device="cpu")
        
        assert model.device == "cpu"

    def test_initialization_custom_model_name(self):
        """Test initialization with custom model name."""
        custom_name = "custom/image-model"
        model = AiImageModel(model_name=custom_name)
        
        assert model.model_name == custom_name

    # Model Loading Tests
    @patch('app.ai.ai_image_model.hf_hub_download')
    @patch('app.ai.ai_image_model.create_model')
    @patch('torch.load')
    def test_load_success(self, mock_torch_load, mock_create_model, mock_hf_download):
        """Test successful model loading."""
        mock_hf_download.return_value = "/fake/path/model.pth"
        mock_model = Mock()
        mock_create_model.return_value = mock_model
        mock_torch_load.return_value = {"state_dict": "fake"}
        
        model = AiImageModel()
        model.load()
        
        assert hasattr(model, 'model')
        assert hasattr(model, 'tokenizer')
        mock_model.load_state_dict.assert_called_once()
        mock_model.to.assert_called_once()
        mock_model.eval.assert_called_once()

    @patch('app.ai.ai_image_model.hf_hub_download')
    def test_load_failure(self, mock_hf_download):
        """Test model loading failure."""
        mock_hf_download.side_effect = Exception("Download failed")
        
        model = AiImageModel()
        
        with pytest.raises(RuntimeError, match="Failed to load model"):
            model.load()

    # Transform Property Test
    def test_transform_property(self):
        """Test transform property returns tokenizer."""
        model = AiImageModel()
        model.tokenizer = Mock()
        
        assert model.transform is model.tokenizer

    # Image Hash Tests
    def test_get_image_hash_success(self):
        """Test successful image hash generation."""
        model = AiImageModel()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"fake image data")
            tmp_path = tmp_file.name
        
        try:
            hash_result = model._get_image_hash(tmp_path)
            expected_hash = hashlib.sha256(b"fake image data").hexdigest()
            
            assert hash_result == expected_hash
        finally:
            os.unlink(tmp_path)

    def test_get_image_hash_fallback(self):
        """Test image hash fallback to path-based hash."""
        model = AiImageModel()
        fake_path = "/fake/nonexistent/path.jpg"
        
        hash_result = model._get_image_hash(fake_path)
        expected_hash = hashlib.sha256(fake_path.encode('utf-8')).hexdigest()
        
        assert hash_result == expected_hash

    # Main Prediction Tests
    @patch.object(AiImageModel, 'is_loaded', return_value=True)
    @patch('os.path.exists', return_value=True)
    @patch('PIL.Image.open')
    def test_predict_success_ai_generated(self, mock_image_open, mock_exists, mock_is_loaded):
        """Test successful prediction for AI-generated image."""
        model = AiImageModel()
        
        # Mock image processing
        mock_img = Mock()
        mock_image_open.return_value = mock_img
        mock_img.convert.return_value = mock_img
        
        # Mock tokenizer (transform)
        mock_tokenizer = Mock()
        mock_tensor = Mock()
        mock_tokenizer.return_value = mock_tensor
        mock_tensor.unsqueeze.return_value = mock_tensor
        mock_tensor.to.return_value = mock_tensor
        
        # Mock model
        mock_model = Mock()
        mock_logits = torch.tensor([[2.0, 1.0]])  # Higher confidence for AI (class 0)
        mock_model.return_value = mock_logits
        
        model.tokenizer = mock_tokenizer
        model.model = mock_model
        model.device = "cpu"
        
        with patch('torch.nn.functional.softmax') as mock_softmax:
            mock_probs = torch.tensor([[0.7, 0.3]])  # 70% AI, 30% human
            mock_softmax.return_value = mock_probs
            
            with patch('torch.argmax', return_value=torch.tensor([0])):
                result = model.predict("/fake/image.jpg")
        
        assert result['is_ai_generated'] is True
        assert round(result['probability'], 1) == 0.7
        assert round(result['confidence'], 1) == 0.7
        assert result['metadata']['label'] == "ai"
        assert result['metadata']['prediction_class'] == 0

    @patch.object(AiImageModel, 'is_loaded', return_value=True)
    @patch('os.path.exists', return_value=True)
    @patch('PIL.Image.open')
    def test_predict_success_human_generated(self, mock_image_open, mock_exists, mock_is_loaded):
        """Test successful prediction for human-generated image."""
        model = AiImageModel()
        
        # Mock image processing
        mock_img = Mock()
        mock_image_open.return_value = mock_img
        mock_img.convert.return_value = mock_img
        
        # Mock tokenizer (transform)
        mock_tokenizer = Mock()
        mock_tensor = Mock()
        mock_tokenizer.return_value = mock_tensor
        mock_tensor.unsqueeze.return_value = mock_tensor
        mock_tensor.to.return_value = mock_tensor
        
        # Mock model
        mock_model = Mock()
        mock_logits = torch.tensor([[1.0, 2.0]])  # Higher confidence for human (class 1)
        mock_model.return_value = mock_logits
        
        model.tokenizer = mock_tokenizer
        model.model = mock_model
        model.device = "cpu"
        
        with patch('torch.nn.functional.softmax') as mock_softmax:
            mock_probs = torch.tensor([[0.3, 0.7]])  # 30% AI, 70% human
            mock_softmax.return_value = mock_probs
            
            with patch('torch.argmax', return_value=torch.tensor([1])):
                result = model.predict("/fake/image.jpg")
        
        assert result['is_ai_generated'] is False
        assert round(result['probability'], 1) == 0.3  # 1 - 0.7 (human confidence)
        assert round(result['confidence'], 1) == 0.7
        assert result['metadata']['label'] == "human"
        assert result['metadata']['prediction_class'] == 1

    def test_predict_model_not_loaded(self):
        """Test prediction when model not loaded."""
        model = AiImageModel()
        
        with patch.object(model, 'is_loaded', return_value=False):
            with pytest.raises(RuntimeError, match="Model not loaded"):
                model.predict("/fake/image.jpg")

    @patch.object(AiImageModel, 'is_loaded', return_value=True)
    @patch('os.path.exists', return_value=False)
    def test_predict_file_not_found(self, mock_exists, mock_is_loaded):
        """Test prediction with non-existent file."""
        model = AiImageModel()
        
        with pytest.raises(FileNotFoundError, match="Image file not found"):
            model.predict("/fake/nonexistent.jpg")

    @patch.object(AiImageModel, 'is_loaded', return_value=True)
    @patch('os.path.exists', return_value=True)
    @patch('PIL.Image.open')
    def test_predict_image_processing_error(self, mock_image_open, mock_exists, mock_is_loaded):
        """Test prediction with image processing error."""
        model = AiImageModel()
        mock_image_open.side_effect = Exception("Cannot open image")
        
        with pytest.raises(ValueError, match="Failed to process image"):
            model.predict("/fake/corrupted.jpg")

    # Cache Tests
    def test_cache_same_image_multiple_calls(self):
        """Test caching behavior with same image."""
        model = AiImageModel()
        
        with patch.object(model, '_cached_predict') as mock_cached:
            mock_cached.return_value = ("ai", 0.8, True)
            
            # Call predict multiple times with same image
            image_path = "/fake/image.jpg"
            result1 = model.predict(image_path)
            result2 = model.predict(image_path)
            
            # Should call cached method with same hash
            assert mock_cached.call_count >= 1
            assert result1 == result2

    def test_clear_cache(self):
        """Test cache clearing functionality."""
        model = AiImageModel()
        
        # Mock the cached method
        model._cached_predict = Mock()
        model._cached_predict.cache_clear = Mock()
        
        model.clear_cache()
        
        model._cached_predict.cache_clear.assert_called_once()

    # Model State Tests
    def test_is_loaded_true_when_model_and_tokenizer_exist(self):
        """Test is_loaded returns True when both model and tokenizer are loaded."""
        model = AiImageModel()
        model.model = Mock()
        model.tokenizer = Mock()
        
        assert model.is_loaded() is True

    def test_is_loaded_false_when_model_missing(self):
        """Test is_loaded returns False when model is missing."""
        model = AiImageModel()
        model.model = None
        model.tokenizer = Mock()
        
        assert model.is_loaded() is False

    def test_is_loaded_false_when_tokenizer_missing(self):
        """Test is_loaded returns False when tokenizer is missing."""
        model = AiImageModel()
        model.model = Mock()
        model.tokenizer = None
        
        assert model.is_loaded() is False

    # Device Configuration Test
    @patch('app.ai.ai_image_model.hf_hub_download')
    @patch('app.ai.ai_image_model.create_model')
    @patch('torch.load')
    def test_device_configuration(self, mock_torch_load, mock_create_model, mock_hf_download):
        """Test device configuration affects model loading."""
        mock_hf_download.return_value = "/fake/path/model.pth"
        mock_model = Mock()
        mock_create_model.return_value = mock_model
        mock_torch_load.return_value = {"state_dict": "fake"}
        
        model = AiImageModel(device="cpu")
        model.load()
        
        # Verify model is moved to correct device
        mock_model.to.assert_called_once_with(torch.device("cpu"))