import random

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import JsonResponse
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from time import sleep

from my_settings import SITE_URL, GMAIL_HOST_USER
from back_app.models.history import save_history
from user_app.models.security import Security
from user_app.views.send_email import send_mail


class ForgotView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            email = request.data['email']
            validate_email(email)
        except:
            return JsonResponse({'status': 402, 'success': False, 'message': 'Email is not valid'})

        try:
            if not User.objects.filter(email=email).exists():
                return JsonResponse({'status': 402, 'success': False, 'message': 'User does not exist'})

            user = User.objects.get(email=email)

            email_code = random.randrange(100000, 999999)
            security = Security.objects.get(user_id=user.id)
            security.otp = str(email_code)
            security.updated_at = timezone.now()
            security.save()

            message = render_to_string('user/email/verify_code.html', {
                'url': SITE_URL,
                'first_name': user.first_name,
                'code': email_code,
                'year': timezone.now().year
            })

            send_mail(GMAIL_HOST_USER, user.email, 'Your Verification Code', message, 'html')

            return JsonResponse({'status': 200, 'success': True, 'message': 'Verification Code Sent to Email'})

        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})


class ResetView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        user = request.user
        if user.is_anonymous:
            try:
                email = request.data['email']
                validate_email(email)
            except:
                return JsonResponse({'status': 401, 'success': False, 'message': 'Email is not valid'})

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({'status': 402, 'success': False, 'message': 'User does not exist'})

        try:
            security = Security.objects.get(user_id=user.id)
            if (timezone.now() - security.updated_at).seconds > 60 * 30:
                return JsonResponse({'status': 403, 'success': False, 'message': 'Verification code expired'})

            password = request.data['password']
            if security.otp != request.data['otp']:
                security.otp_attempt_counts += 1
                security.save()
                if security.otp_attempt_counts > 3:
                    sleep(security.otp_attempt_counts * 20)

                return JsonResponse({'status': 402, 'success': False, 'message': 'Your code is incorrect.'})

            otp = random.randrange(100000, 999999)
            security.otp = str(otp)
            security.updated_at = timezone.now()
            security.save()

            user.password = make_password(password)
            user.save()
            save_history(user, 'Security', 'Password Reset')

            message = render_to_string('user/email/password_changed.html', {
                'url': SITE_URL,
                'first_name': user.first_name.title(),
                'email': user.email,
                'year': timezone.now().year
            })

            send_mail(GMAIL_HOST_USER, user.email, 'Your Sharp Archive Account Password Changed', message, 'html')

            return JsonResponse({'status': 200, 'message': 'Password Updated'})

        except Exception as e:
            return JsonResponse({'status': 400, 'message': repr(e)})


class CheckView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            uid = force_str(urlsafe_base64_decode(request.data['uid']))
            user = User.objects.get(pk=uid)

            if PasswordResetTokenGenerator().check_token(user, request.data['token']):
                return JsonResponse({'status': 200, 'success': True, 'message': 'success'})

            return JsonResponse({'status': 401, 'success': False, 'message': 'Invalid Token'})

        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})


class NewSetView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            uid = force_str(urlsafe_base64_decode(request.data['uid']))
            user = User.objects.get(pk=uid)

            if not PasswordResetTokenGenerator().check_token(user, request.data['token']):
                return JsonResponse({'status': 401, 'success': False, 'message': 'Invalid Token'})

            email = request.data['email']
            password = request.data['password']
            if user.email != email:
                return JsonResponse({'status': 402, 'success': False, 'message': 'Your email is incorrect.'})

            user.password = make_password(password)
            user.save()
            save_history(user, 'Security', 'New Password Set')

            return JsonResponse({'status': 200, 'message': 'Password has been set'})

        except Exception as e:
            return JsonResponse({'status': 400, 'message': repr(e)})
