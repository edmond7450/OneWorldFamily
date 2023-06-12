import json
import math

from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from django.http import JsonResponse, QueryDict
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from api_app.models.api_meta import API_Meta
from back_app.models.history import save_history
from back_app.models.permission import Permission, check_permission
from user_app.models.meta import Meta


@method_decorator(staff_member_required(login_url='/user/login/'), name='dispatch')
class MetaView(ListView):
    template_name = 'back/pages/settings/meta.html'
    permission_label = 'Meta Setting'

    def get(self, request, *args, **kwargs):
        if 'id' in request.GET and request.GET['id']:
            row = API_Meta.objects.get(id=request.GET['id'])
            data = {
                'id': row.id,
                'meta_key': row.meta_key,
                'meta_value': row.meta_value,
            }
            return JsonResponse({'status': 200, 'message': 'success', 'data': data})
        else:
            permissions = []
            permission = Meta.objects.get(user_id=request.user.id, meta_key='admin_permission').meta_value
            rows = Permission.objects.all().order_by('index')
            for row in rows:
                try:
                    item_permission = int(permission[row.index - 1:row.index], 16)

                    if row.label == self.permission_label:
                        if item_permission & 8 == 0:
                            return redirect('/user/login/')

                        permissions.append(row.label)
                        if item_permission & 4 > 0:
                            permissions.append('update')
                        if item_permission & 2 > 0:
                            permissions.append('create')
                        if item_permission & 1 > 0:
                            permissions.append('delete')

                    elif item_permission & 8 > 0:  # 0b1000
                        permissions.append(row.label)
                except:
                    pass

            return render(request, self.template_name, {'permissions': permissions})

    def post(self, request):
        sql = f"FROM api_meta WHERE 1"

        page = 1
        perpage = 20
        sort_field = 'id'
        sort_direction = 'asc'
        for param_key in request.POST.keys():
            if param_key == 'pagination[page]':
                page = int(request.POST.get('pagination[page]'))
            elif param_key == 'pagination[perpage]':
                perpage = int(request.POST.get('pagination[perpage]'))
            if param_key == 'sort[field]':
                sort_field = request.POST.get('sort[field]')
            elif param_key == 'sort[sort]':
                sort_direction = request.POST.get('sort[sort]')

            elif param_key == 'query[generalSearch]' and request.POST.get('query[generalSearch]'):
                search = request.POST.get('query[generalSearch]')
                sql += " AND ( CAST(meta_key AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(meta_value AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%' )"

        with connection.cursor() as cursor:
            cursor.execute(f'SELECT COUNT(*) {sql}')
            row = cursor.fetchone()
            total = row[0]
            pages = math.ceil(total / perpage)

        if sort_field not in ['meta_key', 'meta_value', 'updated_at']:
            sort_field = 'id'

        sql += f' ORDER BY {sort_field} {sort_direction}'

        sql += ' LIMIT ' + str((page - 1) * perpage) + ', ' + str(perpage)

        # print(request.POST)
        # print(f'SELECT * {sql}')
        rows = API_Meta.objects.raw(f'SELECT * {sql}')

        items = []
        if sort_direction == 'asc':
            index = (page - 1) * perpage + 1
        else:
            index = total - (page - 1) * perpage
        for row in rows:
            item = {}
            item['id'] = row.id
            item['index'] = index
            item['meta_key'] = row.meta_key
            item['meta_value'] = row.meta_value.replace('<', '&lt;').replace('>', '&gt')
            item['updated_at'] = row.updated_at.strftime('%m/%d/%Y')

            items.append(item)

            if sort_direction == 'asc':
                index += 1
            else:
                index -= 1

        meta = {
            'page': page,
            'pages': pages,
            'perpage': perpage,
            'total': total,
        }
        return JsonResponse({'status': 200, 'items': items, 'meta': meta})

    def put(self, request):
        try:
            params = QueryDict(request.body)
            id = params.get('id')
            meta_key = params.get('meta_key')
            meta_value = params.get('meta_value')
            meta_value = eval(meta_value)
            meta_value = json.dumps(meta_value, ensure_ascii=False, indent=4)

            if id:
                if not check_permission(request.user, self.permission_label, 'update'):
                    return JsonResponse({'status': 300, 'message': 'You have no permission'})

                row = API_Meta.objects.get(id=id)
                row.meta_key = meta_key
                row.meta_value = meta_value
                row.save()
                save_history(request.user, 'Backend', 'Meta Updated', meta_key)
            else:
                if not check_permission(request.user, self.permission_label, 'create'):
                    return JsonResponse({'status': 300, 'message': 'You have no permission'})

                API_Meta.objects.create(meta_key=meta_key, meta_value=meta_value)
                save_history(request.user, 'Backend', 'Meta Created', meta_key)

            return JsonResponse({'status': 200, 'message': 'success'})

        except:
            return JsonResponse({'status': 400, 'message': 'Failed'})

    def delete(self, request):
        try:
            if not check_permission(request.user, self.permission_label, 'delete'):
                return JsonResponse({'status': 300, 'message': 'You have no permission'})

            params = QueryDict(request.body)
            id = params.get('id')
            API_Meta.objects.get(id=id).delete()
            save_history(request.user, 'Backend', 'Meta Deleted', id)

            return JsonResponse({'status': 200, 'message': 'Deleted successfully'})

        except:
            return JsonResponse({'status': 400, 'message': 'Delete failed'})
