from django.urls import path
from app.views import user_views
from app.views import analysis_views

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
]