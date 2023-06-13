from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.views import APIView

from user_app.models.device import Device


class DeviceView(APIView):
    def get(self, request):
        try:
            user = request.user

            devices = Device.objects.filter(user_id=user.id, is_confirmed=True).order_by('-updated_at')
            data = []
            for device in devices:
                item = {}
                item['id'] = device.id
                item['name'] = user.get_full_name()
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
            id = request.data['id']
            if id == -1:
                Device.objects.filter(user_id=request.user.id, is_confirmed=True).update(is_confirmed=False)
            else:
                Device.objects.filter(id=id, user_id=request.user.id).update(is_confirmed=False)

            return JsonResponse({'status': 200, 'success': True, 'message': 'Success'})
        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})
