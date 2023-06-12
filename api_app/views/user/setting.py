import json
from django.http import JsonResponse
from rest_framework.views import APIView

from user_app.models.meta import Meta


class SettingView(APIView):

    def get(self, request, meta_key):
        try:
            user = request.user
            if not user.profile.is_owner:
                user = user.profile.owner

            meta_value = Meta.objects.get(user_id=user.id, meta_key=meta_key).meta_value
        except:
            return JsonResponse({'status': 401, 'success': False, 'message': 'Data not found'})

        try:
            # meta_value = eval(meta_value)
            meta_value = json.loads(meta_value)

            return JsonResponse({'status': 200, 'success': True, 'message': 'Successfully Loaded', 'data': meta_value})

        except:
            return JsonResponse({'status': 400, 'success': False, 'message': 'Data Parsing Error'})

    def post(self, request, meta_key):
        try:
            user = request.user
            if not user.profile.is_owner:
                if user.profile.user_permission != 'Administrator':
                    return JsonResponse({'status': 401, 'success': False, 'message': 'You do not have permission'})
                else:
                    user = user.profile.owner

            meta_value = request.data

            if meta_key not in ['storage', 'time']:
                return JsonResponse({'status': 402, 'success': False, 'message': 'Parameter Error'})

            if meta_key == 'storage':
                if 'autoDeleteMonths' not in meta_value:
                    return JsonResponse({'status': 403, 'success': False, 'message': 'Parameter Error'})
                if meta_value['autoDeleteMonths']:
                    int(meta_value['autoDeleteMonths'])

            defaults = {
                'user_id': user.id,
                'meta_key': meta_key,
                'meta_value': json.dumps(meta_value, ensure_ascii=False, indent=4)
            }
            meta, created = Meta.objects.update_or_create(user_id=user.id, meta_key=meta_key, defaults=defaults)

            meta_value = json.loads(meta.meta_value)

            return JsonResponse({'status': 200, 'success': True, 'message': 'Successfully Saved', 'data': meta_value})

        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})
