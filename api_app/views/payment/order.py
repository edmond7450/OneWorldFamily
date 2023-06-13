import googlemaps
import json

from django.http import JsonResponse
from django.utils import timezone
from rest_framework.views import APIView

from my_settings import GOOGLE_GEOCODING_API_KEY
from api_app.models.invoice import Invoice
from api_app.views.payment.invoice import get_invoice_data, create_invoice
from back_app.models.notification import save_notification
from user_app.models.coupon import Coupon


class OrderView(APIView):
    def post(self, request):
        try:
            user = request.user
            data = request.data
            if 'code' not in data:
                return JsonResponse({'status': 401, 'success': False, 'message': 'Parameter Error'})

            if not Coupon.objects.filter(coupon_code=data['code'], months=-1, user_id=None).exists():
                return JsonResponse({'status': 402, 'success': False, 'message': 'Parameter Error'})

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

            profile = user.profile
            if not profile.address:
                profile.address = data['address']
                profile.address_components = json.dumps({'street_number': street_number, 'route': route, 'city': city, 'state': state, 'country': country, 'postal_code': postal_code})

            started_at = timezone.now()
            profile.membership_date = started_at.date()
            profile.payment_status = 'ordered'
            profile.save()

            coupon = Coupon.objects.get(coupon_code=data['code'], months=-1, user_id=None)
            coupon.user_id = user.id
            coupon.started_at = started_at
            coupon.save()

            send_due_invoice(user, profile.membership_date)

            save_notification(user, 'Payment', f'Your order cycle starts on the {profile.membership_date.day}th of each month.')

            return JsonResponse({'status': 200, 'success': True, 'message': 'Success'})

        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})


def send_due_invoice(user, current_date):
    invoice_data = get_invoice_data(user)
    subtotal = float(invoice_data['subtotal'])

    address_components = {}
    if user.profile.address_components:
        address_components = json.loads(user.profile.address_components)

    billing_details = {
        'name': user.get_full_name(),
        'address': {
            'line1': (address_components['street_number'] + ' ' + address_components['route']) if address_components else '',
            'line2': '',
            'city': address_components['city'] if address_components else '',
            'state': address_components['state'] if address_components else '',
            'postal_code': address_components['postal_code'] if address_components else '',
            'country': address_components['country'] if address_components else ''
        }
    }

    invoice_number, invoice_path = create_invoice(user.id, subtotal, 0, current_date, billing_details, is_due=True)

    Invoice.objects.create(invoice_number=invoice_number, invoice_path=invoice_path, subtotal=0, tax=0, total=0, fee=0, net=0,
                           description='{0:,.2f}'.format(subtotal), stripe_payment_intent_id='', stripe_invoice_id='', user_id=user.id)


def send_monthly_invoice(user, current_date):
    invoice_data = get_invoice_data(user)
    subtotal = float(invoice_data['subtotal'])

    address_components = {}
    if user.profile.address_components:
        address_components = json.loads(user.profile.address_components)

    billing_details = {
        'name': user.get_full_name(),
        'address': {
            'line1': (address_components['street_number'] + ' ' + address_components['route']) if address_components else '',
            'line2': '',
            'city': address_components['city'] if address_components else '',
            'state': address_components['state'] if address_components else '',
            'postal_code': address_components['postal_code'] if address_components else '',
            'country': address_components['country'] if address_components else ''
        }
    }

    invoice_number, invoice_path = create_invoice(user.id, subtotal, 0, current_date, billing_details)

    Invoice.objects.create(invoice_number=invoice_number, invoice_path=invoice_path, subtotal=0, tax=0, total=0, fee=0, net=0,
                           description='{0:,.2f}'.format(subtotal), stripe_payment_intent_id='', stripe_invoice_id='', user_id=user.id)
