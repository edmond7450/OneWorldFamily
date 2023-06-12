import json
import os.path
import phonenumbers
import googlemaps

from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.http import JsonResponse
from django.http.multipartparser import MultiPartParser
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from PIL import Image

from my_settings import GOOGLE_GEOCODING_API_KEY


@method_decorator(staff_member_required, name='dispatch')
class ProfileView(DetailView):
    def get(self, request, *args, **kwargs):
        id = request.GET['id']

        user = User.objects.get(id=id)
        profile = user.profile
        try:
            postal_code = json.loads(profile.address_components)['postal_code']
        except:
            postal_code = ''

        data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': profile.phone,
            'gender': profile.gender,
            'address': profile.address,
            'postal_code': postal_code
        }
        if profile.birthday:
            try:
                data['birthday'] = profile.birthday.strftime('%B %-d, %Y')
            except:
                data['birthday'] = profile.birthday.strftime('%B %#d, %Y')
        else:
            profile.birthday = ''
        if profile.avatar:
            data['avatar'] = profile.avatar.url
        else:
            data['avatar'] = ''

        return JsonResponse({'status': 200, 'message': 'success', 'data': data})

    def put(self, request):
        try:
            put_data = MultiPartParser(request.META, request, request.upload_handlers).parse()  # it will return a tuple object
            data = put_data[0]  # it will give you the QueryDict object with your form data.
            user_id = data['user_id']
            user = User.objects.get(id=user_id)
            profile = user.profile

            if data['add_email'] != data['email']:
                try:
                    validate_email(data['add_email'])
                except:
                    return JsonResponse({'status': 401, 'message': 'Email is not valid'})

                if User.objects.filter(username=data['add_email']).exists():
                    return JsonResponse({'status': 402, 'message': 'Email Already in Use with Sharp Archive'})

            phone = phonenumbers.parse(data['phone'])
            if not phonenumbers.is_valid_number(phone):
                return JsonResponse({'status': 403, 'message': 'Phone Number is not valid'})

            phone = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

            if data['city'] or data['state'] or data['country']:
                address_components = json.dumps({'street_number': data['street_number'], 'route': data['route'], 'city': data['city'], 'state': data['state'], 'country': data['country'], 'postal_code': data['postal_code']})
            else:
                try:
                    gmaps = googlemaps.Client(key=GOOGLE_GEOCODING_API_KEY)
                    street_number = route = city = state = country = postal_code = ''
                    # Geocoding an address
                    geocode_result = gmaps.geocode(data['address'])
                    for component in geocode_result[0]['address_components']:
                        for j in component['types']:
                            if j == 'street_number':
                                street_number = component['short_name']
                            elif j == 'route':
                                route = component['short_name']
                            elif j == 'locality':
                                city = component['short_name']
                            elif j == 'administrative_area_level_1':
                                state = component['short_name']
                            elif j == 'country':
                                country = component['short_name']
                            elif j == 'postal_code':
                                postal_code = component['short_name']

                    if not postal_code:
                        return JsonResponse({'status': 404, 'message': 'Address is not valid'})

                    address_components = json.dumps({'street_number': street_number, 'route': route, 'city': city, 'state': state, 'country': country, 'postal_code': postal_code})
                except:
                    return JsonResponse({'status': 405, 'message': 'Address is not valid'})

            if user.username != data['add_email'] or user.first_name != data['first_name'] or user.last_name != data['last_name']:
                user.username = data['add_email']
                user.email = data['add_email']
                user.first_name = data['first_name']
                user.last_name = data['last_name']
                user.save()

            if len(put_data) > 1 and 'avatar' in put_data[1]:
                files = put_data[1]
                if files['avatar'].content_type == 'image/jpeg' or files['avatar'].content_type == 'image/png':
                    try:
                        im = Image.open(files['avatar'].file)
                        im.verify()
                    except:
                        return JsonResponse({'status': 406, 'message': 'Invalid image'})

                files['avatar'].name = str(user.id) + os.path.splitext(files['avatar'].name)[1].lower()
                profile.avatar = files['avatar']
            elif data['avatar_remove'] == '1':
                profile.avatar = ''

            profile.phone = phone
            try:
                profile.birthday = datetime.strptime(data['birthday'], '%m/%d/%Y').date()
            except:
                profile.birthday = datetime.strptime(data['birthday'], '%B %d, %Y').date()
            profile.gender = data['gender']
            profile.address = data['address']
            profile.address_components = address_components

            profile.save()

            data = {}
            data['id'] = user.id
            if profile.avatar:
                data['avatar'] = profile.avatar.url
            else:
                data['avatar'] = ''
            data['name'] = user.get_full_name()
            data['username'] = user.username
            if user.last_login:
                data['last_login'] = user.last_login.strftime('%m/%d/%Y')
            else:
                data['last_login'] = ''
            data['phone'] = profile.phone
            address_components = json.loads(profile.address_components)
            data['city'] = address_components['city']
            data['state'] = address_components['state']
            if profile.membership_date:
                data['membership_date'] = profile.membership_date.strftime('%m/%d/%Y')
            else:
                data['membership_date'] = ''

            return JsonResponse({'status': 200, 'message': 'success', 'data': data})

        except Exception as e:
            return JsonResponse({'status': 405, 'message': str(e)})
