# type: ignore
from unittest.mock import Mock, patch
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from datetime import datetime
from app.views.report_views import (
    download_report,
    email_report,
    create_json_response
)
from app.models.text_analysis_result import TextAnalysisResult
from io import BytesIO
import pytest
import uuid

User = get_user_model()

class TestReportViews:
    """
    Unit tests for Report Views.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose 
    :version: 17/09/2025
    """

    @pytest.fixture
    def mock_user(self):
        """
        Create a mock authenticated user.
        """
        user = Mock()
        user.id = uuid.uuid4()
        user.username = 'testuser'
        user.email = 'testuser@example.com'
        user.first_name = 'Test'
        user.last_name = 'User'
        user.is_authenticated = True
        return user
    
    @pytest.fixture
    def mock_other_user(self):
        """
        Create a mock user for testing permissions.
        """
        user = Mock()
        user.id = uuid.uuid4()
        user.username = 'otheruser'
        user.email = 'other@example.com'
        user.first_name = 'Other'
        user.last_name = 'User'
        user.is_authenticated = True
        return user
    
    @pytest.fixture
    def api_factory(self):
        """
        Create APIRequestFactory instance for API request testing.
        """
        return APIRequestFactory()
    
    @pytest.fixture
    def mock_analysis_id(self):
        """
        Create a mock analysis ID.
        """
        return str(uuid.uuid4())
    
    @pytest.fixture
    def mock_submission(self, mock_user):
        """
        Create a mock submission with user ownership.
        """
        submission = Mock()
        submission.user = mock_user
        submission.content = "This is a sample text for analysis."
        submission.id = uuid.uuid4()
        return submission
    
    @pytest.fixture
    def mock_analysis_result(self, mock_submission):
        """
        Create a mock analysis result with submission.
        """
        analysis = Mock(spec=TextAnalysisResult)
        analysis.id = uuid.uuid4()
        analysis.submission = mock_submission
        analysis.detection_result = 'AI_GENERATED'
        analysis.probability = 0.85
        analysis.confidence = 0.92
        analysis.created_at = datetime.now()
        analysis.processing_time_ms = 1500
        analysis.enhanced_analysis_used = True
        analysis.detection_reasons = [
            {
                'type': 'critical',
                'title': 'High AI Probability',
                'description': 'Text shows strong AI generation patterns',
                'impact': 'Strong indicator of AI content'
            }
        ]
        analysis.statistics = {
            'total_words': 150,
            'sentences': 8,
            'avg_sentence_length': 18.75,
            'ai_keywords_count': 5,
            'transition_words_count': 12,
            'corporate_jargon_count': 3,
            'buzzwords_count': 2,
            'human_indicators_count': 1
        }
        return analysis
    
    @pytest.fixture
    def mock_pdf_buffer(self):
        """
        Create a mock PDF buffer.
        """
        buffer = BytesIO()
        buffer.write(b'%PDF-1.4 mock pdf content')
        buffer.seek(0)
        return buffer

    def test_create_json_response_success_structure(self):
        """
        Test that successful JSON response has correct structure.
        """
        
        data = {'key': 'value'}
        response = create_json_response(
            success=True,
            message='Test message',
            data=data
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        if response.data is not None:
            assert response.data['success'] is True
            assert response.data['message'] == 'Test message'
            assert response.data['data'] == data
            assert response.data['error'] is None
            assert 'timestamp' in response.data
            assert isinstance(response.data['timestamp'], str)

    def test_create_json_response_error_structure(self):
        """
        Test that error JSON response has correct structure.
        """
        response = create_json_response(
            success=False,
            error='Test error',
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        if response.data is not None:
            assert response.data['success'] is False
            assert response.data['error'] == 'Test error'
            assert response.data['data'] is None
            assert response.data['message'] is None
            assert 'timestamp' in response.data
            assert isinstance(response.data['timestamp'], str)

    @patch('app.views.report_views.ReportService')
    @patch('app.views.report_views.TextAnalysisResult.objects.get')
    def test_download_report_success(self, mock_get, mock_report_service, api_factory, mock_user, mock_analysis_id, mock_analysis_result, mock_pdf_buffer):
        """
        Test successful PDF report download.
        """
        # Setup mocks
        mock_get.return_value = mock_analysis_result
        mock_service_instance = Mock()
        mock_service_instance.generate_analysis_report.return_value = mock_pdf_buffer
        mock_report_service.return_value = mock_service_instance
        
        # Create request
        request = api_factory.get(f'/api/reports/analysis/{mock_analysis_id}/download/')
        force_authenticate(request, user=mock_user)
        
        # Call view
        response = download_report(request, mock_analysis_id)
        
        # Assertions
        assert isinstance(response, HttpResponse)
        assert response['Content-Type'] == 'application/pdf'
        assert response['Content-Disposition'] == f'attachment; filename="analysis_report_{mock_analysis_id}.pdf"'
        assert response.content == b'%PDF-1.4 mock pdf content'
        
        # Verify service calls
        mock_get.assert_called_once_with(id=mock_analysis_id)
        mock_service_instance.generate_analysis_report.assert_called_once_with(mock_analysis_result, mock_user.email)

    @patch('app.views.report_views.TextAnalysisResult.objects.get')
    def test_download_report_analysis_not_found(self, mock_get, api_factory, mock_user, mock_analysis_id):
        """
        Test download report when analysis doesn't exist.
        """
        mock_get.side_effect = TextAnalysisResult.DoesNotExist()
        
        request = api_factory.get(f'/api/reports/analysis/{mock_analysis_id}/download/')
        force_authenticate(request, user=mock_user)
        
        response = download_report(request, mock_analysis_id)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['success'] is False
        assert response.data['error'] == 'Analysis result not found'

    @patch('app.views.report_views.TextAnalysisResult.objects.get')
    def test_download_report_ownership_check(self, mock_get, api_factory, mock_other_user, mock_analysis_id, mock_analysis_result):
        """
        Test download report ownership validation.
        """
        mock_get.return_value = mock_analysis_result
        
        request = api_factory.get(f'/api/reports/analysis/{mock_analysis_id}/download/')
        force_authenticate(request, user=mock_other_user)
        
        response = download_report(request, mock_analysis_id)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['success'] is False
        assert response.data['error'] == 'You can only download reports for your own analyses'

    @patch('app.views.report_views.ReportService')
    @patch('app.views.report_views.TextAnalysisResult.objects.get')
    def test_download_report_service_exception(self, mock_get, mock_report_service, api_factory, mock_user, mock_analysis_id, mock_analysis_result):
        """
        Test handling of service exceptions in download report.
        """
        mock_get.return_value = mock_analysis_result
        mock_service_instance = Mock()
        mock_service_instance.generate_analysis_report.side_effect = Exception('PDF generation failed')
        mock_report_service.return_value = mock_service_instance
        
        request = api_factory.get(f'/api/reports/analysis/{mock_analysis_id}/download/')
        force_authenticate(request, user=mock_user)
        
        response = download_report(request, mock_analysis_id)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False
        assert 'Failed to generate report: PDF generation failed' in response.data['error']

    @patch('app.views.report_views.TextAnalysisResult.objects.get')
    def test_download_report_analysis_without_submission(self, mock_get, api_factory, mock_user, mock_analysis_id):
        """
        Test download report for analysis without submission (should pass ownership check).
        """
        mock_analysis = Mock()
        mock_analysis.id = mock_analysis_id
        mock_analysis.submission = None  # No submission means no ownership check
        mock_get.return_value = mock_analysis
        
        with patch('app.views.report_views.ReportService') as mock_report_service:
            mock_service_instance = Mock()
            mock_pdf_buffer = BytesIO()
            mock_pdf_buffer.write(b'%PDF-1.4 mock pdf content')
            mock_pdf_buffer.seek(0)
            mock_service_instance.generate_analysis_report.return_value = mock_pdf_buffer
            mock_report_service.return_value = mock_service_instance
            
            request = api_factory.get(f'/api/reports/analysis/{mock_analysis_id}/download/')
            force_authenticate(request, user=mock_user)
            
            response = download_report(request, mock_analysis_id)
            
            assert isinstance(response, HttpResponse)
            assert response['Content-Type'] == 'application/pdf'

    @patch('app.views.report_views.EmailService')
    @patch('app.views.report_views.TextAnalysisResult.objects.get')
    def test_email_report_success(self, mock_get, mock_email_service, api_factory, mock_user, mock_analysis_id, mock_analysis_result):
        """
        Test successful email report sending.
        """
        # Setup mocks
        mock_get.return_value = mock_analysis_result
        mock_service_instance = Mock()
        mock_service_instance.send_analysis_report.return_value = {
            'success': True,
            'recipient': mock_user.email
        }
        mock_email_service.return_value = mock_service_instance
        
        # Create request
        request = api_factory.post(f'/api/reports/analysis/{mock_analysis_id}/email/')
        force_authenticate(request, user=mock_user)
        
        # Call view
        response = email_report(request, mock_analysis_id)
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Report sent successfully to your email'
        assert response.data['data']['recipient'] == mock_user.email
        
        # Verify service calls
        mock_get.assert_called_once_with(id=mock_analysis_id)
        mock_service_instance.send_analysis_report.assert_called_once_with(
            mock_analysis_result, 
            mock_user.email,
            mock_user.first_name
        )

    @patch('app.views.report_views.TextAnalysisResult.objects.get')
    def test_email_report_analysis_not_found(self, mock_get, api_factory, mock_user, mock_analysis_id):
        """
        Test email report when analysis doesn't exist.
        """
        mock_get.side_effect = TextAnalysisResult.DoesNotExist()
        
        request = api_factory.post(f'/api/reports/analysis/{mock_analysis_id}/email/')
        force_authenticate(request, user=mock_user)
        
        response = email_report(request, mock_analysis_id)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['success'] is False
        assert response.data['error'] == 'Analysis result not found'

    @patch('app.views.report_views.TextAnalysisResult.objects.get')
    def test_email_report_ownership_check(self, mock_get, api_factory, mock_other_user, mock_analysis_id, mock_analysis_result):
        """
        Test email report ownership validation.
        """
        mock_get.return_value = mock_analysis_result
        
        request = api_factory.post(f'/api/reports/analysis/{mock_analysis_id}/email/')
        force_authenticate(request, user=mock_other_user)
        
        response = email_report(request, mock_analysis_id)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['success'] is False
        assert response.data['error'] == 'You can only email reports for your own analyses'

    @patch('app.views.report_views.EmailService')
    @patch('app.views.report_views.TextAnalysisResult.objects.get')
    def test_email_report_service_failure(self, mock_get, mock_email_service, api_factory, mock_user, mock_analysis_id, mock_analysis_result):
        """
        Test handling of email service failure.
        """
        mock_get.return_value = mock_analysis_result
        mock_service_instance = Mock()
        mock_service_instance.send_analysis_report.return_value = {
            'success': False,
            'error': 'Email delivery failed'
        }
        mock_email_service.return_value = mock_service_instance
        
        request = api_factory.post(f'/api/reports/analysis/{mock_analysis_id}/email/')
        force_authenticate(request, user=mock_user)
        
        response = email_report(request, mock_analysis_id)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False
        assert response.data['error'] == 'Email delivery failed'

    @patch('app.views.report_views.EmailService')
    @patch('app.views.report_views.TextAnalysisResult.objects.get')
    def test_email_report_service_exception(self, mock_get, mock_email_service, api_factory, mock_user, mock_analysis_id, mock_analysis_result):
        """
        Test handling of service exceptions in email report.
        """
        mock_get.return_value = mock_analysis_result
        mock_service_instance = Mock()
        mock_service_instance.send_analysis_report.side_effect = Exception('SMTP connection failed')
        mock_email_service.return_value = mock_service_instance
        
        request = api_factory.post(f'/api/reports/analysis/{mock_analysis_id}/email/')
        force_authenticate(request, user=mock_user)
        
        response = email_report(request, mock_analysis_id)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False
        assert 'Failed to send report: SMTP connection failed' in response.data['error']

    @patch('app.views.report_views.TextAnalysisResult.objects.get')
    def test_email_report_analysis_without_submission(self, mock_get, api_factory, mock_user, mock_analysis_id):
        """
        Test email report for analysis without submission (should pass ownership check).
        """
        mock_analysis = Mock()
        mock_analysis.id = mock_analysis_id
        mock_analysis.submission = None  # No submission means no ownership check
        mock_get.return_value = mock_analysis
        
        with patch('app.views.report_views.EmailService') as mock_email_service:
            mock_service_instance = Mock()
            mock_service_instance.send_analysis_report.return_value = {
                'success': True,
                'recipient': mock_user.email
            }
            mock_email_service.return_value = mock_service_instance
            
            request = api_factory.post(f'/api/reports/analysis/{mock_analysis_id}/email/')
            force_authenticate(request, user=mock_user)
            
            response = email_report(request, mock_analysis_id)
            
            assert response.status_code == status.HTTP_200_OK
            assert response.data['success'] is True

    def test_email_report_user_with_empty_first_name(self, api_factory, mock_analysis_id, mock_analysis_result):
        """
        Test email report with user having empty first name.
        """
        # Create user with empty first name
        mock_user_no_name = Mock()
        mock_user_no_name.id = uuid.uuid4()
        mock_user_no_name.username = 'testuser'
        mock_user_no_name.email = 'testuser@example.com'
        mock_user_no_name.first_name = ''
        mock_user_no_name.is_authenticated = True
        
        # Update mock_analysis_result to belong to this user
        mock_analysis_result.submission.user = mock_user_no_name
        
        with patch('app.views.report_views.TextAnalysisResult.objects.get') as mock_get:
            mock_get.return_value = mock_analysis_result
            
            with patch('app.views.report_views.EmailService') as mock_email_service:
                mock_service_instance = Mock()
                mock_service_instance.send_analysis_report.return_value = {
                    'success': True,
                    'recipient': mock_user_no_name.email
                }
                mock_email_service.return_value = mock_service_instance
                
                request = api_factory.post(f'/api/reports/analysis/{mock_analysis_id}/email/')
                force_authenticate(request, user=mock_user_no_name)
                
                response = email_report(request, mock_analysis_id)
                
                assert response.status_code == status.HTTP_200_OK
                # Verify that empty string is passed after strip()
                mock_service_instance.send_analysis_report.assert_called_once_with(
                    mock_analysis_result, 
                    mock_user_no_name.email,
                    ''  # Empty string after strip()
                )

    def test_report_views_require_authentication(self, api_factory, mock_analysis_id):
        """
        Test that report views require authentication.
        """
        views_and_requests = [
            (download_report, api_factory.get(f'/api/reports/analysis/{mock_analysis_id}/download/')),
            (email_report, api_factory.post(f'/api/reports/analysis/{mock_analysis_id}/email/')),
        ]
        
        for view, request in views_and_requests:
            response = view(request, mock_analysis_id)
            assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch('app.views.report_views.logger')
    @patch('app.views.report_views.ReportService')
    @patch('app.views.report_views.TextAnalysisResult.objects.get')
    def test_download_report_logging(self, mock_get, mock_report_service, mock_logger, api_factory, mock_user, mock_analysis_id, mock_analysis_result):
        """
        Test that download report exceptions are logged properly.
        """
        mock_get.return_value = mock_analysis_result
        mock_service_instance = Mock()
        mock_service_instance.generate_analysis_report.side_effect = Exception('PDF generation failed')
        mock_report_service.return_value = mock_service_instance
        
        request = api_factory.get(f'/api/reports/analysis/{mock_analysis_id}/download/')
        force_authenticate(request, user=mock_user)
        
        response = download_report(request, mock_analysis_id)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        mock_logger.error.assert_called_once_with('Failed to generate report: PDF generation failed')

    @patch('app.views.report_views.logger')
    @patch('app.views.report_views.EmailService')
    @patch('app.views.report_views.TextAnalysisResult.objects.get')
    def test_email_report_logging(self, mock_get, mock_email_service, mock_logger, api_factory, mock_user, mock_analysis_id, mock_analysis_result):
        """
        Test that email report exceptions are logged properly.
        """
        mock_get.return_value = mock_analysis_result
        mock_service_instance = Mock()
        mock_service_instance.send_analysis_report.side_effect = Exception('SMTP connection failed')
        mock_email_service.return_value = mock_service_instance
        
        request = api_factory.post(f'/api/reports/analysis/{mock_analysis_id}/email/')
        force_authenticate(request, user=mock_user)
        
        response = email_report(request, mock_analysis_id)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        mock_logger.error.assert_called_once_with('Failed to send report: SMTP connection failed')

    @patch('app.views.report_views.ReportService')
    @patch('app.views.report_views.TextAnalysisResult.objects.get')
    def test_download_report_pdf_buffer_handling(self, mock_get, mock_report_service, api_factory, mock_user, mock_analysis_id, mock_analysis_result):
        """
        Test proper handling of PDF buffer in download report.
        """
        mock_get.return_value = mock_analysis_result
        mock_service_instance = Mock()
        
        # Create a mock buffer that tracks read() calls
        mock_buffer = Mock()
        mock_buffer.read.return_value = b'%PDF-1.4 test content'
        mock_service_instance.generate_analysis_report.return_value = mock_buffer
        mock_report_service.return_value = mock_service_instance
        
        request = api_factory.get(f'/api/reports/analysis/{mock_analysis_id}/download/')
        force_authenticate(request, user=mock_user)
        
        response = download_report(request, mock_analysis_id)
        
        # Verify buffer.read() was called
        mock_buffer.read.assert_called_once()
        assert isinstance(response, HttpResponse)
        assert response.content == b'%PDF-1.4 test content'

    def test_create_json_response_default_values(self):
        """
        Test that JSON response uses default values correctly.
        """
        response = create_json_response()

        assert response.status_code == status.HTTP_200_OK
        
        if response.data is not None:
            assert response.data['success'] is True
            assert response.data['message'] is None
            assert response.data['data'] is None
            assert response.data['error'] is None
            assert 'timestamp' in response.data