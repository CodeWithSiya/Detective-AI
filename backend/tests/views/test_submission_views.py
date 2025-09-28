# type: ignore
from unittest.mock import Mock, patch
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from datetime import datetime
from app.views.submission_history_views import (
    get_user_submissions,
    get_submission_detail,
    delete_submission,
    get_submission_statistics,
    create_json_response
)
import pytest
import uuid

class TestSubmissionHistoryViews:
    """
    Unit tests for Submission History Views.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose 
    :version: 28/09/2025
    """

    @pytest.fixture
    def mock_user(self):
        """Create a mock authenticated user."""
        user = Mock()
        user.id = uuid.uuid4()
        user.username = 'testuser'
        user.email = 'testuser@example.com'
        user.is_authenticated = True
        return user
    
    @pytest.fixture
    def api_factory(self):
        """Create APIRequestFactory instance for API request testing."""
        return APIRequestFactory()
    
    @pytest.fixture
    def mock_submission_id(self):
        """Create a mock submission ID."""
        return str(uuid.uuid4())
    
    @pytest.fixture
    def mock_submission_data(self):
        """Create mock submission data."""
        return {
            'id': str(uuid.uuid4()),
            'type': 'text',
            'content': 'Sample text content',
            'created_at': datetime.now().isoformat(),
            'analysis_result': {
                'detection_result': 'AI_GENERATED',
                'probability': 0.85
            }
        }
    
    @pytest.fixture
    def mock_submissions_list(self):
        """Create mock submissions list."""
        return [
            {
                'id': str(uuid.uuid4()),
                'type': 'text',
                'content': 'First submission',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': str(uuid.uuid4()),
                'type': 'image',
                'content': 'image.jpg',
                'created_at': datetime.now().isoformat()
            }
        ]
    
    @pytest.fixture
    def mock_pagination_data(self):
        """Create mock pagination data."""
        return {
            'current_page': 1,
            'total_pages': 2,
            'total_items': 15,
            'has_next': True,
            'has_previous': False
        }
    
    @pytest.fixture
    def mock_statistics_data(self):
        """Create mock statistics data."""
        return {
            'total_submissions': 25,
            'text_submissions': 15,
            'image_submissions': 10,
            'ai_generated_count': 12,
            'human_written_count': 13
        }

    # JSON Response Helper Tests
    def test_create_json_response_success(self):
        """Test successful JSON response structure."""
        data = {'key': 'value'}
        response = create_json_response(success=True, message='Test message', data=data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Test message'
        assert response.data['data'] == data
        assert 'timestamp' in response.data

    def test_create_json_response_error(self):
        """Test error JSON response structure."""
        response = create_json_response(
            success=False, 
            error='Test error', 
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert response.data['error'] == 'Test error'

    @patch('app.views.submission_history_views.SubmissionHistoryService.get_user_submissions')
    def test_get_user_submissions_success(self, mock_service, api_factory, mock_user, 
                                         mock_submissions_list, mock_pagination_data):
        """Test successful user submissions retrieval."""
        mock_service.return_value = {
            'success': True,
            'submissions': mock_submissions_list,
            'pagination': mock_pagination_data
        }
        
        request = api_factory.get('/api/submissions/')
        force_authenticate(request, user=mock_user)
        
        response = get_user_submissions(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Submissions retrieved successfully'
        assert response.data['data']['submissions'] == mock_submissions_list
        assert response.data['data']['pagination'] == mock_pagination_data
        
        mock_service.assert_called_once_with(
            user=mock_user, 
            page=1, 
            page_size=None, 
            search=None, 
            submission_type=None
        )

    @patch('app.views.submission_history_views.SubmissionHistoryService.get_user_submissions')
    def test_get_user_submissions_with_pagination(self, mock_service, api_factory, mock_user):
        """Test user submissions with pagination parameters."""
        mock_service.return_value = {
            'success': True,
            'submissions': [],
            'pagination': {'current_page': 2, 'total_pages': 5}
        }
        
        request = api_factory.get('/api/submissions/?page=2&page_size=10&search=test&type=text')
        force_authenticate(request, user=mock_user)
        
        response = get_user_submissions(request)
        
        assert response.status_code == status.HTTP_200_OK
        mock_service.assert_called_once_with(
            user=mock_user, 
            page=2, 
            page_size=10, 
            search='test', 
            submission_type='text'
        )

    def test_get_user_submissions_invalid_pagination(self, api_factory, mock_user):
        """Test user submissions with invalid pagination parameters."""
        request = api_factory.get('/api/submissions/?page=invalid&page_size=abc')
        force_authenticate(request, user=mock_user)
        
        response = get_user_submissions(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert response.data['error'] == 'Invalid pagination parameters'

    @patch('app.views.submission_history_views.SubmissionHistoryService.get_user_submissions')
    def test_get_user_submissions_service_failure(self, mock_service, api_factory, mock_user):
        """Test handling of service failure in submissions retrieval."""
        mock_service.return_value = {
            'success': False,
            'error': 'Database error'
        }
        
        request = api_factory.get('/api/submissions/')
        force_authenticate(request, user=mock_user)
        
        response = get_user_submissions(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert response.data['error'] == 'Database error'

    @patch('app.views.submission_history_views.SubmissionHistoryService.get_user_submissions')
    def test_get_user_submissions_exception(self, mock_service, api_factory, mock_user):
        """Test handling of service exception."""
        mock_service.side_effect = Exception('Unexpected error')
        
        request = api_factory.get('/api/submissions/')
        force_authenticate(request, user=mock_user)
        
        response = get_user_submissions(request)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['error'] == 'Unexpected error'

    @patch('app.views.submission_history_views.SubmissionHistoryService.get_submission_detail')
    def test_get_submission_detail_success(self, mock_service, api_factory, mock_user, 
                                          mock_submission_id, mock_submission_data):
        """Test successful submission detail retrieval."""
        mock_service.return_value = {
            'success': True,
            'submission': mock_submission_data
        }
        
        request = api_factory.get(f'/api/submissions/{mock_submission_id}/')
        force_authenticate(request, user=mock_user)
        
        response = get_submission_detail(request, mock_submission_id)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Submission details retrieved successfully'
        assert response.data['data']['submission'] == mock_submission_data
        
        mock_service.assert_called_once_with(
            submission_id=mock_submission_id,
            user=mock_user
        )

    @patch('app.views.submission_history_views.SubmissionHistoryService.get_submission_detail')
    def test_get_submission_detail_not_found(self, mock_service, api_factory, mock_user, mock_submission_id):
        """Test submission detail when submission not found."""
        mock_service.return_value = {
            'success': False,
            'error': 'Submission not found'
        }
        
        request = api_factory.get(f'/api/submissions/{mock_submission_id}/')
        force_authenticate(request, user=mock_user)
        
        response = get_submission_detail(request, mock_submission_id)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['success'] is False
        assert response.data['error'] == 'Submission not found'

    @patch('app.views.submission_history_views.SubmissionHistoryService.get_submission_detail')
    def test_get_submission_detail_exception(self, mock_service, api_factory, mock_user, mock_submission_id):
        """Test handling of service exception in detail retrieval."""
        mock_service.side_effect = Exception('Database error')
        
        request = api_factory.get(f'/api/submissions/{mock_submission_id}/')
        force_authenticate(request, user=mock_user)
        
        response = get_submission_detail(request, mock_submission_id)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['error'] == 'Database error'

    @patch('app.views.submission_history_views.SubmissionHistoryService.delete_submission')
    def test_delete_submission_success(self, mock_service, api_factory, mock_user, mock_submission_id):
        """Test successful submission deletion."""
        mock_service.return_value = {
            'success': True,
            'message': 'Submission deleted successfully'
        }
        
        request = api_factory.delete(f'/api/submissions/{mock_submission_id}/')
        force_authenticate(request, user=mock_user)
        
        response = delete_submission(request, mock_submission_id)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Submission deleted successfully'
        
        mock_service.assert_called_once_with(
            submission_id=mock_submission_id,
            user=mock_user
        )

    @patch('app.views.submission_history_views.SubmissionHistoryService.delete_submission')
    def test_delete_submission_not_found(self, mock_service, api_factory, mock_user, mock_submission_id):
        """Test deletion of non-existent submission."""
        mock_service.return_value = {
            'success': False,
            'error': 'Submission not found or you do not have permission to delete it'
        }
        
        request = api_factory.delete(f'/api/submissions/{mock_submission_id}/')
        force_authenticate(request, user=mock_user)
        
        response = delete_submission(request, mock_submission_id)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['success'] is False

    @patch('app.views.submission_history_views.SubmissionHistoryService.delete_submission')
    def test_delete_submission_exception(self, mock_service, api_factory, mock_user, mock_submission_id):
        """Test handling of service exception in deletion."""
        mock_service.side_effect = Exception('Database connection failed')
        
        request = api_factory.delete(f'/api/submissions/{mock_submission_id}/')
        force_authenticate(request, user=mock_user)
        
        response = delete_submission(request, mock_submission_id)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['error'] == 'Database connection failed'

    @patch('app.views.submission_history_views.SubmissionHistoryService.get_submission_statistics')
    def test_get_submission_statistics_success(self, mock_service, api_factory, mock_user, mock_statistics_data):
        """Test successful statistics retrieval."""
        mock_service.return_value = {
            'success': True,
            'statistics': mock_statistics_data
        }
        
        request = api_factory.get('/api/submissions/statistics/')
        force_authenticate(request, user=mock_user)
        
        response = get_submission_statistics(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Statistics retrieved successfully'
        assert response.data['data']['statistics'] == mock_statistics_data
        
        mock_service.assert_called_once_with(user=mock_user)

    @patch('app.views.submission_history_views.SubmissionHistoryService.get_submission_statistics')
    def test_get_submission_statistics_failure(self, mock_service, api_factory, mock_user):
        """Test handling of service failure in statistics retrieval."""
        mock_service.return_value = {
            'success': False,
            'error': 'Unable to calculate statistics'
        }
        
        request = api_factory.get('/api/submissions/statistics/')
        force_authenticate(request, user=mock_user)
        
        response = get_submission_statistics(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert response.data['error'] == 'Unable to calculate statistics'

    @patch('app.views.submission_history_views.SubmissionHistoryService.get_submission_statistics')
    def test_get_submission_statistics_exception(self, mock_service, api_factory, mock_user):
        """Test handling of service exception in statistics retrieval."""
        mock_service.side_effect = Exception('Statistics calculation failed')
        
        request = api_factory.get('/api/submissions/statistics/')
        force_authenticate(request, user=mock_user)
        
        response = get_submission_statistics(request)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['error'] == 'Statistics calculation failed'

    def test_submission_views_require_authentication(self, api_factory, mock_submission_id):
        """Test that all submission views require authentication."""
        views_and_requests = [
            (get_user_submissions, api_factory.get('/api/submissions/'), None),
            (get_submission_detail, api_factory.get(f'/api/submissions/{mock_submission_id}/'), mock_submission_id),
            (delete_submission, api_factory.delete(f'/api/submissions/{mock_submission_id}/'), mock_submission_id),
            (get_submission_statistics, api_factory.get('/api/submissions/statistics/'), None),
        ]
        
        for view, request, param in views_and_requests:
            if param:
                response = view(request, param)
            else:
                response = view(request)
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user_submissions_pagination_bounds(self, api_factory, mock_user):
        """Test pagination parameter boundary validation."""
        # Test negative page defaults to 1
        with patch('app.views.submission_history_views.SubmissionHistoryService.get_user_submissions') as mock_service:
            mock_service.return_value = {'success': True, 'submissions': [], 'pagination': {}}
            
            request = api_factory.get('/api/submissions/?page=0&page_size=0')
            force_authenticate(request, user=mock_user)
            
            response = get_user_submissions(request)
            
            # Page should default to 1, page_size should default to 10 when < 1
            mock_service.assert_called_once_with(
                user=mock_user, 
                page=1, 
                page_size=10, 
                search=None, 
                submission_type=None
            )

    def test_get_user_submissions_invalid_type_filter(self, api_factory, mock_user):
        """Test invalid submission type filter is ignored."""
        with patch('app.views.submission_history_views.SubmissionHistoryService.get_user_submissions') as mock_service:
            mock_service.return_value = {'success': True, 'submissions': [], 'pagination': {}}
            
            request = api_factory.get('/api/submissions/?type=invalid')
            force_authenticate(request, user=mock_user)
            
            response = get_user_submissions(request)
            
            # Invalid type should be ignored (set to None)
            mock_service.assert_called_once_with(
                user=mock_user, 
                page=1, 
                page_size=None, 
                search=None, 
                submission_type=None
            )