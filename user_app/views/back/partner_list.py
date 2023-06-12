import math
import stripe

from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from django.contrib.auth.models import User
from django.http import JsonResponse, QueryDict
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

from my_settings import GOOGLE_MAPS_API_KEY, STRIPE
from back_app.models.history import History, save_history
from back_app.models.notification import Notification
from back_app.models.permission import Permission, check_permission
from user_app.models import Meta, Security
from user_app.models.partner import Partner
from user_app.models.profile import USER_STATUS

stripe.api_key = STRIPE['SECRET_KEY']


@method_decorator(staff_member_required(login_url='/user/login/'), name='dispatch')
class PartnerListView(ListView):
    template_name = 'user/back/partner_list.html'
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

        sql = f"FROM auth_user u, user_profile p WHERE u.id = p.user_id AND p.user_permission = 'Partner'"

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
            elif param_key == 'query[from_date_joined]':
                sql += f" AND DATE(date_joined) >= CAST('{request.POST.get('query[from_date_joined]')}' AS DATE)"
            elif param_key == 'query[to_date_joined]':
                sql += f" AND DATE(date_joined) <= CAST('{request.POST.get('query[to_date_joined]')}' AS DATE)"
            elif param_key == 'query[generalSearch]' and request.POST.get('query[generalSearch]'):
                search = request.POST.get('query[generalSearch]')
                sql += " AND ( CAST(first_name AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(last_name AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(username AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(business_name AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(phone AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(last_login AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(date_joined AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%' )"

        if show_only_owner:
            sql += f" AND p.is_owner=1"

        with connection.cursor() as cursor:
            cursor.execute(f'SELECT COUNT(*) {sql}')
            row = cursor.fetchone()
            total = row[0]
            pages = math.ceil(total / perpage)

        if sort_field not in ['name', 'business_name', 'last_login', 'date_joined']:
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
            item['business_name'] = profile.business_name
            item['phone'] = profile.phone
            if user.last_login:
                item['last_login'] = user.last_login.strftime('%m/%d/%Y')
            else:
                item['last_login'] = ''
            item['date_joined'] = user.date_joined.strftime('%m/%d/%Y')

            item['partner_code'] = Partner.objects.get(email=user.username).code
            item['users'] = User.objects.filter(is_active=1, id__in=Meta.objects.filter(meta_key='partner_id', meta_value=str(user.id)).values('user_id')).count()

            users.append(item)

        meta = {
            'page': page,
            'pages': pages,
            'perpage': perpage,
            'total': total,
        }
        return JsonResponse({'status': 200, 'users': users, 'meta': meta})

    def delete(self, request):  # delete account
        try:
            if not check_permission(request.user, self.permission_label, 'delete'):
                return JsonResponse({'status': 300, 'message': 'You have no permission'})

            params = QueryDict(request.body)
            try:
                id = params.get('id')
                user = User.objects.get(id=id)
                if user.profile.user_permission != 'Partner':
                    raise Exception('Parameter Error')
            except:
                return JsonResponse({'status': 301, 'message': 'Parameter Error'})

            if user.is_superuser or user.is_staff:
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

            user.profile.delete()
            user.delete()

            Partner.objects.filter(email=user.username).delete()

            save_history(request.user, 'Backend', 'Partner Deleted', id)

            return JsonResponse({'status': 200, 'message': 'Deleted successfully'})

        except Exception as e:
            return JsonResponse({'status': 400, 'message': repr(e)})
