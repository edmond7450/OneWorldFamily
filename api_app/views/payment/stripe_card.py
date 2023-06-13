import googlemaps
import json
import stripe

from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from stripe import error

from my_settings import ENVIRONMENT, GOOGLE_GEOCODING_API_KEY, STRIPE
from api_app.models.api_meta import API_Meta
from api_app.models.invoice import Invoice
from api_app.models.payment_method import PaymentMethod
from api_app.views.payment.invoice import create_invoice
from back_app.models.history import save_history
from back_app.models.notification import save_notification
from user_app.models.coupon import Coupon

stripe.api_key = STRIPE['SECRET_KEY']


class CardView(APIView):
    def get(self, request):
        try:
            user = request.user
            profile = user.profile

            if not profile.stripe_customer_id:
                return JsonResponse({'status': 200, 'success': True, 'message': 'Successfully Loaded', 'data': []})

            cards = stripe.Customer.list_payment_methods(profile.stripe_customer_id, type='card', limit=100)

            data = []
            for payment_method in cards.data:
                defaults = {}
                defaults['method_id'] = payment_method.id
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

                PaymentMethod.objects.update_or_create(user_id=user.id, method_id=payment_method.stripe_id, defaults=defaults)

                data.append(defaults)

        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})

        return JsonResponse({'status': 200, 'success': True, 'message': 'Successfully Loaded', 'data': data})

    def post(self, request):
        if ENVIRONMENT == 'demo':
            return JsonResponse({'status': 200, 'success': True, 'message': 'Demo Version'})

        try:
            user = request.user
            data = request.data
            if 'coupon' in data:
                if not Coupon.objects.filter(coupon_code=data['coupon'], user_id=None).exists():
                    return JsonResponse({'status': 402, 'success': False, 'message': 'Invalid Coupon'})

            if 'address' not in data:
                return JsonResponse({'status': 403, 'success': False, 'message': 'Billing Address is required'})

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
                    return JsonResponse({'status': 404, 'success': False, 'message': 'Billing Address is invalid'})

                addresses = geocode_result[0]['formatted_address'].split(', ')
            except:
                return JsonResponse({'status': 405, 'success': False, 'message': 'Billing Address is invalid'})

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
                    metadata={'user_id': user.id, 'phone': profile.phone, 'environment': ENVIRONMENT},
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

            is_default = True if 'isDefault' in data and data['isDefault'] in ['True', 'true', 'T', 't', 1, '1', 'yes', 'y'] else False
            if is_default or not customer.invoice_settings.default_payment_method:
                stripe.Customer.modify(
                    stripe_customer_id,
                    invoice_settings={'default_payment_method': payment_method.stripe_id}
                )
                is_default = True

            if profile.membership_date:
                message = 'Successfully Added'
                if profile.payment_status != 'paid' and profile.payment_status != 'trial' and profile.payment_status != 'INTERNAL':
                    save_history(user, 'Critical', 'NewCard PaymentStatus', profile.payment_status)
            else:
                now = timezone.now()
                if 'coupon' in data:
                    coupon = Coupon.objects.get(coupon_code=data['coupon'], user_id=None)
                    coupon.user_id = user.id
                    coupon.started_at = now
                    coupon.save()

                    profile.membership_date = now.date()
                    profile.payment_status = 'trial'
                    profile.save()

                    trial_end = now + relativedelta(months=coupon.months)
                    save_notification(user, 'Payment', f"Trial ends {trial_end.strftime('%b %#d, %Y')}")

                    message = 'Trial Started'
                else:
                    cost_value = json.loads(API_Meta.objects.get(meta_key='estimated-cost').meta_value)
                    base_cost = cost_value['baseCost'] * 100

                    try:
                        payment_intent = stripe.PaymentIntent.create(
                            amount=base_cost,
                            currency='usd',
                            customer=stripe_customer_id,
                            payment_method=payment_method.stripe_id,
                            off_session=True,
                            confirm=True,
                        )
                        if payment_intent.amount_received != base_cost:
                            save_history(user, 'Critical', 'Stripe Payment', f'Different amount received: {payment_intent.amount_received}/{base_cost}')
                    except stripe.error.CardError as e:
                        stripe.PaymentMethod.detach(payment_method.stripe_id)
                        return JsonResponse({'status': 406, 'success': False, 'message': e.user_message})

                    profile.membership_date = now.date()
                    profile.payment_status = 'paid'
                    profile.save()
                    save_notification(user, 'Payment', f'Your payment cycle starts on the {profile.membership_date.day}th of each month.')

                    subtotal = payment_intent.amount_received / 100
                    fee = round(subtotal * 0.029 + 0.3, 2)
                    net = round(subtotal - fee, 2)

                    invoice_number, invoice_path = create_invoice(user.id, subtotal, 0, profile.membership_date, payment_method.billing_details)

                    Invoice.objects.create(invoice_number=invoice_number, invoice_path=invoice_path, subtotal=subtotal, tax=0, total=subtotal, fee=fee, net=net,
                                           stripe_payment_intent_id=payment_method.stripe_id, stripe_invoice_id=payment_intent.id, user_id=user.id)

                    message = 'Payment Complete'

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
            defaults['is_default'] = is_default

            if is_default:
                PaymentMethod.objects.filter(user_id=user.id, is_default=True).update(is_default=False)
            PaymentMethod.objects.update_or_create(user_id=user.id, method_id=payment_method.stripe_id, defaults=defaults)

            return JsonResponse({'status': 200, 'success': True, 'message': message})

        except stripe.error.CardError as e:
            return JsonResponse({'status': 400, 'success': False, 'message': e.user_message})
        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})

    def put(self, request):
        if ENVIRONMENT == 'demo':
            return JsonResponse({'status': 200, 'success': True, 'message': 'Demo Version'})

        try:
            user = request.user
            data = request.data

            if data['addressLine2']:
                address = f"{data['addressLine1']} #{data['addressLine2']}, {data['addressCity']}, {data['addressState']}, {data['addressCountry']}"
            else:
                address = f"{data['addressLine1']}, {data['addressCity']}, {data['addressState']}, {data['addressCountry']}"

            country = postal_code = ''
            gmaps = googlemaps.Client(key=GOOGLE_GEOCODING_API_KEY)
            geocode_result = gmaps.geocode(address)

            for component in geocode_result[0]['address_components']:
                for j in component['types']:
                    if j == 'country':
                        country = component['short_name']
                    elif j == 'postal_code':
                        postal_code = component['short_name']

            if not postal_code or postal_code != data['addressZip']:
                return JsonResponse({'status': 402, 'success': False, 'message': 'Address is not valid'})

            payment_method = stripe.PaymentMethod.modify(
                data['methodId'],
                billing_details={
                    'name': data['name'],
                    'address': {'line1': data['addressLine1'], 'line2': data['addressLine2'], 'city': data['addressCity'], 'state': data['addressState'], 'country': country, 'postal_code': data['addressZip']}
                },
                card={
                    'exp_month': data['expMonth'],
                    'exp_year': data['expYear']
                }
            )

            is_default = True if data['isDefault'] in ['True', 'true', 'T', 't', 1, '1', 'yes', 'y'] else False
            customer = stripe.Customer.retrieve(user.profile.stripe_customer_id)
            if is_default or not customer.invoice_settings.default_payment_method:
                customer = stripe.Customer.modify(
                    user.profile.stripe_customer_id,
                    invoice_settings={'default_payment_method': payment_method.stripe_id}
                )

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

            if is_default:
                defaults['is_default'] = is_default
                PaymentMethod.objects.filter(user_id=user.id, is_default=True).update(is_default=False)
            method, created = PaymentMethod.objects.update_or_create(user_id=user.id, id=data['id'], method_id=payment_method.stripe_id, defaults=defaults)

            data = {}
            data['id'] = method.id
            data['methodId'] = method.method_id
            data['addressLine1'] = method.address_line1
            data['addressLine2'] = method.address_line2 if method.address_line2 else ''
            data['addressCity'] = method.address_city
            data['addressState'] = method.address_state
            data['addressCountry'] = method.address_country
            data['addressZip'] = method.address_zip
            data['name'] = method.name
            data['email'] = method.email if method.email else ''
            data['brand'] = method.brand
            data['expMonth'] = method.exp_month
            data['expYear'] = method.exp_year
            data['funding'] = method.funding
            data['last4'] = method.last4
            data['isDefault'] = method.is_default

        except error.CardError as e:
            return JsonResponse({'status': 403, 'success': False, 'message': e._message})
        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})

        return JsonResponse({'status': 200, 'success': True, 'message': 'Successfully Saved', 'data': data})


def delete_card(user, method_id):
    if ENVIRONMENT == 'demo':
        return False

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
