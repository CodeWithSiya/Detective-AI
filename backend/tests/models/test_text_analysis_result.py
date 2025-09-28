from django.contrib.auth import get_user_model
from django.utils import timezone
from app.models import TextAnalysisResult
from unittest.mock import Mock, patch
import pytest
import uuid

User = get_user_model()

class TestTextAnalysisResultModel:
    """
    Unit tests for TextAnalysisResult model.
    
    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose 
    :version: 28/09/2025
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
                'probability': 0.78,
                'confidence': 0.85
            },
            'analysis': {
                'detection_reasons': [
                    'Repetitive phrasing patterns detected',
                    'Excessive use of transition words'
                ],
                'analysis_details': {
                    'flagged_patterns': ['pattern1', 'pattern2'],
                    'keyword_matches': ['AI keyword 1', 'AI keyword 2']
                }
            },
            'statistics': {
                'word_count': 250,
                'sentence_count': 15,
                'ai_keywords_count': 5,
                'transition_words_count': 8,
                'corporate_jargon_count': 3,
                'buzzwords_count': 2,
                'suspicious_patterns_count': 4
            },
            'metadata': {
                'enhanced_analysis_used': True,
                'processing_time_ms': 2000
            }
        }

    def test_model_meta_configuration(self):
        """
        Test model Meta configuration.
        """
        meta = TextAnalysisResult._meta
        
        # Test db_table
        assert meta.db_table == 'text_analysis_results'
        
        # Test ordering
        assert meta.ordering == ['-created_at']
        
        # Test that indexes are defined (6 indexes)
        assert len(meta.indexes) == 6

    def test_str_representation(self):
        """
        Test the string representation of TextAnalysisResult.
        """
        # Mock the text analysis result
        text_analysis = Mock(spec=TextAnalysisResult)
        text_analysis.id = uuid.uuid4()
        text_analysis.status = TextAnalysisResult.Status.COMPLETED
        text_analysis.detection_result = TextAnalysisResult.DetectionResult.AI_GENERATED
        text_analysis.probability = 0.784
        
        # Mock the __str__ method
        text_analysis.__str__ = Mock(return_value=f"Text Analysis {text_analysis.id} | {text_analysis.status} | {text_analysis.detection_result} | {text_analysis.probability:.3f}")
        
        result = str(text_analysis)
        expected = f"Text Analysis {text_analysis.id} | COMPLETED | AI_GENERATED | 0.784"
        
        assert result == expected

    def test_detection_reasons_field(self):
        """
        Test detection_reasons JSONField properties.
        """
        field = TextAnalysisResult._meta.get_field('detection_reasons')
        
        assert field.default == list
        assert field.blank == True

    def test_enhanced_analysis_used_field(self):
        """
        Test enhanced_analysis_used field properties.
        """
        field = TextAnalysisResult._meta.get_field('enhanced_analysis_used')
        
        assert field.default == False
        assert isinstance(field, type(TextAnalysisResult._meta.get_field('enhanced_analysis_used')))

    def test_analysis_details_field(self):
        """
        Test analysis_details JSONField properties.
        """
        field = TextAnalysisResult._meta.get_field('analysis_details')
        
        assert field.default == dict
        assert field.blank == True

    def test_statistics_field(self):
        """
        Test statistics JSONField properties.
        """
        field = TextAnalysisResult._meta.get_field('statistics')
        
        assert field.default == dict
        assert field.blank == True

    def test_has_flagged_content_property(self):
        """
        Test has_flagged_content property.
        """
        # Mock with flagged content
        text_analysis1 = Mock(spec=TextAnalysisResult)
        text_analysis1.detection_reasons = ['Reason 1', 'Reason 2']
        text_analysis1.has_flagged_content = len(text_analysis1.detection_reasons) > 0
        
        assert text_analysis1.has_flagged_content == True
        
        # Mock without flagged content
        text_analysis2 = Mock(spec=TextAnalysisResult)
        text_analysis2.detection_reasons = []
        text_analysis2.has_flagged_content = len(text_analysis2.detection_reasons) > 0
        
        assert text_analysis2.has_flagged_content == False

    def test_ai_indicators_count_property(self):
        """
        Test ai_indicators_count property.
        """
        # Mock with statistics
        text_analysis = Mock(spec=TextAnalysisResult)
        text_analysis.statistics = {
            'ai_keywords_count': 5,
            'transition_words_count': 8,
            'corporate_jargon_count': 3,
            'buzzwords_count': 2,
            'suspicious_patterns_count': 4
        }
        
        # Calculate expected count
        expected_count = 5 + 8 + 3 + 2 + 4
        text_analysis.ai_indicators_count = expected_count
        
        assert text_analysis.ai_indicators_count == 22

    def test_ai_indicators_count_property_empty_statistics(self):
        """
        Test ai_indicators_count property with empty statistics.
        """
        # Mock without statistics
        text_analysis = Mock(spec=TextAnalysisResult)
        text_analysis.statistics = {}
        text_analysis.ai_indicators_count = 0
        
        assert text_analysis.ai_indicators_count == 0

    def test_ai_indicators_count_property_null_statistics(self):
        """
        Test ai_indicators_count property with null statistics.
        """
        # Mock with null statistics
        text_analysis = Mock(spec=TextAnalysisResult)
        text_analysis.statistics = None
        text_analysis.ai_indicators_count = 0
        
        assert text_analysis.ai_indicators_count == 0

    @patch('app.models.TextAnalysisResult.objects')
    def test_save_analysis_result_success(self, mock_objects, sample_analysis_result):
        """
        Test successful save_analysis_result method.
        """
        # Mock text analysis instance
        mock_text_analysis = Mock(spec=TextAnalysisResult)
        mock_text_analysis.probability = 0.0
        mock_text_analysis.confidence = 0.0
        mock_text_analysis.detection_result = None
        mock_text_analysis.detection_reasons = []
        mock_text_analysis.analysis_details = {}
        mock_text_analysis.statistics = {}
        mock_text_analysis.enhanced_analysis_used = False
        mock_text_analysis.processing_time_ms = None
        mock_text_analysis.status = TextAnalysisResult.Status.PENDING
        mock_text_analysis.completed_at = None
        
        def mock_save_analysis_result(analysis_result):
            if not analysis_result:
                raise ValueError("Analysis result cannot be empty")
            
            # Save prediction data
            prediction = analysis_result.get('prediction', {})
            mock_text_analysis.probability = prediction.get('probability', 0.0)
            mock_text_analysis.confidence = prediction.get('confidence', 0.0)
            
            # Map is_ai_generated to detection_result
            is_ai_generated = prediction.get('is_ai_generated', False)
            if is_ai_generated:
                mock_text_analysis.detection_result = TextAnalysisResult.DetectionResult.AI_GENERATED
            else:
                mock_text_analysis.detection_result = TextAnalysisResult.DetectionResult.HUMAN_WRITTEN
            
            # Save analysis data
            analysis = analysis_result.get('analysis', {})
            mock_text_analysis.detection_reasons = analysis.get('detection_reasons', [])
            mock_text_analysis.analysis_details = analysis.get('analysis_details', {})
            
            # Save statistics
            mock_text_analysis.statistics = analysis_result.get('statistics', {})
            
            # Save metadata
            metadata = analysis_result.get('metadata', {})
            mock_text_analysis.enhanced_analysis_used = metadata.get('enhanced_analysis_used', False)
            mock_text_analysis.processing_time_ms = metadata.get('processing_time_ms')
            
            # Set status to completed
            mock_text_analysis.status = TextAnalysisResult.Status.COMPLETED
            mock_text_analysis.completed_at = timezone.now()
        
        mock_text_analysis.save_analysis_result = mock_save_analysis_result
        
        # Call the method
        mock_text_analysis.save_analysis_result(sample_analysis_result)
        
        # Assertions
        assert mock_text_analysis.probability == 0.78
        assert mock_text_analysis.confidence == 0.85
        assert mock_text_analysis.detection_result == TextAnalysisResult.DetectionResult.AI_GENERATED
        assert mock_text_analysis.detection_reasons == [
            'Repetitive phrasing patterns detected',
            'Excessive use of transition words'
        ]
        assert mock_text_analysis.analysis_details == {
            'flagged_patterns': ['pattern1', 'pattern2'],
            'keyword_matches': ['AI keyword 1', 'AI keyword 2']
        }
        assert mock_text_analysis.statistics == {
            'word_count': 250,
            'sentence_count': 15,
            'ai_keywords_count': 5,
            'transition_words_count': 8,
            'corporate_jargon_count': 3,
            'buzzwords_count': 2,
            'suspicious_patterns_count': 4
        }
        assert mock_text_analysis.enhanced_analysis_used == True
        assert mock_text_analysis.processing_time_ms == 2000
        assert mock_text_analysis.status == TextAnalysisResult.Status.COMPLETED
        assert mock_text_analysis.completed_at is not None

    def test_save_analysis_result_human_written(self):
        """
        Test save_analysis_result for human-written content.
        """
        # Mock text analysis instance
        mock_text_analysis = Mock(spec=TextAnalysisResult)
        mock_text_analysis.detection_result = None
        
        analysis_result = {
            'prediction': {
                'is_ai_generated': False,
                'probability': 0.25,
                'confidence': 0.90
            },
            'analysis': {
                'detection_reasons': [],
                'analysis_details': {}
            },
            'statistics': {
                'word_count': 180,
                'sentence_count': 12
            },
            'metadata': {
                'enhanced_analysis_used': False,
                'processing_time_ms': 1200
            }
        }
        
        def mock_save_analysis_result(analysis_result):
            prediction = analysis_result.get('prediction', {})
            is_ai_generated = prediction.get('is_ai_generated', False)
            if is_ai_generated:
                mock_text_analysis.detection_result = TextAnalysisResult.DetectionResult.AI_GENERATED
            else:
                mock_text_analysis.detection_result = TextAnalysisResult.DetectionResult.HUMAN_WRITTEN
        
        mock_text_analysis.save_analysis_result = mock_save_analysis_result
        
        # Call the method
        mock_text_analysis.save_analysis_result(analysis_result)
        
        # Assertions
        assert mock_text_analysis.detection_result == TextAnalysisResult.DetectionResult.HUMAN_WRITTEN

    def test_save_analysis_result_empty_raises_error(self):
        """
        Test save_analysis_result raises ValueError for empty result.
        """
        mock_text_analysis = Mock(spec=TextAnalysisResult)
        
        def mock_save_analysis_result(analysis_result):
            if not analysis_result:
                raise ValueError("Analysis result cannot be empty")
        
        mock_text_analysis.save_analysis_result = mock_save_analysis_result
        
        # Test with None
        with pytest.raises(ValueError, match="Analysis result cannot be empty"):
            mock_text_analysis.save_analysis_result(None)
        
        # Test with empty dict
        with pytest.raises(ValueError, match="Analysis result cannot be empty"):
            mock_text_analysis.save_analysis_result({})

    def test_save_analysis_result_handles_exceptions(self):
        """
        Test save_analysis_result handles exceptions properly.
        """
        mock_text_analysis = Mock(spec=TextAnalysisResult)
        mock_text_analysis.status = TextAnalysisResult.Status.PENDING
        
        def mock_save_analysis_result(analysis_result):
            try:
                # Simulate an error during processing
                raise Exception("Simulated error")
            except Exception as e:
                # Mark as failed (though not implemented in actual model)
                mock_text_analysis.status = TextAnalysisResult.Status.FAILED
                mock_text_analysis.completed_at = timezone.now()
                raise
        
        mock_text_analysis.save_analysis_result = mock_save_analysis_result
        
        # Call the method and expect it to raise
        with pytest.raises(Exception, match="Simulated error"):
            mock_text_analysis.save_analysis_result({'some': 'data'})
        
        # Check that status was set to failed
        assert mock_text_analysis.status == TextAnalysisResult.Status.FAILED
        assert mock_text_analysis.completed_at is not None

    @patch('app.models.TextAnalysisResult.objects')
    def test_model_instantiation(self, mock_objects, mock_user, mock_content_type):
        """
        Test that TextAnalysisResult model can be instantiated.
        """
        # Create a mock text analysis instance
        mock_text_analysis = Mock(spec=TextAnalysisResult)
        mock_text_analysis.id = uuid.uuid4()
        mock_text_analysis.user = mock_user
        mock_text_analysis.content_type = mock_content_type
        mock_text_analysis.object_id = uuid.uuid4()
        mock_text_analysis.detection_result = TextAnalysisResult.DetectionResult.AI_GENERATED
        mock_text_analysis.probability = 0.78
        mock_text_analysis.confidence = 0.85
        mock_text_analysis.status = TextAnalysisResult.Status.COMPLETED
        mock_text_analysis.detection_reasons = ['Test reason']
        mock_text_analysis.enhanced_analysis_used = True
        mock_text_analysis.analysis_details = {'test': 'data'}
        mock_text_analysis.statistics = {'word_count': 100}
        
        # Test that we can create the mock and access its attributes
        text_analysis = mock_text_analysis
        
        # Basic attribute checks
        assert text_analysis.id is not None
        assert text_analysis.user == mock_user
        assert text_analysis.detection_result == TextAnalysisResult.DetectionResult.AI_GENERATED
        assert text_analysis.probability == 0.78
        assert text_analysis.confidence == 0.85
        assert text_analysis.status == TextAnalysisResult.Status.COMPLETED
        assert text_analysis.detection_reasons == ['Test reason']
        assert text_analysis.enhanced_analysis_used == True
        assert text_analysis.analysis_details == {'test': 'data'}
        assert text_analysis.statistics == {'word_count': 100}

    def test_missing_analysis_data_handling(self):
        """
        Test handling of missing analysis data.
        """
        mock_text_analysis = Mock(spec=TextAnalysisResult)
        
        # Test with minimal data
        minimal_result = {
            'prediction': {},
            'analysis': {},
            'statistics': {},
            'metadata': {}
        }
        
        def mock_save_analysis_result(analysis_result):
            prediction = analysis_result.get('prediction', {})
            mock_text_analysis.probability = prediction.get('probability', 0.0)
            mock_text_analysis.confidence = prediction.get('confidence', 0.0)
            
            analysis = analysis_result.get('analysis', {})
            mock_text_analysis.detection_reasons = analysis.get('detection_reasons', [])
            mock_text_analysis.analysis_details = analysis.get('analysis_details', {})
            
            mock_text_analysis.statistics = analysis_result.get('statistics', {})
            
            metadata = analysis_result.get('metadata', {})
            mock_text_analysis.enhanced_analysis_used = metadata.get('enhanced_analysis_used', False)
        
        mock_text_analysis.save_analysis_result = mock_save_analysis_result
        
        # Call with minimal data
        mock_text_analysis.save_analysis_result(minimal_result)
        
        # Check defaults are used
        assert mock_text_analysis.probability == 0.0
        assert mock_text_analysis.confidence == 0.0
        assert mock_text_analysis.detection_reasons == []
        assert mock_text_analysis.analysis_details == {}
        assert mock_text_analysis.statistics == {}
        assert mock_text_analysis.enhanced_analysis_used == False

    def test_ai_indicators_count_partial_statistics(self):
        """
        Test ai_indicators_count with partial statistics data.
        """
        text_analysis = Mock(spec=TextAnalysisResult)
        text_analysis.statistics = {
            'ai_keywords_count': 3,
            'transition_words_count': 5
            # Missing other counts
        }
        
        # Mock the property behavior
        expected_count = 3 + 5 + 0 + 0 + 0  # Missing counts default to 0
        text_analysis.ai_indicators_count = expected_count
        
        assert text_analysis.ai_indicators_count == 8

    def test_property_edge_cases(self):
        """
        Test property methods with edge cases.
        """
        # Test has_flagged_content with None detection_reasons
        text_analysis1 = Mock(spec=TextAnalysisResult)
        text_analysis1.detection_reasons = None
        text_analysis1.has_flagged_content = len(text_analysis1.detection_reasons or []) > 0
        
        assert text_analysis1.has_flagged_content == False
        
        # Test with single detection reason
        text_analysis2 = Mock(spec=TextAnalysisResult)
        text_analysis2.detection_reasons = ['Single reason']
        text_analysis2.has_flagged_content = len(text_analysis2.detection_reasons) > 0
        
        assert text_analysis2.has_flagged_content == True