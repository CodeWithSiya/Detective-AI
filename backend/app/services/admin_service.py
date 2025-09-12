from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.models.user import User
from app.models.text_submission import TextSubmission
from app.models.text_analysis_result import TextAnalysisResult
from app.models.feedback import Feedback
from app.models.analysis_result import AnalysisResult

class AdminService:
    """
    Service class for admin dashboard statistics and recent activity.

    :author: Siyabonga Madondo, Ethan Ngwetjana, Lindokuhle Mdlalose
    :version: 12/09/2025
    """

    @staticmethod
    def get_system_statistics() -> Dict[str, Any]:
        """
        Get system-wide statistics for admin dash.

        :return: Dictionary containinig various system statistics.
        """
        try:
            now = timezone.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=7)
            month_start = today_start - timedelta(days=30)

            # Submission statistics.
            submissions_today = TextSubmission.objects.filter(
                created_at__gte=today_start
            ).count()
            
            submissions_this_week = TextSubmission.objects.filter(
                created_at__gte=week_start
            ).count()
            
            submissions_this_month = TextSubmission.objects.filter(
                created_at__gte=month_start
            ).count()
            
            total_submissions = TextSubmission.objects.count()

            # Analysis statistics.
            analyses_today = TextAnalysisResult.objects.filter(
                created_at__gte=today_start
            ).count()
            
            analyses_this_week = TextAnalysisResult.objects.filter(
                created_at__gte=week_start
            ).count()
            
            completed_analyses = TextAnalysisResult.objects.filter(
                status=AnalysisResult.Status.COMPLETED
            ).count()
            
            failed_analyses = TextAnalysisResult.objects.filter(
                status=AnalysisResult.Status.FAILED
            ).count()

            # Processing time statistics.
            avg_processing_time = TextAnalysisResult.objects.filter(
                status=AnalysisResult.Status.COMPLETED,
                processing_time_ms__isnull=False
            ).aggregate(
                avg_time=Avg('processing_time_ms')
            )['avg_time'] or 0

            # Convert to seconds for readability.
            avg_processing_time_seconds = round(avg_processing_time / 1000, 2) if avg_processing_time else 0

            # User statistics.
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            verified_users = User.objects.filter(is_email_verified=True).count()
            admin_users = User.objects.filter(is_staff=True).count()
            
            users_today = User.objects.filter(
                date_joined__gte=today_start
            ).count()
            
            users_this_week = User.objects.filter(
                date_joined__gte=week_start
            ).count()

            # Feedback statistics.
            total_feedback = Feedback.objects.count()
            positive_feedback = Feedback.objects.filter(
                rating=Feedback.FeedbackRating.THUMBS_UP
            ).count()
            
            negative_feedback = Feedback.objects.filter(
                rating=Feedback.FeedbackRating.THUMBS_DOWN
            ).count()
            
            # Detection result statistics.
            ai_generated_count = TextAnalysisResult.objects.filter(
                detection_result=AnalysisResult.DetectionResult.AI_GENERATED
            ).count()
            
            human_written_count = TextAnalysisResult.objects.filter(
                detection_result=AnalysisResult.DetectionResult.HUMAN_WRITTEN
            ).count()

            return {
                'success': True,
                'statistics': {
                    'submissions': {
                        'total': total_submissions,
                        'today': submissions_today,
                        'this_week': submissions_this_week,
                        'this_month': submissions_this_month
                    },
                    'analyses': {
                        'total': completed_analyses + failed_analyses,
                        'today': analyses_today,
                        'this_week': analyses_this_week,
                        'completed': completed_analyses,
                        'failed': failed_analyses,
                        'success_rate': round((completed_analyses / (completed_analyses + failed_analyses)) * 100, 2) if (completed_analyses + failed_analyses) > 0 else 0
                    },
                    'performance': {
                        'avg_processing_time_seconds': avg_processing_time_seconds,
                        'avg_processing_time_ms': round(avg_processing_time, 2) if avg_processing_time else 0
                    },
                    'users': {
                        'total': total_users,
                        'active': active_users,
                        'verified': verified_users,
                        'admins': admin_users,
                        'today': users_today,
                        'this_week': users_this_week
                    },
                    'feedback': {
                        'total': total_feedback,
                        'positive': positive_feedback,
                        'negative': negative_feedback,
                        'satisfaction_rate': round((positive_feedback / total_feedback) * 100, 2) if total_feedback > 0 else 0
                    },
                    'detection_results': {
                        'ai_generated': ai_generated_count,
                        'human_written': human_written_count,
                        'ai_percentage': round((ai_generated_count / (ai_generated_count + human_written_count)) * 100, 2) if (ai_generated_count + human_written_count) > 0 else 0
                    }
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_recent_activity(limit: int = 20) -> Dict[str, Any]:
        """
        Get recent activity across the system for admin dashboard.
        
        :param limit: Number of recent activities to return
        :return: Dictionary containing recent activities
        """
        try:
            activities = []

            # Recent submissions.
            recent_submissions = TextSubmission.objects.select_related('user').order_by('-created_at')[:limit]
            for submission in recent_submissions:
                activities.append({
                    'type': 'submission',
                    'id': str(submission.id),
                    'title': f'New submission: {submission.name}',
                    'description': f'User {submission.user.username} submitted "{submission.name}"',
                    'user': submission.user.username,
                    'user_email': submission.user.email,
                    'timestamp': submission.created_at,
                    'meta': {
                        'submission_name': submission.name,
                        'character_count': getattr(submission, 'character_count', None)
                    }
                })

            # Recent analyses.
            recent_analyses = TextAnalysisResult.objects.select_related('submission__user').order_by('-created_at')[:limit]
            for analysis in recent_analyses:
                if analysis.submission and hasattr(analysis.submission, 'user') and analysis.submission.user:
                    activities.append({
                        'type': 'analysis',
                        'id': str(analysis.id),
                        'title': f'Analysis {analysis.status.lower()}: {analysis.detection_result or "In progress"}',
                        'description': f'Analysis for "{analysis.submission.name}" by {analysis.submission.user.username}',
                        'user': analysis.submission.user.username,
                        'user_email': analysis.submission.user.email,
                        'timestamp': analysis.created_at,
                        'meta': {
                            'status': analysis.status,
                            'detection_result': analysis.detection_result,
                            'confidence': analysis.confidence,
                            'processing_time_ms': analysis.processing_time_ms
                        }
                    })

            # Recent feedback.
            recent_feedback = Feedback.objects.select_related('user').order_by('-created_at')[:limit]
            for feedback in recent_feedback:
                activities.append({
                    'type': 'feedback',
                    'id': str(feedback.id),
                    'title': f'Feedback: {feedback.rating}',
                    'description': f'User {feedback.user.username} gave {feedback.rating.lower().replace("_", " ")} feedback',
                    'user': feedback.user.username,
                    'user_email': feedback.user.email,
                    'timestamp': feedback.created_at,
                    'meta': {
                        'rating': feedback.rating,
                        'comment': feedback.comment[:100] + '...' if len(feedback.comment) > 100 else feedback.comment
                    }
                })

            # Recent user registrations.
            recent_users = User.objects.order_by('-date_joined')[:limit]
            for user in recent_users:
                activities.append({
                    'type': 'user_registration',
                    'id': str(user.id),
                    'title': f'New user registered: {user.username}',
                    'description': f'{user.full_name} ({user.email}) joined the platform',
                    'user': user.username,
                    'user_email': user.email,
                    'timestamp': user.date_joined,
                    'meta': {
                        'is_verified': user.is_email_verified,
                        'is_active': user.is_active,
                        'is_admin': user.is_staff
                    }
                })

            # Sort all activities by timestamp (most recent first).
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Return only the most recent activities up to the limit
            return {
                'success': True,
                'activities': activities[:limit]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        
    @staticmethod
    def get_performance_metrics(days: int = 7) -> Dict[str, Any]:
        """
        Get performance metrics over a specified time period.
        
        :param days: Number of days to analyse
        :return: Performance metrics data
        """
        try:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # Daily breakdown
            daily_stats = []
            for i in range(days):
                day_start = (start_date + timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)
                
                submissions_count = TextSubmission.objects.filter(
                    created_at__gte=day_start,
                    created_at__lt=day_end
                ).count()
                
                analyses_count = TextAnalysisResult.objects.filter(
                    created_at__gte=day_start,
                    created_at__lt=day_end
                ).count()
                
                avg_processing = TextAnalysisResult.objects.filter(
                    created_at__gte=day_start,
                    created_at__lt=day_end,
                    status=AnalysisResult.Status.COMPLETED,
                    processing_time_ms__isnull=False
                ).aggregate(avg_time=Avg('processing_time_ms'))['avg_time'] or 0
                
                daily_stats.append({
                    'date': day_start.strftime('%Y-%m-%d'),
                    'submissions': submissions_count,
                    'analyses': analyses_count,
                    'avg_processing_time_ms': round(avg_processing, 2)
                })
            
            return {
                'success': True,
                'metrics': {
                    'period_days': days,
                    'daily_breakdown': daily_stats
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }