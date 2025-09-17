# type: ignore
from unittest.mock import Mock, patch
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from datetime import datetime
from app.views.feedback_views import (
    submit_feedback,
    get_user_feedback,
    get_feedback_for_analysis,
    delete_feedback,
    get_feedback_statistics,
    get_all_feedback_admin,
)
from app.models.feedback import Feedback
import pytest
import uuid

class TestFeedbackViews:
    """s
    Unit tests for Feedback Views.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose 
    :version: 17/09/2025
    """

    @pytest.fixture
    def mock_user(self):
        """
        Create a mock authenticated user.
        """
        user = Mock()
        user.id = uuid.uuid4()
        user.username = 'testuser'
        user.email = 'testuser@example.com'
        user.is_staff = False
        user.is_superuser = False
        user.is_authenticated = True
        return user
    
    @pytest.fixture
    def mock_admin_user(self):
        """
        Create a mock admin user.
        """
        user = Mock()
        user.id = uuid.uuid4()
        user.username = 'admin'
        user.email = 'admin@example.com'
        user.is_staff = True
        user.is_superuser = True
        user.is_authenticated = True
        return user
    
    @pytest.fixture
    def api_factory(self):
        """
        Create APIRequestFactory instance for API request testing.
        """
        return APIRequestFactory()
    
    @pytest.fixture
    def mock_analysis_id(self):
        """
        Create a mock analysis ID.
        """
        return str(uuid.uuid4())
    
    @pytest.fixture
    def mock_feedback_id(self):
        """
        Create a mock feedback ID.
        """
        return str(uuid.uuid4())
    
    @pytest.fixture
    def mock_feedback_data(self):
        """
        Create mock feedback data.
        """
        return {
            'id': str(uuid.uuid4()),
            'rating': Feedback.FeedbackRating.THUMBS_UP,
            'comment': 'Great analysis!',
            'created_at': datetime.now().isoformat(),
            'analysis_id': str(uuid.uuid4())
        }
    
    @pytest.fixture
    def mock_feedback_list(self):
        """
        Create mock feedback list for pagination.
        """
        return [
            {
                'id': str(uuid.uuid4()),
                'rating': Feedback.FeedbackRating.THUMBS_UP,
                'comment': 'Excellent work',
                'created_at': datetime.now().isoformat(),
                'analysis_id': str(uuid.uuid4())
            },
            {
                'id': str(uuid.uuid4()),
                'rating': Feedback.FeedbackRating.THUMBS_DOWN,
                'comment': 'Could be better',
                'created_at': datetime.now().isoformat(),
                'analysis_id': str(uuid.uuid4())
            }
        ]
    
    @pytest.fixture
    def mock_pagination_data(self):
        """
        Create mock pagination data.
        """
        return {
            'current_page': 1,
            'total_pages': 1,
            'total_items': 2,
            'has_next': False,
            'has_previous': False
        }
    
    @pytest.fixture
    def mock_statistics_data(self):
        """
        Create mock feedback statistics data.
        """
        return {
            'total_feedback': 25,
            'thumbs_up': 20,
            'thumbs_down': 5,
            'satisfaction_rate': 80.0
        }
    
    @patch('app.views.feedback_views.FeedbackService.submit_feedback')
    def test_submit_feedback_success(self, mock_service, api_factory, mock_user, mock_analysis_id, mock_feedback_data):
        """
        Test successful feedback submission.
        """
        # Mock request and return data.
        mock_service.return_value = {
            'success': True,
            'message': 'Feedback submitted successfully',
            'data': mock_feedback_data
        }      
        request_data = {
            'rating': Feedback.FeedbackRating.THUMBS_UP,
            'comment': 'Great analysis!'
        }
        
        # Create authenticated request.
        request = api_factory.post(f'/api/feedback/analysis/{mock_analysis_id}/submit/', request_data)
        force_authenticate(request, user=mock_user)
        
        # Call View.
        response = submit_feedback(request, mock_analysis_id)
        
        # Assertions.
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert response.data['message'] == 'Feedback submitted successfully'
        assert response.data['data'] == mock_feedback_data
        assert response.data['error'] is None
        
        mock_service.assert_called_once_with(
            analysis_id=mock_analysis_id,
            user=mock_user,
            rating=Feedback.FeedbackRating.THUMBS_UP,
            comment='Great analysis!'
        )

    @patch('app.views.feedback_views.FeedbackService.submit_feedback')
    def test_submit_feedback_failure(self, mock_service, api_factory, mock_user, mock_analysis_id):
        """
        Test handling of service-level failure in feedback submission.
        """
        # Mock request and return data.
        mock_service.return_value = {
            'success': False,
            'error': 'Analysis result not found'
        } 
        request_data = {
            'rating': Feedback.FeedbackRating.THUMBS_UP,
            'comment': 'Great analysis!'
        }
        
        # Create authenticated request. 
        request = api_factory.post(f'/api/feedback/analysis/{mock_analysis_id}/submit/', request_data)
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = submit_feedback(request, mock_analysis_id)
        
        # Assertions.
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert response.data['error'] == 'Analysis result not found'

    @patch('app.views.feedback_views.FeedbackService.submit_feedback')
    def test_submit_feedback_exception(self, mock_service, api_factory, mock_user, mock_analysis_id):
        """
        Test handling of unexpected exceptions in feedback submission.
        """
        # Mock data.
        mock_service.side_effect = Exception('Database connection failed')
       
        request_data = {
            'rating': Feedback.FeedbackRating.THUMBS_UP,
            'comment': 'Great analysis!'
        }
        
        # Create authenticated request.
        request = api_factory.post(f'/api/feedback/analysis/{mock_analysis_id}/submit/', request_data)
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = submit_feedback(request, mock_analysis_id)
        
        # Assertions.
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False
        assert response.data['error'] == 'Database connection failed'

    def test_submit_feedback_missing_rating(self, api_factory, mock_user, mock_analysis_id):
        """
        Test feedback submission without rating.
        """
        # Mock data.
        request_data = {
            'comment': 'Great analysis!'
        }
        
        # Create authenticated request.
        request = api_factory.post(f'/api/feedback/analysis/{mock_analysis_id}/submit/', request_data)
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = submit_feedback(request, mock_analysis_id)
        
        # Assertions.
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert response.data['error'] == 'Rating is required'

    def test_submit_feedback_invalid_rating(self, api_factory, mock_user, mock_analysis_id):
        """
        Test feedback submission with invalid rating.
        """
        # Mock data.
        request_data = {
            'rating': 'INVALID_RATING',
            'comment': 'Great analysis!'
        }
        
        # Create authenticated request.
        request = api_factory.post(f'/api/feedback/analysis/{mock_analysis_id}/submit/', request_data)
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = submit_feedback(request, mock_analysis_id)
        
        # Assertions.
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert 'Rating must be one of' in response.data['error']

    @patch('app.views.feedback_views.FeedbackService.get_user_feedback')
    def test_get_user_feedback_success(self, mock_service, api_factory, mock_user, mock_feedback_list, mock_pagination_data):
        """
        Test successful user feedback retrieval.
        """
        # Mock data.
        mock_service.return_value = {
            'success': True,
            'feedback': mock_feedback_list,
            'pagination': mock_pagination_data
        }
        
        # Create authenticated request.
        request = api_factory.get('/api/feedback/')
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = get_user_feedback(request)
        
        # Assertions.
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'User feedback retrieved successfully'
        assert response.data['data']['feedback'] == mock_feedback_list
        assert response.data['data']['pagination'] == mock_pagination_data
        
        mock_service.assert_called_once_with(user=mock_user, page=1, page_size=10)

    @patch('app.views.feedback_views.FeedbackService.get_user_feedback')
    def test_get_user_feedback_custom_pagination(self, mock_service, api_factory, mock_user):
        """
        Test user feedback retrieval with custom pagination parameters.
        """
        # Mock data.
        mock_service.return_value = {
            'success': True,
            'feedback': [],
            'pagination': {
                'current_page': 2,
                'total_pages': 5,
                'total_items': 45,
                'has_next': True,
                'has_previous': True
            }
        }
        
        # Create authenticated request.
        request = api_factory.get('/api/feedback/?page=2&page_size=5')
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = get_user_feedback(request)
        
        # Assertions.
        assert response.status_code == status.HTTP_200_OK
        mock_service.assert_called_once_with(user=mock_user, page=2, page_size=5)

    def test_get_user_feedback_invalid_pagination(self, api_factory, mock_user):
        """
        Test handling of invalid pagination parameters.
        """
        # Mock data.
        request = api_factory.get('/api/feedback/?page=invalid&page_size=abc')
        force_authenticate(request, user=mock_user)
        
        # Create authenticated request.
        response = get_user_feedback(request)
        
        # Assertions.
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Invalid pagination parameters'

    @patch('app.views.feedback_views.FeedbackService.get_user_feedback')
    def test_get_user_feedback_boundary_values(self, mock_service, api_factory, mock_user):
        """
        Test user feedback retrieval with boundary pagination values.
        """
        # Mock data.
        mock_service.return_value = {
            'success': True,
            'feedback': [],
            'pagination': {}
        }
        
        # Test negative page and page_size > 100.
        request = api_factory.get('/api/feedback/?page=-1&page_size=200')
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = get_user_feedback(request)
        
        # Assertions.
        assert response.status_code == status.HTTP_200_OK

        # Should normalize to page=1, page_size=10
        mock_service.assert_called_once_with(user=mock_user, page=1, page_size=10)

    @patch('app.views.feedback_views.FeedbackService.get_feedback_for_analysis')
    def test_get_feedback_for_analysis_success(self, mock_service, api_factory, mock_user, mock_analysis_id, mock_feedback_data):
        """
        Test successful feedback retrieval for specific analysis.
        """
        # Mock data.
        mock_service.return_value = {
            'success': True,
            'feedback': mock_feedback_data,
            'pagination': None
        }
        
        # Create authenticated request.
        request = api_factory.get(f'/api/feedback/analysis/{mock_analysis_id}/')
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = get_feedback_for_analysis(request, mock_analysis_id)
        
        # Assertions.
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'User feedback retrieved successfully'
        assert response.data['data']['feedback'] == mock_feedback_data
        
        mock_service.assert_called_once_with(analysis_id=mock_analysis_id, user=mock_user)

    @patch('app.views.feedback_views.FeedbackService.get_feedback_for_analysis')
    def test_get_feedback_for_analysis_not_found(self, mock_service, api_factory, mock_user, mock_analysis_id):
        """
        Test feedback retrieval for analysis with no feedback.
        """
        # Mock data.
        mock_service.return_value = {
            'success': True,
            'feedback': None,
            'pagination': None
        }
        
        # Create authenticated request.
        request = api_factory.get(f'/api/feedback/analysis/{mock_analysis_id}/')
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = get_feedback_for_analysis(request, mock_analysis_id)
        
        # Assertions.
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['feedback'] is None
    
    @patch('app.views.feedback_views.FeedbackService.get_feedback_for_analysis')
    def test_get_feedback_for_analysis_failure(self, mock_service, api_factory, mock_user, mock_analysis_id):
        """
        Test handling of service failure in feedback retrieval.
        """
        # Mock data.
        mock_service.return_value = {
            'success': False,
            'error': 'You can only access feedback for your own analyses'
        }
        
        # Create authenticated request.
        request = api_factory.get(f'/api/feedback/analysis/{mock_analysis_id}/')
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = get_feedback_for_analysis(request, mock_analysis_id)
        
        # Assertions.
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert response.data['error'] == 'You can only access feedback for your own analyses'

    @patch('app.views.feedback_views.FeedbackService.delete_feedback')
    def test_delete_feedback_success(self, mock_service, api_factory, mock_user, mock_feedback_id):
        """
        Test successful feedback deletion.
        """
        # Mock data.
        mock_service.return_value = {
            'success': True,
            'message': 'Feedback deleted successfully'
        }
        
        # Create authenticated request.
        request = api_factory.delete(f'/api/feedback/{mock_feedback_id}/delete/')
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = delete_feedback(request, mock_feedback_id)
        
        # Assertions.
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Feedback deleted successfully'
        
        mock_service.assert_called_once_with(feedback_id=mock_feedback_id, user=mock_user)

    @patch('app.views.feedback_views.FeedbackService.delete_feedback')
    def test_delete_feedback_not_found(self, mock_service, api_factory, mock_user, mock_feedback_id):
        """
        Test deletion of non-existent feedback.
        """
        # Mock data.
        mock_service.return_value = {
            'success': False,
            'error': 'Feedback not found or you do not have permission to delete it'
        }
        
        # Create authenticated request.
        request = api_factory.delete(f'/api/feedback/{mock_feedback_id}/delete/')
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = delete_feedback(request, mock_feedback_id)
        
        # Assertions.
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert response.data['error'] == 'Feedback not found or you do not have permission to delete it'

    @patch('app.views.feedback_views.FeedbackService.get_feedback_statistics')
    def test_get_feedback_statistics_success(self, mock_service, api_factory, mock_user, mock_statistics_data):
        """
        Test successful feedback statistics retrieval.
        """
        # Mock data.
        mock_service.return_value = {
            'success': True,
            'statistics': mock_statistics_data
        }
        
        # Create authenticated request.
        request = api_factory.get('/api/feedback/statistics/')
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = get_feedback_statistics(request)
        
        # Assertions.
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Feedback statistics retrieved successfully'
        assert response.data['data']['statistics'] == mock_statistics_data
        
        mock_service.assert_called_once_with(user=mock_user)

    @patch('app.views.feedback_views.FeedbackService.get_feedback_statistics')
    def test_get_feedback_statistics_service_failure(self, mock_service, api_factory, mock_user):
        """
        Test handling of service failure in statistics retrieval.
        """
        # Mock data.
        mock_service.return_value = {
            'success': False,
            'error': 'No feedback data available'
        }
        
        # Create authenticated request.
        request = api_factory.get('/api/feedback/statistics/')
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = get_feedback_statistics(request)
        
        # Assertions.
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert response.data['error'] == 'No feedback data available'

    @patch('app.views.feedback_views.FeedbackService.get_all_feedback_for_admin')
    def test_get_all_feedback_admin_success(self, mock_service, api_factory, mock_admin_user, mock_feedback_list, mock_pagination_data):
        """
        Test successful admin feedback retrieval.
        """
        # Mock data.
        mock_service.return_value = {
            'success': True,
            'feedback': mock_feedback_list,
            'pagination': mock_pagination_data
        }
        
        # Create authenticated request.
        request = api_factory.get('/api/admin/feedback/')
        force_authenticate(request, user=mock_admin_user)
        
        # Call view.
        response = get_all_feedback_admin(request)
        
        # Assertions.
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'All feedback retrieved successfully'
        assert response.data['data']['feedback'] == mock_feedback_list
        assert response.data['data']['pagination'] == mock_pagination_data
        
        mock_service.assert_called_once_with(page=1, page_size=20)

    @patch('app.views.feedback_views.FeedbackService.get_all_feedback_for_admin')
    def test_get_all_feedback_admin_custom_pagination(self, mock_service, api_factory, mock_admin_user):
        """
        Test admin feedback retrieval with custom pagination.
        """
        # Mock data.
        mock_service.return_value = {
            'success': True,
            'feedback': [],
            'pagination': {}
        }
        
        # Create authenticated request.
        request = api_factory.get('/api/admin/feedback/?page=3&page_size=50')
        force_authenticate(request, user=mock_admin_user)
        
        # Call view.
        response = get_all_feedback_admin(request)
        
        # Assertions.
        assert response.status_code == status.HTTP_200_OK
        mock_service.assert_called_once_with(page=3, page_size=50)

    def test_get_all_feedback_admin_invalid_pagination(self, api_factory, mock_admin_user):
        """
        Test handling of invalid pagination in admin feedback retrieval.
        """
        # Mock data.
        request = api_factory.get('/api/admin/feedback/?page=invalid&page_size=abc')
        force_authenticate(request, user=mock_admin_user)
        
        # Call view.
        response = get_all_feedback_admin(request)
        
        # Assertions.
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Invalid pagination parameters'

    @patch('app.views.feedback_views.FeedbackService.get_all_feedback_for_admin')
    def test_get_all_feedback_admin_boundary_values(self, mock_service, api_factory, mock_admin_user):
        """
        Test admin feedback retrieval with boundary pagination values.
        """
        # Mock data.
        mock_service.return_value = {
            'success': True,
            'feedback': [],
            'pagination': {}
        }
        
        # Create authenticated request.
        request = api_factory.get('/api/admin/feedback/?page=0&page_size=150')
        force_authenticate(request, user=mock_admin_user)
        
        # Call view.
        response = get_all_feedback_admin(request)
        
        # Assertions.
        assert response.status_code == status.HTTP_200_OK

        # Should normalize to page=1, page_size=20
        mock_service.assert_called_once_with(page=1, page_size=20)

    def test_feedback_views_require_authentication(self, api_factory, mock_analysis_id, mock_feedback_id):
        """
        Test that all feedback views require authentication.
        """
        views_and_requests = [
            (submit_feedback, api_factory.post(f'/api/feedback/analysis/{mock_analysis_id}/submit/'), mock_analysis_id),
            (get_user_feedback, api_factory.get('/api/feedback/'), None),
            (get_feedback_for_analysis, api_factory.get(f'/api/feedback/analysis/{mock_analysis_id}/'), mock_analysis_id),
            (delete_feedback, api_factory.delete(f'/api/feedback/{mock_feedback_id}/delete/'), mock_feedback_id),
            (get_feedback_statistics, api_factory.get('/api/feedback/statistics/'), None),
            (get_all_feedback_admin, api_factory.get('/api/admin/feedback/'), None),
        ]
        
        for view, request, param in views_and_requests:
            if param:
                response = view(request, param)
            else:
                response = view(request)
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_feedback_view_requires_admin_permissions(self, api_factory, mock_user):
        """
        Test that admin feedback view requires admin permissions.
        """
        # Mock data.
        request = api_factory.get('/api/admin/feedback/')
        force_authenticate(request, user=mock_user)
        
        # Create unauthenticated request.
        response = get_all_feedback_admin(request)
        
        # Assertions.
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch('app.views.feedback_views.FeedbackService.get_user_feedback')
    def test_get_user_feedback_exception(self, mock_service, api_factory, mock_user):
        """
        Test handling of unexpected exceptions in user feedback retrieval.
        """
        # Mock data.
        mock_service.side_effect = Exception('Database timeout')
        
        # Create authenticated request.
        request = api_factory.get('/api/feedback/')
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = get_user_feedback(request)
        
        # Assertions.
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False
        assert response.data['error'] == 'Database timeout'

    @patch('app.views.feedback_views.FeedbackService.get_feedback_for_analysis')
    def test_get_feedback_for_analysis_exception(self, mock_service, api_factory, mock_user, mock_analysis_id):
        """
        Test handling of unexpected exceptions in analysis feedback retrieval.
        """
        # Mock data.
        mock_service.side_effect = Exception('Connection error')
        
        # Create authenticated request.
        request = api_factory.get(f'/api/feedback/analysis/{mock_analysis_id}/')
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = get_feedback_for_analysis(request, mock_analysis_id)
        
        # Assertions.
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False
        assert response.data['error'] == 'Connection error'

    @patch('app.views.feedback_views.FeedbackService.delete_feedback')
    def test_delete_feedback_exception(self, mock_service, api_factory, mock_user, mock_feedback_id):
        """
        Test handling of unexpected exceptions in feedback deletion.
        """
        # Mock data.
        mock_service.side_effect = Exception('Delete operation failed')
        
        # Create authenticated request.
        request = api_factory.delete(f'/api/feedback/{mock_feedback_id}/delete/')
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = delete_feedback(request, mock_feedback_id)
        
        # Assertions.
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False
        assert response.data['error'] == 'Delete operation failed'

    @patch('app.views.feedback_views.FeedbackService.get_feedback_statistics')
    def test_get_feedback_statistics_exception(self, mock_service, api_factory, mock_user):
        """
        Test handling of unexpected exceptions in statistics retrieval.
        """
        # Mock data.
        mock_service.side_effect = Exception('Statistics calculation failed')
        
        # Create authenticated request.
        request = api_factory.get('/api/feedback/statistics/')
        force_authenticate(request, user=mock_user)
        
        # Call view.
        response = get_feedback_statistics(request)
        
        # Assertions.
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False
        assert response.data['error'] == 'Statistics calculation failed'

    @patch('app.views.feedback_views.FeedbackService.get_all_feedback_for_admin')
    def test_get_all_feedback_admin_exception(self, mock_service, api_factory, mock_admin_user):
        """
        Test handling of unexpected exceptions in admin feedback retrieval.
        """
        # Mock data.
        mock_service.side_effect = Exception('Admin query failed')
        
        # Create authenticated request.
        request = api_factory.get('/api/admin/feedback/')
        force_authenticate(request, user=mock_admin_user)
        
        # Call view.
        response = get_all_feedback_admin(request)
        
        # Assertions.
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False
        assert response.data['error'] == 'Admin query failed'