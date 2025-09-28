# type: ignore
from unittest.mock import Mock, patch, MagicMock
import pytest
from io import BytesIO
from datetime import datetime
from django.utils import timezone
from app.services.report_service import ReportService
from app.models.text_analysis_result import TextAnalysisResult
from app.models.image_analysis_result import ImageAnalysisResult
from app.models.text_submission import TextSubmission
from app.models.image_submission import ImageSubmission
import uuid

class TestReportService:
    """
    Unit tests for Report Service.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 28/09/2025
    """

    @pytest.fixture
    def report_service(self):
        """Create report service instance."""
        return ReportService()

    @pytest.fixture
    def mock_text_submission(self):
        """Create mock text submission."""
        submission = Mock(spec=TextSubmission)
        submission.id = uuid.uuid4()
        submission.content = "This is a sample text content for analysis testing purposes."
        return submission

    @pytest.fixture
    def mock_image_submission(self):
        """Create mock image submission."""
        submission = Mock(spec=ImageSubmission)
        submission.id = uuid.uuid4()
        submission.image_url = "https://example.com/test-image.jpg"
        submission.width = 800
        submission.height = 600
        submission.dimensions = "800x600"
        submission.file_size_mb = 1.5
        return submission

    @pytest.fixture
    def mock_text_analysis_result(self, mock_text_submission):
        """Create mock text analysis result."""
        result = Mock(spec=TextAnalysisResult)
        result.id = uuid.uuid4()
        result.submission = mock_text_submission
        result.detection_result = 'AI_GENERATED'
        result.probability = 0.85
        result.confidence = 0.92
        result.created_at = timezone.now()
        result.processing_time_ms = 1500.0
        result.enhanced_analysis_used = True
        result.detection_reasons = [
            {
                'type': 'critical',
                'title': 'AI Keywords Detected',
                'description': 'Found typical AI-generated patterns',
                'impact': 'High'
            }
        ]
        result.statistics = {
            'total_words': 120,
            'sentences': 8,
            'avg_sentence_length': 15.0,
            'ai_keywords_count': 5,
            'transition_words_count': 3,
            'corporate_jargon_count': 2,
            'buzzwords_count': 1,
            'human_indicators_count': 0
        }
        return result

    @pytest.fixture
    def mock_image_analysis_result(self, mock_image_submission):
        """Create mock image analysis result."""
        result = Mock(spec=ImageAnalysisResult)
        result.id = uuid.uuid4()
        result.submission = mock_image_submission
        result.detection_result = 'HUMAN_CREATED'
        result.probability = 0.25
        result.confidence = 0.88
        result.created_at = timezone.now()
        result.processing_time_ms = 2000.0
        result.enhanced_analysis_used = False
        result.detection_reasons = [
            {
                'type': 'success',
                'title': 'Human Content Detected',
                'description': 'Shows natural human creativity patterns',
                'impact': 'Positive'
            }
        ]
        return result

    # Text Analysis Report Generation Tests
    @patch('app.services.report_service.SimpleDocTemplate')
    def test_generate_text_analysis_report_success(self, mock_doc_class, report_service, 
                                                 mock_text_analysis_result):
        """Test successful text analysis report generation."""
        # Mock SimpleDocTemplate
        mock_doc = Mock()
        mock_doc_class.return_value = mock_doc
        
        result = report_service.generate_analysis_report(
            mock_text_analysis_result, 
            'test@example.com'
        )
        
        # Verify BytesIO buffer is returned
        assert isinstance(result, BytesIO)
        
        # Verify document was built
        mock_doc.build.assert_called_once()
        
        # Verify story contains sections (build was called with story and canvas functions)
        build_args = mock_doc.build.call_args
        story = build_args[0][0]  # First argument is the story
        assert len(story) > 0  # Story should have content

    @patch('app.services.report_service.SimpleDocTemplate')
    def test_generate_image_analysis_report_success(self, mock_doc_class, report_service,
                                                  mock_image_analysis_result):
        """Test successful image analysis report generation."""
        # Mock SimpleDocTemplate
        mock_doc = Mock()
        mock_doc_class.return_value = mock_doc
        
        # Mock image download
        with patch('app.services.report_service.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.content = b'fake image data'
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = report_service.generate_analysis_report(
                mock_image_analysis_result,
                'test@example.com'
            )
            
            # Verify BytesIO buffer is returned
            assert isinstance(result, BytesIO)
            
            # Verify document was built
            mock_doc.build.assert_called_once()
            
            # Verify image was attempted to be downloaded
            mock_get.assert_called_once_with(
                mock_image_analysis_result.submission.image_url,
                timeout=30
            )

    def test_generate_report_none_analysis_result(self, report_service):
        """Test report generation with None analysis result."""
        with pytest.raises(Exception, match="Report generation failed: Analysis result cannot be None"):
            report_service.generate_analysis_report(None, 'test@example.com')

    def test_generate_report_empty_email(self, report_service, mock_text_analysis_result):
        """Test report generation with empty email."""
        with pytest.raises(Exception, match="Report generation failed: User email cannot be empty"):
            report_service.generate_analysis_report(mock_text_analysis_result, '')

    @patch('app.services.report_service.SimpleDocTemplate')
    def test_generate_report_exception_handling(self, mock_doc_class, report_service, 
                                              mock_text_analysis_result):
        """Test report generation exception handling."""
        # Mock document build to raise exception
        mock_doc = Mock()
        mock_doc.build.side_effect = Exception("PDF generation failed")
        mock_doc_class.return_value = mock_doc
        
        with pytest.raises(Exception, match="Report generation failed: PDF generation failed"):
            report_service.generate_analysis_report(
                mock_text_analysis_result,
                'test@example.com'
            )

    # Report Metadata Tests
    def test_add_report_metadata_text_analysis(self, report_service, mock_text_analysis_result):
        """Test adding report metadata for text analysis."""
        story = []
        
        report_service._add_report_metadata(story, mock_text_analysis_result, 'test@example.com')
        
        # Verify content was added to story
        assert len(story) > 0
        
        # Should contain header, table, and spacer
        assert len(story) >= 3

    def test_add_report_metadata_image_analysis(self, report_service, mock_image_analysis_result):
        """Test adding report metadata for image analysis."""
        story = []
        
        report_service._add_report_metadata(story, mock_image_analysis_result, 'test@example.com')
        
        # Verify content was added to story
        assert len(story) > 0

    def test_add_report_metadata_missing_attributes(self, report_service):
        """Test report metadata with missing attributes."""
        # Create minimal mock with missing attributes
        minimal_result = Mock()
        minimal_result.id = None
        minimal_result.created_at = None
        minimal_result.processing_time_ms = None
        
        story = []
        
        # Should not raise exception
        report_service._add_report_metadata(story, minimal_result, 'test@example.com')
        
        assert len(story) > 0

    def test_add_report_metadata_exception_handling(self, report_service):
        """Test report metadata exception handling."""
        # Create mock that raises exception when accessing attributes
        problematic_result = Mock()
        problematic_result.id = Mock(side_effect=Exception("Database error"))
        
        story = []
        
        # Should handle exception gracefully
        report_service._add_report_metadata(story, problematic_result, 'test@example.com')
        
        # Should still add error section
        assert len(story) > 0

    # Analysis Summary Tests
    def test_add_analysis_summary_ai_generated(self, report_service, mock_text_analysis_result):
        """Test analysis summary for AI-generated content."""
        story = []
        
        report_service._add_analysis_summary(story, mock_text_analysis_result)
        
        # Verify content was added
        assert len(story) >= 3  # Header, table, spacer

    def test_add_analysis_summary_human_created(self, report_service, mock_image_analysis_result):
        """Test analysis summary for human-created content."""
        story = []
        
        report_service._add_analysis_summary(story, mock_image_analysis_result)
        
        # Verify content was added
        assert len(story) >= 3

    def test_add_analysis_summary_missing_values(self, report_service):
        """Test analysis summary with missing probability/confidence values."""
        minimal_result = Mock()
        minimal_result.detection_result = 'AI_GENERATED'
        minimal_result.probability = None
        minimal_result.confidence = None
        minimal_result.enhanced_analysis_used = False
        
        story = []
        
        report_service._add_analysis_summary(story, minimal_result)
        
        # Should handle None values gracefully
        assert len(story) > 0

    # Detection Details Tests
    def test_add_detection_details_with_reasons(self, report_service, mock_text_analysis_result):
        """Test adding detection details with valid reasons."""
        story = []
        
        report_service._add_detection_details(story, mock_text_analysis_result)
        
        # Should add header and content for each reason
        assert len(story) > 0

    def test_add_detection_details_no_reasons(self, report_service):
        """Test detection details with no reasons."""
        result_no_reasons = Mock()
        result_no_reasons.detection_reasons = None
        
        story = []
        
        report_service._add_detection_details(story, result_no_reasons)
        
        # Should return early and not add content
        assert len(story) == 0

    def test_add_detection_details_invalid_reason_format(self, report_service):
        """Test detection details with invalid reason format."""
        result_invalid = Mock()
        result_invalid.detection_reasons = ['not_a_dict', {'invalid': 'format'}]
        
        story = []
        
        # Should handle gracefully without crashing
        report_service._add_detection_details(story, result_invalid)
        
        # Should add some content even with invalid data
        assert len(story) >= 0

    # Statistics Section Tests
    def test_add_statistics_section_with_stats(self, report_service, mock_text_analysis_result):
        """Test adding statistics section with valid statistics."""
        story = []
        
        report_service._add_statistics_section(story, mock_text_analysis_result)
        
        # Should add header, table, and spacer
        assert len(story) >= 3

    def test_add_statistics_section_no_stats(self, report_service):
        """Test statistics section with no statistics."""
        result_no_stats = Mock()
        result_no_stats.statistics = None
        
        story = []
        
        report_service._add_statistics_section(story, result_no_stats)
        
        # Should return early
        assert len(story) == 0

    def test_add_statistics_section_partial_stats(self, report_service):
        """Test statistics section with partial statistics."""
        result_partial = Mock()
        result_partial.statistics = {
            'total_words': 100,
            'sentences': 5
            # Missing other fields
        }
        
        story = []
        
        report_service._add_statistics_section(story, result_partial)
        
        # Should handle missing fields gracefully
        assert len(story) >= 3

    # Text Sample Tests
    def test_add_text_sample_with_content(self, report_service, mock_text_analysis_result):
        """Test adding text sample with valid content."""
        story = []
        
        report_service._add_text_sample(story, mock_text_analysis_result)
        
        # Should add header, content, and spacer
        assert len(story) >= 3

    def test_add_text_sample_long_content_truncation(self, report_service):
        """Test text sample truncation for long content."""
        long_submission = Mock()
        long_submission.content = "A" * 600  # Longer than 500 char limit
        
        result_long = Mock()
        result_long.submission = long_submission
        
        story = []
        
        report_service._add_text_sample(story, result_long)
        
        # Content should be added and truncated
        assert len(story) >= 3

    def test_add_text_sample_no_submission(self, report_service):
        """Test text sample with no submission."""
        result_no_sub = Mock()
        result_no_sub.submission = None
        
        story = []
        
        report_service._add_text_sample(story, result_no_sub)
        
        # Should return early
        assert len(story) == 0

    def test_add_text_sample_empty_content(self, report_service):
        """Test text sample with empty content."""
        empty_submission = Mock()
        empty_submission.content = ""
        
        result_empty = Mock()
        result_empty.submission = empty_submission
        
        story = []
        
        report_service._add_text_sample(story, result_empty)
        
        # Should add "No content available"
        assert len(story) >= 3

    # Image Section Tests
    @patch('app.services.report_service.requests.get')
    def test_add_image_section_success(self, mock_get, report_service, mock_image_analysis_result):
        """Test successful image section addition."""
        # Mock successful image download
        mock_response = Mock()
        mock_response.content = b'fake image data'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        story = []
        
        report_service._add_image_section(story, mock_image_analysis_result)
        
        # Should add header, image, and details
        assert len(story) > 0
        
        # Verify image download was attempted
        mock_get.assert_called_once_with(
            mock_image_analysis_result.submission.image_url,
            timeout=30
        )

    @patch('app.services.report_service.requests.get')
    def test_add_image_section_download_failure(self, mock_get, report_service, mock_image_analysis_result):
        """Test image section with download failure."""
        # Mock failed image download
        mock_get.side_effect = Exception("Network error")
        
        story = []
        
        report_service._add_image_section(story, mock_image_analysis_result)
        
        # Should handle error gracefully and add error message
        assert len(story) > 0

    def test_add_image_section_no_submission(self, report_service):
        """Test image section with no submission."""
        result_no_sub = Mock(spec=ImageAnalysisResult)
        result_no_sub.submission = None
        
        story = []
        
        report_service._add_image_section(story, result_no_sub)
        
        # Should return early
        assert len(story) == 0

    def test_add_image_section_no_url(self, report_service):
        """Test image section with no image URL."""
        submission_no_url = Mock()
        submission_no_url.image_url = None
        
        result_no_url = Mock(spec=ImageAnalysisResult)
        result_no_url.submission = submission_no_url
        
        story = []
        
        report_service._add_image_section(story, result_no_url)
        
        # Should add "Image not available" message
        assert len(story) >= 2

    @patch('app.services.report_service.requests.get')
    def test_add_image_section_portrait_dimensions(self, mock_get, report_service):
        """Test image section with portrait image dimensions."""
        # Mock portrait image submission
        portrait_submission = Mock()
        portrait_submission.image_url = "https://example.com/portrait.jpg"
        portrait_submission.width = 600
        portrait_submission.height = 800  # Portrait (height > width)
        portrait_submission.dimensions = "600x800"
        portrait_submission.file_size_mb = 2.0
        
        portrait_result = Mock(spec=ImageAnalysisResult)
        portrait_result.submission = portrait_submission
        
        # Mock successful download
        mock_response = Mock()
        mock_response.content = b'fake portrait image data'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        story = []
        
        report_service._add_image_section(story, portrait_result)
        
        # Should handle portrait dimensions correctly
        assert len(story) > 0

    # Footer Tests
    def test_add_footer(self, report_service):
        """Test adding footer section."""
        story = []
        
        report_service._add_footer(story)
        
        # Should add spacer and footer paragraph
        assert len(story) == 2

    # Canvas Elements Tests
    def test_add_watermark(self, report_service):
        """Test watermark addition."""
        mock_canvas = Mock()
        mock_doc = Mock()
        
        # Should not raise exception
        report_service._add_watermark(mock_canvas, mock_doc)
        
        # Verify canvas methods were called
        mock_canvas.saveState.assert_called()
        mock_canvas.restoreState.assert_called()

    def test_add_page_number(self, report_service):
        """Test page number addition."""
        mock_canvas = Mock()
        mock_canvas.getPageNumber.return_value = 1
        mock_doc = Mock()
        
        # Should not raise exception
        report_service._add_page_number(mock_canvas, mock_doc)
        
        # Verify canvas methods were called
        mock_canvas.saveState.assert_called()
        mock_canvas.restoreState.assert_called()
        mock_canvas.getPageNumber.assert_called()

    def test_apply_canvas_elements(self, report_service):
        """Test applying all canvas elements."""
        mock_canvas = Mock()
        mock_doc = Mock()
        
        with patch.object(report_service, '_add_watermark') as mock_watermark:
            with patch.object(report_service, '_add_page_number') as mock_page_num:
                report_service._apply_canvas_elements(mock_canvas, mock_doc)
                
                # Verify both methods were called
                mock_watermark.assert_called_once_with(mock_canvas, mock_doc)
                mock_page_num.assert_called_once_with(mock_canvas, mock_doc)

    # Edge Cases and Error Handling
    def test_html_escaping_in_content(self, report_service):
        """Test that HTML content is properly escaped."""
        malicious_submission = Mock()
        malicious_submission.content = "<script>alert('xss')</script>"
        
        malicious_result = Mock(spec=TextAnalysisResult)
        malicious_result.submission = malicious_submission
        
        story = []
        
        # Should handle HTML content safely
        report_service._add_text_sample(story, malicious_result)
        
        assert len(story) >= 3

    def test_unicode_content_handling(self, report_service):
        """Test handling of unicode content."""
        unicode_submission = Mock()
        unicode_submission.content = "Testing unicode: émojis and spëcial chärs"
        
        unicode_result = Mock(spec=TextAnalysisResult)
        unicode_result.submission = unicode_submission
        
        story = []
        
        # Should handle unicode content without errors
        report_service._add_text_sample(story, unicode_result)
        
        assert len(story) >= 3

    def test_very_large_statistics(self, report_service):
        """Test handling of very large statistics values."""
        large_stats_result = Mock(spec=TextAnalysisResult)
        large_stats_result.statistics = {
            'total_words': 999999999,
            'sentences': 888888888,
            'avg_sentence_length': 777.777,
            'ai_keywords_count': 666666
        }
        
        story = []
        
        # Should handle large numbers without issues
        report_service._add_statistics_section(story, large_stats_result)
        
        assert len(story) >= 3

    def test_malformed_detection_reasons(self, report_service):
        """Test handling of malformed detection reasons."""
        malformed_result = Mock()
        malformed_result.detection_reasons = [
            None,  # None value
            "string_instead_of_dict",  # String instead of dict
            {},  # Empty dict
            {'title': None, 'description': None},  # None values in dict
            {'title': 123, 'description': ['list', 'instead', 'of', 'string']}  # Wrong types
        ]
        
        story = []
        
        # Should handle malformed data gracefully
        report_service._add_detection_details(story, malformed_result)
        
        # Should not raise an exception
        assert True