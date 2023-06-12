from django.db import models


class Question(models.Model):
    email = models.EmailField()
    full_name = models.TextField(default='')
    question = models.TextField()
    answer = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_question'
        indexes = [
            models.Index(fields=['email'], name='user_question_email', ),
        ]
