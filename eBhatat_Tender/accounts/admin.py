from django.contrib import admin
from .models import UserProfile
from .models import AdminRequest

# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'role', 'status', 'mobile', 'created_at')
    list_filter = ('role', 'status', 'created_at')
    search_fields = ('user__username', 'user__email', 'full_name', 'mobile')
    readonly_fields = ('user', 'created_at')
    actions = ['approve_users', 'reject_users']

    def approve_users(self, request, queryset):
        queryset.update(status='approved')
    approve_users.short_description = "Approve selected users"

    def reject_users(self, request, queryset):
        queryset.update(status='rejected')
    reject_users.short_description = "Reject selected users"

@admin.register(AdminRequest)
class AdminRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'department_name', 'category_name', 'status', 'created_at')
    list_filter = ('status', 'department_name', 'category_name', 'created_at')
    search_fields = ('user__username', 'department_name', 'category_name')
    readonly_fields = ('created_at',)
    actions = ['approve_requests', 'reject_requests']

    @admin.action(description="Approve selected admin requests")
    def approve_requests(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description="Reject selected admin requests")
    def reject_requests(self, request, queryset):
        queryset.update(status='rejected')
    
