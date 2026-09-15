from django.urls import path
from .api_views import (
    ReceiveLogsAPI,
    GetNewUsersAPI,
    ConfirmUserSyncAPI,
    StudentListCreateAPI,
    AttendanceListAPI
)
from . import views

urlpatterns = [
    # --- Agent API lar (o'zgarmagan) ---
    path('api/upload-logs/', ReceiveLogsAPI.as_view(), name='receive-logs'),
    path('api/get-users/', GetNewUsersAPI.as_view(), name='get-users'),
    path('api/confirm-sync/', ConfirmUserSyncAPI.as_view(), name='confirm-sync'),
    path('api/students/', StudentListCreateAPI.as_view(), name='students-api'),
    path('api/attendance/', AttendanceListAPI.as_view(), name='attendance-api'),

    # --- O'quvchilar web sahifalari ---
    path('', views.student_list, name='student_list'),
    path('students/add/', views.student_create, name='student_create'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
]