# type: ignore
from unittest.mock import Mock, patch
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from datetime import datetime
from app.views.admin_views import (
    get_system_statistics,
    get_recent_activity,
    get_performance_metrics,
    get_admin_dashboard_data,
    create_json_response
)
import pytest
import uuid

User = get_user_model()

class TestAdminViews:
    """
    Unit tests for Admin Views.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose 
    :version: 16/09/2025
    """

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
    def mock_regular_user(self):
        """
        Create a mock regular user for permission testing.
        """
        user = Mock()
        user.id = uuid.uuid4()
        user.username = 'user'
        user.email = 'user@example.com'
        user.is_staff = False
        user.is_superuser = False
        user.is_authenticated = True
        return user
    
    @pytest.fixture
    def api_factory(self):
        """
        Create APIRequestFactory instance for API request testing.
        """
        return APIRequestFactory()
    
    @pytest.fixture
    def mock_statistics_data(self):
        """
        Create mock statistics data.
        """
        return {
            'submissions': {
                'total': 1250,
                'today': 15,
                'this_week': 89,
                'this_month': 320
            },
            'analyses': {
                'total': 1180,
                'today': 12,
                'this_week': 85,
                'completed': 1150,
                'failed': 30,
                'success_rate': 97.46
            },
            'performance': {
                'avg_processing_time_seconds': 2.45,
                'avg_processing_time_ms': 2450.0
            },
            'users': {
                'total': 450,
                'active': 420,
                'verified': 380,
                'admins': 5,
                'today': 3,
                'this_week': 18
            },
            'feedback': {
                'total': 230,
                'positive': 195,
                'negative': 35,
                'satisfaction_rate': 84.78
            },
            'detection_results': {
                'ai_generated': 650,
                'human_written': 500,
                'ai_percentage': 56.52
            }
        }
    
    @pytest.fixture
    def mock_recent_activities(self):
        """
        Create mock recent activities matching AdminService structure.
        """
        return [
            {
                'type': 'submission',
                'id': str(uuid.uuid4()),
                'title': 'New submission: Essay Analysis',
                'description': 'User john_doe submitted "Essay Analysis"',
                'user': 'john_doe',
                'user_email': 'john@example.com',
                'timestamp': datetime.now(),
                'meta': {
                    'submission_name': 'Essay Analysis',
                    'character_count': 1500
                }
            }
        ]
    
    def test_create_json_response_success_structure(self):
        """
        Test that successful JSON response has correct structure.
        """
        # Create the response structure.
        data = {'key': 'value'}
        response = create_json_response(
            success=True,
            message='Test message',
            data=data
        )
        
        # Assert that the fields are valid.
        assert response.status_code == status.HTTP_200_OK

        # Must check since the data field is optional.
        if response.data is not None:
            assert response.data['success'] is True
            assert response.data['message'] == 'Test message'
            assert response.data['data'] == data
            assert response.data['error'] is None
            assert 'timestamp' in response.data
            assert isinstance(response.data['timestamp'], str)

    def test_create_json_response_error_structure(self):
        """
        Test that error JSON response has correct structure.
        """
        # Create the response structure.
        response = create_json_response(
            success=False,
            error='Test error',
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
        # Assert that the fields are valid.
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Must check since the data field is optional.
        if response.data is not None:
            assert response.data['success'] is False
            assert response.data['error'] == 'Test error'
            assert response.data['data'] is None
            assert response.data['message'] is None
            assert 'timestamp' in response.data
            assert isinstance(response.data['timestamp'], str)

    def test_create_json_response_default_values(self):
        """
        Test that JSON response uses default values correctly.
        """
        # Initialise the response structure.
        response = create_json_response()

        # Assert that the fields are valid.
        assert response.status_code == status.HTTP_200_OK

        # Must check since the data field is optional
        if response.data is not None:
            assert response.data['success'] is True
            assert response.data['message'] is None
            assert response.data['data'] is None
            assert response.data['error'] is None

    @patch('app.views.admin_views.AdminService.get_system_statistics')
    def test_get_system_statistics_successful_response(self, mock_service, api_factory, mock_admin_user, mock_statistics_data):
        """
        Test successful system statistics retrieval with realistic data.
        """
        # Mock the service response.
        mock_service.return_value = {
            'success': True,
            'statistics': mock_statistics_data
        }

        # Create authenticated request.
        request = api_factory.get('/api/admin/statistics')
        force_authenticate(request, user=mock_admin_user)

        # Call view.
        response = get_system_statistics(request)

        # Assert that the fields are valid.
        assert response.status_code == status.HTTP_200_OK                                       
        assert response.data['success'] is True                                       
        assert response.data['message'] == 'System statistics retrieved successfully'   
        assert response.data['data'] == mock_statistics_data                            
        assert response.data['error'] is None                                           

        mock_service.assert_called_once()

    @patch('app.views.admin_views.AdminService.get_system_statistics')
    def test_get_system_statistics_service_failure(self, mock_service, api_factory, mock_admin_user):
        """
        Test handling of service-level failure in statistics retrieval.
        """
        # Setup mock service error.
        mock_service.return_value = {
            'success': False,
            'error': 'Database connection timeout while fetching user statistics'
        }
        
        # Create authenticated request.
        request = api_factory.get('/api/admin/statistics/')
        force_authenticate(request, user=mock_admin_user)
        
        # Call view.
        response = get_system_statistics(request)
        
        # Assert that the fields are valid.
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR                                                                    # type: ignore
        assert response.data['success'] is False                                                        # type: ignore
        assert response.data['error'] == 'Database connection timeout while fetching user statistics'   # type: ignore
        assert response.data['data'] is None                                                            # type: ignore

    @patch('app.views.admin_views.AdminService.get_system_statistics')
    def test_get_system_statistics_exception(self, mock_service, api_factory, mock_admin_user):
        """
        Test handling of unexpected exceptions in statistics retrieval.
        """
        # Setup mock service to raise exception.
        mock_service.side_effect = Exception('Query timeout on TextAnalysisResult table')
        
        # Create authenticated request.
        request = api_factory.get('/api/admin/statistics/')
        force_authenticate(request, user=mock_admin_user)
        
        # Call view.
        response = get_system_statistics(request)
        
        # Assert that the fields are valid.
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR            
        assert response.data['success'] is False                                        
        assert response.data['error'] == 'Query timeout on TextAnalysisResult table'    

    @patch('app.views.admin_views.AdminService.get_recent_activity')
    def test_get_recent_activity_success(self, mock_service, api_factory, mock_admin_user, mock_recent_activities):
        """
        Test successful recent activity retrieval.
        """
        # Setup mock service.
        mock_service.return_value = {
            'success': True,
            'activities': mock_recent_activities
        }
        
        # Create authenticated request.
        request = api_factory.get('/api/admin/activity/')
        force_authenticate(request, user=mock_admin_user)
        
        # Call view.
        response = get_recent_activity(request)
        
        # Assert that the fields are valid.
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Recent activity retrieved successfully'
        assert response.data['data']['activities'] == mock_recent_activities
        assert response.data['data']['total_returned'] == len(mock_recent_activities)
        
        mock_service.assert_called_once_with(limit=20)

    @patch('app.views.admin_views.AdminService.get_recent_activity')
    def test_get_recent_activity_custom_limit(self, mock_service, api_factory, mock_admin_user):
        """
        Test recent activity retrieval with custom limit parameter.
        """
        # Setup mock service.
        mock_service.return_value = {
            'success': True,
            'activities': []
        }
        
        # Create authenticated request.
        request = api_factory.get('/api/admin/activity/?limit=5')
        force_authenticate(request, user=mock_admin_user)
        
        # Call view.
        response = get_recent_activity(request)
        
        # Assert that the fields are valid.
        assert response.status_code == status.HTTP_200_OK
        mock_service.assert_called_once_with(limit=5)

    def test_get_recent_activity_invalid_limit_parameter(self, api_factory, mock_admin_user):
        """
        Test handling of invalid limit parameters.
        """
        # Create authenticated request.
        request = api_factory.get('/api/admin/activity/?limit=invalid')
        force_authenticate(request, user=mock_admin_user)
        
        # Call view.
        response = get_recent_activity(request)
        
        # Assert that the fields are valid.
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Invalid limit parameter'
    
    @patch('app.views.admin_views.AdminService.get_performance_metrics')
    def test_get_performance_metrics_success(self, mock_service, api_factory, mock_admin_user):
        """
        Test successful performance metrics retrieval.
        """
        # Mock performance metrics.
        mock_metrics = {'period_days': 7, 'daily_breakdown': []}
        mock_service.return_value = {
            'success': True,
            'metrics': mock_metrics
        }
        
        # Create authenticated request.
        request = api_factory.get('/api/admin/performance/')
        force_authenticate(request, user=mock_admin_user)
        
        # Call view.
        response = get_performance_metrics(request)
        
        # Assert that the fields are valid.
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data'] == mock_metrics
        mock_service.assert_called_once_with(days=7)

    def test_get_performance_metrics_invalid_days(self, api_factory, mock_admin_user):
        """
        Test handling of invalid days parameter.
        """
        # Create authenticated request.
        request = api_factory.get('/api/admin/performance/?days=abc')
        force_authenticate(request, user=mock_admin_user)
        
        # Call view.
        response = get_performance_metrics(request)
        
        # Assert that the fields are valid.
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Invalid days parameter'

    @patch('app.views.admin_views.AdminService.get_recent_activity')
    @patch('app.views.admin_views.AdminService.get_system_statistics')
    def test_get_admin_dashboard_data_success(self, mock_stats, mock_activity, api_factory, mock_admin_user, mock_statistics_data, mock_recent_activities):
        """
        Test successful dashboard data retrieval.
        """
        # Mock dashboard data.
        mock_stats.return_value = {
            'success': True,
            'statistics': mock_statistics_data
        }  
        mock_activity.return_value = {
            'success': True,
            'activities': mock_recent_activities
        }
        
        # Create authenticated request.
        request = api_factory.get('/api/admin/dashboard/')
        force_authenticate(request, user=mock_admin_user)
        
        # Call view.
        response = get_admin_dashboard_data(request)
        
        # Assert that the fields are valid.
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['statistics'] == mock_statistics_data
        assert response.data['data']['recent_activity'] == mock_recent_activities
        
        mock_stats.assert_called_once()
        mock_activity.assert_called_once_with(limit=10)

    @patch('app.views.admin_views.AdminService.get_recent_activity')
    @patch('app.views.admin_views.AdminService.get_system_statistics')
    def test_get_admin_dashboard_data_service_failures(self, mock_stats, mock_activity, api_factory, mock_admin_user):
        """
        Test dashboard data with service failures.
        """
        # Mock dashboard data.
        mock_stats.return_value = {
            'success': False,
            'error': 'Stats error'
        }
        
        mock_activity.return_value = {
            'success': False,
            'error': 'Activity error'
        }
        
        # Create authenticated request.
        request = api_factory.get('/api/admin/dashboard/')
        force_authenticate(request, user=mock_admin_user)
        
        # Call view.
        response = get_admin_dashboard_data(request)
        
        # Assert that the fields are valid.
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['success'] is False
        assert 'Statistics error: Stats error' in response.data['error']
        assert 'Activity error: Activity error' in response.data['error']

    def test_admin_views_require_authentication(self, api_factory):
        """
        Test that admin views require authentication.
        """
        views = [get_system_statistics, get_recent_activity, get_performance_metrics, get_admin_dashboard_data]
        
        for view in views:
            request = api_factory.get('/')
            response = view(request)
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_views_require_admin_permissions(self, api_factory, mock_regular_user):
        """
        Test that admin views require admin permissions.
        """
        views = [get_system_statistics, get_recent_activity, get_performance_metrics, get_admin_dashboard_data]
        
        for view in views:
            request = api_factory.get('/')
            force_authenticate(request, user=mock_regular_user)
            response = view(request)
            assert response.status_code == status.HTTP_403_FORBIDDEN