import json
from datetime import datetime
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from api_app.models.api_meta import API_Meta


class MetaView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, meta_key):
        try:
            # meta_value = eval(API_Meta.objects.get(meta_key=meta_key).meta_value)
            meta_value = json.loads(API_Meta.objects.get(meta_key=meta_key).meta_value)

            if meta_key == 'date-format':
                now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
                return JsonResponse({'status': 200, 'success': True, 'message': 'Successfully Loaded', 'data': meta_value, 'now': now})

            return JsonResponse({'status': 200, 'success': True, 'message': 'Successfully Loaded', 'data': meta_value})

        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})
