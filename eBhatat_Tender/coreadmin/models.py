from django.db import models
from django.contrib.auth.models import User

class ActionLog(models.Model):
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_actions')
    action_type = models.CharField(max_length=100) # e.g., 'ROLE_ALLOCATION', 'APP_APPROVAL'
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='targeted_actions')
    target_department = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.admin_user.username} - {self.action_type}"

class Notice(models.Model):
    CATEGORY_CHOICES = (
        ('Urgent', 'Urgent'),
        ('Tender Notice', 'Tender Notice'),
        ('Policy Update', 'Policy Update'),
        ('Training', 'Training'),
        ('System Notice', 'System Notice'),
        ('Contract Award', 'Contract Award'),
        ('General', 'General'),
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='General')
    is_active = models.BooleanField(default=True)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

class ImportantEvent(models.Model):
    EVENT_TYPES = (
        ('info', 'Information (Blue)'),
        ('warning', 'Warning (Amber)'),
        ('critical', 'Critical (Red)'),
    )

    title = models.CharField(max_length=255)
    event_date = models.DateField()
    event_time = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., 10 AM – 2 PM IST")
    description = models.CharField(max_length=255, blank=True, null=True, help_text="Short detail below title")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='info')
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['event_date']

    def __str__(self):
        return f"{self.event_date} - {self.title}"
