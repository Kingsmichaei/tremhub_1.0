from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'branch', 'unit', 'occupation', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'occupation']
    list_filter = ['branch', 'unit']
