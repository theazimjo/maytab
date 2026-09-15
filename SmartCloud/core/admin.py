from django.contrib import admin
from .models import School, Student

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'api_key', 'is_active', 'is_online', 'last_activity')
    readonly_fields = ('api_key', 'last_activity')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'hikvision_id', 'school', 'is_synced')
    list_filter = ('school', 'is_synced')
    search_fields = ('full_name', 'hikvision_id')
    readonly_fields = ('hikvision_id',)
