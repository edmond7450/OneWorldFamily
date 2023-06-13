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
from random import randrange
from ringcentral import SDK
from time import sleep
from twilio.rest import Client

from my_settings import SITE_URL, GMAIL_HOST_USER, TWILIO, RINGCENTRAL
from user_app.models.profile import USER_STATUS
from user_app.models.security import Security
from user_app.views.send_email import send_mail


class ForgotView(View):
    template_name = 'user/back/forgot.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        try:
            if User.objects.filter(username=request.POST['email']).exists():
                user = User.objects.get(username=request.POST['email'])

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

            else:
                return JsonResponse({'status': 401, 'message': "We can't find a user with that e-mail address."})
        except Exception as e:
            return JsonResponse({'status': 400, 'message': str(e)})
