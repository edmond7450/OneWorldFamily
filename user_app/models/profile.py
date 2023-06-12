from django.db import models
from django.contrib.auth.models import User

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female')
)


class USER_STATUS():
    INACTIVE = 0
    VERIFIED = 1
    INTERNAL = 2
    SECURITY_CHECKING = 3  # Don't use
    RESTRICTED = 4
    CLOSED = 5


STATUS_CHOICES = (
    (0, ''),
    (USER_STATUS.VERIFIED, 'Verified'),
    (USER_STATUS.INTERNAL, 'Internal User'),
    (USER_STATUS.SECURITY_CHECKING, 'Security Checking'),
    (USER_STATUS.RESTRICTED, 'Restricted'),
    (USER_STATUS.CLOSED, 'Closed')
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    user_permission = models.CharField(max_length=20, default='Administrator')
    birthday = models.DateField(null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=60)
    address = models.CharField(max_length=254)
    address_components = models.CharField(max_length=510)
    two_factor = models.SmallIntegerField(default=1)  # 1: mobile, 2: email
    status = models.SmallIntegerField(default=0, choices=STATUS_CHOICES)
    membership_date = models.DateField(null=True)
    payment_status = models.CharField(max_length=30)
    avatar = models.ImageField(upload_to='images/users/')
    description = models.CharField(max_length=510)
    close_account_info = models.CharField(max_length=254, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    stripe_customer_id = models.CharField(max_length=120)

    class Meta:
        db_table = 'user_profile'
        indexes = [
            models.Index(fields=['status'], name='profile_status'),
            models.Index(fields=['membership_date'], name='profile_membership_date'),

            models.Index(fields=['stripe_customer_id'], name='profile_stripe_customer_id', ),
        ]


class User_Status(models.Model):
    status = models.CharField(max_length=20)
    description = models.CharField(max_length=254, null=True)

    class Meta:
        db_table = 'user_status'
