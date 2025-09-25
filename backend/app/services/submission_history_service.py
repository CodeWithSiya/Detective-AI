from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from app.models.text_submission import TextSubmission
from app.models.image_submission import ImageSubmission 
from app.models.text_analysis_result import TextAnalysisResult
from app.models.image_analysis_result import ImageAnalysisResult
from app.serializers.submission_serializers import (
    TextSubmissionListSerializer,
    TextSubmissionDetailSerializer,
    ImageSubmissionListSerializer,
    ImageSubmissionDetailSerializer,    
)
from typing import Dict, Any, Optional

class SubmissionHistoryService:
    """
    Service class for handling user submission history operations.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 10/09/2025
    """

    @staticmethod
    def get_user_submissions(user: User, page: int = 1, page_size: Optional[int] = 10, search: Optional[str] = None, submission_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get paginated submission history for a user (both text and images).
        
        :param user: User to get submissions for 
        :param page: Page number
        :param page_size: Items per page (None = return all)
        :param search: Optional search term for submission names/content
        :param submission_type: Optional filter ('text', 'image', or None for both)
        :return: Paginated submission data
        """
        try:
            all_submissions = []
            
            # Get text submissions using serializer.
            if submission_type != 'image':
                text_submissions = TextSubmission.objects.filter(user=user)
                if search:
                    text_submissions = text_submissions.filter(
                        Q(name__icontains=search) | Q(content__icontains=search)
                    )
                
                # Use TextSubmissionListSerializer.
                text_serializer = TextSubmissionListSerializer(text_submissions, many=True)
                for submission_data in text_serializer.data:
                    submission_data['type'] = 'text'  # Add type field.
                    all_submissions.append(submission_data)
            
            # Get image submissions using serializer.
            if submission_type != 'text':
                image_submissions = ImageSubmission.objects.filter(user=user)
                if search:
                    image_submissions = image_submissions.filter(name__icontains=search)
                
                # Use ImageSubmissionListSerializer.
                image_serializer = ImageSubmissionListSerializer(image_submissions, many=True)
                for submission_data in image_serializer.data:
                    submission_data['type'] = 'image'  # Add type field.
                    all_submissions.append(submission_data)
            
            # Sort by creation date (most recent first).
            all_submissions.sort(key=lambda x: x['created_at'], reverse=True)
            
            # Handle pagination - if page_size is None, return all results
            if page_size is None:
                # Return all submissions without pagination
                return {
                    'success': True,
                    'submissions': all_submissions,
                    'pagination': {
                        'current_page': 1,
                        'total_pages': 1,
                        'total_items': len(all_submissions),
                        'has_next': False,
                        'has_previous': False,
                        'showing_all': True  # Indicate this is showing all results.
                    }
                }
            else:
                # Use normal pagination.
                paginator = Paginator(all_submissions, page_size)
                page_obj = paginator.get_page(page)
                
                return {
                    'success': True,
                    'submissions': page_obj.object_list,
                    'pagination': {
                        'current_page': page,
                        'total_pages': paginator.num_pages,
                        'total_items': paginator.count,
                        'has_next': page_obj.has_next(),
                        'has_previous': page_obj.has_previous(),
                        'showing_all': False
                    }
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_submission_detail(submission_id: str, user: User, submission_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information for a specific submission (text or image).

        :param user: User requesting the submission
        :param submission_type: 'text' or 'image' (optional, will try both if not specified)
        :return: Detailed submission data
        """
        try:
            # Try to find as text submission first.
            if submission_type != 'image':
                try:
                    submission = TextSubmission.objects.get(id=submission_id, user=user)
                    serializer = TextSubmissionDetailSerializer(submission)
            
                    return {
                        'success': True,
                        'submission': serializer.data,
                        'type': 'text'
                    }
                except TextSubmission.DoesNotExist:
                    pass  # Continue to try image submission.

            # Try to find as image submission.
            if submission_type != 'text':
                try:
                    submission = ImageSubmission.objects.get(id=submission_id, user=user)
                    serializer = ImageSubmissionDetailSerializer(submission)
            
                    return {
                        'success': True,
                        'submission': serializer.data,
                        'type': 'image'
                    }
                except ImageSubmission.DoesNotExist:
                    pass  # Continue to return not found error
            
            # If we get here, submission wasn't found in either table.
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
        Delete a submission (text or image) and its associated analysis results.

        :param submission_id: ID of the submission to delete
        :param user: User deleting the submission
        :return: Success/error response
        """
        try:
            submission_name = None
            submission_type = None
            
            # Try to find and delete text submission first
            try:
                submission = TextSubmission.objects.get(id=submission_id, user=user)
                submission_name = submission.name
                submission_type = 'text'
                submission.delete()
                
                return {
                    'success': True,
                    'message': f'{submission_type.title()} submission "{submission_name}" deleted successfully'
                }
                
            except TextSubmission.DoesNotExist:
                pass  # Continue to try image submission
            
            # Try to find and delete image submission
            try:
                submission = ImageSubmission.objects.get(id=submission_id, user=user)
                submission_name = submission.name
                submission_type = 'image'
                submission.delete()
                
                return {
                    'success': True,
                    'message': f'{submission_type.title()} submission "{submission_name}" deleted successfully'
                }
                
            except ImageSubmission.DoesNotExist:
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
        Get submission statistics for a user (both text and image).

        :param user: User to get statistics for
        :return: Statistics data
        """
        try:
            # Text submission statistics
            total_text_submissions = TextSubmission.objects.filter(user=user).count()
            text_content_type = ContentType.objects.get_for_model(TextSubmission)
            
            total_text_analyses = TextAnalysisResult.objects.filter(
                content_type=text_content_type,
                object_id__in=TextSubmission.objects.filter(user=user).values_list('id', flat=True)
            ).count()
            
            text_ai_detected = TextAnalysisResult.objects.filter(
                content_type=text_content_type,
                object_id__in=TextSubmission.objects.filter(user=user).values_list('id', flat=True),
                detection_result=TextAnalysisResult.DetectionResult.AI_GENERATED
            ).count()
            
            text_human_detected = TextAnalysisResult.objects.filter(
                content_type=text_content_type,
                object_id__in=TextSubmission.objects.filter(user=user).values_list('id', flat=True),
                detection_result=TextAnalysisResult.DetectionResult.HUMAN_WRITTEN
            ).count()
            
            # Image submission statistics
            total_image_submissions = ImageSubmission.objects.filter(user=user).count()
            image_content_type = ContentType.objects.get_for_model(ImageSubmission)
            
            total_image_analyses = ImageAnalysisResult.objects.filter(
                content_type=image_content_type,
                object_id__in=ImageSubmission.objects.filter(user=user).values_list('id', flat=True)
            ).count()
            
            image_ai_detected = ImageAnalysisResult.objects.filter(
                content_type=image_content_type,
                object_id__in=ImageSubmission.objects.filter(user=user).values_list('id', flat=True),
                detection_result=ImageAnalysisResult.DetectionResult.AI_GENERATED
            ).count()
            
            image_human_detected = ImageAnalysisResult.objects.filter(
                content_type=image_content_type,
                object_id__in=ImageSubmission.objects.filter(user=user).values_list('id', flat=True),
                detection_result=ImageAnalysisResult.DetectionResult.HUMAN_WRITTEN
            ).count()
            
            # Combined statistics
            total_submissions = total_text_submissions + total_image_submissions
            total_analyses = total_text_analyses + total_image_analyses
            total_ai_detected = text_ai_detected + image_ai_detected
            total_human_detected = text_human_detected + image_human_detected
            
            return {
                'success': True,
                'statistics': {
                    'total_submissions': total_submissions,
                    'total_analyses': total_analyses,
                    'ai_detected_count': total_ai_detected,
                    'human_detected_count': total_human_detected,
                    'ai_detection_rate': round((total_ai_detected / total_analyses * 100), 2) if total_analyses > 0 else 0,
                    'breakdown': {
                        'text': {
                            'submissions': total_text_submissions,
                            'analyses': total_text_analyses,
                            'ai_detected': text_ai_detected,
                            'human_detected': text_human_detected
                        },
                        'image': {
                            'submissions': total_image_submissions,
                            'analyses': total_image_analyses,
                            'ai_detected': image_ai_detected,
                            'human_detected': image_human_detected
                        }
                    }
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }