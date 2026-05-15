from django.contrib import admin
from .models import Business


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'category', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'owner__first_name', 'owner__last_name', 'description']
    list_filter = ['category', 'is_active', 'is_featured']
    list_editable = ['is_active', 'is_featured']
