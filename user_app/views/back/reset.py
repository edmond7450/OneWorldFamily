from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from my_settings import SITE_URL, GMAIL_HOST_USER
from back_app.models.history import save_history
from user_app.views.send_email import send_mail


class ResetView(View):
    template_name = 'user/back/reset.html'

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if PasswordResetTokenGenerator().check_token(user, token):
                return render(request, self.template_name, {'uidb64': uidb64, 'token': token})

            return JsonResponse({'status': 400, 'message': 'AUTH_FAIL'}, status=400)

        except Exception as e:
            return JsonResponse({'status': 400, 'message': str(e)}, status=400)

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if PasswordResetTokenGenerator().check_token(user, token):
                user.password = make_password(request.POST['password'])
                user.save()
                save_history(user, 'Backend', 'Password Reset')

                message = render_to_string('user/email/password_changed.html', {
                    'url': SITE_URL,
                    'first_name': user.first_name.title(),
                    'email': user.email,
                    'year': timezone.now().year
                })

                send_mail(GMAIL_HOST_USER, user.email, 'Your Sharp Archive Account Password Changed', message, 'html')

                user = auth.authenticate(request, username=user.username, password=request.POST['password'])

                auth.login(request, user)
                request.session.set_expiry(0)
                save_history(user, 'Backend', 'Log In')

                return JsonResponse({'status': 200, 'message': 'success'})

            return JsonResponse({'status': 400, 'message': 'AUTH_FAIL'})

        except Exception as e:
            return JsonResponse({'status': 400, 'message': str(e)})
