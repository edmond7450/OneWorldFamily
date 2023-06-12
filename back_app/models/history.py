from django.conf import settings
from django.db import models

from my_settings import GMAIL_HOST_USER, LOG_RECIPIENT_ADDRESS
from user_app.views.send_email import send_mail

CATEGORY_CHOICES = (
    ('Backend', 'Backend'),
    ('Account', 'Account'),
    ('Setting', 'Setting'),
    ('Feed', 'Feed'),
    ('Payment', 'Payment')
)


class History(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    category = models.CharField(max_length=60)
    action = models.TextField()
    comment = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'back_history'
        indexes = [
            models.Index(fields=['user_id'], name='history_user_id', ),
            models.Index(fields=['category'], name='history_category', )
        ]


def save_history(user, category, action, comment=None):
    if isinstance(user, int):
        History.objects.create(user_id=user, category=category, action=action, comment=comment)
    else:
        History.objects.create(user=user, category=category, action=action, comment=comment)

    if category == 'Critical':
        send_mail(GMAIL_HOST_USER, LOG_RECIPIENT_ADDRESS, 'SharpArchive Error',
                  f'Category: {category}\n'
                  f'Action: {action}\n'
                  f'Comment: {comment}')
