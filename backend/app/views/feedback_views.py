from datetime import datetime
from typing import Optional, Any
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from app.services.feedback_service import FeedbackService
from app.models.feedback import Feedback

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
@permission_classes([IsAuthenticated])
def submit_feedback(request, analysis_id):
    """
    Submit feedback for a specific text analysis result.

    POST /api/feedback/analysis/<analysis_id>/submit/
    """
    try:
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')
        
        if not rating:
            return create_json_response(
                success=False,
                error='Rating is required',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate rating value.
        valid_ratings = [Feedback.FeedbackRating.THUMBS_UP, Feedback.FeedbackRating.THUMBS_DOWN]
        if rating not in valid_ratings:
            return create_json_response(
                success=False,
                error=f'Rating must be one of: {valid_ratings}',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        result = FeedbackService.submit_feedback(
            analysis_id=analysis_id,
            user=request.user,
            rating=rating,
            comment=comment
        )
        
        if result['success']:
            return create_json_response(
                success=True,
                message=result.get('message'),
                data=result.get('data'),
                status_code=status.HTTP_201_CREATED
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_feedback(request):
    """
    Get all feedback submitted by a registered user.

    GET /api/feedback/?page=1&page_size=10
    """
    try:
        # Parse and validate pagination params
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10

        # Fetch feedback
        result = FeedbackService.get_user_feedback(
            user=request.user,
            page=page,
            page_size=page_size
        )

        if result['success']:
            return create_json_response(
                success=True,
                message='User feedback retrieved successfully',
                data={
                    'feedback': result.get('feedback'),
                    'pagination': result.get('pagination')
                }
            )

        return create_json_response(
            success=False,
            error=result.get('error'),
            status_code=status.HTTP_400_BAD_REQUEST
        )

    except ValueError:
        # Bad pagination params.
        return create_json_response(
            success=False,
            error="Invalid pagination parameters",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        # Unexpected server error.
        return create_json_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_feedback_for_analysis(request, analysis_id):
    """
    Get feedback for a specific analysis.

    GET /api/feedback/analysis/<analysis_id>/
    """
    try:
        result = FeedbackService.get_feedback_for_analysis(
            analysis_id=analysis_id,
            user=request.user
        )
        
        if result['success']:
            return create_json_response(
                success=True,
                message='User feedback retrieved successfully',
                data={
                    'feedback': result.get('feedback'),
                    'pagination': result.get('pagination')
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

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_feedback(request, feedback_id):
    """
    Delete user's feedback.

    DELETE /api/feedback/<feedback_id>/delete/
    """
    try:
        result = FeedbackService.delete_feedback(
            feedback_id=feedback_id,
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
def get_feedback_statistics(request):
    """
    Get feedback statistics for the authenticated user.

    GET /api/feedback/statistics/
    """
    try:
        result = FeedbackService.get_feedback_statistics(user=request.user)
        
        if result['success']:
            return create_json_response(
                success=True,
                message='Feedback statistics retrieved successfully',
                data={'statistics': result.get('statistics')}
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
    
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_all_feedback_admin(request):
    """
    Get all feedback for admin users.
    
    GET /api/admin/feedback/?page=1&page_size=20
    """
    try:

        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20
    
        result = FeedbackService.get_all_feedback_for_admin(
            page=page,
            page_size=page_size
        )
    
        if result['success']:
            return create_json_response(
                success=True,
                message='All feedback retrieved successfully',
                data={
                    'feedback': result.get('feedback'),
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
    
@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def mark_feedback_as_reviewed(request, feedback_id):
    """
    Mark feedback as reviewed (Admin only).

    PATCH /api/admin/feedback/<feedback_id>/reviewed/
    """
    try:
        result = FeedbackService.mark_feedback_as_reviewed(
            feedback_id=feedback_id,
            admin_user=request.user
        )
        
        if result['success']:
            return create_json_response(
                success=True,
                message=result['message'],
                data={'feedback': result['data']},
                status_code=status.HTTP_200_OK
            )
        else:
            return create_json_response(
                success=False,
                error=result['error'],
                status_code=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        return create_json_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def mark_feedback_as_resolved(request, feedback_id):
    """
    Mark feedback as resolved (Admin only).

    PATCH /api/admin/feedback/<feedback_id>/resolved/
    """
    try:
        result = FeedbackService.mark_feedback_as_resolved(
            feedback_id=feedback_id,
            admin_user=request.user
        )
        
        if result['success']:
            return create_json_response(
                success=True,
                message=result['message'],
                data={'feedback': result['data']},
                status_code=status.HTTP_200_OK
            )
        else:
            return create_json_response(
                success=False,
                error=result['error'],
                status_code=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        return create_json_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )