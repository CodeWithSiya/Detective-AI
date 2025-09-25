from datetime import datetime
from typing import Optional, Any
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from app.services.submission_history_service import SubmissionHistoryService

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_submissions(request):
    """
    Get user's submission history.

    GET /api/submissions/?page=1&page_size=10&search=query&type=text|image
    GET /api/submissions/ (returns all submissions)
    """
    try:
        # Parse pagination parameters
        page = request.GET.get('page', None)
        page_size = request.GET.get('page_size', None)
        search = request.GET.get('search', None)
        submission_type = request.GET.get('type', None)  # Add this line
        
        # Convert to integers if provided
        if page is not None:
            page = int(page)
            if page < 1:
                page = 1
        else:
            page = 1  # Default page
            
        if page_size is not None:
            page_size = int(page_size)
            if page_size < 1 or page_size > 50:
                page_size = 10
        else:
            # If no page_size provided, return ALL results
            page_size = None
        
        # Validate submission_type
        if submission_type and submission_type not in ['text', 'image']:
            submission_type = None
        
        result = SubmissionHistoryService.get_user_submissions(
            user=request.user,
            page=page,
            page_size=page_size,    # type: ignore
            search=search,
            submission_type=submission_type 
        )
        
        if result['success']:
            return create_json_response(
                success=True,
                message='Submissions retrieved successfully',
                data={
                    'submissions': result.get('submissions'),
                    'pagination': result.get('pagination')
                }
            )
        else:
            return create_json_response(
                success=False,
                error=result.get('error'),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    except ValueError:
        return create_json_response(
            success=False,
            error='Invalid pagination parameters',
            status_code=status.HTTP_400_BAD_REQUEST
        )
            
    except Exception as e:
        return create_json_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_submission_detail(request, submission_id):
    """
    Get detailed information for a specific submission.

    GET /api/submissions/<submission_id>/
    """
    try:
        result = SubmissionHistoryService.get_submission_detail(
            submission_id=submission_id,
            user=request.user
        )
        
        if result['success']:
            return create_json_response(
                success=True,
                message='Submission details retrieved successfully',
                data={'submission': result.get('submission')}
            )
        else:
            return create_json_response(
                success=False,
                error=result.get('error'),
                status_code=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        return create_json_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_submission(request, submission_id):
    """
    Delete a submission.

    DELETE /api/submissions/<submission_id>/
    """
    try:
        result = SubmissionHistoryService.delete_submission(
            submission_id=submission_id,
            user=request.user
        )
        
        if result['success']:
            return create_json_response(
                success=True,
                message=result.get('message')
            )
        else:
            return create_json_response(
                success=False,
                error=result.get('error'),
                status_code=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        return create_json_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_submission_statistics(request):
    """
    Get submission statistics for the user.

    GET /api/submissions/statistics/
    """
    try:
        result = SubmissionHistoryService.get_submission_statistics(
            user=request.user
        )
        
        if result['success']:
            return create_json_response(
                success=True,
                message='Statistics retrieved successfully',
                data={
                    'statistics': result.get('statistics')
                }
            )
        else:
            return create_json_response(
                success=False,
                error=result.get('error'),
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        return create_json_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )