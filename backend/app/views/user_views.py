from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from app.services.user_service import UserService
from typing import Optional, Any
from datetime import datetime

User = get_user_model()

def user_to_dict(user):
    """
    Convert user instance to dictionary for JSON response.
    """
    return {
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'user_type': user.user_type,
        'is_admin': user.is_admin_user()
    }

def create_json_response(success: bool = True, message: Optional[str] = None, data: Optional[Any] = None, error: Optional[str] = None, status_code = status.HTTP_200_OK):
    """
    Create standardised JSON response.
    """
    response_data = {
        'success': success,
        'message': message,
        'data': data,
        'error': error,
        'timestamp': datetime.now().isoformat()
    }
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
        return create_json_response(
            success=True,
            message='User registered successfully',
            data=user_to_dict(user),
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
    
    user = UserService.authenticate_user(email, password)

    if user:
        return create_json_response(
            success=True,
            message='Login successful',
            data=user_to_dict(user)
        )
    else:
        return create_json_response(
            success=False,
            error='Invalid credentials',
            status_code=status.HTTP_401_UNAUTHORIZED
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
        data=user_to_dict(user)
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
        data=user_to_dict(request.user)
    )

@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_user_profile(request, user_id: str):
    """
    Update user profile.

    PUT/PATCH /api/users/{user_id}/
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
            data=user_to_dict(user)
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

    DELETE /api/users/{user_id}/
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