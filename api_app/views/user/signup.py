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
            business_name = data['businessName']
            business_type = data['businessType']
            partner_code = data.get('partnerCode') if data.get('partnerCode') else ''
        except:
            return JsonResponse({'status': 401, 'success': False, 'message': 'Parameter Error'})

        try:
            validate_email(email)
        except:
            return JsonResponse({'status': 402, 'success': False, 'message': 'Email is not valid'})

        if User.objects.filter(username=username, profile__status__gt=0).exists():
            return JsonResponse({'status': 403, 'success': False, 'message': 'Email Already in Use with Sharp Archive'})

        if partner_code and not Partner.objects.filter(code=partner_code).exists():
            return JsonResponse({'status': 404, 'success': False, 'message': 'Partner Code Error'})

        try:
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                user.first_name = first_name
                user.last_name = last_name
                user.password = make_password(password)

                profile = user.profile
                security = Security.objects.get(user_id=user.id)
            else:
                user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name,
                                                is_active=0)

                profile = Profile.objects.create(id=user.id, user_id=user.id)
                security = Security.objects.create(id=user.id, user_id=user.id)

            profile.business_name = business_name
            profile.business_type = business_type
            profile.two_factor = 2
            profile.save()

            email_code = random.randrange(100000, 999999)
            security.otp = str(email_code)
            security.updated_at = timezone.now()
            security.save()

            message = render_to_string('user/email/verify_code.html', {
                'url': SITE_URL,
                'first_name': first_name,
                'code': email_code,
                'year': timezone.now().year
            })

            send_mail(GMAIL_HOST_USER, user.email, 'Your Verification Code', message, 'html')

            if partner_code:
                partner_id = User.objects.get(username=Partner.objects.get(code=partner_code).email).id
                Meta.objects.update_or_create(user_id=user.id, meta_key='partner_id', defaults={'meta_value': str(partner_id)})

            data = {}
            data['id'] = user.id
            data['firstName'] = user.first_name
            data['lastName'] = user.last_name
            data['email'] = user.email
            data['businessName'] = user.profile.business_name
            data['businessType'] = user.profile.business_type

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


class SavePhoneView(APIView):
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
                if not user or not user.check_password(request.data['password']):
                    return JsonResponse({'status': 402, 'success': False, 'message': 'Email or password is incorrect'})
            except User.DoesNotExist:
                return JsonResponse({'status': 403, 'success': False, 'message': 'User does not exist'})

        try:
            phone = request.data['phone']
            # phone = phonenumbers.format_number(phonenumbers.parse(phone, 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
            phone = phonenumbers.format_number(phonenumbers.parse(phone), phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        except:
            return JsonResponse({'status': 404, 'success': False, 'message': 'Phone Number is not valid'})

        try:
            profile = user.profile
            if profile.status == USER_STATUS.RESTRICTED:
                return JsonResponse({'status': 405, 'success': False, 'message': 'Your account is restricted'})

            defaults = {
                'user_id': user.id,
                'meta_key': 'phone',
                'meta_value': phone
            }
            Meta.objects.update_or_create(user_id=user.id, meta_key='phone', defaults=defaults)

            security = Security.objects.get(user_id=user.id)
            if security.sms_counts >= 5:
                profile.status = USER_STATUS.RESTRICTED
                profile.save()
                return JsonResponse({'status': 406, 'success': False, 'message': 'Your account is restricted'})

            security.sms_counts += 1
            security.save()

            if TWILIO.get('ACCOUNT_SID'):
                verify = Client(TWILIO['ACCOUNT_SID'], TWILIO['AUTH_TOKEN']).verify.v2.services(TWILIO['VERIFY_SID'])
                try:
                    verify.verifications.create(to=phone, channel='sms')
                except:
                    return JsonResponse({'status': 407, 'success': False, 'message': "Can't send SMS to your phone number"})
            else:
                phone_code = random.randrange(100000, 999999)
                security.otp = str(phone_code)
                security.updated_at = timezone.now()
                security.save()
                sdk = SDK(RINGCENTRAL['CLIENT_ID'], RINGCENTRAL['CLIENT_SECRET'], RINGCENTRAL['URL'])
                platform = sdk.platform()
                platform.login(RINGCENTRAL['PHONE_NUMBER'], RINGCENTRAL['EXTENSION'], RINGCENTRAL['PASSWORD'])
                builder = sdk.create_multipart_builder()

                builder.set_body({
                    'from': {'phoneNumber': RINGCENTRAL['PHONE_NUMBER']},
                    'to': [{'phoneNumber': phone}],
                    'text': f'Your Sharp Archive verification code is: {phone_code}.'
                })
                request = builder.request('/account/~/extension/~/sms')
                response = platform.send_request(request)

            return JsonResponse({'status': 200, 'success': True, 'message': 'Verification Code Sent to Phone'})

        except:
            return JsonResponse({'status': 400, 'success': False, 'message': 'Exception happened'})


class SendSMSView(APIView):
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
                if not user or not user.check_password(request.data['password']):
                    return JsonResponse({'status': 402, 'success': False, 'message': 'Email or password is incorrect'})
            except User.DoesNotExist:
                return JsonResponse({'status': 403, 'success': False, 'message': 'User does not exist'})

        if user.profile.status == USER_STATUS.RESTRICTED:
            return JsonResponse({'status': 404, 'success': False, 'message': 'Your account is restricted'})

        try:
            phone = Meta.objects.get(user_id=user.id, meta_key='phone').meta_value
        except:
            return JsonResponse({'status': 405, 'success': False, 'message': 'You have not registered your phone number'})

        try:
            security = Security.objects.get(user_id=user.id)
            if security.sms_counts >= 5:
                user.profile.status = USER_STATUS.RESTRICTED
                user.profile.save()
                return JsonResponse({'status': 406, 'success': False, 'message': 'Your account is restricted'})

            security.sms_counts += 1
            security.save()

            if TWILIO.get('ACCOUNT_SID'):
                verify = Client(TWILIO['ACCOUNT_SID'], TWILIO['AUTH_TOKEN']).verify.v2.services(TWILIO['VERIFY_SID'])
                try:
                    verify.verifications.create(to=phone, channel='sms')
                except:
                    return JsonResponse({'status': 407, 'success': False, 'message': "Can't send SMS to your phone number"})

            else:
                phone_code = random.randrange(100000, 999999)
                security.otp = str(phone_code)
                security.updated_at = timezone.now()
                security.save()
                sdk = SDK(RINGCENTRAL['CLIENT_ID'], RINGCENTRAL['CLIENT_SECRET'], RINGCENTRAL['URL'])
                platform = sdk.platform()
                platform.login(RINGCENTRAL['PHONE_NUMBER'], RINGCENTRAL['EXTENSION'], RINGCENTRAL['PASSWORD'])
                builder = sdk.create_multipart_builder()

                builder.set_body({
                    'from': {'phoneNumber': RINGCENTRAL['PHONE_NUMBER']},
                    'to': [{'phoneNumber': phone}],
                    'text': f'Your Sharp Archive verification code is: {phone_code}.'
                })
                request = builder.request('/account/~/extension/~/sms')
                response = platform.send_request(request)

            return JsonResponse({'status': 200, 'success': True, 'message': 'New Code Sent'})

        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})


class VerifyPhoneView(APIView):
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

            is_anonymous = True
        else:
            is_anonymous = False

        if user.profile.status == USER_STATUS.RESTRICTED:
            return JsonResponse({'status': 403, 'success': False, 'message': 'Your account is restricted'})

        try:
            phone = Meta.objects.get(user_id=user.id, meta_key='phone').meta_value
        except:
            return JsonResponse({'status': 404, 'success': False, 'message': 'You have not registered your phone number'})

        security = Security.objects.get(user_id=user.id)
        try:
            if TWILIO.get('ACCOUNT_SID'):
                verify = Client(TWILIO['ACCOUNT_SID'], TWILIO['AUTH_TOKEN']).verify.v2.services(TWILIO['VERIFY_SID'])
                verification_check = verify.verification_checks.create(to=phone, code=request.data['otp'])
                if verification_check.status != 'approved':
                    raise Exception('pending')
            else:
                if (timezone.now() - security.updated_at).seconds > 60 * 30:
                    return JsonResponse({'status': 405, 'message': 'Verification code expired'})

                if security.otp != request.data['otp']:
                    raise Exception('wrong')

            security.sms_counts = 0
            security.otp_attempt_counts = 0
            security.save()
        except:
            security.otp_attempt_counts += 1
            security.save()
            if security.otp_attempt_counts > 3:
                sleep(security.otp_attempt_counts * 20)

            return JsonResponse({'status': 406, 'success': False, 'message': 'Your code is incorrect.'})

        try:
            if is_anonymous:
                user.is_active = 1
                user.save()
                user.profile.status = USER_STATUS.VERIFIED

            user.profile.phone = phone
            user.profile.save()

            if not is_anonymous:
                return JsonResponse({'status': 200, 'success': True, 'message': 'Phone Verified'})

            message = render_to_string('user/email/signup.html', {
                'url': SITE_URL,
                'first_name': user.first_name.title(),
                'year': timezone.now().year
            })

            send_mail(GMAIL_HOST_USER, user.email, 'Welcome to Sharp Archive', message, 'html')

            refresh = RefreshToken.for_user(user)

            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }

            return JsonResponse({'status': 200, 'success': True, 'message': 'Phone Verified', 'data': data})

        except:
            return JsonResponse({'status': 400, 'success': False, 'message': 'Exception happened'})
