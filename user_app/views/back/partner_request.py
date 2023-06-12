import math
import random
import string

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db import connection
from django.http import JsonResponse, QueryDict
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic import ListView

from my_settings import SITE_URL, GMAIL_HOST_USER
from back_app.models.history import save_history
from back_app.models.permission import Permission, check_permission
from user_app.models.meta import Meta
from user_app.models.partner import Partner
from user_app.models.profile import Profile
from user_app.models.security import Security
from user_app.views.send_email import send_mail


@method_decorator(staff_member_required(login_url='/user/login/'), name='dispatch')
class PartnerRequestView(ListView):
    template_name = 'user/back/partner_request.html'
    permission_label = 'User Management'

    def get(self, request, *args, **kwargs):
        if 'id' in request.GET and request.GET['id']:
            row = Partner.objects.get(id=request.GET['id'])
            data = {
                'id': row.id,
                'full_name': row.full_name,
                'title': row.title,
                'email': row.email,
                'phone': row.phone,
                'company_name': row.company_name,
                'comments': row.comments,
                'status': row.status,
                'requested_at': row.requested_at.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            if row.status == 'Approved':
                data['code'] = row.code
                data['approved_at'] = row.approved_at.strftime('%Y-%m-%dT%H:%M:%SZ')

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
        sql = f"FROM user_partner WHERE 1"

        page = 1
        perpage = 20
        sort_field = 'id'
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

            elif param_key == 'query[status]':
                sql += f" AND status = '{request.POST.get('query[status]')}'"
            elif param_key == 'query[generalSearch]' and request.POST.get('query[generalSearch]'):
                search = request.POST.get('query[generalSearch]')
                sql += " AND ( CAST(email AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(full_name AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(title AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(phone AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(company_name AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(requested_at AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%' )"

        with connection.cursor() as cursor:
            cursor.execute(f'SELECT COUNT(*) {sql}')
            row = cursor.fetchone()
            total = row[0]
            pages = math.ceil(total / perpage)

        if sort_field not in ['full_name', 'title', 'email', 'phone', 'company_name', 'status', 'requested_at']:
            sort_field = 'id'
            sort_direction = 'desc'

        sql += f' ORDER BY {sort_field} {sort_direction}'

        sql += ' LIMIT ' + str((page - 1) * perpage) + ', ' + str(perpage)

        # print(request.POST)
        # print(f'SELECT * {sql}')
        rows = Partner.objects.raw(f'SELECT * {sql}')

        items = []
        if sort_direction == 'asc':
            index = (page - 1) * perpage + 1
        else:
            index = total - (page - 1) * perpage
        for row in rows:
            item = {}
            item['id'] = row.id
            item['index'] = index
            item['full_name'] = row.full_name
            item['title'] = row.title
            item['email'] = row.email
            item['phone'] = row.phone
            item['company_name'] = row.company_name
            item['status'] = row.status
            item['requested_at'] = row.requested_at.strftime('%m/%d/%Y')

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
            if not check_permission(request.user, self.permission_label, 'update') and not check_permission(request.user, self.permission_label, 'create'):
                return JsonResponse({'status': 300, 'message': 'You have no permission'})

            params = QueryDict(request.body)
            id = params.get('id')
            status = params.get('status')

            partner = Partner.objects.get(id=id)

            if status == 'Approved':
                if partner.status == 'Approved':
                    return JsonResponse({'status': 200, 'message': f'Already Approved. Code: {partner.code}'})

                if User.objects.filter(username=partner.email).exists():
                    return JsonResponse({'status': 401, 'message': f'Email Already in Use with Sharp Archive'})

                code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
                while Partner.objects.filter(code=code).exists():
                    code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))

                names = partner.full_name.split()
                first_name = names[0]
                if len(names) > 1:
                    last_name = names[-1]
                else:
                    last_name = ''

                user = User.objects.create_user(username=partner.email, email=partner.email, first_name=first_name, last_name=last_name, is_active=1)

                profile = Profile.objects.create(id=user.id, user_id=user.id, user_permission='Partner', phone=partner.phone, business_name=partner.company_name, two_factor=2)
                Security.objects.create(id=user.id, user_id=user.id)

                partner.code = code
                partner.status = status
                partner.approved_at = timezone.now()
                partner.save()

                save_history(request.user, 'Backend', 'Partner Request Approved', id)

                token = PasswordResetTokenGenerator().make_token(user)
                uid = urlsafe_base64_encode(force_bytes((user.id)))

                message = render_to_string('user/email/partner.html', {
                    'url': SITE_URL,
                    'first_name': user.first_name.title(),
                    'business_name': profile.business_name.title(),
                    'partner_code': code,
                    'uid': uid,
                    'token': token,
                    'year': timezone.now().year
                })

                send_mail(GMAIL_HOST_USER, user.email, 'Welcome to Sharp Archive', message, 'html')

                return JsonResponse({'status': 200, 'message': f'Approved. Code: {code}'})

            else:
                if partner.status == 'Refused':
                    return JsonResponse({'status': 200, 'message': 'Already Refused.'})

                partner.status = status
                partner.approved_at = timezone.now()
                partner.save()

                save_history(request.user, 'Backend', 'Partner Request Refused', id)

                return JsonResponse({'status': 200, 'message': 'Web Request Refused'})

        except Exception as e:
            return JsonResponse({'status': 400, 'message': repr(e)})
