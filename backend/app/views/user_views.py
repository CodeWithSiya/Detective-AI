from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.conf import settings
from app.services.user_service import UserService
from app.serializers.user_serializers import UserSerializer
from app.services.email_service import EmailService
from app.models.user import User
from typing import Optional, Any
from datetime import datetime
import logging

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
    Register a new user with email verification required.

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
        # Obtain user instance and the user's verification code.
        user, verification_code = UserService.create_user_with_verification(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            is_admin=False
        )

        # Send verification code email.
        email_service = EmailService()
        user_name = f"{user.first_name}".strip()
        if not user_name:
            user_name = user.username

        email_result = email_service.send_verification_code_email(
            user.email, user_name, verification_code
        )

        if email_result['success']:
            response_message = "User registered successfully. Please check your email for verification code."
        else:
            response_message = "User registered but verification email failed to send."

        return create_json_response(
            success=True,
            message=response_message,
            data={
                'user_id': str(user.id),
                'email': user.email,
                'requires_verification': True
            },
            verification_email={
                'sent': email_result['success'],
                'status': email_result.get('message', 'Verification email sent') if email_result['success'] 
                         else email_result.get('error', 'Failed to send verification email')
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
def verify_email(request):
    """
    Verify user's email with verification code.

    POST /api/users/verify-email/
    """
    data = request.data
    email = data.get('email')
    verification_code = data.get('verification_code')

    if not email or not verification_code:
        return create_json_response(
            success=False,
            error='Email and verification code are required',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = UserService.verify_email(email, verification_code)

        if result['success']:
            user = result['user']
            token = result['token']

            # Send Welcome Email.
            email_service = EmailService()
            user_name = f"{user.first_name}".strip()
            if not user_name:
                user_name = user.username

            welcome_result = email_service.send_welcome_email(user.email, user_name)

            # Determine response message.
            if welcome_result['success']:
                response_message = "Email verified successfully."
            else:
                response_message = "Email verified successfully but welcome email failed to send."

            # Return user data with token.
            user_data = dict(UserSerializer(user).data)
            user_data['token'] = token

            return create_json_response(
                success=True,
                message=response_message,
                data=user_data,
                welcome_email={
                    'sent': welcome_result['success'],
                    'status': welcome_result.get('message', 'Welcome email sent successfully') if welcome_result['success'] 
                              else welcome_result.get('error', 'Failed to send welcome email')
                },
            )
        
        else:
            return create_json_response(
                success=False,
                error=result.get('error', 'Email verification failed'),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    except Exception as e:
        logger.error(f"Error verifying email: {str(e)}")
        return create_json_response(
            success=False,
            error='An error occurred while verifying your email',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def resend_verification_code(request):
    """
    Resend verification code to user's email.

    POST /api/users/resend-verification/
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
        result = UserService.resend_verification_code(email)
        
        if result['success']:
            user = result['user']
            verification_code = result['verification_code']
            
            # Send new verification code
            email_service = EmailService()
            user_name = f"{user.first_name}".strip()
            if not user_name:
                user_name = user.username
                
            email_result = email_service.send_verification_code_email(
                user.email, user_name, verification_code
            )
            
            # Determine response message
            if email_result['success']:
                response_message = "Verification code resent successfully"
            else:
                response_message = "New verification code generated but email failed to send"
            
            return create_json_response(
                success=True,
                message=response_message,
                data={
                    'email': user.email,
                    'requires_verification': True
                },
                verification_email={
                    'sent': email_result['success'],
                    'status': email_result.get('message', 'Verification code sent') if email_result['success']
                             else email_result.get('error', 'Failed to send verification code')
                }
            )
        else:
            return create_json_response(
                success=False,
                error=result['error'],
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Error resending verification code: {str(e)}")
        return create_json_response(
            success=False,
            error='An error occurred while resending verification code',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
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
    
    try:
        # Check if user exists and if email is verified.
        user = User.objects.get(email=email)

        # Check if email is verified.
        if not user.is_email_verified:
            return create_json_response(
                success=False,
                error='Please verify your email before logging in',
                data={
                    'requires_verification': True, 
                    'email': email
                },
                status_code=status.HTTP_403_FORBIDDEN
            )
        
    except User.DoesNotExist:
        # Continue with normal authentication flow.
        pass
    
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
    if not request.user.is_staff and str(request.user.id) != user_id:
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
    if not request.user.is_staff and str(request.user.id) != user_id:
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
        result = UserService.update_user_profile(user_id, update_data)
        
        if not result:
            return create_json_response(
                success=False,
                error='User not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        user = result['user']
        user_data = UserSerializer(user).data
        
        # If email was changed, send verification email and provide instructions
        if result.get('email_changed'):
            try:
                # Send verification email to new address
                email_service = EmailService()
                user_name = f"{user.first_name}".strip()
                if not user_name:
                    user_name = user.username

                email_result = email_service.send_verification_code_email(
                    user.email, user_name, result['verification_code']
                )
                
                return create_json_response(
                    success=True,
                    message='Profile updated. Please verify your new email address to reactivate your account.',
                    data={
                        'user': user_data,
                        'email_verification_required': True,
                        'new_email': user.email,
                        'original_email': result['original_email']
                    },
                    verification_email={
                        'sent': email_result['success'],
                        'status': email_result.get('message', 'Verification email sent') if email_result['success']
                                 else email_result.get('error', 'Failed to send verification email')
                    },
                    instructions={
                        'message': 'Your account has been temporarily deactivated. Please check your new email for a verification code.',
                        'next_steps': [
                            'Check your new email address for a verification code',
                            'Use the existing /api/users/verify-email/ endpoint to verify your new email',
                            'Or use /api/users/resend-verification/ if you need a new code'
                        ]
                    }
                )
                
            except Exception as e:
                logger.error(f"Failed to send verification email: {str(e)}")
                return create_json_response(
                    success=True,
                    message='Profile updated but verification email failed to send. Please use the resend verification endpoint.',
                    data={
                        'user': user_data,
                        'email_verification_required': True,
                        'new_email': user.email
                    },
                    error='Verification email failed to send'
                )
        else:
            return create_json_response(
                success=True,
                message='User profile updated successfully',
                data={'user': user_data}
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
    if not request.user.is_staff and str(request.user.id) != user_id:
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
    if not request.user.is_staff and str(request.user.id) != user_id:
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
    
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def validate_token(request):
    """
    Validate authentication token.

    POST /api/users/validate-token/
    """
    data = request.data
    token = data.get('token')

    if not token:
        return create_json_response(
            success=False,
            error='Token is required',
            status_code=status.HTTP_400_BAD_REQUEST
        )

    result = UserService.validate_user_token(token)
    
    if result['valid']:
        user_data = dict(UserSerializer(result['user']).data)
        user_data['token'] = result['token']
        
        return create_json_response(
            success=True,
            message='Token is valid',
            data=user_data
        )
    else:
        return create_json_response(
            success=False,
            error=result['error'],
            status_code=status.HTTP_401_UNAUTHORIZED
        )