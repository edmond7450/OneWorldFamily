import phonenumbers
import random

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from time import sleep
from ringcentral import SDK
from twilio.rest import Client

from my_settings import ENVIRONMENT, SITE_URL, GMAIL_HOST_USER, TWILIO, RINGCENTRAL
from user_app.models.meta import Meta
from user_app.models.partner import Partner
from user_app.models.profile import Profile, USER_STATUS
from user_app.models.security import Security
from user_app.views.send_email import send_mail


class CheckEmailView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            validate_email(request.data['email'])
        except:
            return JsonResponse({'status': 401, 'success': False, 'message': 'Email is not valid'})

        if User.objects.filter(username=request.data['email'], profile__status__gt=0).exists():
            return JsonResponse({'status': 402, 'success': False, 'message': 'Email Already in Use with Sharp Archive'})
        else:
            return JsonResponse({'status': 200, 'success': True, 'message': 'Successfully Checked'})


class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            data = request.data
            username = data['email']
            email = data['email']
            password = data['password']
            first_name = data['firstName']
            last_name = data['lastName']
            invitation_code = data.get('invitationCode') if data.get('invitationCode') else ''
        except:
            return JsonResponse({'status': 401, 'success': False, 'message': 'Parameter Error'})

        try:
            validate_email(email)
        except:
            return JsonResponse({'status': 402, 'success': False, 'message': 'Email is not valid'})

        if User.objects.filter(username=username, profile__status__gt=0).exists():
            return JsonResponse({'status': 403, 'success': False, 'message': 'Email Already in Use with Sharp Archive'})

        if invitation_code and not Partner.objects.filter(code=invitation_code).exists():
            return JsonResponse({'status': 404, 'success': False, 'message': 'Partner Code Error'})

        try:
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                user.first_name = first_name
                user.last_name = last_name
                user.password = make_password(password)

                profile = user.profile
            else:
                user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name, is_active=0)

                profile = Profile.objects.create(id=user.id, user_id=user.id)
                Security.objects.create(id=user.id, user_id=user.id)

            profile.two_factor = 2
            profile.save()

            if invitation_code:
                partner_id = User.objects.get(username=Partner.objects.get(code=invitation_code).email).id
                Meta.objects.update_or_create(user_id=user.id, meta_key='partner_id', defaults={'meta_value': str(partner_id)})

            data = {}
            data['id'] = user.id
            data['firstName'] = user.first_name
            data['lastName'] = user.last_name
            data['email'] = user.email

            return JsonResponse({'status': 200, 'success': True, 'message': 'Account Successfully Created', 'data': data})
        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})


class SendEmailView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        user = request.user
        if user.is_anonymous:
            try:
                email = request.data['email']
                validate_email(email)
            except:
                return JsonResponse({'status': 400, 'success': False, 'message': 'Email is not valid'})

            try:
                user = User.objects.get(email=email)
                if not user or not user.check_password(request.data['password']):
                    return JsonResponse({'status': 401, 'success': False, 'message': 'Email or password is incorrect'})
            except User.DoesNotExist:
                return JsonResponse({'status': 402, 'success': False, 'message': 'User does not exist'})

        try:
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
        except User.DoesNotExist:
            return JsonResponse({'status': 403, 'success': False, 'message': 'User does not exist'})
        except Exception as e:
            return JsonResponse({'status': 404, 'success': False, 'message': repr(e)})


class VerifyEmailView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        user = request.user
        if user.is_anonymous:
            try:
                email = request.data['email']
                validate_email(email)
            except:
                return JsonResponse({'status': 400, 'success': False, 'message': 'Email is not valid'})

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({'status': 401, 'success': False, 'message': 'User does not exist'})

        try:
            security = Security.objects.get(user_id=user.id)
            if (timezone.now() - security.updated_at).seconds > 60 * 30:
                return JsonResponse({'status': 402, 'success': False, 'message': 'Verification code expired'})

            if security.otp == request.data['otp']:
                security.otp_attempt_counts = 0
                security.save()
                return JsonResponse({'status': 200, 'success': True, 'message': 'Email Verified'})

            security.otp_attempt_counts += 1
            security.save()
            if security.otp_attempt_counts > 3:
                sleep(security.otp_attempt_counts * 20)

            return JsonResponse({'status': 403, 'success': False, 'message': 'Your code is incorrect.'})

        except:
            return JsonResponse({'status': 404, 'success': False, 'message': 'Exception happened'})
