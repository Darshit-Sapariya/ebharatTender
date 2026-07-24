from django.contrib import admin
from .models import Tenderss

@admin.register(Tenderss)
class TenderssAdmin(admin.ModelAdmin):
    list_display = ('tender_id', 'title', 'category', 'status', 'closing_date', 'estimated_value', 'created_at')
    list_filter = ('status', 'category', 'created_at', 'closing_date')
    search_fields = ('tender_id', 'title', 'department', 'description')
    readonly_fields = ('tender_id', 'created_at')
    
    actions = ['publish_tenders', 'close_tenders']

    @admin.action(description="Mark selected tenders as Published")
    def publish_tenders(self, request, queryset):
        queryset.update(status='Published')

    @admin.action(description="Mark selected tenders as Closed")
    def close_tenders(self, request, queryset):
        queryset.update(status='Closed')
