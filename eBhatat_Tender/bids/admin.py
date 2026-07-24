from django.contrib import admin
from bids.models import TenderApplication

@admin.register(TenderApplication)
class TenderApplicationAdmin(admin.ModelAdmin):
    list_display = ('tender', 'applicant', 'company_name', 'status', 'applied_at', 'bid_amount')
    list_filter = ('status', 'applied_at')
    search_fields = ('tender__title', 'applicant__username', 'company_name')
    readonly_fields = ('applied_at',)
    
    actions = ['approve_applications', 'reject_applications']

    @admin.action(description="Approve selected applications")
    def approve_applications(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description="Reject selected applications")
    def reject_applications(self, request, queryset):
        queryset.update(status='rejected')

# Admin Site Customization
admin.site.site_header = "eBharat Tender Admin"
admin.site.site_title = "eBharat Tender Admin Portal"   
admin.site.index_title = "Welcome to eBharat Tender Admin Portal"
