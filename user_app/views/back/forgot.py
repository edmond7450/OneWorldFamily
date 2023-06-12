from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils import timezone
from django.views import View
from time import sleep
from twilio.rest import Client

from my_settings import SITE_URL, GMAIL_HOST_USER, TWILIO
from user_app.models.profile import USER_STATUS
from user_app.models.security import Security
from user_app.views.send_email import send_mail


class ForgotView(View):
    template_name = 'user/back/forgot.html'

    def get(self, request):
        return render(request, self.template_name)


def clean(request):
    if request.method == 'POST':
        try:
            try:
                validate_email(request.POST['email'])
            except:
                return JsonResponse({'status': 401, 'message': 'Email is not valid'})

            if User.objects.filter(username=request.POST['email']).exists():
                user = User.objects.get(username=request.POST['email'])

                if user.profile.status == USER_STATUS.RESTRICTED:
                    return JsonResponse({'status': 402, 'success': False, 'message': 'Your account is restricted'})

                security = Security.objects.get(user_id=user.id)
                if security.sms_counts >= 5:
                    user.profile.status = USER_STATUS.RESTRICTED
                    user.profile.save()
                    return JsonResponse({'status': 403, 'success': False, 'message': 'Your account is restricted'})

                security.sms_counts += 1
                security.save()

                verify = Client(TWILIO['ACCOUNT_SID'], TWILIO['AUTH_TOKEN']).verify.services(TWILIO['VERIFY_SID'])
                try:
                    verify.verifications.create(to=user.profile.phone, channel='sms')
                except:
                    return JsonResponse({'status': 404, 'success': False, 'message': "Can't send SMS to your phone number"})

                return JsonResponse({'status': 200, 'message': 'success', 'phone': user.profile.phone[-2:]})
            else:
                return JsonResponse({'status': 405, 'message': "We can't find a user with that e-mail address."})

        except Exception as e:
            return JsonResponse({'status': 400, 'message': str(e)})


def send_otp(request):
    try:
        if User.objects.filter(username=request.POST['email']).exists():
            user = User.objects.get(username=request.POST['email'])

            if user.profile.status == USER_STATUS.RESTRICTED:
                return JsonResponse({'status': 401, 'success': False, 'message': 'Your account is restricted'})

            security = Security.objects.get(user_id=user.id)
            if security.sms_counts >= 5:
                user.profile.status = USER_STATUS.RESTRICTED
                user.profile.save()
                return JsonResponse({'status': 402, 'success': False, 'message': 'Your account is restricted'})

            security.sms_counts += 1
            security.save()

            verify = Client(TWILIO['ACCOUNT_SID'], TWILIO['AUTH_TOKEN']).verify.services(TWILIO['VERIFY_SID'])
            try:
                verify.verifications.create(to=user.profile.phone, channel='sms')
            except:
                return JsonResponse({'status': 403, 'success': False, 'message': "Can't send SMS to your phone number"})

            return JsonResponse({'status': 200, 'message': 'success'})
        else:
            return JsonResponse({'status': 404, 'message': "We can't find a user with that e-mail address."})

    except Exception as e:
        return JsonResponse({'status': 400, 'message': str(e)})


def check_otp(request):
    try:
        post_value = request.POST

        if User.objects.filter(username=request.POST['email']).exists():
            user = User.objects.get(username=request.POST['email'])

            if user.profile.status == USER_STATUS.RESTRICTED:
                return JsonResponse({'status': 401, 'success': False, 'message': 'Your account is restricted'})

            security = Security.objects.get(user_id=user.id)
            try:
                verify = Client(TWILIO['ACCOUNT_SID'], TWILIO['AUTH_TOKEN']).verify.services(TWILIO['VERIFY_SID'])
                verification_check = verify.verification_checks.create(to=user.profile.phone, code=post_value['otp'])
                if verification_check.status != 'approved':
                    raise Exception('pending')

                security.otp = post_value['otp']
                security.sms_counts = 0
                security.otp_attempt_counts = 0
                security.updated_at = timezone.now()
                security.save()

                return JsonResponse({'status': 200, 'message': 'success'})
            except:
                security.otp_attempt_counts += 1
                security.save()
                if security.otp_attempt_counts > 3:
                    sleep(security.otp_attempt_counts * 20)

                return JsonResponse({'status': 402, 'message': 'Your code is incorrect.'})
        else:
            return JsonResponse({'status': 403, 'message': "We can't find a user with that e-mail address."})
    except Exception as e:
        return JsonResponse({'status': 400, 'message': str(e)})


def send_email(request):
    try:
        post_value = request.POST

        if User.objects.filter(username=request.POST['email']).exists():
            user = User.objects.get(username=request.POST['email'])

            security = Security.objects.get(user_id=user.id)
            if (timezone.now() - security.updated_at).seconds > 60 * 30:
                return JsonResponse({'status': 401, 'message': 'Verification code expired'})

            if security.otp == post_value['otp']:
                security.otp_attempt_counts = 0
                security.save()

                token = PasswordResetTokenGenerator().make_token(user)
                uid = urlsafe_base64_encode(force_bytes((user.id)))
                reset_url = reverse('reset', urlconf='user_app.urls', kwargs={'uidb64': uid, 'token': token})

                message = render_to_string('user/email/reset_password.html', {
                    'url': SITE_URL,
                    'domain': request.get_host(),
                    'first_name': user.first_name.title(),
                    'reset_url': '/user' + reset_url,
                })

                send_mail(GMAIL_HOST_USER, user.email, 'Reset your SharpArchive password', message, 'html')

                return JsonResponse({'status': 200, 'message': 'success'})

            security.otp_attempt_counts += 1
            security.save()
            if security.otp_attempt_counts > 3:
                sleep(security.otp_attempt_counts * 20)

            return JsonResponse({'status': 402, 'message': 'Your code is incorrect.'})
        else:
            return JsonResponse({'status': 403, 'message': "We can't find a user with that e-mail address."})
    except Exception as e:
        return JsonResponse({'status': 400, 'message': str(e)})
