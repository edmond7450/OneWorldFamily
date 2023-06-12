from datetime import timedelta
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils import timezone


class Device(models.Model):
    ip = models.CharField(max_length=50)
    location = models.CharField(max_length=50, null=True)
    os = models.CharField(max_length=50)
    browser = models.CharField(max_length=50)
    device = models.CharField(max_length=50)

    is_confirmed = models.BooleanField(default=False)

    confirmed_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # last_login

    user_id = models.IntegerField()

    def last_seen(self):
        return cache.get('seen_%s_%s' % (self.user_id, self.id))

    def is_active(self):
        if self.last_seen():
            if timezone.now() > self.last_seen() + timedelta(seconds=settings.DEVICE_ACTIVE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False

    class Meta:
        db_table = 'user_device'
        indexes = [
            models.Index(fields=['user_id'], name='device_user_id'),
            models.Index(fields=['-updated_at'], name='device_updated_at'),
        ]
