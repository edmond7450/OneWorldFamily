from django.http import JsonResponse
from rest_framework.views import APIView

from my_settings import API_URL
from back_app.models.notification import Notification


class NotificationView(APIView):
    def get(self, request):
        try:
            offset = int(request.GET['offset'])
            limit = int(request.GET['limit'])
        except:
            offset = 0
            limit = 100

        try:
            user = request.user
            data = []
            count = Notification.objects.filter(user=user, is_shown=True).count()

            if offset > 0:
                if offset > limit:
                    previous = f'{API_URL}/user/notification/?offset={offset - limit}&limit={limit}'
                else:
                    previous = f'{API_URL}/user/notification/?offset=0&limit={limit}'
            else:
                previous = ''

            if offset + limit < count:
                next = f'{API_URL}/user/notification/?offset={offset + limit}&limit={limit}'
            else:
                next = ''

            rows = Notification.objects.filter(user=user, is_shown=True).order_by('-id')[offset:offset + limit]
            for row in rows:
                item = {}
                item['id'] = row.id
                item['category'] = row.category
                item['message'] = row.message
                item['is_read'] = row.is_read
                item['createdAt'] = row.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                data.append(item)

            return JsonResponse({'status': 200, 'success': True, 'message': 'Successfully Loaded', 'count': count, 'previous': previous, 'next': next, 'data': data})

        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})

    def post(self, request):
        try:
            user = request.user
            id = request.data['id']

            data = []
            if id == -1:
                Notification.objects.filter(user=user).update(is_read=True)
                rows = Notification.objects.filter(user=user, is_shown=True)
                for row in rows:
                    item = {}
                    item['id'] = row.id
                    item['category'] = row.category
                    item['message'] = row.message
                    item['is_read'] = row.is_read
                    item['createdAt'] = row.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                    data.append(item)
            else:
                Notification.objects.filter(id=id, user=user).update(is_read=True)
                row = Notification.objects.get(id=id, user=user)
                item = {}
                item['id'] = row.id
                item['category'] = row.category
                item['message'] = row.message
                item['is_read'] = row.is_read
                item['createdAt'] = row.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                data.append(item)

            return JsonResponse({'status': 200, 'success': True, 'message': 'Marked as Read', 'data': data})
        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})

    def delete(self, request):
        try:
            user = request.user
            id = request.data['id']

            if id == -1:
                Notification.objects.filter(user=user).update(is_shown=False)
            else:
                Notification.objects.filter(id=id, user=user).update(is_shown=False)

            return JsonResponse({'status': 200, 'success': True, 'message': 'Successfully Deleted'})
        except Exception as e:
            return JsonResponse({'status': 400, 'success': False, 'message': repr(e)})
