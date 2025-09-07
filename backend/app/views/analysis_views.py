from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from app.services.ai_text_analyser import AiTextAnalyser
from app.models.text_submission import TextSubmission
from app.ai.ai_text_model import AiTextModel
from typing import Optional, Any
from datetime import datetime

def create_json_response(success: bool = True, message: Optional[str] = None, data: Optional[Any] = None, error: Optional[str] = None, status_code = status.HTTP_200_OK):
    """
    Create standardised JSON response.
    """
    response_data = {
        'success': success,
        'message': message,
        'data': data,
        'error': error,
        'timestamp': datetime.now().isoformat()
    }
    return Response(response_data, status=status_code)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def analyse_text(request):
    """
    Analyse text for AI generation detection.

    POST /api/analysis/text/
    """
    data = request.data

    # Validate required fields.
    text = data.get('text')
    submission_name = data.get('name', None)

    if not text:
        return create_json_response(
            success=False,
            error='Text field is required',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Create model and analyser instances.
        model = AiTextModel()
        analyser = AiTextAnalyser(model)

        # For registered users, create a submission.
        submission = None
        if request.user.is_authenticated:
            # Generate submission name if not provided.
            if not submission_name:
                submission_name = f"Text Analysis {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            # Create the submission.
            submission = TextSubmission.objects.create(
                name=submission_name,
                content=text,
                user=request.user
            )

        # Perform analysis.
        result = analyser.analyse(text, user=request.user, submission=submission)

        response_data = {
            'input_text': text,
            'analysis_result': result
        }

        # Add submission information for registered users.
        if request.user.is_authenticated and submission:
            response_data['submission'] = {
                'id': str(submission.id),
                'name': submission.name,
                'created_at': submission.created_at.isoformat()
            }

        return create_json_response(
            success=True,
            message='Text analysis completed successfully',
            data=response_data,
            status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return create_json_response(
            success=False,
            error=f"Analysis failed: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )