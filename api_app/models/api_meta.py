from django.db import models


class API_Meta(models.Model):
    meta_key = models.CharField(max_length=254)
    meta_value = models.TextField()

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_meta'
        indexes = [
            models.Index(fields=['meta_key'], name='api_meta_key', ),
        ]
