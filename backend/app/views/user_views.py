from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.conf import settings
from app.services.user_service import UserService
from app.serializers.user_serializers import UserSerializer
from app.services.email_service import EmailService
from typing import Optional, Any
from datetime import datetime
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

def create_json_response(success: bool = True, message: Optional[str] = None, data: Optional[Any] = None, error: Optional[str] = None, status_code = status.HTTP_200_OK, **kwargs):
    """
    Create standardised JSON response.
    """
    response_data = {
        'success': success,
        'message': message,
        'data': data,
    }

    # Add any additional fields.
    response_data.update(kwargs)

    # Add error and timestamp at the end.
    response_data.update({
        'error': error,
        'timestamp': datetime.now().isoformat()
    })

    return Response(response_data, status=status_code)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """
    Register a new user.

    POST /api/users/register/
    """
    data = request.data

    # Validate required fields.
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
    missing_fields = [field for field in required_fields if not data.get(field)]

    # Send error message if some fields are missing.
    if missing_fields:
        return create_json_response(
            success=False,
            error=f"Missing required fields: {', '.join(missing_fields)}",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = UserService.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            user_type=data.get('user_type', 'REGISTERED')
        )

        # Send Welcome Email.
        email_service = EmailService()
        user_name = f"{user.first_name}".strip()
        if not user_name:
            user_name = user.username

        welcome_result = email_service.send_welcome_email(user.email, user_name)

        # Determine response message.
        if welcome_result['success']:
            response_message = "User registered successfully and welcome email sent"
        else:
            response_message = "User registered successfully but welcome email failed to send"

        return create_json_response(
            success=True,
            message=response_message,
            data=UserSerializer(user).data,
            welcome_email={
                'sent': welcome_result['success'],
                'status': welcome_result.get('message', 'Welcome email sent successfully') if welcome_result['success'] else welcome_result.get('error', 'Failed to send welcome email')
            },
            status_code=status.HTTP_201_CREATED
        )
    
    except ValueError as e:
        return create_json_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    """
    Authenticate user login.

    POST /api/users/login/
    """
    data = request.data

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return create_json_response(
            success=False,
            error='Email and password are required',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    user, token = UserService.authenticate_user(email, password)

    if user and token:
        user_data = dict(UserSerializer(user).data)
        user_data['token'] = token

        return create_json_response(
            success=True,
            message='Login successful',
            data=user_data
        )
    else:
        return create_json_response(
            success=False,
            error='Invalid credentials',
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_user(request):
    """
    Logout current user.

    POST /api/users/logout/
    """
    if UserService.logout_user(request.user):
        return create_json_response(
            success=True,
            message='Logout successful'
        )
    else:
        return create_json_response(
            success=False,
            error='Logout failed',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_profile(request, user_id: str):
    """
    Get user profile by ID.

    GET /api/users/{user_id}/
    """
    user = UserService.get_user_by_id(user_id)

    if not user:
        return create_json_response(
            success=False,
            error='User not found',
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    # User can only view their own profile unless admin.
    if not request.user.is_admin_user() and str(request.user.id) != user_id:
        return create_json_response(
            success=False,
            error='Permission denied',
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    return create_json_response(
        success=True,
        message='User profile retrieved successfully',
        data=UserSerializer(user).data
    )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_current_user(request):
    """
    Get current authenticated user's profile.

    GET /api/users/me/
    """
    return create_json_response(
        success=True,
        message='Current user profile retrieved successfully',
        data=UserSerializer(request.user).data
    )

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_user_profile(request, user_id: str):
    """
    Update user profile.

    PUT /api/users/{user_id}/update/
    """
    # Only admins or the user themselves can update profile.
    if not request.user.is_admin_user() and str(request.user.id) != user_id:
        return create_json_response(
            success=False,
            error='Permission denied',
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    data = request.data
    
    # Remove empty strings and None values.
    update_data = {k: v for k, v in data.items() if v is not None and v != ''}
    
    if not update_data:
        return create_json_response(
            success=False,
            error='No valid data provided for update',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = UserService.update_user_profile(user_id, update_data)
        
        if not user:
            return create_json_response(
                success=False,
                error='User not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return create_json_response(
            success=True,
            message='User profile updated successfully',
            data=UserSerializer(user).data
        )
    
    except ValueError as e:
        return create_json_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_400_BAD_REQUEST
        )

@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def change_user_password(request, user_id: str):
    """
    Change user password.

    PUT /api/users/{user_id}/change-password/
    """
    # Only admins or the user themselves can change password.
    if not request.user.is_admin_user() and str(request.user.id) != user_id:
        return create_json_response(
            success=False,
            error='Permission denied',
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    data = request.data
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    # Validate required fields.
    if not current_password or not new_password or not confirm_password:
        return create_json_response(
            success=False,
            error='Current password, new password, and confirm password are required',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if new passwords match.
    if new_password != confirm_password:
        return create_json_response(
            success=False,
            error='New password and confirm password do not match',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        success = UserService.change_password(user_id, current_password, new_password)
        
        if not success:
            return create_json_response(
                success=False,
                error='User not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return create_json_response(
            success=True,
            message='Password changed successfully'
        )
    
    except ValueError as e:
        return create_json_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_400_BAD_REQUEST
        )

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_user(request, user_id: str):
    """
    Delete user account.

    DELETE /api/users/{user_id}/delete
    """
    # Only admins or the user themselves can delete
    if not request.user.is_admin_user() and str(request.user.id) != user_id:
        return create_json_response(
            success=False,
            error='Permission denied',
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    if UserService.delete_user(user_id):
        return create_json_response(
            success=True,
            message='User deleted successfully'
        )
    else:
        return create_json_response(
            success=False,
            error='User not found',
            status_code=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def forgot_password(request):
    """
    Send password reset email to user.

    POST /api/users/forgot-password/
    """
    data = request.data
    email = data.get('email')

    if not email:
        return create_json_response(
            success=False,
            error='Email address is required',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Find user by email.
        user = User.objects.filter(email=email).first()

        if not user:
            # For security, always return success even if user doesn't exist
            return create_json_response(
                success=True,
                message='If an account with this email exists, a password reset link has been sent',
                password_reset_email={
                    'sent': False,
                    'status': 'No account found with this email'
                }
            )
        
        # Generate password reset token.
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Create reset URL.
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

        # Send password reset email.
        email_service = EmailService()
        user_name = f"{user.first_name} {user.last_name}".strip()
        if not user_name:
            user_name = user.username

        email_result = email_service.send_forgot_password_email(
            user_email=user.email,
            user_name=user_name,
            reset_url=reset_url,
            expiry_hours=1
        )

        if email_result['success']:
            logging.info(f"Password reset email sent successfully to {user.email}")
        else:
            logging.warning(f"Password reset email failed for user {user.email}: {email_result.get('error')}")

        return create_json_response(
            success=True,
            message='If an account with this email exists, a password reset link has been sent',
            password_reset_email={
                'sent': email_result['success'],
                'status': email_result.get('message', 'Password reset email sent successfully') if email_result['success'] else email_result.get('error', 'Failed to send password reset email')
            }
        )
    
    except Exception as e:
        logging.error(f"Error in forgot password process for {email}: {str(e)}")
        return create_json_response(
            success=False,
            error='An error occurred while processing your request',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    """
    Reset user password with token.

    POST /api/users/reset-password/
    """
    data = request.data
    uid = data.get('uid')
    token = data.get('token')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not all([uid, token, new_password, confirm_password]):
        return create_json_response(
            success=False,
            error='UID, token, new password, and confirm password are required',
            status_code=status.HTTP_400_BAD_REQUEST
        )

    if new_password != confirm_password:
        return create_json_response(
            success=False,
            error='New password and confirm password do not match',
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Decode the user ID
        user_id = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_id)
        
        # Verify the token
        if not default_token_generator.check_token(user, token):
            return create_json_response(
                success=False,
                error='Invalid or expired reset token',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset the password
        user.set_password(new_password)
        user.save()
        
        logging.info(f"Password reset successfully for user {user.email}")
        
        return create_json_response(
            success=True,
            message='Password reset successfully'
        )

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return create_json_response(
            success=False,
            error='Invalid reset token',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logging.error(f"Error resetting password: {str(e)}")
        return create_json_response(
            success=False,
            error='An error occurred while resetting your password',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )