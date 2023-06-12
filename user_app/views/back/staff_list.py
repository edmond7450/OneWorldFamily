import json
import math

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db import connection
from django.http import JsonResponse, QueryDict
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from my_settings import GOOGLE_MAPS_API_KEY
from back_app.models.history import save_history
from back_app.models.permission import Permission, check_permission
from user_app.models.meta import Meta
from user_app.models.profile import USER_STATUS


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class StaffListView(ListView):
    template_name = 'user/back/staff_list.html'
    permission_label = 'User Management'

    def get(self, request, *args, **kwargs):
        result = {}
        result['GOOGLE_MAPS_API_KEY'] = GOOGLE_MAPS_API_KEY

        permissions = []
        permission_list = []
        permission = Meta.objects.get(user_id=request.user.id, meta_key='admin_permission').meta_value
        rows = Permission.objects.all().order_by('index')
        for row in rows:
            try:
                item_permission = int(permission[row.index - 1:row.index], 16)

                if item_permission & 8 > 0:  # 0b1000
                    permissions.append(row.label)
            except:
                pass

            item = {}
            item['index'] = row.index
            item['label'] = row.label
            item['read'] = 0
            item['update'] = 0
            item['create'] = 0
            item['delete'] = 0

            permission_list.append(item)

        result['permissions'] = permissions
        result['permission_list'] = json.dumps(permission_list)

        return render(request, self.template_name, result)

    def post(self, request):
        sql = f"FROM auth_user u, user_profile p WHERE u.id = p.user_id AND is_staff = 1"

        page = 1
        perpage = 20
        sort_field = 'u.id'
        sort_direction = 'asc'
        deleted = False
        for param_key in request.POST.keys():
            if param_key == 'pagination[page]':
                page = int(request.POST.get('pagination[page]'))
            elif param_key == 'pagination[perpage]':
                perpage = int(request.POST.get('pagination[perpage]'))
            if param_key == 'sort[field]':
                sort_field = request.POST.get('sort[field]')
            elif param_key == 'sort[sort]':
                sort_direction = request.POST.get('sort[sort]')

            elif param_key == 'query[from_last_login]':
                sql += f" AND DATE(last_login) >= CAST('{request.POST.get('query[from_last_login]')}' AS DATE)"
            elif param_key == 'query[to_last_login]':
                sql += f" AND DATE(last_login) <= CAST('{request.POST.get('query[to_last_login]')}' AS DATE)"
            elif param_key == 'query[from_membership_date]':
                sql += f" AND DATE(membership_date) >= CAST('{request.POST.get('query[from_membership_date]')}' AS DATE)"
            elif param_key == 'query[to_membership_date]':
                sql += f" AND DATE(membership_date) <= CAST('{request.POST.get('query[to_membership_date]')}' AS DATE)"
            elif param_key == 'query[generalSearch]' and request.POST.get('query[generalSearch]'):
                search = request.POST.get('query[generalSearch]')
                sql += " AND ( CAST(first_name AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(last_name AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(username AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(phone AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(last_login AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(SUBSTRING_INDEX(address, ', ', -2) AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(SUBSTRING_INDEX(address, ', ', -3) AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(membership_date AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%' )"

        if not deleted:
            sql += f" AND is_active = 1"

        users = []
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT COUNT(*) {sql}')
            row = cursor.fetchone()
            total = row[0]
            pages = math.ceil(total / perpage)

            if sort_field not in ['name', 'phone', 'last_login', 'city', 'membership_date']:
                sort_field = 'u.id'

            if sort_field == 'name':
                sql += f' ORDER BY first_name {sort_direction}, last_name {sort_direction}'
            elif sort_field == 'city':
                sql += f" ORDER BY SUBSTRING_INDEX(address, ', ', -2) {sort_direction}, SUBSTRING_INDEX(address, ', ', -3) {sort_direction}"
            else:
                sql += f' ORDER BY {sort_field} {sort_direction}'

            sql += ' LIMIT ' + str((page - 1) * perpage) + ', ' + str(perpage)

            # print(request.POST)
            # print(f'SELECT * {sql}')
            cursor.execute(f'SELECT u.id, u.first_name, u.last_name, u.username, u.last_login, p.phone, p.address_components, p.membership_date, p.avatar {sql}')
            rows = cursor.fetchall()

            if sort_direction == 'asc':
                index = (page - 1) * perpage + 1
            else:
                index = total - (page - 1) * perpage

            for row in rows:
                item = {}
                item['index'] = index
                item['id'] = row[0]
                if row[8]:
                    item['avatar'] = '/media/' + row[8]
                else:
                    item['avatar'] = ''
                item['name'] = f'{row[1]} {row[2]}'
                item['username'] = row[3]
                if row[4]:
                    item['last_login'] = row[4].strftime('%m/%d/%Y')
                else:
                    item['last_login'] = ''
                item['phone'] = row[5]
                if row[6]:
                    addresses_components = json.loads(row[6])
                    item['city'] = addresses_components['city']
                    item['state'] = addresses_components['state']
                else:
                    item['city'] = ''
                    item['state'] = ''
                if row[7]:
                    item['membership_date'] = row[7].strftime('%m/%d/%Y')
                else:
                    item['membership_date'] = ''

                users.append(item)

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
        return JsonResponse({'status': 200, 'users': users, 'meta': meta})

    def delete(self, request):
        try:
            if not check_permission(request.user, self.permission_label, 'delete'):
                return JsonResponse({'status': 300, 'message': 'You have no permission'})

            params = QueryDict(request.body)
            id = params.get('id')
            user = User.objects.get(id=id)
            user.is_active = 0
            user.save()

            user.profile.status = USER_STATUS.CLOSED
            user.profile.close_account_info = timezone.now()
            user.profile.save()

            save_history(request.user, 'Backend', 'Staff Deleted', id)

            return JsonResponse({'status': 200, 'message': 'Deleted successfully'})

        except:
            return JsonResponse({'status': 400, 'message': 'Delete failed'})
