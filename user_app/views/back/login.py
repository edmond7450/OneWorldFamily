from django.contrib import auth
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.views import View
from random import randrange
from time import sleep
from ringcentral import SDK
from twilio.rest import Client

from my_settings import SITE_URL, GMAIL_HOST_USER, TWILIO, RINGCENTRAL
from back_app.models.history import save_history
from user_app.models.profile import USER_STATUS
from user_app.models.security import Security
from user_app.views.send_email import send_mail


class LoginView(View):
    template_name = 'user/back/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        post_value = request.POST
        user = auth.authenticate(request, username=post_value['email'], password=post_value['password'])

        if user is not None:
            if user.is_staff != 1:
                return JsonResponse({'status': 401, 'message': 'You have no permission.'})

            profile = user.profile
            if profile.status == USER_STATUS.RESTRICTED:
                return JsonResponse({'status': 402, 'success': False, 'message': 'Your account is restricted'})

            security = Security.objects.get(user_id=user.id)
            if profile.two_factor == 2:
                try:
                    otp = randrange(100000, 999999)
                    security.otp = str(otp)
                    security.updated_at = timezone.now()
                    security.save()

                    message = render_to_string('user/email/verify_code.html', {
                        'url': SITE_URL,
                        'first_name': user.first_name,
                        'code': otp,
                        'year': timezone.now().year
                    })

                    send_mail(GMAIL_HOST_USER, user.email, 'Your Verification Code', message, 'html')

                    return JsonResponse({'status': 200, 'message': 'send_email_otp'})
                except Exception as e:
                    return JsonResponse({'status': 405, 'message': repr(e)})

            else:
                result = check_user_status(profile.status)
                if result['status'] == 200:
                    auth.login(request, user)
                    request.session.set_expiry(0)
                    save_history(user, 'Backend', 'Log In')

                return JsonResponse(result)
        else:
            try:
                user = User.objects.get(username=post_value['email'])
                if user is not None and user.check_password(post_value['password']):  # is_active = 0
                    return JsonResponse(check_user_status(user.profile.status))
            except:
                pass

            return JsonResponse({'status': 400, 'message': 'Email or password is incorrect'})


def logout(request):
    save_history(request.user, 'Backend', 'Log Out')
    auth.logout(request)
    return redirect('/')


def send_otp(request):
    try:
        user = auth.authenticate(request, username=request.POST['email'], password=request.POST['password'])

        if user is None:
            return JsonResponse({'status': 401, 'message': 'Email or password is incorrect'})

        if user.profile.status == USER_STATUS.RESTRICTED:
            return JsonResponse({'status': 402, 'message': 'Your account is restricted'})

        security = Security.objects.get(user_id=user.id)

        if request.POST['otp_class'] == 'send_email_otp':
            otp = randrange(100000, 999999)
            security.otp = str(otp)
            security.updated_at = timezone.now()
            security.save()

            message = render_to_string('user/email/verify_code.html', {
                'url': SITE_URL,
                'first_name': user.first_name,
                'code': otp,
                'year': timezone.now().year
            })

            send_mail(GMAIL_HOST_USER, user.email, 'Your Verification Code', message, 'html')

            return JsonResponse({'status': 200, 'message': 'success'})

    except Exception as e:
        return JsonResponse({'status': 400, 'message': repr(e)})


def check_otp(request):
    try:
        post_value = request.POST
        user = auth.authenticate(request, username=post_value['email'], password=post_value['password'])

        if user is None:
            return JsonResponse({'status': 401, 'message': 'Email or password is incorrect'})

        profile = user.profile
        if profile.status == USER_STATUS.RESTRICTED:
            return JsonResponse({'status': 402, 'message': 'Your account is restricted'})

        security = Security.objects.get(user_id=user.id)

        if profile.two_factor == 2:
            if (timezone.now() - security.updated_at).seconds > 60 * 30:
                return JsonResponse({'status': 405, 'message': 'Verification code expired'})

            if security.otp != post_value['otp']:
                security.otp_attempt_counts += 1
                security.save()
                if security.otp_attempt_counts > 3:
                    sleep(security.otp_attempt_counts * 20)

                return JsonResponse({'status': 406, 'message': 'Your code is incorrect.'})

        security.otp_attempt_counts = 0
        security.save()

        result = check_user_status(profile.status)
        if result['status'] == 200:
            auth.login(request, user)
            request.session.set_expiry(0)
            save_history(user, 'Backend', 'Log In')

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({'status': 400, 'message': repr(e)})


def check_user_status(status):
    if status == USER_STATUS.VERIFIED:
        return {'status': 200, 'message': 'success'}

    elif status == USER_STATUS.INTERNAL:
        return {'status': 200, 'message': 'success'}

    elif status == USER_STATUS.INACTIVE:
        return {'status': 501, 'message': 'Your account has not been activated.'}

    elif status == USER_STATUS.SECURITY_CHECKING:
        return {'status': 503, 'message': 'Security questions have been asked.'}

    elif status == USER_STATUS.RESTRICTED:
        return {'status': 504, 'message': 'This account has been restricted.'}

    elif status == USER_STATUS.CLOSED:
        return {'status': 505, 'message': 'This account has been closed.'}
