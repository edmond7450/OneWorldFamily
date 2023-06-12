import os.path
import phonenumbers
import stripe

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from PIL import Image
from rest_framework.views import APIView

from my_settings import SITE_URL, GMAIL_HOST_USER, STRIPE
from user_app.models.profile import USER_STATUS, Profile
from user_app.views.send_email import send_mail

stripe.api_key = STRIPE['SECRET_KEY']


class ProfileView(APIView):
    def get(self, request):
        try:
            user = request.user
            profile = user.profile
            data = {}
            data['id'] = user.id
            data['firstName'] = user.first_name
            data['lastName'] = user.last_name
            data['email'] = user.email
            data['dateJoined'] = user.date_joined.strftime('%Y-%m-%dT%H:%M:%SZ')
            data['gender'] = profile.gender
            data['phone'] = profile.phone
            data['address'] = profile.address
            if profile.avatar:
                data['avatar'] = 'https://' + request.get_host() + profile.avatar.url
            else:
                data['avatar'] = ''
            data['paymentStatus'] = profile.payment_status
            data['closeAccountInfo'] = profile.close_account_info if profile.close_account_info else ''

            data['isOwner'] = profile.is_owner
            data['userPermission'] = profile.user_permission

        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})

        return JsonResponse({'status': 200, 'success': True, 'message': 'Successfully Loaded', 'data': data})

    def put(self, request):
        try:
            user = request.user
            profile = user.profile
            data = request.data

            try:
                phone = data['phone']
                phone = phonenumbers.format_number(phonenumbers.parse(phone), phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            except:
                return JsonResponse({'status': 401, 'success': False, 'message': 'Phone Number is not valid'})

            user.first_name = data['firstName']
            user.last_name = data['lastName']
            profile.gender = data['gender']
            profile.phone = phone
            profile.address = data['address']

            if request.FILES and request.FILES['avatar']:
                if request.FILES['avatar'].content_type == 'image/jpeg' or request.FILES['avatar'].content_type == 'image/png':
                    try:
                        im = Image.open(request.FILES['avatar'].file)
                        im.verify()
                    except:
                        return JsonResponse({'status': 402, 'success': False, 'message': 'Invalid image'})

                request.FILES['avatar'].name = str(user.id) + os.path.splitext(request.FILES['avatar'].name)[1].lower()
                profile.avatar = request.FILES['avatar']

            elif 'avatar_remove' in data and data['avatar_remove'] == '1':
                profile.avatar = ''

            profile.save()
            user.save()

            data = {}
            data['id'] = user.id
            data['firstName'] = user.first_name
            data['lastName'] = user.last_name
            data['email'] = user.email
            data['dateJoined'] = user.date_joined.strftime('%Y-%m-%dT%H:%M:%SZ')
            data['gender'] = profile.gender
            data['phone'] = profile.phone
            data['address'] = profile.address
            if profile.avatar:
                data['avatar'] = 'https://' + request.get_host() + profile.avatar.url
            else:
                data['avatar'] = ''
            data['closeAccountInfo'] = profile.close_account_info if profile.close_account_info else ''

        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})

        return JsonResponse({'status': 200, 'success': True, 'message': 'Successfully Saved', 'data': data})

    def delete(self, request):
        try:
            user = request.user
            user.is_active = 0
            user.save()

            now = timezone.now()
            profile = user.profile
            profile.status = USER_STATUS.CLOSED
            profile.close_account_info = now
            profile.save()

            if not user.profile.is_owner:
                return JsonResponse({'status': 200, 'success': True, 'message': 'Account Successfully Closed'})

            Profile.objects.filter(owner=user, user__is_active=1).update(close_account_info=now, status=USER_STATUS.CLOSED)
            User.objects.filter(is_active=1, profile__owner=user).update(is_active=0)

            message = render_to_string('user/email/close.html', {
                'url': SITE_URL,
                'first_name': user.first_name.title(),
                'year': timezone.now().year
            })

            send_mail(GMAIL_HOST_USER, user.email, 'Account Closed', message, 'html')

        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})

        return JsonResponse({'status': 200, 'success': True, 'message': 'Account Successfully Closed'})


class CheckPasswordView(APIView):
    def post(self, request):
        user = request.user
        try:
            if not user or not user.check_password(request.data['password']):
                return JsonResponse({'status': 401, 'success': False, 'message': 'Your password is incorrect'})

            return JsonResponse({'status': 200, 'success': True, 'message': 'Password Confirmed'})

        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})
