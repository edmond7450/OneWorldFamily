from django.db import models


class Anonymous(models.Model):
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    business_name = models.CharField(max_length=254)
    business_type = models.CharField(max_length=60)
    email = models.CharField(max_length=150)
    phone = models.CharField(max_length=60)
    email_code = models.CharField(max_length=6, null=True)
    email_attempt_counts = models.SmallIntegerField(default=0)
    phone_code = models.CharField(max_length=6, null=True)
    phone_attempt_counts = models.SmallIntegerField(default=0)
    locked = models.SmallIntegerField(null=True)

    class Meta:
        db_table = 'user_anonymous'
        indexes = [
            models.Index(fields=['username'], name='anonymous_username', ),
            models.Index(fields=['username', 'email', 'phone'], name='anonymous_user', ),
        ]
