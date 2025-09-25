from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from app.services.report_service import ReportService
from app.services.email_service import EmailService
from app.models.text_analysis_result import TextAnalysisResult
from app.models.image_analysis_result import ImageAnalysisResult
from typing import Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def create_json_response(success: bool = True, message: Optional[str] = None, data: Optional[Any] = None, error: Optional[str] = None, status_code = status.HTTP_200_OK):
    """Create standardised JSON response."""
    response_data = {
        'success': success,
        'message': message,
        'data': data,
        'error': error,
        'timestamp': datetime.now().isoformat()
    }
    return Response(response_data, status=status_code)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_report(request, analysis_id):
    """
    Download PDF report for an analysis (text or image).
    
    GET /api/reports/analysis/<analysis_id>/download/
    """
    try:
        # Try to get text analysis first
        analysis = None
        analysis_type = None
        
        try:
            analysis = TextAnalysisResult.objects.get(id=analysis_id)
            analysis_type = 'text'
        except TextAnalysisResult.DoesNotExist:
            try:
                analysis = ImageAnalysisResult.objects.get(id=analysis_id)
                analysis_type = 'image'
            except ImageAnalysisResult.DoesNotExist:
                return create_json_response(
                    success=False,
                    error='Analysis result not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        
        # Check ownership
        if analysis.submission and analysis.submission.user != request.user:
            return create_json_response(
                success=False,
                error='You can only download reports for your own analyses',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Generate report
        report_service = ReportService()
        pdf_buffer = report_service.generate_analysis_report(analysis, request.user.email)
        
        # Return PDF response
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{analysis_type}_analysis_report_{analysis_id}.pdf"'
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        return create_json_response(
            success=False,
            error=f'Failed to generate report: {str(e)}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def email_report(request, analysis_id):
    """
    Email PDF report for an analysis (text or image).
    
    POST /api/reports/analysis/<analysis_id>/email/
    """
    try:
        # Try to get text analysis first
        analysis = None
        analysis_type = None
        
        try:
            analysis = TextAnalysisResult.objects.get(id=analysis_id)
            analysis_type = 'text'
        except TextAnalysisResult.DoesNotExist:
            try:
                analysis = ImageAnalysisResult.objects.get(id=analysis_id)
                analysis_type = 'image'
            except ImageAnalysisResult.DoesNotExist:
                return create_json_response(
                    success=False,
                    error='Analysis result not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
        
        # Check ownership
        if analysis.submission and analysis.submission.user != request.user:
            return create_json_response(
                success=False,
                error='You can only email reports for your own analyses',
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        # Send email
        email_service = EmailService()
        result = email_service.send_analysis_report(
            analysis, 
            request.user.email,
            f"{request.user.first_name}".strip()
        )
        
        if result['success']:
            return create_json_response(
                success=True,
                message=f'{analysis_type.title()} analysis report sent successfully to your email',
                data={'recipient': result['recipient']}
            )
        else:
            return create_json_response(
                success=False,
                error=result['error'],
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Failed to send report: {str(e)}")
        return create_json_response(
            success=False,
            error=f'Failed to send report: {str(e)}',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )