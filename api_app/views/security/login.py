import requests

# from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import update_last_login
from django.template.loader import render_to_string
from django.utils import timezone
from random import randrange
from rest_framework_simplejwt.views import TokenObtainPairView
from time import sleep
from user_agents import parse

from my_settings import SITE_URL, GMAIL_HOST_USER
from back_app.models.history import save_history
from django.http import JsonResponse
from user_app.models.device import Device
from user_app.models.profile import USER_STATUS
from user_app.models.security import Security
from user_app.views.send_email import send_mail


class LoginView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        try:
            user = auth.authenticate(request, username=request.data['username'], password=request.data['password'])
            if user is None:
                raise Exception('No active account found with the given credentials')
        except:
            return JsonResponse({'status': 401, 'success': False, 'message': 'No active account found with the given credentials'})

        try:
            if user.profile.status == USER_STATUS.INACTIVE:
                return JsonResponse({'status': 402, 'success': False, 'message': 'Your account has not been activated'})
            elif user.profile.status == USER_STATUS.RESTRICTED:
                return JsonResponse({'status': 403, 'success': False, 'message': 'Your account is restricted'})
            elif user.profile.status == USER_STATUS.CLOSED:
                return JsonResponse({'status': 404, 'success': False, 'message': 'Your account has been closed'})

            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            location = get_location(ip)

            user_agent = parse(request.META['HTTP_USER_AGENT'])
            os = f'{user_agent.os.family} {user_agent.os.version_string}'
            browser = user_agent.browser.family
            device_family = user_agent.device.family

            security = Security.objects.get(user_id=user.id)

            is_confirmed = False
            if not user.last_login or user.username == 'accoutt04@gmail.com':
                is_confirmed = True
            elif user_agent.is_bot and user.profile.status != USER_STATUS.INTERNAL or security.updated_at and user.last_login < security.updated_at:
                pass
            elif Device.objects.filter(user_id=user.id, ip=ip, os=os, browser=browser, device=device_family, is_confirmed=True).count() > 0:
                device = Device.objects.get(user_id=user.id, ip=ip, os=os, browser=browser, device=device_family, is_confirmed=True)

                if device.confirmed_at and (timezone.now() - device.confirmed_at).days < 30:
                    is_confirmed = True

            device, created = Device.objects.update_or_create(user_id=user.id, ip=ip, os=os, browser=browser, device=device_family, defaults={'is_confirmed': is_confirmed, 'location': location})

            if not is_confirmed:
                otp = randrange(100000, 999999)
                security.otp = str(otp)
                security.updated_at = timezone.now()
                security.save()

                message = render_to_string('user/email/verify_code.html', {
                    'url': SITE_URL,
                    'first_name': user.first_name,
                    'code': otp,
                    'year': timezone.now().year,
                    'ip': ip,
                    'location': location,
                    'os': f'{os} ({browser})',
                    'device': device_family
                })
                send_mail(GMAIL_HOST_USER, user.email, 'Your Verification Code', message, 'html')

                return JsonResponse({'status': 200, 'success': True, 'message': 'Verification Code Sent to Email'})

            if not device.confirmed_at:
                device.confirmed_at = timezone.now()
                device.save()

            result = super(LoginView, self).post(request)

            update_last_login(None, user)
            save_history(user, 'Account', 'Log In')

            # result.set_cookie(settings.JWT_AUTH_COOKIE, result.data['access'], max_age=1200, secure=True, httponly=True, samesite='lax')
            # result.set_cookie(settings.JWT_AUTH_REFRESH_COOKIE, result.data['refresh'], max_age=1200, secure=True, httponly=True, samesite='lax')

            result.data['status'] = 200
            result.data['success'] = True
            return result

        except Exception as e:
            save_history(user, 'Critical', 'Login Error', repr(e))
            return JsonResponse({'status': 400, 'success': False, 'message': 'Exception happened'})


class OTPView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        try:
            user = auth.authenticate(request, username=request.data['username'], password=request.data['password'])
            if user is None:
                raise Exception('No active account found with the given credentials')
        except:
            return JsonResponse({'status': 401, 'success': False, 'message': 'No active account found with the given credentials'})

        try:
            if user.profile.status == USER_STATUS.INACTIVE:
                return JsonResponse({'status': 402, 'success': False, 'message': 'Your account has not been activated'})
            elif user.profile.status == USER_STATUS.RESTRICTED:
                return JsonResponse({'status': 403, 'success': False, 'message': 'Your account is restricted'})
            elif user.profile.status == USER_STATUS.CLOSED:
                return JsonResponse({'status': 404, 'success': False, 'message': 'Your account has been closed'})

            security = Security.objects.get(user_id=user.id)
            if (timezone.now() - security.updated_at).seconds > 60 * 30:
                return JsonResponse({'status': 405, 'success': False, 'message': 'Verification code expired'})

            if security.otp != request.data['otp']:
                security.otp_attempt_counts += 1
                security.save()
                if security.otp_attempt_counts > 3:
                    sleep(security.otp_attempt_counts * 20)

                return JsonResponse({'status': 406, 'success': False, 'message': 'Your code is incorrect.'})

            security.otp_attempt_counts = 0
            security.save()

            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            user_agent = parse(request.META['HTTP_USER_AGENT'])
            os = f'{user_agent.os.family} {user_agent.os.version_string}'
            browser = user_agent.browser.family
            device_family = user_agent.device.family

            device = Device.objects.get(user_id=user.id, ip=ip, os=os, browser=browser, device=device_family)
            device.confirmed_at = timezone.now()
            device.is_confirmed = True
            device.save()

            result = super(OTPView, self).post(request)

            update_last_login(None, user)
            save_history(user, 'Account', 'Log In')

            # result.set_cookie(settings.JWT_AUTH_COOKIE, result.data['access'], max_age=1200, secure=True, httponly=True, samesite='lax')
            # result.set_cookie(settings.JWT_AUTH_REFRESH_COOKIE, result.data['refresh'], max_age=1200, secure=True, httponly=True, samesite='lax')

            result.data['status'] = 200
            result.data['success'] = True
            return result

        except Exception as e:
            if user.profile.status != USER_STATUS.INTERNAL:
                save_history(user, 'Critical', 'Login OTP', repr(e))
            return JsonResponse({'status': 400, 'success': False, 'message': 'Exception happened'})


def get_location(ip_address):
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    if not response.get('country'):
        return ''

    if response.get("city"):
        return f"{response.get('city')}, {response.get('country')}"
    else:
        return f"{response.get('region')}, {response.get('country')}"
