import googlemaps
import json
import stripe

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from stripe import error

from my_settings import GOOGLE_GEOCODING_API_KEY, STRIPE
from api_app.models.api_meta import API_Meta
from api_app.models.invoice import Invoice
from api_app.models.payment_method import PaymentMethod
from api_app.views.payment.invoice import create_invoice
from back_app.models.history import save_history
from back_app.models.notification import save_notification

stripe.api_key = STRIPE['SECRET_KEY']


class CardView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            data = request.data

            user = User.objects.get(username=data['email'])
            token = data['token']
            address = data['address']
            if not token or not address:
                raise Exception('Parameter Error')

            tier_name = data['tierName']
            tier_number = int(data['tierNumber'])
            donation = int(data['donation'])
            total = int(data['total'])

            tier_checked = False
            tiers = json.loads(API_Meta.objects.get(meta_key='tier-cost').meta_value)
            for tier in tiers:
                if tier['value'] == tier_name:
                    if tier['price'] * tier_number + donation == total:
                        tier_checked = True
                        break
                    else:
                        raise Exception('Parameter Error')
            if not tier_checked:
                raise Exception('Parameter Error')
        except:
            return JsonResponse({'status': 401, 'success': False, 'message': 'Parameter Error'})

        try:
            street_number = route = city = state = country = postal_code = ''
            try:
                gmaps = googlemaps.Client(key=GOOGLE_GEOCODING_API_KEY)
                geocode_result = gmaps.geocode(data['address'])

                for component in geocode_result[0]['address_components']:
                    for j in component['types']:
                        if j == 'street_number':
                            street_number = component['short_name']
                        elif j == 'route':
                            route = component['short_name']
                        elif j == 'locality':
                            city = component['short_name']
                        elif j == 'administrative_area_level_1':
                            state = component['short_name']
                        elif j == 'country':
                            country = component['short_name']
                        elif j == 'postal_code':
                            postal_code = component['short_name']

                if not postal_code:
                    return JsonResponse({'status': 402, 'success': False, 'message': 'Billing Address is invalid'})

                addresses = geocode_result[0]['formatted_address'].split(', ')
            except:
                return JsonResponse({'status': 403, 'success': False, 'message': 'Billing Address is invalid'})

            # create payment method
            payment_method = stripe.PaymentMethod.create(
                type='card',
                card={'token': data['token']},
                billing_details={
                    'address': {'line1': addresses[0], 'city': city, 'state': state, 'country': country, 'postal_code': postal_code},
                    'email': user.username,
                    'name': user.get_full_name()
                }
            )

            # create/retrieve customer
            profile = user.profile
            stripe_customer_id = profile.stripe_customer_id
            if not stripe_customer_id:
                # Create Stripe user
                customer = stripe.Customer.create(
                    email=user.email,
                    name=user.get_full_name(),
                    description='Created from One World Family',
                    metadata={'user_id': user.id, 'phone': profile.phone},
                    address={'line1': addresses[0], 'city': city, 'state': state, 'country': country, 'postal_code': postal_code, },
                    expand=['tax'],
                )

                stripe_customer_id = customer.id
                profile.stripe_customer_id = stripe_customer_id
                if not profile.address:
                    profile.address = data['address']
                    profile.address_components = json.dumps({'street_number': street_number, 'route': route, 'city': city, 'state': state, 'country': country, 'postal_code': postal_code})
                profile.save()
            else:
                customer = stripe.Customer.retrieve(stripe_customer_id)

            # attach payment method to customer
            stripe.PaymentMethod.attach(
                payment_method.stripe_id,
                customer=stripe_customer_id,
            )
            stripe.Customer.modify(
                stripe_customer_id,
                invoice_settings={'default_payment_method': payment_method.stripe_id}
            )

            now = timezone.now()
            try:
                payment_intent = stripe.PaymentIntent.create(
                    amount=total * 100,
                    currency='usd',
                    customer=stripe_customer_id,
                    payment_method=payment_method.stripe_id,
                    off_session=True,
                    confirm=True,
                )
                if payment_intent.amount_received != total * 100:
                    save_history(user, 'Critical', 'Stripe Payment', f'Different amount received: {payment_intent.amount_received}/{total * 100}')
            except stripe.error.CardError as e:
                stripe.PaymentMethod.detach(payment_method.stripe_id)
                return JsonResponse({'status': 404, 'success': False, 'message': e.user_message})

            profile.payment_status = 'paid'
            profile.save()

            fee = round(total * 0.029 + 0.3, 2)
            net = round(total - fee, 2)

            invoice_number, invoice_path = create_invoice(user.id, total, 0, tier_name, tier_number, donation, payment_method.billing_details)

            Invoice.objects.create(invoice_number=invoice_number, invoice_path=invoice_path, subtotal=total - donation, tax=0, total=total, fee=fee, net=net,
                                   stripe_payment_intent_id=payment_method.stripe_id, stripe_invoice_id=payment_intent.id, user_id=user.id)

            save_notification(user.id, 'Payment', f'You paid ${"%.2f" % total}. Invoice Number: {invoice_number}')

            defaults = {}
            defaults['address_line1'] = payment_method.billing_details.address.line1
            defaults['address_line2'] = payment_method.billing_details.address.line2
            defaults['address_city'] = payment_method.billing_details.address.city
            defaults['address_state'] = payment_method.billing_details.address.state
            defaults['address_country'] = payment_method.billing_details.address.country
            defaults['address_zip'] = payment_method.billing_details.address.postal_code
            defaults['name'] = payment_method.billing_details.name
            defaults['brand'] = payment_method.card.brand
            defaults['exp_month'] = payment_method.card.exp_month
            defaults['exp_year'] = payment_method.card.exp_year
            defaults['funding'] = payment_method.card.funding
            defaults['last4'] = payment_method.card.last4
            defaults['is_default'] = True

            PaymentMethod.objects.update_or_create(user_id=user.id, method_id=payment_method.stripe_id, defaults=defaults)

            return JsonResponse({'status': 200, 'success': True, 'message': 'Payment Complete'})

        except stripe.error.CardError as e:
            return JsonResponse({'status': 405, 'success': False, 'message': e.user_message})
        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})


def delete_card(user, method_id):
    try:
        if user.profile.user_permission != 'Administrator':
            return False

        if PaymentMethod.objects.filter(user_id=user.id).count() == 1:
            return False

        # stripe.Customer.delete_source(user.profile.stripe_customer_id, method_id)
        stripe.PaymentMethod.detach(method_id)

    except stripe.error.InvalidRequestError as e:
        return True
    except Exception as e:
        save_history(user, 'Critical', 'Delete Card', repr(e))
        return False

    return True


class CardTokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        address_zip = None
        try:
            data = request.data
            number = data['number']
            exp_month = int(data['exp_month'])
            exp_year = int(data['exp_year'])
            cvc = data['cvc']
            if 'address_zip' in data:
                address_zip = data['address_zip']
        except:
            number = '4242424242424242'  # Successful payment
            # number = '4000002760003184'  # Payment failed
            exp_month = 4
            exp_year = 2024
            cvc = '424'

        try:
            if address_zip:
                token = stripe.Token.create(
                    card={
                        'number': number,
                        'exp_month': exp_month,
                        'exp_year': exp_year,
                        'cvc': cvc,
                        'address_zip': address_zip
                    },
                )
            else:
                token = stripe.Token.create(
                    card={
                        'number': number,
                        'exp_month': exp_month,
                        'exp_year': exp_year,
                        'cvc': cvc,
                    },
                )

            return JsonResponse({'status': 200, 'success': True, 'data': token})

        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})
