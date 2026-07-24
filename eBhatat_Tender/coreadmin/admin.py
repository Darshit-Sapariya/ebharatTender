from django.contrib import admin
from .models import ActionLog, Notice, ImportantEvent

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_active', 'is_pinned', 'created_at')
    list_filter = ('category', 'is_active', 'is_pinned')
    search_fields = ('title', 'description')

@admin.register(ImportantEvent)
class ImportantEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'event_type', 'is_active')
    list_filter = ('event_type', 'is_active')
    search_fields = ('title', 'description')

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('admin_user', 'action_type', 'target_user', 'timestamp')
    readonly_fields = ('timestamp',)
