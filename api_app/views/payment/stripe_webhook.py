import stripe
import pytz

from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

from my_settings import ENVIRONMENT, STRIPE
from api_app.models.invoice import Invoice
from api_app.views.payment.invoice import get_invoice_data, create_invoice, create_refund
from back_app.models.history import save_history
from back_app.models.notification import save_notification
from user_app.models.profile import Profile

stripe.api_key = STRIPE['SECRET_KEY']


@require_POST
@csrf_exempt
def endpoint(request):
    try:
        event = None
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE['ENDPOINT_SECRET']
            )
        except ValueError as e:
            # Invalid payload
            raise e
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            raise e

        if event['type'] == 'invoice.upcoming':
            invoice = event['data']['object']

            customer = stripe.Customer.retrieve(invoice.customer)
            if (ENVIRONMENT != 'product' and 'deleted' in customer and customer['deleted']) or ENVIRONMENT != customer['metadata']['environment']:
                return HttpResponse(status=200)

            user_id = int(customer['metadata']['user_id'])

            set_usage(invoice)

        elif event['type'] == 'invoice.created':
            invoice = event['data']['object']

            customer = stripe.Customer.retrieve(invoice.customer)
            if (ENVIRONMENT != 'product' and 'deleted' in customer and customer['deleted']) or ENVIRONMENT != customer['metadata']['environment']:
                return HttpResponse(status=200)

            subscription = stripe.Subscription.retrieve(invoice.subscription)
            if subscription.status == 'trialing' or subscription.status == 'incomplete_expired' or subscription.status == 'canceled':
                return HttpResponse(status=200)

            user_id = int(customer['metadata']['user_id'])

            check_usage(invoice)

        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']

            customer = stripe.Customer.retrieve(payment_intent.customer)
            try:
                if (ENVIRONMENT != 'product' and 'deleted' in customer and customer['deleted']) or ENVIRONMENT != customer['metadata']['environment']:
                    return HttpResponse(status=200)

                profile = Profile.objects.get(stripe_customer_id=payment_intent.customer)
                user_id = profile.user_id
            except Exception as e:
                save_history(1, 'Critical', 'Stripe User Error', repr(e))
                return HttpResponse(status=200)

            if payment_intent.status == 'succeeded':
                if not payment_intent.invoice:
                    return HttpResponse(status=200)

                stripe_invoice = stripe.Invoice.retrieve(payment_intent.invoice)
                total = stripe_invoice.total / 100
                try:
                    tax = stripe_invoice.tax / 100
                except:
                    tax = 0
                subtotal = round(total - tax, 2)
                fee = round(total * 0.029 + 0.3, 2)
                net = round(total - fee, 2)

                period_end_date = datetime.fromtimestamp(stripe_invoice.period_end, pytz.timezone('UTC')).date()
                invoice_number, invoice_path = create_invoice(user_id, subtotal, tax, period_end_date, payment_intent.charges.data[0].billing_details)

                Invoice.objects.create(invoice_number=invoice_number, invoice_path=invoice_path, subtotal=subtotal, tax=tax, total=total, fee=fee, net=net,
                                       stripe_payment_intent_id=payment_intent.id, stripe_invoice_id=payment_intent.invoice, user_id=user_id)

                profile.payment_status = 'paid'
                profile.save()
                save_notification(user_id, 'Payment', f'You paid ${"%.2f" % total}. Invoice Number: {invoice_number}')
            else:
                profile.payment_status = payment_intent.status
                profile.save()
                save_history(user_id, 'Critical', 'Payment Error', payment_intent.status)

        elif event['type'] == 'charge.refunded':
            charge = event['data']['object']

            customer = stripe.Customer.retrieve(charge.customer)
            if ('deleted' in customer and customer['deleted']) or ENVIRONMENT != customer['metadata']['environment']:
                return HttpResponse(status=200)

            profile = Profile.objects.get(stripe_customer_id=charge.customer)
            user_id = profile.user_id

            refund = charge.refunds.data[-1]
            if refund.status == 'succeeded':
                total = float('%.2f' % (refund.amount / 100))

                invoice_number, invoice_path, subtotal, tax = create_refund(user_id, charge.payment_intent, total)

                Invoice.objects.create(invoice_number=invoice_number, invoice_path=invoice_path, subtotal=0 - subtotal, tax=0 - tax, total=0 - total, fee=0, net=0 - total,
                                       stripe_payment_intent_id=charge.payment_intent, stripe_invoice_id=refund.id, user_id=user_id)

                save_notification(user_id, 'Payment', f'Refunded ${"%.2f" % total}. Invoice Number: {invoice_number}')
            else:
                profile.payment_status = refund.status
                profile.save()
                save_history(user_id, 'Critical', 'Refund Error', refund.status)

        elif event['type'] == 'charge.refund.updated':
            refund = event['data']['object']

            if refund.status == 'failed':
                payment_intent = stripe.PaymentIntent.retrieve(refund.payment_intent, expand=['customer'])
                if ('deleted' in payment_intent['customer'] and payment_intent['customer']['deleted']) or ENVIRONMENT != payment_intent['customer']['metadata']['environment']:
                    return HttpResponse(status=200)

                user_id = payment_intent['customer']['metadata']['user_id']
                profile = Profile.objects.get(user_id=user_id)
                profile.payment_status = refund.failure_reason
                profile.save()

                save_history(user_id, 'Critical', 'Refund Failed', f'amount: {refund.amount}, reason: {refund.failure_reason}')

        return HttpResponse(status=200)

    except Exception as e:
        # if str(e) == 'Profile matching query does not exist.':  # todo remove before launch
        #     return HttpResponse(status=200)
        try:
            save_history(user_id, 'Critical', 'Stripe WebHook Error', repr(e))
        except:
            save_history(1, 'Critical', 'Stripe WebHook Error', repr(e))
        return HttpResponse(repr(e), content_type='text/plain', status=500)


def set_usage(invoice):
    profile = Profile.objects.get(stripe_customer_id=invoice.customer)
    data = get_invoice_data(profile.user, datetime.fromtimestamp(invoice.period_end, pytz.timezone('UTC')))
    if 'arrears' in data and 'daysCycle' in data['arrears']:
        daysCycle = data['arrears']['daysCycle']
    else:
        return

    subscription_feed_id = ''
    subscription_storage_id = ''
    subscription_sub_id = ''
    customer = stripe.Customer.retrieve(invoice.customer, expand=['subscriptions'])
    subscription = customer.subscriptions.data[0]
    for item in subscription['items'].data:
        subscription_item_price_id = item['price']['id']

        if subscription_item_price_id == STRIPE['FEED_PRICE_ID']:
            subscription_feed_id = item['id']
        # elif subscription_item_price_id == STRIPE['STORAGE_PRICE_ID']:
        #     subscription_storage_id = item['id']
        elif daysCycle == 31 and subscription_item_price_id == STRIPE['FEED_SUB31_PRICE_ID']:
            subscription_sub_id = item['id']
        elif daysCycle == 30 and subscription_item_price_id == STRIPE['FEED_SUB30_PRICE_ID']:
            subscription_sub_id = item['id']
        elif daysCycle == 29 and subscription_item_price_id == STRIPE['FEED_SUB29_PRICE_ID']:
            subscription_sub_id = item['id']
        elif daysCycle == 28 and subscription_item_price_id == STRIPE['FEED_SUB28_PRICE_ID']:
            subscription_sub_id = item['id']

    stripe.SubscriptionItem.create_usage_record(
        subscription_feed_id,
        quantity=data['advance']['numberFeeds'],
        timestamp=int(timezone.now().timestamp())
    )

    # stripe.SubscriptionItem.create_usage_record(
    #     subscription_storage_id,
    #     quantity=data['arrears']['currentGB'],
    #     timestamp=int(timezone.now().timestamp())
    # )

    daysLeft = 0
    for feed in data['arrears']['newFeeds']:
        daysLeft += feed['daysLeft']
    for feed in data['arrears']['partialFeeds']:
        daysLeft += feed['daysLeft']

    if daysLeft > 0:
        stripe.SubscriptionItem.create_usage_record(
            subscription_sub_id,
            quantity=daysLeft,
            timestamp=int(timezone.now().timestamp())
        )

    if float(data['arrears']['totalTerminatedCost']) > 0:
        coupon = stripe.Coupon.create(
            currency='usd',
            duration='once',
            amount_off=round(float(data['arrears']['totalTerminatedCost']) * 100),
        )
        stripe.Subscription.modify(subscription.id, coupon=coupon.id)
        stripe.Coupon.delete(coupon.id)


def check_usage(invoice):
    profile = Profile.objects.get(stripe_customer_id=invoice.customer)
    data = get_invoice_data(profile.user, datetime.fromtimestamp(invoice.period_end, pytz.timezone('UTC')))

    subtotal = float('%.2f' % (invoice.subtotal / 100))
    if float(data['subtotal']) == subtotal:
        return

    diff = round(float(data['subtotal']) - subtotal, 2)

    if diff > 0:
        stripe.InvoiceItem.create(
            customer=invoice.customer,
            price_data={
                'product': STRIPE['FEED_PRODUCT_ID'],
                'currency': 'usd',
                'unit_amount': round(diff * 100),
                'tax_behavior': 'exclusive',
            },
            invoice=invoice.id
        )
    else:
        coupon = stripe.Coupon.create(
            currency='usd',
            duration='once',
            amount_off=abs(round(diff * 100)),
        )
        stripe.Invoice.modify(invoice.id, discounts=[{'coupon': coupon.id}])
        stripe.Coupon.delete(coupon.id)

    # customer = stripe.Customer.retrieve(invoice.customer, expand=['subscriptions'])
    # subscription = customer.subscriptions.data[0]
    # stripe.Subscription.modify(subscription.id, coupon=None)
