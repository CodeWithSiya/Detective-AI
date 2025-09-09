from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from app.models.feedback import Feedback
from app.models.text_analysis_result import TextAnalysisResult
from app.serializers.feedback_serializers import (
    FeedbackSerializer,
    FeedbackAdminSerializer,
    FeedbackUpdateSerializer
)
from typing import Dict, Any

class FeedbackService:
    """
    Service class for handling user feedback operations.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 08/09/2025
    """

    @staticmethod
    def submit_feedback(analysis_id: str, user: User, rating: str, comment: str = "") -> Dict[str, Any]:
        """
        Submit feedback for an analysis result.

        :param analysis_id: ID of the analysis result
        :param user: User submitting feedback
        :param rating: Rating (THUMBS_UP or THUMBS_DOWN)
        :param comment: Optional comment
        :return: Feedback data or error
        """
        try:
            # Validate analysis access and return error if not.
            validation_result = FeedbackService._validate_analysis_access(analysis_id, user)
            if not validation_result['success']:
                return validation_result
            
            analysis = validation_result['analysis']
            content_type = ContentType.objects.get_for_model(analysis)

            # Check if feedback already exists.
            existing_feedback = Feedback.objects.filter(
                user=user,
                content_type=content_type,
                object_id=analysis.id
            ).first()
            
            if existing_feedback:
                # Update existing feedback using serializer.
                serializer = FeedbackUpdateSerializer(
                    existing_feedback,
                    data={'rating': rating, 'comment': comment}
                )
                if serializer.is_valid():
                    feedback = serializer.save()
                    message = 'Feedback updated successfully'
                else:
                    return {
                        'success': False,
                        'error': serializer.errors
                    }
            else:
                # Create new feedback directly
                feedback = Feedback.objects.create(
                    user=user,
                    content_type=content_type,
                    object_id=analysis.id,
                    rating=rating,
                    comment=comment
                )
                message = 'Feedback submitted successfully'

            # Serialize the feedback for response
            feedback_serializer = FeedbackSerializer(feedback)
            
            return {
                'success': True,
                'message': message,
                'data': feedback_serializer.data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to submit feedback: {str(e)}'
            }
    
    @staticmethod
    def get_user_feedback(user: User, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        Get paginated feedback history for a user.
         
        :param user: User to get feedback for 
        :param page: Page number
        :param page_size: Items per page
        :return: Paginated feedback data
        """
        try:
            feedback_queryset = Feedback.objects.filter(user=user).order_by('-created_at')
            paginator = Paginator(feedback_queryset, page_size)
            page_obj = paginator.get_page(page)

            serializer = FeedbackSerializer(page_obj.object_list, many=True)

            return {
                'success': True,
                'feedback': serializer.data,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_items': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        
    @staticmethod
    def get_feedback_for_analysis(analysis_id: str, user: User) -> Dict[str, Any]:
        """
        Get feedback for a specific analysis if it exists.

        :param analysis_id: ID of the analysis result
        :param user: User requesting the feedback
        :return: Feedback data or None
        """
        try:
            # Validate analysis access
            validation_result = FeedbackService._validate_analysis_access(analysis_id, user)
            if not validation_result['success']:
                return validation_result
            
            analysis = validation_result['analysis']
            content_type = ContentType.objects.get_for_model(analysis)

            # Get feedback if it exists
            feedback = Feedback.objects.filter(
                user=user,
                content_type=content_type,
                object_id=analysis.id
            ).first()

            if feedback:
                # Use serializer instead of manual dictionary creation
                serializer = FeedbackSerializer(feedback)
                return {
                    'success': True,
                    'feedback': serializer.data
                }
            else:
                return {
                    'success': True,
                    'feedback': None
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def delete_feedback(feedback_id: str, user: User) -> Dict[str, Any]:
        """
        Delete user's feedback.
        
        :param feedback_id: ID of the feedback to delete
        :param user: User requesting deletion
        :return: Success/error response
        """
        try:
            feedback = Feedback.objects.get(id=feedback_id, user=user)
            feedback.delete()
            
            return {
                'success': True,
                'message': 'Feedback deleted successfully'
            }
            
        except Feedback.DoesNotExist:
            return {
                'success': False,
                'error': 'Feedback not found or you do not have permission to delete it'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_feedback_statistics(user: User) -> Dict[str, Any]:
        """
        Get feedback statistics for a user.
        
        :param user: User to get statistics for
        :return: Feedback statistics
        """
        try:
            total_feedback = Feedback.objects.filter(user=user).count()
            thumbs_up = Feedback.objects.filter(
                user=user, 
                rating=Feedback.FeedbackRating.THUMBS_UP
            ).count()
            thumbs_down = Feedback.objects.filter(
                user=user, 
                rating=Feedback.FeedbackRating.THUMBS_DOWN
            ).count()
            
            # Calculate satisfaction rate
            satisfaction_rate = (thumbs_up / total_feedback * 100) if total_feedback > 0 else 0
            
            return {
                'success': True,
                'statistics': {
                    'total_feedback': total_feedback,
                    'thumbs_up': thumbs_up,
                    'thumbs_down': thumbs_down,
                    'satisfaction_rate': round(satisfaction_rate, 2)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        
    @staticmethod
    def get_all_feedback_for_admin(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Get all feedback for admin users.
        
        :param page: Page number
        :param page_size: Items per page
        :return: Paginated feedback data for all users
        """
        try:
            feedback_queryset = Feedback.objects.select_related('user').order_by('-created_at')
            paginator = Paginator(feedback_queryset, page_size)
            page_obj = paginator.get_page(page)

            # Use admin serializer
            serializer = FeedbackAdminSerializer(page_obj.object_list, many=True)

            return {
                'success': True,
                'feedback': serializer.data,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_items': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        
    @staticmethod
    def _validate_analysis_access(analysis_id: str, user: User) -> Dict[str, Any]:
        """
        Helper method to validate user access to analysis and associated feedback.

        :param analysis_id: ID of the analysis result
        :param user: User requesting access
        :return: Dictionary with success status and analysis object or error
        """
        try:
            analysis = TextAnalysisResult.objects.get(id=analysis_id)

            # Check if user has ownership over the analysis
            if analysis.submission is not None and analysis.submission.user != user:
                return {
                    'success': False,
                    'error': 'You can only access feedback for your own analyses'
                }
                
            return {
                'success': True,
                'analysis': analysis
            }
        
        except TextAnalysisResult.DoesNotExist:
            return {
                'success': False,
                'error': 'Analysis result not found'
            }