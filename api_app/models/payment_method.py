from django.db import models


class PaymentMethod(models.Model):
    method_id = models.CharField(max_length=120, unique=True)
    address_line1 = models.CharField(max_length=127, null=True)
    address_line2 = models.CharField(max_length=127, null=True)
    address_city = models.CharField(max_length=127, null=True)
    address_state = models.CharField(max_length=127, null=True)
    address_country = models.CharField(max_length=127, null=True)
    address_zip = models.CharField(max_length=10, null=True)
    name = models.CharField(max_length=254, null=True)
    email = models.CharField(max_length=254, null=True)  # PayPal

    brand = models.CharField(max_length=20)  # visa, amex, mastercard, discover, diners, jcb, unionpay, PayPal

    # Stripe Card
    exp_month = models.SmallIntegerField(null=True)
    exp_year = models.SmallIntegerField(null=True)
    funding = models.CharField(max_length=20, null=True)  # credit, debit, prepaid, PayPal: payment_method_token_id (Billing ID)
    last4 = models.CharField(max_length=4, null=True)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user_id = models.IntegerField()

    class Meta:
        db_table = 'user_payment_method'
        indexes = [
            models.Index(fields=['method_id'], name='payment_method_id', ),
            models.Index(fields=['user_id'], name='payment_method_user_id', ),
        ]
