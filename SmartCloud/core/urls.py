from django.urls import path
from .api_views import (
    ReceiveLogsAPI,
    GetNewUsersAPI,
    ConfirmUserSyncAPI,
    StudentListCreateAPI,
    AttendanceListAPI
)

urlpatterns = [
    path('api/upload-logs/', ReceiveLogsAPI.as_view(), name='receive-logs'),
    path('api/get-users/', GetNewUsersAPI.as_view(), name='get-users'),
    path('api/confirm-sync/', ConfirmUserSyncAPI.as_view(), name='confirm-sync'),
    path('api/students/', StudentListCreateAPI.as_view(), name='students-api'),
    path('api/attendance/', AttendanceListAPI.as_view(), name='attendance-api'),
]