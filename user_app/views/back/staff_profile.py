import json

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse, QueryDict
from django.utils.decorators import method_decorator
from django.views.generic import DetailView

from back_app.models.permission import Permission
from user_app.models.meta import Meta


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class PermissionView(DetailView):
    def get(self, request, *args, **kwargs):
        id = request.GET['id']

        user = User.objects.get(id=id)
        try:
            permission = Meta.objects.get(user_id=user.id, meta_key='admin_permission').meta_value
        except:
            permission = ''

        permissions = []
        rows = Permission.objects.all().order_by('index')
        for row in rows:
            item = {}
            item['index'] = row.index
            item['label'] = row.label
            try:
                item_permission = int(permission[row.index - 1:row.index], 16)

                item['read'] = 1 if item_permission & 8 > 0 else 0
                item['update'] = 1 if item_permission & 4 > 0 else 0
                item['create'] = 1 if item_permission & 2 > 0 else 0
                item['delete'] = 1 if item_permission & 1 > 0 else 0
            except:
                item['read'] = 0
                item['update'] = 0
                item['create'] = 0
                item['delete'] = 0

            permissions.append(item)

        return JsonResponse({'status': 200, 'message': 'success', 'permissions': permissions})

    def put(self, request):
        params = QueryDict(request.body)
        user_id = params.get('user_id')
        permissions = json.loads(params.get('permissions'))

        str_permission = ''
        for index in permissions:
            permission = str(permissions[index]['read']) + str(permissions[index]['update']) + str(permissions[index]['create']) + str(permissions[index]['delete'])
            str_permission += '%x' % int(permission, 2)

        Meta.objects.update_or_create(user_id=user_id, meta_key='admin_permission', defaults={'meta_value': str_permission.upper()})

        return JsonResponse({'status': 200, 'message': 'success'})
