import json
import math
import mimetypes
import os.path

from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from wsgiref.util import FileWrapper

from api_app.models.invoice import Invoice
from back_app.models.permission import Permission
from user_app.models.meta import Meta


@method_decorator(staff_member_required(login_url='/user/login/'), name='dispatch')
class InvoiceView(ListView):
    template_name = 'back/pages/manage/invoice.html'

    def get(self, request, *args, **kwargs):
        if 'id' in request.GET and request.GET['id']:
            try:
                id = request.GET['id']
                invoice_path = Invoice.objects.get(id=id).invoice_path

                mime_type, _ = mimetypes.guess_type(invoice_path)
                response = FileResponse(FileWrapper(open(invoice_path, 'rb')), content_type=mime_type)
                response['Content-Disposition'] = "attachment; filename=%s" % os.path.basename(invoice_path)
                return response
            except:
                raise Http404

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

        users = []
        rows = User.objects.filter(profile__is_owner=True)
        for row in rows:
            item = {}
            item['id'] = row.id
            item['username'] = row.username
            item['is_active'] = row.is_active

            users.append(item)

        return render(request, self.template_name, {'permissions': permissions, 'users': json.dumps(users)})

    def post(self, request):
        sql = f"FROM invoice i LEFT JOIN auth_user u ON i.user_id = u.id WHERE 1"

        page = 1
        perpage = 20
        sort_field = 'i.id'
        sort_direction = 'desc'
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
                sql += f" AND i.user_id = '{request.POST.get('query[user_id]')}'"
            elif param_key == 'query[category]':
                sql += f" AND category = '{request.POST.get('query[category]')}'"
            elif param_key == 'query[from_date]':
                sql += f" AND DATE(created_at) >= CAST('{request.POST.get('query[from_date]')}' AS DATE)"
            elif param_key == 'query[to_date]':
                sql += f" AND DATE(created_at) <= CAST('{request.POST.get('query[to_date]')}' AS DATE)"
            elif param_key == 'query[generalSearch]' and request.POST.get('query[generalSearch]'):
                search = request.POST.get('query[generalSearch]')
                sql += " AND ( CAST(invoice_number AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(subtotal AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(tax AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(total AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(username AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(created_at AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%' )"

        items = []
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT COUNT(*) {sql}')
            row = cursor.fetchone()
            total = row[0]
            pages = math.ceil(total / perpage)

            if sort_field not in ['invoice_number', 'subtotal', 'tax', 'total', 'created_at', 'username']:
                sort_field = 'i.id'
                sort_direction = 'desc'

            sql += f' ORDER BY {sort_field} {sort_direction}'

            sql += ' LIMIT ' + str((page - 1) * perpage) + ', ' + str(perpage)

            # print(request.POST)
            # print(f'SELECT * {sql}')
            cursor.execute(f'SELECT i.id, invoice_number, subtotal, tax, total, created_at, username {sql}')
            rows = cursor.fetchall()

            if sort_direction == 'asc':
                index = (page - 1) * perpage + 1
            else:
                index = total - (page - 1) * perpage

            for row in rows:
                item = {}
                item['index'] = index
                item['id'] = row[0]
                item['invoice_number'] = row[1]
                item['subtotal'] = '%.2f' % row[2]
                item['tax'] = '%.2f' % row[3]
                item['total'] = '%.2f' % row[4]
                if row[5]:
                    item['created_at'] = row[5].strftime('%m/%d/%Y')
                else:
                    item['created_at'] = ''
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
