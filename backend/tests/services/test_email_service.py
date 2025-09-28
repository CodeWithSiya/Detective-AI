# type: ignore
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from app.services.email_service import EmailService
from app.models.text_analysis_result import TextAnalysisResult
from app.models.image_analysis_result import ImageAnalysisResult
from app.models.text_submission import TextSubmission
from app.models.image_submission import ImageSubmission
import pytest
import uuid
from datetime import datetime
from io import BytesIO

class TestEmailService:
    """
    Unit tests for Email Service.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 28/09/2025
    """

    @pytest.fixture
    def email_service(self):
        """Create email service instance."""
        return EmailService()

    @pytest.fixture
    def mock_text_submission(self):
        """Create mock text submission."""
        submission = Mock(spec=TextSubmission)
        submission.id = uuid.uuid4()
        submission.name = "Test Text Analysis"
        submission.content = "Sample text content"
        return submission

    @pytest.fixture
    def mock_image_submission(self):
        """Create mock image submission."""
        submission = Mock(spec=ImageSubmission)
        submission.id = uuid.uuid4()
        submission.name = "Test Image Analysis"
        submission.image.url = "https://example.com/image.jpg"
        return submission

    @pytest.fixture
    def mock_text_analysis_result(self, mock_text_submission):
        """Create mock text analysis result."""
        result = Mock(spec=TextAnalysisResult)
        result.id = uuid.uuid4()
        result.submission = mock_text_submission
        result.confidence = 0.85
        result.created_at = timezone.now()
        result.is_ai_generated = True
        result.probability = 0.85
        return result

    @pytest.fixture
    def mock_image_analysis_result(self, mock_image_submission):
        """Create mock image analysis result."""
        result = Mock(spec=ImageAnalysisResult)
        result.id = uuid.uuid4()
        result.submission = mock_image_submission
        result.confidence = 0.92
        result.created_at = timezone.now()
        result.is_ai_generated = True
        result.probability = 0.92
        return result

    @pytest.fixture
    def mock_pdf_buffer(self):
        """Create mock PDF buffer."""
        buffer = BytesIO(b'fake pdf content')
        return buffer

    # Initialization Tests
    def test_init_creates_report_service(self, email_service):
        """Test that initialization creates report service."""
        assert email_service.report_service is not None

    # Analysis Report Email Tests
    @patch('app.services.email_service.EmailMultiAlternatives')
    @patch('app.services.email_service.render_to_string')
    def test_send_analysis_report_text_success(self, mock_render, mock_email_class, 
                                             email_service, mock_text_analysis_result, mock_pdf_buffer):
        """Test successful text analysis report email sending."""
        # Setup mocks
        mock_render.side_effect = ['<html>content</html>', 'text content']
        mock_email = Mock()
        mock_email_class.return_value = mock_email
        
        with patch.object(email_service.report_service, 'generate_analysis_report') as mock_generate:
            mock_generate.return_value = mock_pdf_buffer
            
            result = email_service.send_analysis_report(
                mock_text_analysis_result, 
                'test@example.com', 
                'Test User'
            )
            
            # Verify success
            assert result['success'] is True
            assert 'Text analysis report sent successfully' in result['message']
            assert result['recipient'] == 'test@example.com'
            
            # Verify email was created and sent
            mock_email_class.assert_called_once()
            mock_email.attach_alternative.assert_called_once_with('<html>content</html>', "text/html")
            mock_email.attach.assert_called_once()
            mock_email.send.assert_called_once()
            
            # Verify report generation
            mock_generate.assert_called_once_with(mock_text_analysis_result, 'test@example.com')

    @patch('app.services.email_service.EmailMultiAlternatives')
    @patch('app.services.email_service.render_to_string')
    def test_send_analysis_report_image_success(self, mock_render, mock_email_class,
                                              email_service, mock_image_analysis_result, mock_pdf_buffer):
        """Test successful image analysis report email sending."""
        # Setup mocks
        mock_render.side_effect = ['<html>content</html>', 'text content']
        mock_email = Mock()
        mock_email_class.return_value = mock_email
        
        with patch.object(email_service.report_service, 'generate_analysis_report') as mock_generate:
            mock_generate.return_value = mock_pdf_buffer
            
            result = email_service.send_analysis_report(
                mock_image_analysis_result,
                'test@example.com'
            )
            
            # Verify success
            assert result['success'] is True
            assert 'Image analysis report sent successfully' in result['message']
            
            # Verify email creation with correct subject
            call_args = mock_email_class.call_args[1]
            assert 'Detective AI Image Analysis Report' in call_args['subject']
            assert call_args['to'] == ['test@example.com']
            assert call_args['from_email'] == settings.DEFAULT_FROM_EMAIL
            
            # Verify PDF attachment with correct filename
            attach_call = mock_email.attach.call_args
            assert 'image_analysis_report_' in attach_call[0][0]
            assert attach_call[0][2] == 'application/pdf'

    def test_send_analysis_report_none_analysis_result(self, email_service):
        """Test sending report with None analysis result."""
        result = email_service.send_analysis_report(None, 'test@example.com')
        
        assert result['success'] is False
        assert 'Analysis result cannot be None' in result['error']

    def test_send_analysis_report_invalid_email(self, email_service, mock_text_analysis_result):
        """Test sending report with invalid email."""
        result = email_service.send_analysis_report(
            mock_text_analysis_result, 
            'invalid-email'
        )
        
        assert result['success'] is False
        assert 'Valid recipient email is required' in result['error']

    def test_send_analysis_report_no_recipient_name_uses_email(self, email_service, mock_text_analysis_result, mock_pdf_buffer):
        """Test that missing recipient name defaults to email username."""
        with patch.object(email_service.report_service, 'generate_analysis_report') as mock_generate:
            with patch('app.services.email_service.EmailMultiAlternatives') as mock_email_class:
                with patch('app.services.email_service.render_to_string') as mock_render:
                    mock_generate.return_value = mock_pdf_buffer
                    mock_render.side_effect = ['<html>content</html>', 'text content']
                    mock_email = Mock()
                    mock_email_class.return_value = mock_email
                    
                    result = email_service.send_analysis_report(
                        mock_text_analysis_result,
                        'john.doe@example.com'  # No recipient_name provided
                    )
                    
                    # Should use email username as name
                    render_calls = mock_render.call_args_list
                    context = render_calls[0][0][1]  # Second argument of first call
                    assert context['recipient_name'] == 'john.doe'

    @patch('app.services.email_service.EmailMultiAlternatives')
    def test_send_analysis_report_handles_email_send_failure(self, mock_email_class, 
                                                           email_service, mock_text_analysis_result, mock_pdf_buffer):
        """Test handling of email send failure."""
        mock_email = Mock()
        mock_email.send.side_effect = Exception("SMTP connection failed")
        mock_email_class.return_value = mock_email
        
        with patch.object(email_service.report_service, 'generate_analysis_report') as mock_generate:
            with patch('app.services.email_service.render_to_string'):
                mock_generate.return_value = mock_pdf_buffer
                
                result = email_service.send_analysis_report(
                    mock_text_analysis_result,
                    'test@example.com'
                )
                
                assert result['success'] is False
                assert 'SMTP connection failed' in result['error']

    # Welcome Email Tests
    @patch('app.services.email_service.EmailMultiAlternatives')
    @patch('app.services.email_service.render_to_string')
    def test_send_welcome_email_success(self, mock_render, mock_email_class, email_service):
        """Test successful welcome email sending."""
        # Setup mocks
        mock_render.side_effect = ['<html>welcome</html>', 'welcome text']
        mock_email = Mock()
        mock_email_class.return_value = mock_email
        
        result = email_service.send_welcome_email('newuser@example.com', 'New User')
        
        # Verify success
        assert result['success'] is True
        assert 'Welcome email sent successfully' in result['message']
        assert result['recipient'] == 'newuser@example.com'
        
        # Verify email creation
        call_args = mock_email_class.call_args[1]
        assert call_args['subject'] == "Welcome to Detective AI - Your Account is Ready!"
        assert call_args['to'] == ['newuser@example.com']
        
        # Verify templates were rendered with correct context
        render_calls = mock_render.call_args_list
        context = render_calls[0][0][1]
        assert context['user_name'] == 'New User'
        assert 'current_year' in context

    def test_send_welcome_email_invalid_email(self, email_service):
        """Test welcome email with invalid email address."""
        result = email_service.send_welcome_email('invalid-email', 'User')
        
        assert result['success'] is False
        assert 'Valid user email is required' in result['error']

    def test_send_welcome_email_empty_name_uses_email_username(self, email_service):
        """Test welcome email with empty name uses email username."""
        with patch('app.services.email_service.EmailMultiAlternatives') as mock_email_class:
            with patch('app.services.email_service.render_to_string') as mock_render:
                mock_render.side_effect = ['<html>content</html>', 'text content']
                mock_email = Mock()
                mock_email_class.return_value = mock_email
                
                result = email_service.send_welcome_email('jane.smith@example.com', '')
                
                # Should use email username as fallback
                render_calls = mock_render.call_args_list
                context = render_calls[0][0][1]
                assert context['user_name'] == 'jane.smith'

    # Forgot Password Email Tests
    @patch('app.services.email_service.EmailMultiAlternatives')
    @patch('app.services.email_service.render_to_string')
    def test_send_forgot_password_email_success(self, mock_render, mock_email_class, email_service):
        """Test successful forgot password email sending."""
        # Setup mocks
        mock_render.side_effect = ['<html>reset</html>', 'reset text']
        mock_email = Mock()
        mock_email_class.return_value = mock_email
        
        reset_url = 'https://example.com/reset/token123'
        result = email_service.send_forgot_password_email(
            'user@example.com', 
            'Test User', 
            reset_url,
            48  # Custom expiry hours
        )
        
        # Verify success
        assert result['success'] is True
        assert 'Password reset email sent successfully' in result['message']
        
        # Verify email creation
        call_args = mock_email_class.call_args[1]
        assert call_args['subject'] == "Password Reset Request - Detective AI"
        
        # Verify template context
        render_calls = mock_render.call_args_list
        context = render_calls[0][0][1]
        assert context['user_name'] == 'Test User'
        assert context['reset_url'] == reset_url
        assert context['expiry_hours'] == 48

    def test_send_forgot_password_email_missing_reset_url(self, email_service):
        """Test forgot password email with missing reset URL."""
        result = email_service.send_forgot_password_email(
            'user@example.com',
            'User',
            ''  # Empty reset URL
        )
        
        assert result['success'] is False
        assert 'Reset URL is required' in result['error']

    def test_send_forgot_password_email_default_expiry(self, email_service):
        """Test forgot password email uses default expiry hours."""
        with patch('app.services.email_service.EmailMultiAlternatives') as mock_email_class:
            with patch('app.services.email_service.render_to_string') as mock_render:
                mock_render.side_effect = ['<html>content</html>', 'text content']
                mock_email = Mock()
                mock_email_class.return_value = mock_email
                
                result = email_service.send_forgot_password_email(
                    'user@example.com',
                    'User',
                    'https://example.com/reset/token'
                    # No expiry_hours parameter - should default to 24
                )
                
                # Verify default expiry is used
                render_calls = mock_render.call_args_list
                context = render_calls[0][0][1]
                assert context['expiry_hours'] == 24

    # Verification Code Email Tests
    @patch('app.services.email_service.EmailMultiAlternatives')
    @patch('app.services.email_service.render_to_string')
    def test_send_verification_code_email_success(self, mock_render, mock_email_class, email_service):
        """Test successful verification code email sending."""
        # Setup mocks
        mock_render.side_effect = ['<html>verify</html>', 'verify text']
        mock_email = Mock()
        mock_email_class.return_value = mock_email
        
        result = email_service.send_verification_code_email(
            'newuser@example.com',
            'New User',
            '123456'
        )
        
        # Verify success
        assert result['success'] is True
        assert 'Verification code sent successfully' in result['message']
        
        # Verify email creation
        call_args = mock_email_class.call_args[1]
        assert call_args['subject'] == "Verify Your Detective AI Account - Verification Code"
        
        # Verify template context
        render_calls = mock_render.call_args_list
        context = render_calls[0][0][1]
        assert context['user_name'] == 'New User'
        assert context['verification_code'] == '123456'
        assert context['expiry_minutes'] == 15

    def test_send_verification_code_email_missing_code(self, email_service):
        """Test verification code email with missing code."""
        result = email_service.send_verification_code_email(
            'user@example.com',
            'User',
            ''  # Empty verification code
        )
        
        assert result['success'] is False
        assert 'Verification code is required' in result['error']

    def test_send_verification_code_email_empty_name_fallback(self, email_service):
        """Test verification code email with empty name uses email fallback."""
        with patch('app.services.email_service.EmailMultiAlternatives') as mock_email_class:
            with patch('app.services.email_service.render_to_string') as mock_render:
                mock_render.side_effect = ['<html>content</html>', 'text content']
                mock_email = Mock()
                mock_email_class.return_value = mock_email
                
                result = email_service.send_verification_code_email(
                    'bob.wilson@example.com',
                    '',  # Empty name
                    '654321'
                )
                
                # Should use email username as fallback
                render_calls = mock_render.call_args_list
                context = render_calls[0][0][1]
                assert context['user_name'] == 'bob.wilson'

    # Edge Cases and Error Handling
    def test_send_analysis_report_no_submission_name(self, email_service, mock_pdf_buffer):
        """Test analysis report when submission has no name."""
        # Create analysis result with submission that has no name
        result_mock = Mock(spec=TextAnalysisResult)
        result_mock.id = uuid.uuid4()
        result_mock.confidence = 0.75
        result_mock.created_at = timezone.now()
        
        submission_mock = Mock()
        submission_mock.name = None  # Fix: Set to None instead of undefined getattr
        result_mock.submission = submission_mock
        
        with patch.object(email_service.report_service, 'generate_analysis_report') as mock_generate:
            with patch('app.services.email_service.EmailMultiAlternatives') as mock_email_class:
                with patch('app.services.email_service.render_to_string') as mock_render:
                    mock_generate.return_value = mock_pdf_buffer
                    mock_render.side_effect = ['<html>content</html>', 'text content']
                    mock_email = Mock()
                    mock_email_class.return_value = mock_email
                    
                    result = email_service.send_analysis_report(
                        result_mock,
                        'test@example.com'
                    )
                    
                    # Should handle missing name gracefully
                    render_calls = mock_render.call_args_list
                    context = render_calls[0][0][1]
                    assert context['submission_name'] == 'Unknown' or context['submission_name'] is None

    def test_send_analysis_report_no_submission(self, email_service, mock_pdf_buffer):
        """Test analysis report when analysis has no submission."""
        # Create analysis result with no submission
        result_mock = Mock(spec=TextAnalysisResult)
        result_mock.id = uuid.uuid4()
        result_mock.confidence = 0.75
        result_mock.created_at = timezone.now()
        result_mock.submission = None  # No submission
        
        with patch.object(email_service.report_service, 'generate_analysis_report') as mock_generate:
            with patch('app.services.email_service.EmailMultiAlternatives') as mock_email_class:
                with patch('app.services.email_service.render_to_string') as mock_render:
                    mock_generate.return_value = mock_pdf_buffer
                    mock_render.side_effect = ['<html>content</html>', 'text content']
                    mock_email = Mock()
                    mock_email_class.return_value = mock_email
                    
                    result = email_service.send_analysis_report(
                        result_mock,
                        'test@example.com'
                    )
                    
                    # Should handle missing submission gracefully
                    render_calls = mock_render.call_args_list
                    context = render_calls[0][0][1]
                    assert context['submission_name'] == 'Unknown'

    def test_send_analysis_report_no_created_at(self, email_service, mock_pdf_buffer):
        """Test analysis report when analysis has no created_at date."""
        # Create analysis result with no created_at
        result_mock = Mock(spec=TextAnalysisResult)
        result_mock.id = uuid.uuid4()
        result_mock.confidence = 0.75
        result_mock.created_at = None  # No created_at
        result_mock.submission = Mock()
        result_mock.submission.name = "Test"
        
        with patch.object(email_service.report_service, 'generate_analysis_report') as mock_generate:
            with patch('app.services.email_service.EmailMultiAlternatives') as mock_email_class:
                with patch('app.services.email_service.render_to_string') as mock_render:
                    mock_generate.return_value = mock_pdf_buffer
                    mock_render.side_effect = ['<html>content</html>', 'text content']
                    mock_email = Mock()
                    mock_email_class.return_value = mock_email
                    
                    result = email_service.send_analysis_report(
                        result_mock,
                        'test@example.com'
                    )
                    
                    # Should use current date as fallback
                    render_calls = mock_render.call_args_list
                    context = render_calls[0][0][1]
                    assert context['report_date'] == datetime.now().strftime('%Y-%m-%d')

    @patch('app.services.email_service.EmailMultiAlternatives')
    def test_email_send_exception_handling(self, mock_email_class, email_service):
        """Test that all email methods handle send exceptions gracefully."""
        mock_email = Mock()
        mock_email.send.side_effect = Exception("Network error")
        mock_email_class.return_value = mock_email
        
        with patch('app.services.email_service.render_to_string'):
            # Test welcome email
            result = email_service.send_welcome_email('test@example.com', 'User')
            assert result['success'] is False
            assert 'Network error' in result['error']
            
            # Test forgot password email
            result = email_service.send_forgot_password_email(
                'test@example.com', 'User', 'https://example.com/reset'
            )
            assert result['success'] is False
            assert 'Network error' in result['error']
            
            # Test verification code email
            result = email_service.send_verification_code_email(
                'test@example.com', 'User', '123456'
            )
            assert result['success'] is False
            assert 'Network error' in result['error']

    def test_confidence_percentage_calculation(self, email_service, mock_pdf_buffer):
        """Test that confidence percentage is calculated correctly."""
        # Create analysis result with specific confidence
        result_mock = Mock(spec=TextAnalysisResult)
        result_mock.id = uuid.uuid4()
        result_mock.confidence = 0.8567  # Should round to 85.67%
        result_mock.created_at = timezone.now()
        result_mock.submission = Mock()
        result_mock.submission.name = "Test"
        
        with patch.object(email_service.report_service, 'generate_analysis_report') as mock_generate:
            with patch('app.services.email_service.EmailMultiAlternatives') as mock_email_class:
                with patch('app.services.email_service.render_to_string') as mock_render:
                    mock_generate.return_value = mock_pdf_buffer
                    mock_render.side_effect = ['<html>content</html>', 'text content']
                    mock_email = Mock()
                    mock_email_class.return_value = mock_email
                    
                    result = email_service.send_analysis_report(
                        result_mock,
                        'test@example.com'
                    )
                    
                    # Verify confidence percentage calculation
                    render_calls = mock_render.call_args_list
                    context = render_calls[0][0][1]
                    assert context['confidence_percent'] == 85.67