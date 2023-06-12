import math
import shutil
import stripe

from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse, QueryDict
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from my_settings import GOOGLE_MAPS_API_KEY, STRIPE
from back_app.models.history import History, save_history
from back_app.models.notification import Notification
from back_app.models.permission import Permission, check_permission
from user_app.models import Meta, Security
from user_app.models.profile import USER_STATUS

stripe.api_key = STRIPE['SECRET_KEY']


@method_decorator(staff_member_required(login_url='/user/login/'), name='dispatch')
class ClientListView(ListView):
    template_name = 'user/back/client_list.html'
    permission_label = 'User Management'

    def get(self, request, *args, **kwargs):
        if not check_permission(request.user, self.permission_label, 'read'):
            return redirect('/user/login/')

        result = {}
        result['GOOGLE_MAPS_API_KEY'] = GOOGLE_MAPS_API_KEY

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

        result['permissions'] = permissions

        return render(request, self.template_name, result)

    def post(self, request):
        if not check_permission(request.user, self.permission_label, 'read'):
            return JsonResponse({'status': 300, 'message': 'You have no permission'})

        sql = f"FROM auth_user u, user_profile p WHERE u.id = p.user_id AND p.user_permission != 'Partner'"

        page = 1
        perpage = 20
        sort_field = 'u.id'
        sort_direction = 'asc'
        show_only_owner = True
        for param_key in request.POST.keys():
            if param_key == 'pagination[page]':
                page = int(request.POST.get('pagination[page]'))
            elif param_key == 'pagination[perpage]':
                perpage = int(request.POST.get('pagination[perpage]'))
            if param_key == 'sort[field]':
                sort_field = request.POST.get('sort[field]')
            elif param_key == 'sort[sort]':
                sort_direction = request.POST.get('sort[sort]')

            elif param_key == 'query[show_only_owner]':
                show_only_owner = request.POST.get('query[show_only_owner]')
                if show_only_owner == 'false':
                    show_only_owner = False

            elif param_key == 'query[from_last_login]':
                sql += f" AND DATE(last_login) >= CAST('{request.POST.get('query[from_last_login]')}' AS DATE)"
            elif param_key == 'query[to_last_login]':
                sql += f" AND DATE(last_login) <= CAST('{request.POST.get('query[to_last_login]')}' AS DATE)"
            elif param_key == 'query[from_membership_date]':
                sql += f" AND DATE(membership_date) >= CAST('{request.POST.get('query[from_membership_date]')}' AS DATE)"
            elif param_key == 'query[to_membership_date]':
                sql += f" AND DATE(membership_date) <= CAST('{request.POST.get('query[to_membership_date]')}' AS DATE)"
            elif param_key == 'query[status]':
                status = request.POST.get('query[status]')
                sql += f" AND status = '{status}'"
            elif param_key == 'query[generalSearch]' and request.POST.get('query[generalSearch]'):
                search = request.POST.get('query[generalSearch]')
                sql += " AND ( CAST(first_name AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(last_name AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(username AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(phone AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(last_login AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(date_joined AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(membership_date AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%' )"

        if show_only_owner:
            sql += f" AND p.is_owner=1"

        with connection.cursor() as cursor:
            cursor.execute(f'SELECT COUNT(*) {sql}')
            row = cursor.fetchone()
            total = row[0]
            pages = math.ceil(total / perpage)

        if sort_field not in ['name', 'last_login', 'membership_date', 'status']:
            sort_field = 'u.id'

        if sort_field == 'name':
            sql += f' ORDER BY first_name {sort_direction}, last_name {sort_direction}'
        else:
            sql += f' ORDER BY {sort_field} {sort_direction}'

        sql += ' LIMIT ' + str((page - 1) * perpage) + ', ' + str(perpage)

        # print(request.POST)
        # print(f'SELECT * {sql}')
        rows = User.objects.raw(f'SELECT * {sql}')

        users = []
        for user in rows:
            profile = user.profile
            item = {}
            item['id'] = user.id
            if profile.avatar:
                item['avatar'] = profile.avatar.url
            else:
                item['avatar'] = ''
            item['name'] = user.get_full_name()
            item['username'] = user.username
            item['phone'] = profile.phone
            if user.last_login:
                item['last_login'] = user.last_login.strftime('%m/%d/%Y')
            else:
                item['last_login'] = ''
            item['date_joined'] = user.date_joined.strftime('%m/%d/%Y')
            if user.profile.membership_date:
                item['membership_date'] = user.profile.membership_date.strftime('%m/%d/%Y')
            else:
                item['membership_date'] = ''
            if user.profile.close_account_info:
                item['close_account_info'] = datetime.strptime(user.profile.close_account_info, '%Y-%m-%d %H:%M:%S.%f%z').strftime('%m/%d/%Y')
            else:
                item['close_account_info'] = ''
            item['status'] = profile.status
            item['owner'] = profile.owner_id if profile.owner else ''

            users.append(item)

        meta = {
            'page': page,
            'pages': pages,
            'perpage': perpage,
            'total': total,
        }
        return JsonResponse({'status': 200, 'users': users, 'meta': meta})

    def put(self, request):  # close account
        try:
            if not check_permission(request.user, self.permission_label, 'delete'):
                return JsonResponse({'status': 300, 'message': 'You have no permission'})

            params = QueryDict(request.body)
            if 'id' in params:
                id = params.get('id')
                users = User.objects.filter(id=id)
            elif 'ids[]' in params:
                id = params.getlist('ids[]')
                users = User.objects.filter(id__in=id)
            else:
                return JsonResponse({'status': 301, 'message': 'Parameter Error'})

            now = timezone.now()
            for user in users:
                if user.is_superuser or user.is_staff:
                    return JsonResponse({'status': 302, 'message': 'You can not close this user.'})

                user.is_active = 0
                user.save()

                user.profile.status = USER_STATUS.CLOSED
                user.profile.close_account_info = now
                user.profile.save()

            save_history(request.user, 'Backend', 'Client Closed', id)

            return JsonResponse({'status': 200, 'message': 'Closed successfully'})

        except:
            return JsonResponse({'status': 400, 'message': 'Closed failed'})

    def delete(self, request):  # delete account
        try:
            if not check_permission(request.user, self.permission_label, 'delete'):
                return JsonResponse({'status': 300, 'message': 'You have no permission'})

            params = QueryDict(request.body)
            if 'id' in params:
                id = params.get('id')
                users = User.objects.filter(id=id)
            elif 'ids[]' in params:
                id = params.getlist('ids[]')
                users = User.objects.filter(id__in=id)
            else:
                return JsonResponse({'status': 301, 'message': 'Parameter Error'})

            for user in users:
                if user.is_superuser or user.is_staff or user.is_active or user.profile.status != USER_STATUS.CLOSED:
                    return JsonResponse({'status': 302, 'message': 'You can not delete this user.'})

                if user.profile.stripe_customer_id:
                    try:
                        stripe.Customer.delete(user.profile.stripe_customer_id)
                    except:
                        pass

                Notification.objects.filter(user=user).delete()
                History.objects.filter(user=user).delete()
                Meta.objects.filter(user_id=user.id).delete()
                Security.objects.filter(user_id=user.id).delete()
                OutstandingToken.objects.filter(user=user).delete()

                try:
                    archive_dir = settings.ARCHIVE_DIR.joinpath(str(user.id))
                    shutil.rmtree(archive_dir)
                except:
                    pass

                user.profile.delete()
                user.delete()

            save_history(request.user, 'Backend', 'Client Deleted', id)

            return JsonResponse({'status': 200, 'message': 'Deleted successfully'})

        except Exception as e:
            return JsonResponse({'status': 400, 'message': repr(e)})
