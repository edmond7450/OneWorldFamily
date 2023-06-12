from django.db import models


class Security(models.Model):
    otp = models.CharField(max_length=6, null=True)
    otp_attempt_counts = models.SmallIntegerField(default=0)
    sms_counts = models.SmallIntegerField(default=0)

    question1 = models.CharField(max_length=50, null=True)
    answer1 = models.CharField(max_length=50, null=True)
    question2 = models.CharField(max_length=50, null=True)
    answer2 = models.CharField(max_length=50, null=True)
    question3 = models.CharField(max_length=50, null=True)
    answer3 = models.CharField(max_length=50, null=True)
    question4 = models.CharField(max_length=50, null=True)
    answer4 = models.CharField(max_length=50, null=True)

    updated_at = models.DateTimeField(null=True)

    user_id = models.IntegerField()

    class Meta:
        db_table = 'user_security'
        indexes = [
            models.Index(fields=['user_id'], name='security_user_id'),
        ]
