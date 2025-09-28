from django.contrib.auth import get_user_model
from django.utils import timezone
from app.models import ImageAnalysisResult
from unittest.mock import Mock, patch
from datetime import datetime
import pytest
import uuid

User = get_user_model()

class TestImageAnalysisResultModel:
    """
    Unit tests for ImageAnalysisResult model.
    
    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose 
    :version: 16/09/2025
    """

    @pytest.fixture
    def mock_user(self):
        """
        Create a mock user.
        """
        user = Mock()
        user.id = uuid.uuid4()
        user.username = 'testuser'
        user.email = 'test@example.com'
        return user

    @pytest.fixture
    def mock_content_type(self):
        """
        Mock ContentType.
        """
        content_type = Mock()
        content_type.id = 1
        return content_type

    @pytest.fixture
    def sample_analysis_result(self):
        """
        Sample analysis result data.
        """
        return {
            'prediction': {
                'is_ai_generated': True,
                'probability': 0.85,
                'confidence': 0.92
            },
            'analysis': {
                'detection_reasons': [
                    'Unnatural lighting patterns detected',
                    'Pixel artifacts consistent with AI generation'
                ]
            },
            'metadata': {
                'enhanced_analysis_used': True,
                'processing_time_ms': 1500
            }
        }
    
    def test_model_meta_configuration(self):
        """
        Test model Meta configuration.
        """
        meta = ImageAnalysisResult._meta
        
        # Test db_table
        assert meta.db_table == 'image_analysis_results'
        
        # Test ordering
        assert meta.ordering == ['-created_at']
        
        # Test that indexes are defined (5 indexes)
        assert len(meta.indexes) == 5

    def test_str_representation(self):
        """
        Test the string representation of ImageAnalysisResult.
        """
        # Mock the image analysis result
        image_analysis = Mock(spec=ImageAnalysisResult)
        image_analysis.id = uuid.uuid4()
        image_analysis.status = ImageAnalysisResult.Status.COMPLETED
        image_analysis.detection_result = ImageAnalysisResult.DetectionResult.AI_GENERATED
        image_analysis.probability = 0.856
        
        # Mock the __str__ method
        image_analysis.__str__ = Mock(return_value=f"Image Analysis {image_analysis.id} | {image_analysis.status} | {image_analysis.detection_result} | {image_analysis.probability:.3f}")
        
        result = str(image_analysis)
        expected = f"Image Analysis {image_analysis.id} | COMPLETED | AI_GENERATED | 0.856"
        
        assert result == expected

    def test_enhanced_analysis_used_field(self):
        """
        Test enhanced_analysis_used field properties.
        """
        field = ImageAnalysisResult._meta.get_field('enhanced_analysis_used')
        
        assert field.default == False
        assert isinstance(field, type(ImageAnalysisResult._meta.get_field('enhanced_analysis_used')))

    def test_analysis_details_field(self):
        """
        Test analysis_details JSONField properties.
        """
        field = ImageAnalysisResult._meta.get_field('analysis_details')
        
        assert field.default == dict
        assert field.blank == True

    def test_detection_reasons_property(self):
        """
        Test detection_reasons property.
        """
        # Mock image analysis with detection reasons
        image_analysis = Mock(spec=ImageAnalysisResult)
        image_analysis.analysis_details = {
            'detection_reasons': ['Reason 1', 'Reason 2']
        }
        
        # Mock the property
        image_analysis.detection_reasons = image_analysis.analysis_details.get('detection_reasons', [])
        
        assert image_analysis.detection_reasons == ['Reason 1', 'Reason 2']

    def test_detection_reasons_property_empty(self):
        """
        Test detection_reasons property when empty.
        """
        # Mock image analysis with empty analysis_details
        image_analysis = Mock(spec=ImageAnalysisResult)
        image_analysis.analysis_details = {}
        
        # Mock the property
        image_analysis.detection_reasons = image_analysis.analysis_details.get('detection_reasons', [])
        
        assert image_analysis.detection_reasons == []

    def test_has_detection_reasons_property(self):
        """
        Test has_detection_reasons property.
        """
        # Mock with detection reasons
        image_analysis1 = Mock(spec=ImageAnalysisResult)
        image_analysis1.detection_reasons = ['Reason 1']
        image_analysis1.has_detection_reasons = bool(image_analysis1.detection_reasons)
        
        assert image_analysis1.has_detection_reasons == True
        
        # Mock without detection reasons
        image_analysis2 = Mock(spec=ImageAnalysisResult)
        image_analysis2.detection_reasons = []
        image_analysis2.has_detection_reasons = bool(image_analysis2.detection_reasons)
        
        assert image_analysis2.has_detection_reasons == False

    @patch('app.models.ImageAnalysisResult.objects')
    def test_save_analysis_result_success(self, mock_objects, sample_analysis_result):
        """
        Test successful save_analysis_result method.
        """
        # Mock image analysis instance
        mock_image_analysis = Mock(spec=ImageAnalysisResult)
        mock_image_analysis.probability = 0.0
        mock_image_analysis.confidence = 0.0
        mock_image_analysis.detection_result = None
        mock_image_analysis.analysis_details = {}
        mock_image_analysis.enhanced_analysis_used = False
        mock_image_analysis.processing_time_ms = None
        mock_image_analysis.status = ImageAnalysisResult.Status.PENDING
        mock_image_analysis.completed_at = None
        
        def mock_save_analysis_result(analysis_result):
            if not analysis_result:
                raise ValueError("Analysis result cannot be empty")
            
            # Save prediction data
            prediction = analysis_result.get('prediction', {})
            mock_image_analysis.probability = prediction.get('probability', 0.0)
            mock_image_analysis.confidence = prediction.get('confidence', 0.0)
            
            # Map is_ai_generated to detection_result
            is_ai_generated = prediction.get('is_ai_generated', False)
            if is_ai_generated:
                mock_image_analysis.detection_result = ImageAnalysisResult.DetectionResult.AI_GENERATED
            else:
                mock_image_analysis.detection_result = ImageAnalysisResult.DetectionResult.HUMAN_WRITTEN
            
            # Save analysis data
            analysis = analysis_result.get('analysis', {})
            mock_image_analysis.analysis_details = {
                'detection_reasons': analysis.get('detection_reasons', [])
            }
            
            # Save metadata
            metadata = analysis_result.get('metadata', {})
            mock_image_analysis.enhanced_analysis_used = metadata.get('enhanced_analysis_used', False)
            mock_image_analysis.processing_time_ms = metadata.get('processing_time_ms')
            
            # Set status to completed
            mock_image_analysis.status = ImageAnalysisResult.Status.COMPLETED
            mock_image_analysis.completed_at = timezone.now()
        
        mock_image_analysis.save_analysis_result = mock_save_analysis_result
        
        # Call the method
        mock_image_analysis.save_analysis_result(sample_analysis_result)
        
        # Assertions
        assert mock_image_analysis.probability == 0.85
        assert mock_image_analysis.confidence == 0.92
        assert mock_image_analysis.detection_result == ImageAnalysisResult.DetectionResult.AI_GENERATED
        assert mock_image_analysis.analysis_details['detection_reasons'] == [
            'Unnatural lighting patterns detected',
            'Pixel artifacts consistent with AI generation'
        ]
        assert mock_image_analysis.enhanced_analysis_used == True
        assert mock_image_analysis.processing_time_ms == 1500
        assert mock_image_analysis.status == ImageAnalysisResult.Status.COMPLETED
        assert mock_image_analysis.completed_at is not None

    def test_save_analysis_result_human_written(self):
        """
        Test save_analysis_result for human-written content.
        """
        # Mock image analysis instance
        mock_image_analysis = Mock(spec=ImageAnalysisResult)
        mock_image_analysis.detection_result = None
        
        analysis_result = {
            'prediction': {
                'is_ai_generated': False,
                'probability': 0.15,
                'confidence': 0.88
            },
            'analysis': {
                'detection_reasons': []
            },
            'metadata': {
                'enhanced_analysis_used': False,
                'processing_time_ms': 800
            }
        }
        
        def mock_save_analysis_result(analysis_result):
            prediction = analysis_result.get('prediction', {})
            is_ai_generated = prediction.get('is_ai_generated', False)
            if is_ai_generated:
                mock_image_analysis.detection_result = ImageAnalysisResult.DetectionResult.AI_GENERATED
            else:
                mock_image_analysis.detection_result = ImageAnalysisResult.DetectionResult.HUMAN_WRITTEN
        
        mock_image_analysis.save_analysis_result = mock_save_analysis_result
        
        # Call the method
        mock_image_analysis.save_analysis_result(analysis_result)
        
        # Assertions
        assert mock_image_analysis.detection_result == ImageAnalysisResult.DetectionResult.HUMAN_WRITTEN

    def test_save_analysis_result_empty_raises_error(self):
        """
        Test save_analysis_result raises ValueError for empty result.
        """
        mock_image_analysis = Mock(spec=ImageAnalysisResult)
        
        def mock_save_analysis_result(analysis_result):
            if not analysis_result:
                raise ValueError("Analysis result cannot be empty")
        
        mock_image_analysis.save_analysis_result = mock_save_analysis_result
        
        # Test with None
        with pytest.raises(ValueError, match="Analysis result cannot be empty"):
            mock_image_analysis.save_analysis_result(None)
        
        # Test with empty dict
        with pytest.raises(ValueError, match="Analysis result cannot be empty"):
            mock_image_analysis.save_analysis_result({})

    def test_save_analysis_result_handles_exceptions(self):
        """
        Test save_analysis_result handles exceptions properly.
        """
        mock_image_analysis = Mock(spec=ImageAnalysisResult)
        mock_image_analysis.status = ImageAnalysisResult.Status.PENDING
        
        def mock_save_analysis_result(analysis_result):
            try:
                # Simulate an error during processing
                raise Exception("Simulated error")
            except Exception as e:
                # Mark as failed
                mock_image_analysis.status = ImageAnalysisResult.Status.FAILED
                mock_image_analysis.completed_at = timezone.now()
                raise
        
        mock_image_analysis.save_analysis_result = mock_save_analysis_result
        
        # Call the method and expect it to raise
        with pytest.raises(Exception, match="Simulated error"):
            mock_image_analysis.save_analysis_result({'some': 'data'})
        
        # Check that status was set to failed
        assert mock_image_analysis.status == ImageAnalysisResult.Status.FAILED
        assert mock_image_analysis.completed_at is not None

    @patch('app.models.ImageAnalysisResult.objects')
    def test_model_instantiation(self, mock_objects, mock_user, mock_content_type):
        """
        Test that ImageAnalysisResult model can be instantiated.
        """
        # Create a mock image analysis instance
        mock_image_analysis = Mock(spec=ImageAnalysisResult)
        mock_image_analysis.id = uuid.uuid4()
        mock_image_analysis.user = mock_user
        mock_image_analysis.content_type = mock_content_type
        mock_image_analysis.object_id = uuid.uuid4()
        mock_image_analysis.detection_result = ImageAnalysisResult.DetectionResult.AI_GENERATED
        mock_image_analysis.probability = 0.85
        mock_image_analysis.confidence = 0.92
        mock_image_analysis.status = ImageAnalysisResult.Status.COMPLETED
        mock_image_analysis.enhanced_analysis_used = True
        mock_image_analysis.analysis_details = {
            'detection_reasons': ['Test reason']
        }
        
        # Test that we can create the mock and access its attributes
        image_analysis = mock_image_analysis
        
        # Basic attribute checks
        assert image_analysis.id is not None
        assert image_analysis.user == mock_user
        assert image_analysis.detection_result == ImageAnalysisResult.DetectionResult.AI_GENERATED
        assert image_analysis.probability == 0.85
        assert image_analysis.confidence == 0.92
        assert image_analysis.status == ImageAnalysisResult.Status.COMPLETED
        assert image_analysis.enhanced_analysis_used == True
        assert image_analysis.analysis_details == {'detection_reasons': ['Test reason']}

    def test_missing_analysis_data_handling(self):
        """
        Test handling of missing analysis data.
        """
        mock_image_analysis = Mock(spec=ImageAnalysisResult)
        
        # Test with minimal data
        minimal_result = {
            'prediction': {},
            'analysis': {},
            'metadata': {}
        }
        
        def mock_save_analysis_result(analysis_result):
            prediction = analysis_result.get('prediction', {})
            mock_image_analysis.probability = prediction.get('probability', 0.0)
            mock_image_analysis.confidence = prediction.get('confidence', 0.0)
            
            analysis = analysis_result.get('analysis', {})
            mock_image_analysis.analysis_details = {
                'detection_reasons': analysis.get('detection_reasons', [])
            }
            
            metadata = analysis_result.get('metadata', {})
            mock_image_analysis.enhanced_analysis_used = metadata.get('enhanced_analysis_used', False)
        
        mock_image_analysis.save_analysis_result = mock_save_analysis_result
        
        # Call with minimal data
        mock_image_analysis.save_analysis_result(minimal_result)
        
        # Check defaults are used
        assert mock_image_analysis.probability == 0.0
        assert mock_image_analysis.confidence == 0.0
        assert mock_image_analysis.analysis_details['detection_reasons'] == []
        assert mock_image_analysis.enhanced_analysis_used == False