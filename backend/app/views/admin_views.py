from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from datetime import datetime
from app.services.admin_service import AdminService
from typing import Optional, Any

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

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_system_statistics(request):
    """
    Get system-wide statistics for admin dashboard.

    GET /api/admin/statistics/
    """
    try:
        result = AdminService.get_system_statistics()

        if result['success']:
            return create_json_response(
                success=True,
                message='System statistics retrieved successfully',
                data=result['statistics']
            )
        else:
            return create_json_response(
                success=False,
                error=result['error'],
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        return create_json_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_recent_activity(request):
    """
    Get recent activity across the system.
    
    GET /api/admin/activity/?limit=20
    """
    try:
        limit = int(request.GET.get('limit', 20))
        
        # Validate limit
        if limit < 1 or limit > 100:
            limit = 20
            
        result = AdminService.get_recent_activity(limit=limit)
        
        if result['success']:
            return create_json_response(
                success=True,
                message='Recent activity retrieved successfully',
                data={
                    'activities': result['activities'],
                    'total_returned': len(result['activities'])
                }
            )
        else:
            return create_json_response(
                success=False,
                error=result['error'],
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except ValueError:
        return create_json_response(
            success=False,
            error='Invalid limit parameter',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return create_json_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_performance_metrics(request):
    """
    Get performance metrics over a specified time period.
    
    GET /api/admin/performance/?days=7
    """
    try:
        days = int(request.GET.get('days', 7))
        
        # Validate days parameter
        if days < 1 or days > 90:
            days = 7
            
        result = AdminService.get_performance_metrics(days=days)
        
        if result['success']:
            return create_json_response(
                success=True,
                message='Performance metrics retrieved successfully',
                data=result['metrics']
            )
        else:
            return create_json_response(
                success=False,
                error=result['error'],
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except ValueError:
        return create_json_response(
            success=False,
            error='Invalid days parameter',
            status_code=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return create_json_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_admin_dashboard_data(request):
    """
    Get comprehensive admin dashboard data (statistics + recent activity).
    
    GET /api/admin/dashboard/
    """
    try:
        # Get both statistics and recent activity.
        stats_result = AdminService.get_system_statistics()
        activity_result = AdminService.get_recent_activity(limit=10)
        
        if stats_result['success'] and activity_result['success']:
            return create_json_response(
                success=True,
                message='Admin dashboard data retrieved successfully',
                data={
                    'statistics': stats_result['statistics'],
                    'recent_activity': activity_result['activities']
                }
            )
        else:
            # Return partial data if one fails.
            errors = []
            if not stats_result['success']:
                errors.append(f"Statistics error: {stats_result['error']}")
            if not activity_result['success']:
                errors.append(f"Activity error: {activity_result['error']}")
                
            return create_json_response(
                success=False,
                error='; '.join(errors),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        return create_json_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_users_list(request):
    """
    Get list of all users with their statistics for admin dashboard.
    
    GET /api/admin/users/
    """
    try:
        result = AdminService.get_users_list()
        
        if result['success']:
            return create_json_response(
                success=True,
                message='Users retrieved successfully',
                data={
                    'users': result['users']
                }
            )
        else:
            return create_json_response(
                success=False,
                error=result['error'],
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        return create_json_response(
            success=False,
            error=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )