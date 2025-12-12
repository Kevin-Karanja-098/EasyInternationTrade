from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone
from datetime import timedelta

class EmailVerificationToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return self.created_at < timezone.now() - timedelta(hours=24)

    def __str__(self):
        return f"{self.user.email} - {self.token}"
