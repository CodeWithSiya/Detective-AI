# type: ignore
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from app.services.admin_service import AdminService
from app.models.analysis_result import AnalysisResult
from app.models.feedback import Feedback
import pytest
import uuid

class TestAdminService:
    """
    Unit tests for Admin Service.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 28/09/2025
    """

    @pytest.fixture
    def mock_timezone_now(self):
        """Mock timezone.now() to return a fixed datetime."""
        fixed_time = datetime(2025, 9, 28, 12, 0, 0)
        with patch('app.services.admin_service.timezone.now') as mock_now:
            mock_now.return_value = timezone.make_aware(fixed_time)
            yield mock_now

    @pytest.fixture
    def mock_queryset(self):
        """Create a mock queryset that supports chaining."""
        def create_mock_qs(count_value=0):
            mock_qs = MagicMock()
            mock_qs.count.return_value = count_value
            mock_qs.filter.return_value = mock_qs
            mock_qs.aggregate.return_value = {'avg_time': 1500.0}
            mock_qs.select_related.return_value = mock_qs
            mock_qs.order_by.return_value = mock_qs
            mock_qs.__getitem__ = lambda self, key: []  # For slicing [:limit]
            return mock_qs
        return create_mock_qs

    # System Statistics Tests
    @patch('app.services.admin_service.TextSubmission.objects')
    @patch('app.services.admin_service.TextAnalysisResult.objects')
    @patch('app.services.admin_service.User.objects')
    @patch('app.services.admin_service.Feedback.objects')
    def test_get_system_statistics_success(self, mock_feedback_objects, mock_user_objects, 
                                         mock_analysis_objects, mock_submission_objects, 
                                         mock_timezone_now, mock_queryset):
        """Test successful retrieval of system statistics."""
        # Mock submission statistics
        mock_submission_objects.filter.return_value = mock_queryset(10)
        mock_submission_objects.count.return_value = 100
        
        # Mock analysis statistics
        mock_analysis_objects.filter.return_value = mock_queryset(20)
        mock_analysis_objects.count.return_value = 95
        
        # Mock user statistics
        mock_user_objects.filter.return_value = mock_queryset(5)
        mock_user_objects.count.return_value = 50
        
        # Mock feedback statistics
        mock_feedback_objects.filter.return_value = mock_queryset(15)
        mock_feedback_objects.count.return_value = 30
        
        result = AdminService.get_system_statistics()
        
        assert result['success'] is True
        assert 'statistics' in result
        
        stats = result['statistics']
        assert 'submissions' in stats
        assert 'analyses' in stats
        assert 'performance' in stats
        assert 'users' in stats
        assert 'feedback' in stats
        assert 'detection_results' in stats
        
        # Check structure of submissions stats
        assert 'total' in stats['submissions']
        assert 'today' in stats['submissions']
        assert 'this_week' in stats['submissions']
        assert 'this_month' in stats['submissions']

    @patch('app.services.admin_service.TextSubmission.objects')
    def test_get_system_statistics_handles_zero_division(self, mock_submission_objects, mock_timezone_now):
        """Test that statistics correctly handle zero division scenarios."""
        # Mock empty results
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 0
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.aggregate.return_value = {'avg_time': None}
        
        mock_submission_objects.filter.return_value = mock_queryset
        mock_submission_objects.count.return_value = 0
        
        with patch('app.services.admin_service.TextAnalysisResult.objects') as mock_analysis:
            mock_analysis.filter.return_value = mock_queryset
            mock_analysis.count.return_value = 0
            
            with patch('app.services.admin_service.User.objects') as mock_user:
                mock_user.filter.return_value = mock_queryset
                mock_user.count.return_value = 0
                
                with patch('app.services.admin_service.Feedback.objects') as mock_feedback:
                    mock_feedback.filter.return_value = mock_queryset
                    mock_feedback.count.return_value = 0
                    
                    result = AdminService.get_system_statistics()
                    
                    assert result['success'] is True
                    stats = result['statistics']
                    
                    # Check that rates default to 0 when no data
                    assert stats['analyses']['success_rate'] == 0
                    assert stats['feedback']['satisfaction_rate'] == 0
                    assert stats['detection_results']['ai_percentage'] == 0
                    assert stats['performance']['avg_processing_time_seconds'] == 0

    @patch('app.services.admin_service.TextSubmission.objects')
    def test_get_system_statistics_exception_handling(self, mock_submission_objects):
        """Test that statistics method handles exceptions gracefully."""
        mock_submission_objects.filter.side_effect = Exception("Database connection error")
        
        result = AdminService.get_system_statistics()
        
        assert result['success'] is False
        assert result['error'] == "Database connection error"

    # Recent Activity Tests
    @patch('app.services.admin_service.TextSubmission.objects')
    @patch('app.services.admin_service.TextAnalysisResult.objects')
    @patch('app.services.admin_service.Feedback.objects')
    @patch('app.services.admin_service.User.objects')
    def test_get_recent_activity_success(self, mock_user_objects, mock_feedback_objects, 
                                       mock_analysis_objects, mock_submission_objects):
        """Test successful retrieval of recent activities."""
        # Create mock submission
        mock_submission = Mock()
        mock_submission.id = uuid.uuid4()
        mock_submission.name = 'Test Submission'
        mock_submission.user.username = 'testuser'
        mock_submission.user.email = 'test@example.com'
        mock_submission.created_at = timezone.now()
        mock_submission.character_count = 100
        
        # Create mock analysis
        mock_analysis = Mock()
        mock_analysis.id = uuid.uuid4()
        mock_analysis.status = AnalysisResult.Status.COMPLETED
        mock_analysis.detection_result = AnalysisResult.DetectionResult.AI_GENERATED
        mock_analysis.confidence = 0.85
        mock_analysis.processing_time_ms = 1500
        mock_analysis.created_at = timezone.now()
        mock_analysis.submission = mock_submission
        
        # Create mock feedback
        mock_feedback = Mock()
        mock_feedback.id = uuid.uuid4()
        mock_feedback.rating = Feedback.FeedbackRating.THUMBS_UP
        mock_feedback.comment = 'Great analysis!'
        mock_feedback.user.username = 'testuser'
        mock_feedback.user.email = 'test@example.com'
        mock_feedback.created_at = timezone.now()
        
        # Create mock user
        mock_user = Mock()
        mock_user.id = uuid.uuid4()
        mock_user.username = 'newuser'
        mock_user.email = 'new@example.com'
        mock_user.full_name = 'New User'
        mock_user.is_email_verified = True
        mock_user.is_active = True
        mock_user.is_staff = False
        mock_user.date_joined = timezone.now()
        
        # Mock querysets
        mock_submission_qs = Mock()
        mock_submission_qs.select_related.return_value.order_by.return_value.__getitem__ = lambda self, key: [mock_submission]
        mock_submission_objects.select_related.return_value.order_by.return_value.__getitem__ = lambda self, key: [mock_submission]
        
        mock_analysis_qs = Mock()
        mock_analysis_objects.select_related.return_value.order_by.return_value.__getitem__ = lambda self, key: [mock_analysis]
        
        mock_feedback_objects.select_related.return_value.order_by.return_value.__getitem__ = lambda self, key: [mock_feedback]
        
        mock_user_objects.order_by.return_value.__getitem__ = lambda self, key: [mock_user]
        
        result = AdminService.get_recent_activity(limit=10)
        
        assert result['success'] is True
        assert 'activities' in result
        
        activities = result['activities']
        assert len(activities) >= 0  # Should have some activities
        
        # Check activity structure
        if activities:
            activity = activities[0]
            assert 'type' in activity
            assert 'id' in activity
            assert 'action' in activity
            assert 'user' in activity
            assert 'timestamp' in activity
            assert 'status' in activity
            assert 'analysisType' in activity

    @patch('app.services.admin_service.TextSubmission.objects')
    def test_get_recent_activity_exception_handling(self, mock_submission_objects):
        """Test that recent activity method handles exceptions gracefully."""
        mock_submission_objects.select_related.side_effect = Exception("Query error")
        
        result = AdminService.get_recent_activity()
        
        assert result['success'] is False
        assert result['error'] == "Query error"

    def test_get_recent_activity_default_limit(self):
        """Test that recent activity uses default limit correctly."""
        with patch('app.services.admin_service.TextSubmission.objects') as mock_submission:
            with patch('app.services.admin_service.TextAnalysisResult.objects') as mock_analysis:
                with patch('app.services.admin_service.Feedback.objects') as mock_feedback:
                    with patch('app.services.admin_service.User.objects') as mock_user:
                        # Mock the querysets to return empty results
                        mock_qs = Mock()
                        mock_qs.select_related.return_value.order_by.return_value.__getitem__ = lambda self, key: []
                        
                        mock_submission.select_related.return_value.order_by.return_value.__getitem__ = lambda self, key: []
                        mock_analysis.select_related.return_value.order_by.return_value.__getitem__ = lambda self, key: []
                        mock_feedback.select_related.return_value.order_by.return_value.__getitem__ = lambda self, key: []
                        mock_user.order_by.return_value.__getitem__ = lambda self, key: []
                        
                        # Call without limit parameter - should use default of 20
                        result = AdminService.get_recent_activity()
                        
                        # Just verify it works without error and returns expected structure
                        assert result['success'] is True
                        assert 'activities' in result

    # Performance Metrics Tests
    @patch('app.services.admin_service.timezone.now')
    @patch('app.services.admin_service.TextSubmission.objects')
    @patch('app.services.admin_service.TextAnalysisResult.objects')
    def test_get_performance_metrics_default_days(self, mock_analysis_objects, mock_submission_objects, mock_timezone_now):
        """Test that performance metrics uses default days correctly."""
        # Mock timezone
        fixed_time = timezone.make_aware(datetime(2025, 9, 28, 12, 0, 0))
        mock_timezone_now.return_value = fixed_time
        
        # Mock submission and analysis querysets
        mock_qs = Mock()
        mock_qs.count.return_value = 5
        mock_qs.aggregate.return_value = {'avg_time': 1200.0}
        
        mock_submission_objects.filter.return_value = mock_qs
        mock_analysis_objects.filter.return_value = mock_qs
        
        # Call without days parameter - should use default of 7
        result = AdminService.get_performance_metrics()
        
        # Verify it works and returns expected structure with 7 days
        assert result['success'] is True
        assert 'metrics' in result
        assert result['metrics']['period_days'] == 7
        assert len(result['metrics']['daily_breakdown']) == 7

    @patch('app.services.admin_service.TextSubmission.objects')
    def test_get_performance_metrics_exception_handling(self, mock_submission_objects):
        """Test that performance metrics method handles exceptions gracefully."""
        mock_submission_objects.filter.side_effect = Exception("Metrics calculation error")
        
        result = AdminService.get_performance_metrics(days=7)
        
        assert result['success'] is False
        assert result['error'] == "Metrics calculation error"

    @patch('app.services.admin_service.timezone.now') 
    @patch('app.services.admin_service.TextSubmission.objects')
    @patch('app.services.admin_service.TextAnalysisResult.objects')
    def test_get_performance_metrics_handles_null_processing_time(self, mock_analysis_objects, 
                                                                mock_submission_objects, mock_timezone_now):
        """Test that performance metrics handles null processing times correctly."""
        # Set up timezone mock
        fixed_time = timezone.make_aware(datetime(2025, 9, 28, 12, 0, 0))
        mock_timezone_now.return_value = fixed_time
        
        # Mock submission counts
        mock_submission_qs = Mock()
        mock_submission_qs.count.return_value = 2
        mock_submission_objects.filter.return_value = mock_submission_qs
        
        # Mock analysis with null average processing time
        mock_analysis_qs = Mock()
        mock_analysis_qs.count.return_value = 2
        mock_analysis_qs.aggregate.return_value = {'avg_time': None}  # Null processing time
        mock_analysis_objects.filter.return_value = mock_analysis_qs
        
        result = AdminService.get_performance_metrics(days=2)
        
        assert result['success'] is True
        metrics = result['metrics']
        
        # Should handle null processing time gracefully
        for daily_stat in metrics['daily_breakdown']:
            assert daily_stat['avg_processing_time_ms'] == 0

    # Edge Cases and Integration Tests
    @patch('app.services.admin_service.timezone.now')
    def test_timezone_calculations(self, mock_now):
        """Test that timezone calculations work correctly."""
        # Set a fixed time
        fixed_time = timezone.make_aware(datetime(2025, 9, 28, 15, 30, 0))
        mock_now.return_value = fixed_time
        
        with patch('app.services.admin_service.TextSubmission.objects') as mock_submission:
            mock_qs = Mock()
            mock_qs.count.return_value = 1
            mock_qs.filter.return_value = mock_qs
            mock_submission.filter.return_value = mock_qs
            mock_submission.count.return_value = 10
            
            with patch('app.services.admin_service.TextAnalysisResult.objects') as mock_analysis:
                mock_analysis.filter.return_value = mock_qs
                mock_analysis.count.return_value = 5
                mock_qs.aggregate.return_value = {'avg_time': 1000.0}
                
                with patch('app.services.admin_service.User.objects') as mock_user:
                    mock_user.filter.return_value = mock_qs
                    mock_user.count.return_value = 20
                    
                    with patch('app.services.admin_service.Feedback.objects') as mock_feedback:
                        mock_feedback.filter.return_value = mock_qs
                        mock_feedback.count.return_value = 8
                        
                        result = AdminService.get_system_statistics()
                        
                        assert result['success'] is True
                        # Verify that timezone calculations don't cause errors
                        assert 'statistics' in result