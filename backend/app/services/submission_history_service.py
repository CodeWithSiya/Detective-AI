from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from app.models.text_submission import TextSubmission
from app.models.text_analysis_result import TextAnalysisResult
from app.serializers.submission_serializers import (
    TextSubmissionListSerializer,
    TextSubmissionUpdateSerializer,
    TextSubmissionDetailSerializer
)
from typing import Dict, Any, Optional

class SubmissionHistoryService:
    """
    Service class for handling user submission history operations.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 10/09/2025
    """

    @staticmethod
    def get_user_submissions(user: User, page: int = 1, page_size: int = 10, search: Optional[str] = None) -> Dict[str, Any]:
        """
        Get paginated submission history for a user.
         
        :param user: User to get submissions for 
        :param page: Page number
        :param page_size: Items per page
        :param search: Optional search term for submission names/content
        :return: Paginated submission data
        """
        try:
            # Base queryset.
            submissions_queryset = TextSubmission.objects.filter(user=user)
            
            # Apply search filter if provided.
            if search:
                submissions_queryset = submissions_queryset.filter(
                    Q(name__icontains=search) | Q(content__icontains=search)
                )
            
            # Order by most recent.
            submissions_queryset = submissions_queryset.order_by('-created_at')
            
            # Paginate.
            paginator = Paginator(submissions_queryset, page_size)
            page_obj = paginator.get_page(page)

            # Serialize with list serializer for basic information only.
            serializer = TextSubmissionListSerializer(page_obj.object_list, many=True)

            return {
                'success': True,
                'submissions': serializer.data,
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
    def get_submission_detail(submission_id: str, user: User) -> Dict[str, Any]:
        """
        Get detailed information for a specific submission.

        :param submission_id: ID of the submission
        :param user: User requesting the submission
        :return: Detailed submission data
        """
        try:
            # Get the submission with the given id and serialize it.
            submission = TextSubmission.objects.get(id=submission_id, user=user)
            serializer = TextSubmissionDetailSerializer(submission)
            
            return {
                'success': True,
                'submission': serializer.data
            }
            
        except TextSubmission.DoesNotExist:
            return {
                'success': False,
                'error': 'Submission not found or you do not have permission to access it'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def update_submission(submission_id: str, user: User, name: Optional[str] = None, content: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a submission's name or content.

        :param submission_id: ID of the submission to update
        :param user: User updating the submission
        :param name: New name (optional)
        :param content: New content (optional)
        :return: Updated submission data
        """
        try:
            submission = TextSubmission.objects.get(id=submission_id, user=user)
            
            # Prepare update data
            update_data = {}
            if name is not None:
                update_data['name'] = name
            if content is not None:
                update_data['content'] = content
            
            if not update_data:
                return {
                    'success': False,
                    'error': 'No data provided for update'
                }
            
            # Use serializer for validation
            serializer = TextSubmissionUpdateSerializer(submission, data=update_data, partial=True)
            
            if serializer.is_valid():
                updated_submission = serializer.save()
                
                # Return updated submission with basic info
                response_serializer = TextSubmissionUpdateSerializer(updated_submission)
                
                return {
                    'success': True,
                    'message': 'Submission updated successfully',
                    'submission': response_serializer.data
                }
            else:
                return {
                    'success': False,
                    'error': serializer.errors
                }
            
        except TextSubmission.DoesNotExist:
            return {
                'success': False,
                'error': 'Submission not found or you do not have permission to access it'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def delete_submission(submission_id: str, user: User) -> Dict[str, Any]:
        """
        Delete a submission and its associated analysis results.

        :param submission_id: ID of the submission to delete
        :param user: User deleting the submission
        :return: Success/error response
        """
        try:
            submission = TextSubmission.objects.get(id=submission_id, user=user)
            submission_name = submission.name
            
            # Delete the submission (this should cascade to analysis results)
            submission.delete()
            
            return {
                'success': True,
                'message': f'Submission "{submission_name}" deleted successfully'
            }
            
        except TextSubmission.DoesNotExist:
            return {
                'success': False,
                'error': 'Submission not found or you do not have permission to delete it'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_submission_statistics(user: User) -> Dict[str, Any]:
        """
        Get submission statistics for a user.

        :param user: User to get statistics for
        :return: Statistics data
        """
        try:
            total_submissions = TextSubmission.objects.filter(user=user).count()
            
            # Get analysis statistics
            content_type = ContentType.objects.get_for_model(TextSubmission)
            
            total_analyses = TextAnalysisResult.objects.filter(
                content_type=content_type,
                object_id__in=TextSubmission.objects.filter(user=user).values_list('id', flat=True)
            ).count()
            
            ai_detected = TextAnalysisResult.objects.filter(
                content_type=content_type,
                object_id__in=TextSubmission.objects.filter(user=user).values_list('id', flat=True),
                detection_result=TextAnalysisResult.DetectionResult.AI_GENERATED
            ).count()
            
            human_detected = TextAnalysisResult.objects.filter(
                content_type=content_type,
                object_id__in=TextSubmission.objects.filter(user=user).values_list('id', flat=True),
                detection_result=TextAnalysisResult.DetectionResult.HUMAN_WRITTEN
            ).count()
            
            return {
                'success': True,
                'statistics': {
                    'total_submissions': total_submissions,
                    'total_analyses': total_analyses,
                    'ai_detected_count': ai_detected,
                    'human_detected_count': human_detected,
                    'ai_detection_rate': round((ai_detected / total_analyses * 100), 2) if total_analyses > 0 else 0
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }