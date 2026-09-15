from django.contrib import admin
from .models import DailyAttendance

@admin.register(DailyAttendance)
class DailyAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'arrived_at', 'left_at')
    list_filter = ('date',)
    search_fields = ('student__full_name', 'student__hikvision_id')