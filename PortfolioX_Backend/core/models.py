from django.db import models
from django.conf import settings
from portfolios.models import Portfolio

class Alert(models.Model):
    PRIORITY_CHOICES = [('high', 'High'), ('medium', 'Medium'), ('low', 'Low')]
    TYPE_CHOICES = [
        ('concentration_risk', 'Concentration Risk'),
        ('sector_imbalance', 'Sector Imbalance'),
        ('price_alert', 'Price Alert'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.SET_NULL, null=True)
    alert_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=['user'], name='idx_alerts_user_unread', condition=models.Q(is_read=False)),
        ]
class UploadJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('processing', 'Processing'),
        ('completed', 'Completed'), ('failed', 'Failed')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_log = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
