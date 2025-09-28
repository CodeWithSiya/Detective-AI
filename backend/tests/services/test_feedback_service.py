# type: ignore
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from app.services.feedback_service import FeedbackService
from app.models.feedback import Feedback
from app.models.text_analysis_result import TextAnalysisResult
from app.models.image_analysis_result import ImageAnalysisResult
from app.models.text_submission import TextSubmission
from app.models.image_submission import ImageSubmission
import pytest
import uuid
from datetime import datetime
from django.utils import timezone

class TestFeedbackService:
    """
    Unit tests for Feedback Service.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 28/09/2025
    """

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        user = Mock(spec=User)
        user.id = uuid.uuid4()
        user.email = 'test@example.com'
        return user

    @pytest.fixture
    def mock_admin_user(self):
        """Create a mock admin user."""
        user = Mock(spec=User)
        user.id = uuid.uuid4()
        user.email = 'admin@example.com'
        user.is_staff = True
        return user

    @pytest.fixture
    def mock_text_submission(self, mock_user):
        """Create a mock text submission."""
        submission = Mock(spec=TextSubmission)
        submission.id = uuid.uuid4()
        submission.user = mock_user
        submission.content = "Sample text"
        return submission

    @pytest.fixture
    def mock_text_analysis_result(self, mock_text_submission):
        """Create a mock text analysis result."""
        result = Mock(spec=TextAnalysisResult)
        result.id = uuid.uuid4()
        result.submission = mock_text_submission
        result.confidence = 0.85
        result.is_ai_generated = True
        return result

    @pytest.fixture
    def mock_image_analysis_result(self, mock_user):
        """Create a mock image analysis result."""
        submission = Mock(spec=ImageSubmission)
        submission.id = uuid.uuid4()
        submission.user = mock_user
        
        result = Mock(spec=ImageAnalysisResult)
        result.id = uuid.uuid4()
        result.submission = submission
        result.confidence = 0.92
        result.is_ai_generated = False
        return result

    @pytest.fixture
    def mock_feedback(self, mock_user, mock_text_analysis_result):
        """Create a mock feedback object."""
        feedback = Mock(spec=Feedback)
        feedback.id = uuid.uuid4()
        feedback.user = mock_user
        feedback.rating = Feedback.FeedbackRating.THUMBS_UP
        feedback.comment = "Great analysis!"
        feedback.created_at = timezone.now()
        feedback.is_reviewed = False
        feedback.is_resolved = False
        return feedback

    # Submit Feedback Tests
    @patch('app.services.feedback_service.ContentType.objects.get_for_model')
    @patch('app.services.feedback_service.Feedback.objects')
    def test_submit_feedback_new_feedback_success(self, mock_feedback_objects, mock_content_type,
                                                mock_user, mock_text_analysis_result):
        """Test successful submission of new feedback."""
        # Mock validation
        with patch.object(FeedbackService, '_validate_analysis_access') as mock_validate:
            mock_validate.return_value = {'success': True, 'analysis': mock_text_analysis_result}
            
            # Mock no existing feedback
            mock_feedback_objects.filter.return_value.first.return_value = None
            
            # Mock feedback creation
            mock_feedback = Mock()
            mock_feedback.id = uuid.uuid4()
            mock_feedback_objects.create.return_value = mock_feedback
            
            # Mock serializer
            with patch('app.services.feedback_service.FeedbackSerializer') as mock_serializer_class:
                mock_serializer = Mock()
                mock_serializer.data = {'id': str(mock_feedback.id), 'rating': 'THUMBS_UP'}
                mock_serializer_class.return_value = mock_serializer
                
                result = FeedbackService.submit_feedback(
                    str(mock_text_analysis_result.id),
                    mock_user,
                    'THUMBS_UP',
                    'Great analysis!'
                )
                
                # Verify success
                assert result['success'] is True
                assert result['message'] == 'Feedback submitted successfully'
                assert 'data' in result
                
                # Verify feedback was created
                mock_feedback_objects.create.assert_called_once()
                create_call = mock_feedback_objects.create.call_args[1]
                assert create_call['user'] == mock_user
                assert create_call['rating'] == 'THUMBS_UP'
                assert create_call['comment'] == 'Great analysis!'

    @patch('app.services.feedback_service.ContentType.objects.get_for_model')
    @patch('app.services.feedback_service.Feedback.objects')
    def test_submit_feedback_update_existing_success(self, mock_feedback_objects, mock_content_type,
                                                   mock_user, mock_text_analysis_result, mock_feedback):
        """Test successful update of existing feedback."""
        # Mock validation
        with patch.object(FeedbackService, '_validate_analysis_access') as mock_validate:
            mock_validate.return_value = {'success': True, 'analysis': mock_text_analysis_result}
            
            # Mock existing feedback
            mock_feedback_objects.filter.return_value.first.return_value = mock_feedback
            
            # Mock update serializer
            with patch('app.services.feedback_service.FeedbackUpdateSerializer') as mock_update_serializer:
                with patch('app.services.feedback_service.FeedbackSerializer') as mock_serializer:
                    mock_update_instance = Mock()
                    mock_update_instance.is_valid.return_value = True
                    mock_update_instance.save.return_value = mock_feedback
                    mock_update_serializer.return_value = mock_update_instance
                    
                    mock_serializer_instance = Mock()
                    mock_serializer_instance.data = {'id': str(mock_feedback.id), 'rating': 'THUMBS_DOWN'}
                    mock_serializer.return_value = mock_serializer_instance
                    
                    result = FeedbackService.submit_feedback(
                        str(mock_text_analysis_result.id),
                        mock_user,
                        'THUMBS_DOWN',
                        'Updated comment'
                    )
                    
                    # Verify success
                    assert result['success'] is True
                    assert result['message'] == 'Feedback updated successfully'
                    
                    # Verify update was attempted
                    mock_update_serializer.assert_called_once_with(
                        mock_feedback,
                        data={'rating': 'THUMBS_DOWN', 'comment': 'Updated comment'}
                    )

    def test_submit_feedback_invalid_analysis_access(self, mock_user):
        """Test feedback submission with invalid analysis access."""
        with patch.object(FeedbackService, '_validate_analysis_access') as mock_validate:
            mock_validate.return_value = {
                'success': False,
                'error': 'You can only access feedback for your own analyses'
            }
            
            result = FeedbackService.submit_feedback('invalid-id', mock_user, 'THUMBS_UP')
            
            assert result['success'] is False
            assert 'You can only access feedback for your own analyses' in result['error']

    def test_submit_feedback_exception_handling(self, mock_user, mock_text_analysis_result):
        """Test feedback submission exception handling."""
        with patch.object(FeedbackService, '_validate_analysis_access') as mock_validate:
            mock_validate.side_effect = Exception("Database connection failed")
            
            result = FeedbackService.submit_feedback(
                str(mock_text_analysis_result.id),
                mock_user,
                'THUMBS_UP'
            )
            
            assert result['success'] is False
            assert 'Failed to submit feedback' in result['error']
            assert 'Database connection failed' in result['error']

    # Get User Feedback Tests
    @patch('app.services.feedback_service.Feedback.objects')
    @patch('app.services.feedback_service.Paginator')
    def test_get_user_feedback_success(self, mock_paginator_class, mock_feedback_objects, mock_user):
        """Test successful retrieval of user feedback."""
        # Mock feedback queryset
        mock_queryset = Mock()
        mock_feedback_objects.filter.return_value.order_by.return_value = mock_queryset
        
        # Mock paginator
        mock_paginator = Mock()
        mock_page_obj = Mock()
        mock_page_obj.object_list = [Mock(), Mock()]
        mock_page_obj.has_next.return_value = False
        mock_page_obj.has_previous.return_value = False
        mock_paginator.get_page.return_value = mock_page_obj
        mock_paginator.num_pages = 1
        mock_paginator.count = 2
        mock_paginator_class.return_value = mock_paginator
        
        # Mock serializer
        with patch('app.services.feedback_service.FeedbackSerializer') as mock_serializer_class:
            mock_serializer = Mock()
            mock_serializer.data = [{'id': '1'}, {'id': '2'}]
            mock_serializer_class.return_value = mock_serializer
            
            result = FeedbackService.get_user_feedback(mock_user, page=1, page_size=10)
            
            # Verify success
            assert result['success'] is True
            assert 'feedback' in result
            assert 'pagination' in result
            assert result['pagination']['current_page'] == 1
            assert result['pagination']['total_pages'] == 1
            assert result['pagination']['total_items'] == 2
            
            # Verify correct filtering
            mock_feedback_objects.filter.assert_called_once_with(user=mock_user)

    def test_get_user_feedback_exception_handling(self, mock_user):
        """Test user feedback retrieval exception handling."""
        with patch('app.services.feedback_service.Feedback.objects') as mock_feedback_objects:
            mock_feedback_objects.filter.side_effect = Exception("Database error")
            
            result = FeedbackService.get_user_feedback(mock_user)
            
            assert result['success'] is False
            assert 'Database error' in result['error']

    # Get Feedback for Analysis Tests
    @patch('app.services.feedback_service.ContentType.objects.get_for_model')
    @patch('app.services.feedback_service.Feedback.objects')
    def test_get_feedback_for_analysis_exists(self, mock_feedback_objects, mock_content_type,
                                            mock_user, mock_text_analysis_result, mock_feedback):
        """Test getting existing feedback for analysis."""
        with patch.object(FeedbackService, '_validate_analysis_access') as mock_validate:
            mock_validate.return_value = {'success': True, 'analysis': mock_text_analysis_result}
            
            # Mock existing feedback
            mock_feedback_objects.filter.return_value.first.return_value = mock_feedback
            
            # Mock serializer
            with patch('app.services.feedback_service.FeedbackSerializer') as mock_serializer_class:
                mock_serializer = Mock()
                mock_serializer.data = {'id': str(mock_feedback.id), 'rating': 'THUMBS_UP'}
                mock_serializer_class.return_value = mock_serializer
                
                result = FeedbackService.get_feedback_for_analysis(
                    str(mock_text_analysis_result.id),
                    mock_user
                )
                
                # Verify success
                assert result['success'] is True
                assert result['feedback'] is not None
                assert result['feedback']['id'] == str(mock_feedback.id)

    @patch('app.services.feedback_service.ContentType.objects.get_for_model')
    @patch('app.services.feedback_service.Feedback.objects')
    def test_get_feedback_for_analysis_not_exists(self, mock_feedback_objects, mock_content_type,
                                                mock_user, mock_text_analysis_result):
        """Test getting non-existent feedback for analysis."""
        with patch.object(FeedbackService, '_validate_analysis_access') as mock_validate:
            mock_validate.return_value = {'success': True, 'analysis': mock_text_analysis_result}
            
            # Mock no feedback
            mock_feedback_objects.filter.return_value.first.return_value = None
            
            result = FeedbackService.get_feedback_for_analysis(
                str(mock_text_analysis_result.id),
                mock_user
            )
            
            # Verify success with no feedback
            assert result['success'] is True
            assert result['feedback'] is None

    # Delete Feedback Tests
    @patch('app.services.feedback_service.Feedback.objects')
    def test_delete_feedback_success(self, mock_feedback_objects, mock_user, mock_feedback):
        """Test successful feedback deletion."""
        mock_feedback_objects.get.return_value = mock_feedback
        
        result = FeedbackService.delete_feedback(str(mock_feedback.id), mock_user)
        
        # Verify success
        assert result['success'] is True
        assert result['message'] == 'Feedback deleted successfully'
        
        # Verify deletion was called
        mock_feedback.delete.assert_called_once()
        mock_feedback_objects.get.assert_called_once_with(id=str(mock_feedback.id), user=mock_user)

    @patch('app.services.feedback_service.Feedback.objects')
    def test_delete_feedback_not_found(self, mock_feedback_objects, mock_user):
        """Test deleting non-existent feedback."""
        mock_feedback_objects.get.side_effect = Feedback.DoesNotExist()
        
        result = FeedbackService.delete_feedback('non-existent-id', mock_user)
        
        assert result['success'] is False
        assert 'Feedback not found or you do not have permission' in result['error']

    # Feedback Statistics Tests
    @patch('app.services.feedback_service.Feedback.objects')
    def test_get_feedback_statistics_success(self, mock_feedback_objects, mock_user):
        """Test successful feedback statistics retrieval."""
        # Mock count queries
        mock_feedback_objects.filter.return_value.count.side_effect = [10, 7, 3]  # total, thumbs_up, thumbs_down
        
        result = FeedbackService.get_feedback_statistics(mock_user)
        
        # Verify success
        assert result['success'] is True
        assert 'statistics' in result
        
        stats = result['statistics']
        assert stats['total_feedback'] == 10
        assert stats['thumbs_up'] == 7
        assert stats['thumbs_down'] == 3
        assert stats['satisfaction_rate'] == 70.0

    @patch('app.services.feedback_service.Feedback.objects')
    def test_get_feedback_statistics_no_feedback(self, mock_feedback_objects, mock_user):
        """Test feedback statistics with no feedback."""
        # Mock zero feedback
        mock_feedback_objects.filter.return_value.count.return_value = 0
        
        result = FeedbackService.get_feedback_statistics(mock_user)
        
        # Verify success with zero stats
        assert result['success'] is True
        stats = result['statistics']
        assert stats['total_feedback'] == 0
        assert stats['satisfaction_rate'] == 0

    # Admin Feedback Tests
    @patch('app.services.feedback_service.Feedback.objects')
    @patch('app.services.feedback_service.Paginator')
    def test_get_all_feedback_for_admin_success(self, mock_paginator_class, mock_feedback_objects):
        """Test successful admin feedback retrieval."""
        # Mock feedback queryset
        mock_queryset = Mock()
        mock_feedback_objects.select_related.return_value.order_by.return_value = mock_queryset
        
        # Mock paginator
        mock_paginator = Mock()
        mock_page_obj = Mock()
        mock_page_obj.object_list = [Mock(), Mock(), Mock()]
        mock_page_obj.has_next.return_value = True
        mock_page_obj.has_previous.return_value = False
        mock_paginator.get_page.return_value = mock_page_obj
        mock_paginator.num_pages = 5
        mock_paginator.count = 95
        mock_paginator_class.return_value = mock_paginator
        
        # Mock admin serializer
        with patch('app.services.feedback_service.FeedbackAdminSerializer') as mock_serializer_class:
            mock_serializer = Mock()
            mock_serializer.data = [{'id': '1'}, {'id': '2'}, {'id': '3'}]
            mock_serializer_class.return_value = mock_serializer
            
            result = FeedbackService.get_all_feedback_for_admin(page=2, page_size=20)
            
            # Verify success
            assert result['success'] is True
            assert 'feedback' in result
            assert 'pagination' in result
            assert result['pagination']['current_page'] == 2
            assert result['pagination']['total_pages'] == 5
            assert result['pagination']['has_next'] is True

    # Mark as Reviewed/Resolved Tests
    @patch('app.services.feedback_service.Feedback.objects')
    def test_mark_feedback_as_reviewed_success(self, mock_feedback_objects, mock_admin_user, mock_feedback):
        """Test successful marking feedback as reviewed."""
        mock_feedback_objects.get.return_value = mock_feedback
        
        with patch('app.services.feedback_service.FeedbackAdminSerializer') as mock_serializer_class:
            mock_serializer = Mock()
            mock_serializer.data = {'id': str(mock_feedback.id), 'is_reviewed': True}
            mock_serializer_class.return_value = mock_serializer
            
            result = FeedbackService.mark_feedback_as_reviewed(str(mock_feedback.id), mock_admin_user)
            
            # Verify success
            assert result['success'] is True
            assert result['message'] == 'Feedback marked as reviewed successfully'
            assert 'data' in result
            
            # Verify method was called
            mock_feedback.mark_as_reviewed.assert_called_once()

    @patch('app.services.feedback_service.Feedback.objects')
    def test_mark_feedback_as_resolved_success(self, mock_feedback_objects, mock_admin_user, mock_feedback):
        """Test successful marking feedback as resolved."""
        mock_feedback_objects.get.return_value = mock_feedback
        
        with patch('app.services.feedback_service.FeedbackAdminSerializer') as mock_serializer_class:
            mock_serializer = Mock()
            mock_serializer.data = {'id': str(mock_feedback.id), 'is_resolved': True}
            mock_serializer_class.return_value = mock_serializer
            
            result = FeedbackService.mark_feedback_as_resolved(str(mock_feedback.id), mock_admin_user)
            
            # Verify success
            assert result['success'] is True
            assert result['message'] == 'Feedback marked as resolved successfully'
            
            # Verify method was called
            mock_feedback.mark_as_resolved.assert_called_once()

    @patch('app.services.feedback_service.Feedback.objects')
    def test_mark_feedback_not_found(self, mock_feedback_objects, mock_admin_user):
        """Test marking non-existent feedback."""
        mock_feedback_objects.get.side_effect = Feedback.DoesNotExist()
        
        result = FeedbackService.mark_feedback_as_reviewed('non-existent-id', mock_admin_user)
        
        assert result['success'] is False
        assert 'Feedback not found' in result['error']

    # Validate Analysis Access Tests
    @patch('app.services.feedback_service.TextAnalysisResult.objects')
    def test_validate_analysis_access_text_success(self, mock_text_objects, mock_user, mock_text_analysis_result):
        """Test successful text analysis access validation."""
        mock_text_objects.get.return_value = mock_text_analysis_result
        
        result = FeedbackService._validate_analysis_access(str(mock_text_analysis_result.id), mock_user)
        
        assert result['success'] is True
        assert result['analysis'] == mock_text_analysis_result

    @patch('app.services.feedback_service.TextAnalysisResult.objects')
    @patch('app.services.feedback_service.ImageAnalysisResult.objects')
    def test_validate_analysis_access_image_success(self, mock_image_objects, mock_text_objects, 
                                                  mock_user, mock_image_analysis_result):
        """Test successful image analysis access validation."""
        # Text analysis doesn't exist
        mock_text_objects.get.side_effect = TextAnalysisResult.DoesNotExist()
        
        # Image analysis exists
        mock_image_objects.get.return_value = mock_image_analysis_result
        
        result = FeedbackService._validate_analysis_access(str(mock_image_analysis_result.id), mock_user)
        
        assert result['success'] is True
        assert result['analysis'] == mock_image_analysis_result

    @patch('app.services.feedback_service.TextAnalysisResult.objects')
    @patch('app.services.feedback_service.ImageAnalysisResult.objects')
    def test_validate_analysis_access_not_found(self, mock_image_objects, mock_text_objects, mock_user):
        """Test analysis access validation when analysis not found."""
        # Both analyses don't exist
        mock_text_objects.get.side_effect = TextAnalysisResult.DoesNotExist()
        mock_image_objects.get.side_effect = ImageAnalysisResult.DoesNotExist()
        
        result = FeedbackService._validate_analysis_access('non-existent-id', mock_user)
        
        assert result['success'] is False
        assert 'Analysis result not found' in result['error']

    @patch('app.services.feedback_service.TextAnalysisResult.objects')
    def test_validate_analysis_access_wrong_user(self, mock_text_objects, mock_user):
        """Test analysis access validation with wrong user."""
        # Create analysis with different user
        other_user = Mock()
        other_user.id = uuid.uuid4()
        
        analysis = Mock()
        analysis.submission = Mock()
        analysis.submission.user = other_user
        
        mock_text_objects.get.return_value = analysis
        
        result = FeedbackService._validate_analysis_access('analysis-id', mock_user)
        
        assert result['success'] is False
        assert 'You can only access feedback for your own analyses' in result['error']

    @patch('app.services.feedback_service.TextAnalysisResult.objects')
    def test_validate_analysis_access_no_submission(self, mock_text_objects, mock_user):
        """Test analysis access validation with no submission (anonymous analysis)."""
        analysis = Mock()
        analysis.submission = None  # Anonymous analysis
        
        mock_text_objects.get.return_value = analysis
        
        result = FeedbackService._validate_analysis_access('analysis-id', mock_user)
        
        assert result['success'] is True
        assert result['analysis'] == analysis

    # Edge Cases
    def test_submit_feedback_invalid_serializer(self, mock_user, mock_text_analysis_result, mock_feedback):
        """Test feedback submission with invalid serializer data."""
        with patch.object(FeedbackService, '_validate_analysis_access') as mock_validate:
            with patch('app.services.feedback_service.ContentType.objects.get_for_model'):
                with patch('app.services.feedback_service.Feedback.objects') as mock_feedback_objects:
                    mock_validate.return_value = {'success': True, 'analysis': mock_text_analysis_result}
                    mock_feedback_objects.filter.return_value.first.return_value = mock_feedback
                    
                    # Mock invalid serializer
                    with patch('app.services.feedback_service.FeedbackUpdateSerializer') as mock_update_serializer:
                        mock_update_instance = Mock()
                        mock_update_instance.is_valid.return_value = False
                        mock_update_instance.errors = {'rating': ['Invalid choice']}
                        mock_update_serializer.return_value = mock_update_instance
                        
                        result = FeedbackService.submit_feedback(
                            str(mock_text_analysis_result.id),
                            mock_user,
                            'INVALID_RATING'
                        )
                        
                        assert result['success'] is False
                        assert 'error' in result
                        assert result['error']['rating'] == ['Invalid choice']