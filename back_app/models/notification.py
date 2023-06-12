from django.conf import settings
from django.db import models


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    category = models.CharField(max_length=60)
    message = models.TextField(null=True)
    is_auto = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)
    is_shown = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'back_notification'
        indexes = [
            models.Index(fields=['user_id'], name='notification_user_id', ),
            models.Index(fields=['category'], name='notification_category', )
        ]


def save_notification(user, category, message, is_auto=True):
    if isinstance(user, int):
        Notification.objects.create(user_id=user, category=category, message=message, is_auto=is_auto)
    else:
        Notification.objects.create(user=user, category=category, message=message, is_auto=is_auto)
