import math

from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from django.contrib.auth.models import User
from django.http import JsonResponse, QueryDict
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from random import randrange

from back_app.models.permission import Permission
from user_app.models.coupon import Coupon
from user_app.models.meta import Meta


@method_decorator(staff_member_required(login_url='/user/login/'), name='dispatch')
class CouponListView(ListView):
    template_name = 'user/back/coupon.html'

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

        return render(request, self.template_name, {'permissions': permissions})

    def post(self, request):
        sql = f"FROM user_coupon LEFT JOIN auth_user on user_coupon.user_id = auth_user.id WHERE 1"

        page = 1
        perpage = 20
        sort_field = 'user_coupon.id'
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

            elif param_key == 'query[from_started_at]':
                sql += f" AND DATE(started_at) >= CAST('{request.POST.get('query[from_started_at]')}' AS DATE)"
            elif param_key == 'query[to_started_at]':
                sql += f" AND DATE(started_at) <= CAST('{request.POST.get('query[to_started_at]')}' AS DATE)"
            elif param_key == 'query[status]':
                if request.POST.get('query[status]') == '1':
                    sql += f" AND started_at IS NOT NULL"
                if request.POST.get('query[status]') == '0':
                    sql += f" AND started_at IS NULL"
            elif param_key == 'query[generalSearch]' and request.POST.get('query[generalSearch]'):
                search = request.POST.get('query[generalSearch]')
                sql += " AND ( CAST(coupon_code AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(username AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%' )"

        with connection.cursor() as cursor:
            cursor.execute(f'SELECT COUNT(*) {sql}')
            row = cursor.fetchone()
            total = row[0]
            pages = math.ceil(total / perpage)

            if sort_field not in ['coupon_code', 'started_at', 'user_id']:
                sort_field = 'user_coupon.id'

            sql += f' ORDER BY {sort_field} {sort_direction}'

            sql += ' LIMIT ' + str((page - 1) * perpage) + ', ' + str(perpage)

            # print(request.POST)
            # print(f'SELECT * {sql}')
            rows = User.objects.raw(f'SELECT * {sql}')
            cursor.execute(f'SELECT user_coupon.id, user_coupon.coupon_code, user_coupon.months, user_coupon.started_at, auth_user.username {sql}')
            rows = cursor.fetchall()

            coupons = []
            if sort_direction == 'asc':
                index = (page - 1) * perpage + 1
            else:
                index = total - (page - 1) * perpage

            for row in rows:
                item = {}
                item['index'] = index
                item['id'] = row[0]
                item['coupon_code'] = row[1]
                item['months'] = row[2]
                if row[3]:
                    item['started_at'] = row[3].strftime('%m/%d/%Y')
                else:
                    item['started_at'] = ''
                if row[4]:
                    item['username'] = row[4]
                else:
                    item['username'] = ''

                coupons.append(item)

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
        return JsonResponse({'status': 200, 'coupons': coupons, 'meta': meta})

    def put(self, request):
        try:
            params = QueryDict(request.body)
            months = int(params.get('months'))
            if months != 1 and months != -1:
                raise Exception('Parameter Error')
        except:
            return JsonResponse({'status': 401, 'message': 'Parameter Error'})

        if months == 1:
            coupon_code = f'{randrange(1000, 9999)}-{randrange(1000, 9999)}-{randrange(1000, 9999)}-{randrange(1000, 9999)}'
            while Coupon.objects.filter(coupon_code=coupon_code).count() != 0:
                coupon_code = f'{randrange(1000, 9999)}-{randrange(1000, 9999)}-{randrange(1000, 9999)}-{randrange(1000, 9999)}'
        else:
            coupon_code = f'{randrange(1000, 9999)}-{randrange(1000, 9999)}-{randrange(1000, 9999)}'
            while Coupon.objects.filter(coupon_code=coupon_code).count() != 0:
                coupon_code = f'{randrange(1000, 9999)}-{randrange(1000, 9999)}-{randrange(1000, 9999)}'

        Coupon.objects.create(coupon_code=coupon_code, months=months)

        return JsonResponse({'status': 200, 'message': 'success', 'coupon_code': coupon_code})

    def delete(self, request):
        try:
            params = QueryDict(request.body)
            id = params.get('id')

            if len(Coupon.objects.filter(id=id, user_id=None)) == 0:
                return JsonResponse({'status': 301, 'message': 'Can not delete this coupon.'})

            Coupon.objects.filter(id=id, user_id=None).delete()

            return JsonResponse({'status': 200, 'message': 'Deleted successfully'})

        except:
            return JsonResponse({'status': 400, 'message': 'Delete failed'})
