from django.db import models


class Meta(models.Model):
    user_id = models.IntegerField()
    meta_key = models.CharField(max_length=254)
    meta_value = models.TextField()

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_meta'
        indexes = [
            models.Index(fields=['user_id'], name='user_meta_user_id', ),
            models.Index(fields=['meta_key'], name='user_meta_key', ),
        ]
