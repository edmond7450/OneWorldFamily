import math

from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from api_app.models.user_question import Question
from back_app.models.permission import Permission
from user_app.models.meta import Meta


@method_decorator(staff_member_required(login_url='/user/login/'), name='dispatch')
class QuestionView(ListView):
    template_name = 'back/pages/manage/question.html'
    permission_label = 'Question & Suggestion'

    def get(self, request, *args, **kwargs):
        if 'id' in request.GET and request.GET['id']:
            row = Question.objects.get(id=request.GET['id'])
            data = {
                'id': row.id,
                'email': row.email,
                'full_name': row.full_name,
                'question': row.question,
                'answer': row.answer,
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
        sql = f"FROM user_question WHERE 1"

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

            elif param_key == 'query[generalSearch]' and request.POST.get('query[generalSearch]'):
                search = request.POST.get('query[generalSearch]')
                sql += " AND ( CAST(email AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%'"
                sql += " OR CAST(question AS CHAR CHARACTER SET utf8) COLLATE utf8_general_ci LIKE '%%" + search + "%%' )"

        with connection.cursor() as cursor:
            cursor.execute(f'SELECT COUNT(*) {sql}')
            row = cursor.fetchone()
            total = row[0]
            pages = math.ceil(total / perpage)

        if sort_field not in ['email', 'question', 'created_at']:
            sort_field = 'id'
            sort_direction = 'desc'

        sql += f' ORDER BY {sort_field} {sort_direction}'

        sql += ' LIMIT ' + str((page - 1) * perpage) + ', ' + str(perpage)

        # print(request.POST)
        # print(f'SELECT * {sql}')
        rows = Question.objects.raw(f'SELECT * {sql}')

        items = []
        if sort_direction == 'asc':
            index = (page - 1) * perpage + 1
        else:
            index = total - (page - 1) * perpage
        for row in rows:
            item = {}
            item['id'] = row.id
            item['index'] = index
            item['email'] = row.email
            item['question'] = row.question  # .replace('<', '&lt;').replace('>', '&gt')
            item['created_at'] = row.created_at.strftime('%m/%d/%Y')

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
