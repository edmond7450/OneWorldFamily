import json
import math

from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from back_app.models.permission import Permission
from back_app.models.notification import Notification
from user_app.models.meta import Meta


@method_decorator(staff_member_required(login_url='/user/login/'), name='dispatch')
class NotificationView(ListView):
    template_name = 'back/pages/manage/notification.html'

    def get(self, request, *args, **kwargs):
        permissions = []
        permission = Meta.objects.get(user_id=request.user.id, meta_key='admin_permission').meta_value
        rows = Permission.objects.all().order_by('index')
        for row in rows:
            try:
                item_permission = int(permission[row.index - 1:row.index], 16)

                if item_permission & 8 > 0:  # 0b1000
                    permissions.append(row.label)
            except:
                pass

        categories = []
        rows = Notification.objects.values('category').distinct()
        for row in rows:
            categories.append(row['category'])

        users = []
        rows = User.objects.all()
        for row in rows:
            item = {}
            item['id'] = row.id
            item['username'] = row.username
            item['is_active'] = row.is_active

            users.append(item)

        return render(request, self.template_name, {'permissions': permissions, 'categories': json.dumps(categories), 'users': json.dumps(users)})

    def post(self, request):
        sql = f"FROM back_notification h LEFT JOIN auth_user u ON h.user_id = u.id WHERE is_auto=1"

        page = 1
        perpage = 20
        sort_field = 'h.id'
        sort_direction = 'desc'
        deleted = True
        for param_key in request.POST.keys():
            if param_key == 'pagination[page]':
                page = int(request.POST.get('pagination[page]'))
            elif param_key == 'pagination[perpage]':
                perpage = int(request.POST.get('pagination[perpage]'))
            if param_key == 'sort[field]':
                sort_field = request.POST.get('sort[field]')
            elif param_key == 'sort[sort]':
                sort_direction = request.POST.get('sort[sort]')

            elif param_key == 'query[user_id]':
                sql += f" AND h.user_id = '{request.POST.get('query[user_id]')}'"
            elif param_key == 'query[category]':
                sql += f" AND category = '{request.POST.get('query[category]')}'"
            elif param_key == 'query[is_read]':
                sql += f" AND is_read = '{request.POST.get('query[is_read]')}'"
            elif param_key == 'query[is_shown]':
                sql += f" AND is_shown = '{request.POST.get('query[is_shown]')}'"
            elif param_key == 'query[from_date]':
                sql += f" AND DATE(created_at) >= CAST('{request.POST.get('query[from_date]')}' AS DATE)"
            elif param_key == 'query[to_date]':
                sql += f" AND DATE(created_at) <= CAST('{request.POST.get('query[to_date]')}' AS DATE)"
            elif param_key == 'query[generalSearch]' and request.POST.get('query[generalSearch]'):
                search = request.POST.get('query[generalSearch]')
                sql += " AND ( CAST(category AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(message AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(username AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(created_at AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%' )"

        if not deleted:
            sql += f" AND is_shown = 1"

        items = []
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT COUNT(*) {sql}')
            row = cursor.fetchone()
            total = row[0]
            pages = math.ceil(total / perpage)

            if sort_field not in ['category', 'message', 'is_read', 'is_shown', 'created_at', 'username']:
                sort_field = 'h.id'
                sort_direction = 'desc'

            sql += f' ORDER BY {sort_field} {sort_direction}'

            sql += ' LIMIT ' + str((page - 1) * perpage) + ', ' + str(perpage)

            # print(request.POST)
            # print(f'SELECT * {sql}')
            cursor.execute(f'SELECT category, message, is_read, is_shown, created_at, user_id, username {sql}')
            rows = cursor.fetchall()

            if sort_direction == 'asc':
                index = (page - 1) * perpage + 1
            else:
                index = total - (page - 1) * perpage

            for row in rows:
                item = {}
                item['index'] = index
                item['category'] = row[0]
                item['message'] = row[1]
                item['is_read'] = row[2]
                item['is_shown'] = row[3]
                if row[4]:
                    item['created_at'] = row[4].strftime('%m/%d/%Y')
                else:
                    item['created_at'] = ''
                item['user_id'] = row[5]
                item['username'] = row[6]

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
