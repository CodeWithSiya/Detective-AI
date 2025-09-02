from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from app.services.ai_text_analyser import AiTextAnalyser
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

        # Perform analysis.
        result = analyser.analyse(text)

        return create_json_response(
            success=True,
            message='Text analysis completed successfully',
            data={
                'input_text': text,
                'analysis_result': result
            },
            status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return create_json_response(
            success=False,
            error=f"Analysis failed: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )