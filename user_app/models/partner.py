from django.db import models

STATUS_CHOICES = (
    ('Unverified', 'Unverified'),
    ('Email_Verified', 'Email_Verified'),
    ('Phone_Verified', 'Phone_Verified'),
    ('Refused', 'Refused'),
    ('Approved', 'Approved'),
)


class Partner(models.Model):
    email = models.CharField(max_length=254, unique=True)
    full_name = models.CharField(max_length=254)
    title = models.CharField(max_length=254)
    phone = models.CharField(max_length=60)
    company_name = models.CharField(max_length=254)
    comments = models.TextField()

    status = models.CharField(max_length=20, default='Unverified', choices=STATUS_CHOICES)
    otp = models.CharField(max_length=6)
    otp_attempt_counts = models.SmallIntegerField(default=0)

    code = models.CharField(max_length=120, unique=True, null=True)

    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_partner'
