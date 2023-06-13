import json
import os.path
from datetime import datetime

import phonenumbers
from PIL import Image
from django.contrib import auth
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import DetailView

from my_settings import SITE_URL, GMAIL_HOST_USER, GOOGLE_MAPS_API_KEY
from back_app.models.history import save_history
from back_app.models.permission import Permission
from user_app.models.meta import Meta
from user_app.views.send_email import send_mail


@method_decorator(staff_member_required(login_url='/user/login/'), name='dispatch')
class ProfileView(DetailView):
    template_name = 'back/pages/settings/profile.html'

    def get(self, request, *args, **kwargs):
        result = self.get_permissions(request.user)

        return render(request, self.template_name, result)

    def post(self, request):
        user = request.user
        profile = user.profile

        post_value = request.POST
        request_class = post_value['request_class']

        if request_class == 'personal-information':
            if request.FILES and request.FILES['avatar']:
                if request.FILES['avatar'].content_type == 'image/jpeg' or request.FILES['avatar'].content_type == 'image/png':
                    try:
                        im = Image.open(request.FILES['avatar'].file)
                        im.verify()
                    except:
                        return render(request, self.template_name, {'request_class': request_class, 'result': 'fail', 'message': 'Invalid image', 'GOOGLE_MAPS_API_KEY': GOOGLE_MAPS_API_KEY})

                request.FILES['avatar'].name = str(user.id) + os.path.splitext(request.FILES['avatar'].name)[1].lower()
                profile.avatar = request.FILES['avatar']
            elif post_value['avatar_remove'] == '1':
                profile.avatar = ''

            phone = phonenumbers.parse(post_value['phone'])
            if not phonenumbers.is_valid_number(phone):
                return render(request, self.template_name, {'request_class': request_class, 'result': 'fail', 'message': 'Phone Number is not valid', 'GOOGLE_MAPS_API_KEY': GOOGLE_MAPS_API_KEY})

            profile.phone = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

            try:
                profile.birthday = datetime.strptime(post_value['birthday'], '%m/%d/%Y').date()
            except:
                profile.birthday = datetime.strptime(post_value['birthday'], '%B %d, %Y').date()
            profile.gender = post_value['gender']
            if post_value['city'] or post_value['state'] or post_value['country']:
                profile.address = post_value['address']
                profile.address_components = json.dumps(
                    {'street_number': post_value['street_number'], 'route': post_value['route'], 'city': post_value['city'], 'state': post_value['state'], 'country': post_value['country'], 'postal_code': post_value['postal_code']})

            profile.save()
            save_history(user, 'Backend', 'Profile Updated')

        elif request_class == 'change-password':
            current_password = post_value['current_password']

            if not check_password(current_password, user.password):
                return render(request, self.template_name, {'request_class': request_class, 'result': 'fail', 'message': 'Current Password is incorrect', 'GOOGLE_MAPS_API_KEY': GOOGLE_MAPS_API_KEY})

            user.password = make_password(request.POST['password'])
            user.save()

            user = auth.authenticate(request, username=user.username, password=request.POST['password'])
            auth.login(request, user)
            request.session.set_expiry(0)
            save_history(user, 'Backend', 'Password Reset')

            message = render_to_string('user/email/password_changed.html', {
                'url': SITE_URL,
                'first_name': user.first_name.title(),
                'email': user.email,
                'year': timezone.now().year
            })

            send_mail(GMAIL_HOST_USER, user.email, 'Your One World Family Account Password Changed', message, 'html')

        else:
            return render(request, self.template_name, {'request_class': request_class, 'result': 'fail', 'message': 'Unknown Request', 'GOOGLE_MAPS_API_KEY': GOOGLE_MAPS_API_KEY})

        result = self.get_permissions(user)
        result['request_class'] = request_class
        result['result'] = 'success'

        return render(request, self.template_name, result)

    def get_permissions(self, user):
        result = {}
        permissions = []
        permission = Meta.objects.get(user_id=user.id, meta_key='admin_permission').meta_value
        rows = Permission.objects.all().order_by('index')
        for row in rows:
            try:
                item_permission = int(permission[row.index - 1:row.index], 16)

                if item_permission & 8 > 0:  # 0b1000
                    permissions.append(row.label)
            except:
                pass

        result['permissions'] = permissions

        try:
            result['postal_code'] = json.loads(user.profile.address_components)['postal_code']
        except:
            result['postal_code'] = ''

        return result


@login_required
def change_two_factor(request):
    try:
        request.user.profile.two_factor = int(request.POST['two_factor'])
        request.user.profile.save()
        save_history(request.user, 'Backend', 'Two Factor', request.POST['two_factor'])

        return JsonResponse({'status': 200, 'message': 'success'})

    except:
        return JsonResponse({'status': 400, 'message': 'Exception happened'})
