from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from app.services.ai_text_analyser import AiTextAnalyser
from app.services.ai_image_analyser import AiImageAnalyser
from app.models.text_submission import TextSubmission
from app.models.image_submission import ImageSubmission
from app.services.claude_service import ClaudeService
from app.ai.ai_text_model import AiTextModel
from app.ai.ai_image_model import AiImageModel
from typing import Optional, Any
from datetime import datetime
import tempfile
import os

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

    if not text or not str(text).strip():
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
                try:
                    # Use Claude to generate a smart name
                    claude_service = ClaudeService()
                    submission_name = claude_service.create_text_submission_name(text, max_length=50)
                except Exception:
                    # Fallback to date-based name if Claude fails
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
    
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def analyse_image(request):
    """
    Analyse image for AI generation detection.

    POST /api/analysis/image/
    """
    # Check if image file is provided.
    if 'image' not in request.FILES:
        return create_json_response(
            success=False,
            error='Image file is required',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    image_file = request.FILES['image']
    submission_name = request.data.get('name', None)

    # Validate file size.  # Fixed typo
    max_size = 10 * 1024 * 1024
    if image_file.size > max_size:
        return create_json_response(
            success=False,
            error='Image file too large. Maximum size is 10MB.',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png']
    file_extension = os.path.splitext(image_file.name)[1].lower()
    if file_extension not in allowed_extensions:
        return create_json_response(
            success=False,
            error='Unsupported file format. Please upload JPG, JPEG, or PNG files.',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    temp_file_path = None

    try:
        # Save uploaded file temporarily for analysis
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        # Create model and analyser instances
        model = AiImageModel()
        analyser = AiImageAnalyser(model)

        # For registered users, create a submission.
        submission = None
        if request.user.is_authenticated:
            # Generate submission name if not provided
            if not submission_name:
                try:
                    # Use Claude to generate a smart name
                    claude_service = ClaudeService()
                    submission_name = claude_service.create_image_submission_name(temp_file_path, max_length=50)
                except Exception:
                    # Fallback to filename-based name if Claude fails
                    submission_name = f"Image Analysis - {os.path.splitext(image_file.name)[0]}"

            # Create the submission with the uploaded image
            submission = ImageSubmission(
                name=submission_name,
                user=request.user
            )
            # Save the image file to Supabase storage
            submission.image.save(image_file.name, image_file, save=True)

        # Perform analysis (FIXED: moved outside the auth check)
        result = analyser.analyse(temp_file_path, user=request.user, submission=submission)

        response_data = {
            'analysis_result': result
        }

        # Add submission information for registered users
        if request.user.is_authenticated and submission:
            response_data['submission'] = {
                'id': str(submission.id),
                'name': submission.name,
                'image_url': submission.image.url if submission.image else None,  
                'file_size_mb': submission.file_size_mb,
                'dimensions': submission.dimensions,
                'created_at': submission.created_at.isoformat() if submission.created_at else None
            }

        return create_json_response(
            success=True,
            message='Image analysis completed successfully',
            data=response_data,
            status_code=status.HTTP_200_OK
        )
        
    except Exception as e:
        # Get the full stack trace
        import traceback
        tb_str = traceback.format_exc()
        print("=== FULL ERROR TRACEBACK ===")
        print(tb_str)
        print("============================")

        return create_json_response(
            success=False,
            error=f"Image analysis failed: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                print(f"Warning: Failed to clean up temporary file: {cleanup_error}")