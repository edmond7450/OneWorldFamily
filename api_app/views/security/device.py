from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.views import APIView

from user_app.models.device import Device


class DeviceView(APIView):
    def get(self, request):
        try:
            user = request.user
            if not user.profile.is_owner:
                user = user.profile.owner

            user_ids = [user.id]
            user_names = {}
            user_names[user.id] = user.get_full_name()

            rows = User.objects.filter(profile__is_owner=False, profile__owner=user, id__gt=3)  # hide managers
            for row in rows:
                user_ids.append(row.id)
                user_names[row.id] = row.get_full_name()

            devices = Device.objects.filter(user_id__in=user_ids, is_confirmed=True).order_by('-updated_at')
            data = []
            for device in devices:
                item = {}
                item['id'] = device.id
                item['name'] = user_names[device.user_id]
                item['ip'] = device.ip
                item['location'] = device.location
                item['os'] = device.os.strip() if device.os.strip() != 'Other' else ''
                item['browser'] = device.browser
                item['device'] = device.device if device.device != 'Other' else ''
                item['lastLogin'] = device.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                item['firstLogin'] = device.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                item['isActive'] = device.is_active()

                data.append(item)

        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})

        return JsonResponse({'status': 200, 'success': True, 'message': 'Successfully Loaded', 'data': data})

    def delete(self, request):
        try:
            user = request.user
            if not user.profile.is_owner:
                if user.profile.user_permission != 'Administrator':
                    return JsonResponse({'status': 401, 'success': False, 'message': 'You do not have permission'})
                else:
                    user = user.profile.owner

            user_ids = [user.id]
            rows = User.objects.filter(profile__is_owner=False, profile__owner=user)
            for row in rows:
                user_ids.append(row.id)

            id = request.data['id']

            if id == -1:
                Device.objects.filter(user_id__in=user_ids, is_confirmed=True).update(is_confirmed=False)

                for user_id in user_ids:
                    if user_id != request.user.id:
                        send_notification(user_id, 'logout')
            else:
                device = Device.objects.get(id=id, user_id__in=user_ids)
                device.is_confirmed = False
                device.save()

                if device.user_id != request.user.id and device.is_active():
                    send_notification(device.user_id, 'logout')

            return JsonResponse({'status': 200, 'success': True, 'message': 'Success'})
        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})
