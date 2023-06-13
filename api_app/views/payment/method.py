import stripe

from django.http import JsonResponse
from rest_framework.views import APIView

from my_settings import STRIPE
from api_app.models.payment_method import PaymentMethod
from api_app.views.payment.stripe_card import delete_card
from back_app.models.notification import save_notification

stripe.api_key = STRIPE['SECRET_KEY']


class PaymentMethodView(APIView):
    def get(self, request):
        try:
            data = []
            rows = PaymentMethod.objects.filter(user_id=request.user.id)
            for row in rows:
                if row.brand == 'PayPal' and not row.funding:
                    continue

                method = {}
                method['id'] = row.id
                method['methodId'] = row.method_id
                method['addressLine1'] = row.address_line1 if row.address_line1 else ''
                method['addressLine2'] = row.address_line2 if row.address_line2 else ''
                method['addressCity'] = row.address_city if row.address_city else ''
                method['addressState'] = row.address_state if row.address_state else ''
                method['addressCountry'] = row.address_country if row.address_country else ''
                method['addressZip'] = row.address_zip if row.address_zip else ''

                method['name'] = row.name if row.name else ''
                method['email'] = f"{row.email[:3]}*******{row.email[row.email.find('@'):]}" if row.email else ''
                method['brand'] = row.brand

                method['expMonth'] = row.exp_month if row.exp_month else ''
                method['expYear'] = row.exp_year if row.exp_year else ''
                method['funding'] = row.funding if row.brand != 'PayPal' else ''
                method['last4'] = row.last4 if row.last4 else ''

                method['isDefault'] = row.is_default

                data.append(method)

        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})

        return JsonResponse({'status': 200, 'success': True, 'message': 'Successfully Loaded', 'data': data})

    def delete(self, request):
        try:
            user = request.user
            data = request.data

            if PaymentMethod.objects.filter(user_id=user.id).count() == 1:
                return JsonResponse({'status': 402, 'success': False, 'message': "Can't delete the payment method. At least one payment method is required."})

            payment_method = PaymentMethod.objects.get(user_id=user.id, id=data['id'])
            if payment_method.brand != "PayPal":
                payment_name = f'{payment_method.brand.capitalize()} **** {payment_method.last4}'
                if delete_card(user, payment_method.method_id):
                    payment_method.delete()
            else:
                payment_name = f"PayPal {payment_method.email[:3]}*******{payment_method.email[payment_method.email.find('@'):]}"
                payment_method.delete()

            save_notification(user, 'Payment', f'Deleted Payment Method. {payment_name}')

        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})

        return JsonResponse({'status': 200, 'success': True, 'message': 'Successfully Deleted'})
