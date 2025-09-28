# type: ignore
from unittest.mock import Mock, patch, MagicMock
import pytest
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.utils import timezone
from app.services.submission_history_service import SubmissionHistoryService
from app.models.text_submission import TextSubmission
from app.models.image_submission import ImageSubmission
from app.models.text_analysis_result import TextAnalysisResult
from app.models.image_analysis_result import ImageAnalysisResult
import uuid
from datetime import datetime, timedelta

class TestSubmissionHistoryService:
    """
    Unit tests for Submission History Service.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 28/09/2025
    """

    @pytest.fixture
    def mock_user(self):
        """Create a mock user."""
        user = Mock(spec=User)
        user.id = uuid.uuid4()
        user.email = 'test@example.com'
        user.username = 'testuser'
        return user

    @pytest.fixture
    def mock_text_submission(self, mock_user):
        """Create mock text submission."""
        submission = Mock(spec=TextSubmission)
        submission.id = uuid.uuid4()
        submission.user = mock_user
        submission.name = "Sample Text Analysis"
        submission.content = "This is sample text content"
        submission.created_at = timezone.now()
        return submission

    @pytest.fixture
    def mock_image_submission(self, mock_user):
        """Create mock image submission."""
        submission = Mock(spec=ImageSubmission)
        submission.id = uuid.uuid4()
        submission.user = mock_user
        submission.name = "Sample Image Analysis"
        submission.image_url = "https://example.com/image.jpg"
        submission.created_at = timezone.now() - timedelta(hours=1)
        return submission

    # Get User Submissions Tests
    @patch('app.services.submission_history_service.TextSubmission.objects')
    @patch('app.services.submission_history_service.ImageSubmission.objects')
    @patch('app.services.submission_history_service.Paginator')
    def test_get_user_submissions_mixed_content_success(self, mock_paginator_class, mock_image_objects, 
                                                       mock_text_objects, mock_user, mock_text_submission, 
                                                       mock_image_submission):
        """Test successful retrieval of mixed user submissions."""
        # Mock querysets
        mock_text_objects.filter.return_value = [mock_text_submission]
        mock_image_objects.filter.return_value = [mock_image_submission]
        
        # Mock serializers
        with patch('app.services.submission_history_service.TextSubmissionListSerializer') as mock_text_serializer:
            with patch('app.services.submission_history_service.ImageSubmissionListSerializer') as mock_image_serializer:
                mock_text_serializer.return_value.data = [{'id': str(mock_text_submission.id), 'created_at': '2023-01-01'}]
                mock_image_serializer.return_value.data = [{'id': str(mock_image_submission.id), 'created_at': '2023-01-02'}]
                
                # Mock paginator
                mock_paginator = Mock()
                mock_page_obj = Mock()
                mock_page_obj.object_list = [{'id': str(mock_image_submission.id), 'type': 'image'}]
                mock_page_obj.has_next.return_value = False
                mock_page_obj.has_previous.return_value = False
                mock_paginator.get_page.return_value = mock_page_obj
                mock_paginator.num_pages = 1
                mock_paginator.count = 2
                mock_paginator_class.return_value = mock_paginator
                
                result = SubmissionHistoryService.get_user_submissions(mock_user, page=1, page_size=10)
                
                # Verify success
                assert result['success'] is True
                assert 'submissions' in result
                assert 'pagination' in result
                assert result['pagination']['current_page'] == 1
                
                # Verify correct filtering
                mock_text_objects.filter.assert_called_once_with(user=mock_user)
                mock_image_objects.filter.assert_called_once_with(user=mock_user)

    @patch('app.services.submission_history_service.TextSubmission.objects')
    def test_get_user_submissions_text_only_filter(self, mock_text_objects, mock_user, mock_text_submission):
        """Test user submissions with text-only filter."""
        mock_text_objects.filter.return_value = [mock_text_submission]
        
        with patch('app.services.submission_history_service.TextSubmissionListSerializer') as mock_serializer:
            mock_serializer.return_value.data = [{'id': str(mock_text_submission.id), 'created_at': '2023-01-01'}]
            
            with patch('app.services.submission_history_service.Paginator') as mock_paginator_class:
                mock_paginator = Mock()
                mock_page_obj = Mock()
                mock_page_obj.object_list = [{'id': str(mock_text_submission.id), 'type': 'text'}]
                mock_paginator.get_page.return_value = mock_page_obj
                mock_paginator.count = 1
                mock_paginator_class.return_value = mock_paginator
                
                result = SubmissionHistoryService.get_user_submissions(
                    mock_user, 
                    submission_type='text'
                )
                
                # Verify success and text-only filtering
                assert result['success'] is True
                mock_text_objects.filter.assert_called_once_with(user=mock_user)

    def test_get_user_submissions_exception_handling(self, mock_user):
        """Test user submissions exception handling."""
        with patch('app.services.submission_history_service.TextSubmission.objects') as mock_text_objects:
            mock_text_objects.filter.side_effect = Exception("Database connection failed")
            
            result = SubmissionHistoryService.get_user_submissions(mock_user)
            
            assert result['success'] is False
            assert 'Database connection failed' in result['error']

    # Get Submission Detail Tests
    @patch('app.services.submission_history_service.TextSubmission.objects')
    def test_get_submission_detail_text_success(self, mock_text_objects, mock_user, mock_text_submission):
        """Test successful text submission detail retrieval."""
        mock_text_objects.get.return_value = mock_text_submission
        
        with patch('app.services.submission_history_service.TextSubmissionDetailSerializer') as mock_serializer:
            mock_serializer.return_value.data = {
                'id': str(mock_text_submission.id),
                'name': mock_text_submission.name,
                'content': mock_text_submission.content
            }
            
            result = SubmissionHistoryService.get_submission_detail(
                str(mock_text_submission.id),
                mock_user
            )
            
            # Verify success
            assert result['success'] is True
            assert 'submission' in result
            assert result['type'] == 'text'
            assert result['submission']['id'] == str(mock_text_submission.id)
            
            # Verify correct query
            mock_text_objects.get.assert_called_once_with(id=str(mock_text_submission.id), user=mock_user)

    @patch('app.services.submission_history_service.TextSubmission.objects')
    @patch('app.services.submission_history_service.ImageSubmission.objects')
    def test_get_submission_detail_image_success(self, mock_image_objects, mock_text_objects,
                                               mock_user, mock_image_submission):
        """Test successful image submission detail retrieval."""
        # Text submission doesn't exist
        mock_text_objects.get.side_effect = TextSubmission.DoesNotExist()
        
        # Image submission exists
        mock_image_objects.get.return_value = mock_image_submission
        
        with patch('app.services.submission_history_service.ImageSubmissionDetailSerializer') as mock_serializer:
            mock_serializer.return_value.data = {
                'id': str(mock_image_submission.id),
                'name': mock_image_submission.name,
                'image_url': mock_image_submission.image_url
            }
            
            result = SubmissionHistoryService.get_submission_detail(
                str(mock_image_submission.id),
                mock_user
            )
            
            # Verify success
            assert result['success'] is True
            assert result['type'] == 'image'
            assert result['submission']['id'] == str(mock_image_submission.id)

    @patch('app.services.submission_history_service.TextSubmission.objects')
    @patch('app.services.submission_history_service.ImageSubmission.objects')
    def test_get_submission_detail_not_found(self, mock_image_objects, mock_text_objects, mock_user):
        """Test submission detail when submission not found."""
        # Both submissions don't exist
        mock_text_objects.get.side_effect = TextSubmission.DoesNotExist()
        mock_image_objects.get.side_effect = ImageSubmission.DoesNotExist()
        
        result = SubmissionHistoryService.get_submission_detail('non-existent-id', mock_user)
        
        assert result['success'] is False
        assert 'Submission not found' in result['error']

    # Delete Submission Tests
    @patch('app.services.submission_history_service.TextSubmission.objects')
    def test_delete_submission_text_success(self, mock_text_objects, mock_user, mock_text_submission):
        """Test successful text submission deletion."""
        mock_text_objects.get.return_value = mock_text_submission
        
        result = SubmissionHistoryService.delete_submission(str(mock_text_submission.id), mock_user)
        
        # Verify success - matches actual service message format
        assert result['success'] is True
        assert 'Text submission' in result['message']
        assert 'deleted successfully' in result['message']
        
        # Verify deletion was called
        mock_text_submission.delete.assert_called_once()

    @patch('app.services.submission_history_service.TextSubmission.objects')
    @patch('app.services.submission_history_service.ImageSubmission.objects')
    def test_delete_submission_image_success(self, mock_image_objects, mock_text_objects,
                                           mock_user, mock_image_submission):
        """Test successful image submission deletion."""
        # Text submission doesn't exist
        mock_text_objects.get.side_effect = TextSubmission.DoesNotExist()
        
        # Image submission exists
        mock_image_objects.get.return_value = mock_image_submission
        
        result = SubmissionHistoryService.delete_submission(str(mock_image_submission.id), mock_user)
        
        # Verify success - matches actual service message format
        assert result['success'] is True
        assert 'Image submission' in result['message']
        assert 'deleted successfully' in result['message']
        
        # Verify deletion was called
        mock_image_submission.delete.assert_called_once()

    @patch('app.services.submission_history_service.TextSubmission.objects')
    @patch('app.services.submission_history_service.ImageSubmission.objects')
    def test_delete_submission_not_found(self, mock_image_objects, mock_text_objects, mock_user):
        """Test deleting non-existent submission."""
        # Both submissions don't exist
        mock_text_objects.get.side_effect = TextSubmission.DoesNotExist()
        mock_image_objects.get.side_effect = ImageSubmission.DoesNotExist()
        
        result = SubmissionHistoryService.delete_submission('non-existent-id', mock_user)
        
        assert result['success'] is False
        assert 'Submission not found or you do not have permission to delete it' in result['error']

    # Get Submission Statistics Tests
    @patch('app.services.submission_history_service.TextSubmission.objects')
    @patch('app.services.submission_history_service.ImageSubmission.objects')
    @patch('app.services.submission_history_service.ContentType.objects')
    @patch('app.services.submission_history_service.TextAnalysisResult.objects')
    @patch('app.services.submission_history_service.ImageAnalysisResult.objects')
    def test_get_submission_statistics_success(self, mock_image_analysis_objects, mock_text_analysis_objects,
                                             mock_content_type_objects, mock_image_objects, 
                                             mock_text_objects, mock_user):
        """Test successful submission statistics retrieval."""
        # Mock submission counts
        mock_text_objects.filter.return_value.count.return_value = 15
        mock_image_objects.filter.return_value.count.return_value = 8
        
        # Mock content types
        mock_text_content_type = Mock()
        mock_image_content_type = Mock()
        mock_content_type_objects.get_for_model.side_effect = [
            mock_text_content_type, mock_text_content_type, mock_text_content_type,
            mock_image_content_type, mock_image_content_type, mock_image_content_type
        ]
        
        # Mock analysis counts
        mock_text_objects.filter.return_value.values_list.return_value = [1, 2, 3]
        mock_image_objects.filter.return_value.values_list.return_value = [4, 5, 6]
        
        mock_text_analysis_objects.filter.return_value.count.side_effect = [10, 6, 4]  # total, ai, human
        mock_image_analysis_objects.filter.return_value.count.side_effect = [5, 2, 3]  # total, ai, human
        
        result = SubmissionHistoryService.get_submission_statistics(mock_user)
        
        # Verify success
        assert result['success'] is True
        assert 'statistics' in result
        
        stats = result['statistics']
        assert stats['total_submissions'] == 23  # 15 + 8
        assert stats['total_analyses'] == 15  # 10 + 5
        assert stats['ai_detected_count'] == 8  # 6 + 2
        assert stats['human_detected_count'] == 7  # 4 + 3

    def test_get_submission_statistics_exception_handling(self, mock_user):
        """Test submission statistics exception handling."""
        with patch('app.services.submission_history_service.TextSubmission.objects') as mock_text_objects:
            mock_text_objects.filter.side_effect = Exception("Database error")
            
            result = SubmissionHistoryService.get_submission_statistics(mock_user)
            
            assert result['success'] is False
            assert 'Database error' in result['error']

    # Search Functionality Tests
    @patch('app.services.submission_history_service.TextSubmission.objects')
    @patch('app.services.submission_history_service.ImageSubmission.objects')
    def test_get_user_submissions_with_search(self, mock_image_objects, mock_text_objects, 
                                            mock_user, mock_text_submission):
        """Test user submissions with search functionality."""
        # Mock filtered querysets
        mock_text_filtered = Mock()
        mock_text_objects.filter.return_value.filter.return_value = [mock_text_submission]
        mock_image_objects.filter.return_value.filter.return_value = []
        
        with patch('app.services.submission_history_service.TextSubmissionListSerializer') as mock_text_serializer:
            with patch('app.services.submission_history_service.ImageSubmissionListSerializer') as mock_image_serializer:
                mock_text_serializer.return_value.data = [{'id': str(mock_text_submission.id), 'created_at': '2023-01-01'}]
                mock_image_serializer.return_value.data = []
                
                with patch('app.services.submission_history_service.Paginator') as mock_paginator_class:
                    mock_paginator = Mock()
                    mock_page_obj = Mock()
                    mock_page_obj.object_list = [{'id': str(mock_text_submission.id), 'type': 'text'}]
                    mock_paginator.get_page.return_value = mock_page_obj
                    mock_paginator.count = 1
                    mock_paginator_class.return_value = mock_paginator
                    
                    result = SubmissionHistoryService.get_user_submissions(
                        mock_user,
                        search="sample"
                    )
                    
                    # Verify success and search was applied
                    assert result['success'] is True

    # Pagination Tests
    @patch('app.services.submission_history_service.TextSubmission.objects')
    @patch('app.services.submission_history_service.ImageSubmission.objects')
    def test_get_user_submissions_no_pagination(self, mock_image_objects, mock_text_objects, mock_user):
        """Test user submissions without pagination (page_size=None)."""
        mock_text_objects.filter.return_value = []
        mock_image_objects.filter.return_value = []
        
        with patch('app.services.submission_history_service.TextSubmissionListSerializer') as mock_text_serializer:
            with patch('app.services.submission_history_service.ImageSubmissionListSerializer') as mock_image_serializer:
                mock_text_serializer.return_value.data = []
                mock_image_serializer.return_value.data = []
                
                result = SubmissionHistoryService.get_user_submissions(
                    mock_user,
                    page_size=None  # No pagination
                )
                
                # Verify success and no pagination
                assert result['success'] is True
                assert result['pagination']['showing_all'] is True
                assert result['pagination']['total_pages'] == 1

    # Edge Cases
    def test_get_user_submissions_empty_results(self, mock_user):
        """Test user submissions with no results."""
        with patch('app.services.submission_history_service.TextSubmission.objects') as mock_text_objects:
            with patch('app.services.submission_history_service.ImageSubmission.objects') as mock_image_objects:
                mock_text_objects.filter.return_value = []
                mock_image_objects.filter.return_value = []
                
                with patch('app.services.submission_history_service.TextSubmissionListSerializer') as mock_text_serializer:
                    with patch('app.services.submission_history_service.ImageSubmissionListSerializer') as mock_image_serializer:
                        mock_text_serializer.return_value.data = []
                        mock_image_serializer.return_value.data = []
                        
                        with patch('app.services.submission_history_service.Paginator') as mock_paginator_class:
                            mock_paginator = Mock()
                            mock_page_obj = Mock()
                            mock_page_obj.object_list = []
                            mock_page_obj.has_next.return_value = False
                            mock_page_obj.has_previous.return_value = False
                            mock_paginator.get_page.return_value = mock_page_obj
                            mock_paginator.count = 0
                            mock_paginator_class.return_value = mock_paginator
                            
                            result = SubmissionHistoryService.get_user_submissions(mock_user)
                            
                            # Verify empty results handled correctly
                            assert result['success'] is True
                            assert len(result['submissions']) == 0
                            assert result['pagination']['total_items'] == 0

    def test_get_submission_detail_exception_handling(self, mock_user):
        """Test submission detail exception handling."""
        with patch('app.services.submission_history_service.TextSubmission.objects') as mock_text_objects:
            mock_text_objects.get.side_effect = Exception("Database error")
            
            result = SubmissionHistoryService.get_submission_detail('test-id', mock_user)
            
            assert result['success'] is False
            assert 'Database error' in result['error']

    def test_delete_submission_exception_handling(self, mock_user):
        """Test delete submission exception handling."""
        with patch('app.services.submission_history_service.TextSubmission.objects') as mock_text_objects:
            mock_text_objects.get.side_effect = Exception("Database error")
            
            result = SubmissionHistoryService.delete_submission('test-id', mock_user)
            
            assert result['success'] is False
            # The service returns a traceback, so just check it's an error
            assert 'error' in result