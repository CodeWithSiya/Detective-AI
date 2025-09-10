from django.urls import path
from app.views import user_views
from app.views import analysis_views
from app.views import feedback_views
from app.views import report_views
from app.views import submission_history_views

urlpatterns = [
    # Text analysis
    path('analysis/text/', analysis_views.analyse_text, name="analyse_text"),

    # User authentication
    path('users/register/', user_views.register_user, name='register_user'),
    path('users/login/', user_views.login_user, name='login_user'),
    path('users/logout/', user_views.logout_user, name='logout_user'),

    # User profile management
    path('users/me/', user_views.get_current_user, name='get_current_user'),
    path('users/<str:user_id>/', user_views.get_user_profile, name='get_user_profile'),
    path('users/<str:user_id>/update/', user_views.update_user_profile, name='update_user_profile'),
    path('users/<str:user_id>/change-password/', user_views.change_user_password, name='change_user_password'),
    path('users/<str:user_id>/delete/', user_views.delete_user, name='delete_user'),

    # User feedback management
    path('feedback/', feedback_views.get_user_feedback, name='get_user_feedback'),
    path('feedback/statistics/', feedback_views.get_feedback_statistics, name='get_feedback_statistics'),
    path('feedback/<str:feedback_id>/delete/', feedback_views.delete_feedback, name='delete_feedback'),
    path('feedback/analysis/<str:analysis_id>/', feedback_views.get_feedback_for_analysis, name='get_feedback_for_analysis'),
    path('feedback/analysis/<str:analysis_id>/submit/', feedback_views.submit_feedback, name='submit_feedback'),
    
    # Admin feedback management
    path('admin/feedback/', feedback_views.get_all_feedback_admin, name='get_all_feedback_admin'),

    # Analysis report download and email management
    path('reports/analysis/<str:analysis_id>/download/', report_views.download_report, name='download_report'),
    path('reports/analysis/<str:analysis_id>/email/', report_views.email_report, name='email_report'),

    # Submission history management
    path('submissions/', submission_history_views.get_user_submissions, name='get_user_submissions'),
    path('submissions/statistics/', submission_history_views.get_submission_statistics, name='get_submission_statistics'),
    path('submissions/<str:submission_id>/', submission_history_views.get_submission_detail, name='get_submission_detail'),
    path('submissions/<str:submission_id>/update/', submission_history_views.update_submission, name='update_submission'),
    path('submissions/<str:submission_id>/delete/', submission_history_views.delete_submission, name='delete_submission')
]
