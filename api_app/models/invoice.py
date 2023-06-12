from django.db import models


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=60, unique=True)
    invoice_path = models.TextField(default=None, null=True)

    subtotal = models.FloatField(default=None, null=True)
    tax = models.FloatField(default=None, null=True)
    total = models.FloatField(default=None, null=True)
    fee = models.FloatField(default=None, null=True)
    net = models.FloatField(default=None, null=True)
    description = models.TextField(default=None, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    stripe_payment_intent_id = models.CharField(max_length=120)  # PayPal: payment_method_token_id (Billing ID)
    stripe_invoice_id = models.CharField(max_length=120)  # PayPal: order Id

    user_id = models.IntegerField()

    class Meta:
        db_table = 'invoice'
        indexes = [
            models.Index(fields=['user_id'], name='invoice_user_id', ),
        ]
