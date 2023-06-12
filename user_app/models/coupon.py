from django.db import models


class Coupon(models.Model):
    coupon_code = models.CharField(max_length=20)
    months = models.SmallIntegerField()

    user_id = models.IntegerField(null=True)
    started_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'user_coupon'
        indexes = [
            models.Index(fields=['user_id'], name='user_coupon_user_id', ),
            models.Index(fields=['coupon_code'], name='user_coupon_code', ),
        ]
