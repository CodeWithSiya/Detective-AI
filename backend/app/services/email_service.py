from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.text_analysis_result import TextAnalysisResult
from .report_service import ReportService
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """
    Service for sending emails on Detective AI.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 09/09/2025
    """

    def __init__(self):
        """
        Initialise the Email Service.
        """
        self.report_service = ReportService()

    def send_analysis_report(self, analysis_result: TextAnalysisResult, recipient_email: str,
                             recipient_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Send analysis report via email.

        :param analysis_result: TextAnalysisResult instance.
        :param recipient_email: Email address to send to.
        :param recipient_name: Optional recipient name
        :return: Dictionary with success status and message
        """
        try:
            # Input validation.
            if not analysis_result:
                raise ValueError("Analysis result cannot be None")
            if not recipient_email or '@' not in recipient_email:
                raise ValueError("Valid recipient email is required")

            # Generate PDF report.
            pdf_buffer = self.report_service.generate_analysis_report(
                analysis_result, recipient_email
            )
            pdf_buffer.seek(0)  # Reset buffer position
            
            # Date handling.
            created_at = getattr(analysis_result, 'created_at', None)
            report_date = created_at.strftime('%Y-%m-%d') if created_at else datetime.now().strftime('%Y-%m-%d')
            
            # Prepare email content
            context = {
                'recipient_name': recipient_name or recipient_email.split('@')[0],
                'analysis_result': analysis_result,
                'report_date': report_date,
                'confidence_percent': round(float(analysis_result.confidence * 100),2),
                'has_logo': True
            }

            subject = f"Detective AI Analysis Report - {report_date}"

            # Render HTML email template
            html_content = render_to_string('emails/analysis_report.html', context)
            text_content = render_to_string('emails/analysis_report.txt', context)
            
            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email]
            )
            
            # Add HTML version.
            email.attach_alternative(html_content, "text/html")
            
            # Attach PDF report
            analysis_id = getattr(analysis_result, 'id', 'unknown')
            filename = f"analysis_report_{analysis_id}.pdf"
            email.attach(filename, pdf_buffer.read(), 'application/pdf')
            
            # Send email
            email.send()

            logger.info(f"Analysis report sent successfully to {recipient_email}")
            
            return {
                'success': True,
                'message': 'Report sent successfully',
                'recipient': recipient_email
            }
            
        except Exception as e:
            logger.error(f"Failed to send analysis report to {recipient_email}: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to send report: {str(e)}'
            }
        
    def send_welcome_email(self, user_email: str, user_name: str) -> Dict[str, Any]:
        """Send welcome email to new users."""
        return {}