from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = [
        ('retail', 'Retail'),
        ('premium', 'Premium'),
        ('admin', 'Admin'),
    ]
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='retail')
    is_verified = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        indexes = [
            models.Index(fields=['email'], name='idx_users_email'),
            models.Index(fields=['role'], name='idx_users_role'),
        ]
class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token_hash = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=['user'], name='idx_sessions_user'),
            models.Index(fields=['token_hash'], name='idx_sessions_token'),
        ]
