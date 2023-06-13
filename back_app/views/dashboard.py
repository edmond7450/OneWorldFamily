import json

from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db import connection
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import TemplateView

from back_app.models.permission import Permission
from user_app.models.meta import Meta
from user_app.models.profile import Profile, USER_STATUS


class DashboardView(TemplateView):
    template_name = 'back/index.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/user/login/')

        today = timezone.now()
        start_date = (today - relativedelta(months=1))
        delta = today - start_date
        try:
            days = [(start_date + relativedelta(days=i)).strftime('%b %-d, %Y') for i in range(delta.days + 1)]
        except:
            days = [(start_date + relativedelta(days=i)).strftime('%b %#d, %Y') for i in range(delta.days + 1)]
        categories = []
        series = []
        for day in days:
            categories.append(day)
            series.append(0)

        start_date = start_date.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        first_date = datetime(today.year, today.month, 1).date()

        data = {}
        chart_data = {}
        with connection.cursor() as cursor:
            sql = f"SELECT DATE_FORMAT(created_at, '%b %e, %Y'), SUM(net) FROM invoice, user_profile " \
                  f"WHERE DATE(created_at) >= CAST('{start_date}' AS DATE) AND DATE(created_at) <= CAST('{end_date}' AS DATE) " \
                  f"AND invoice.user_id = user_profile.user_id AND user_profile.status != {USER_STATUS.INTERNAL} " \
                  f"GROUP BY DATE_FORMAT(created_at, '%b %e, %Y') ORDER BY invoice.id"
            cursor.execute(sql)
            rows = cursor.fetchall()

            new = 0
            min_y = 0
            max_y = 0
            income_series = series.copy()
            for row in rows:
                if (datetime.strptime(row[0], '%b %d, %Y').date() >= first_date):
                    new += row[1]
                if row[1] < min_y:
                    min_y = row[1]
                if row[1] > max_y:
                    max_y = row[1]
                income_series[categories.index(row[0])] = row[1]

            # total = Invoice.objects.all().aggregate(Sum('net'))['net__sum']
            sql = f"SELECT SUM(net) FROM invoice, user_profile " \
                  f"WHERE invoice.user_id = user_profile.user_id AND user_profile.status != {USER_STATUS.INTERNAL}"
            cursor.execute(sql)
            row = cursor.fetchone()
            total = row[0]

            data['income'] = {
                'total': '%.2f' % total if total else '0.00',
                'new': '%.2f' % new,
            }
            chart_data['income'] = {
                'min_y': int(min_y),
                'max_y': max_y if max_y > 1000 else int(max_y * 1.2),
                'categories': categories,
                'series': income_series
            }

            sql = f"SELECT DATE_FORMAT(date_joined, '%b %e, %Y'), COUNT(*) FROM auth_user " \
                  f"WHERE id IN (SELECT user_id FROM user_profile WHERE payment_status != '' AND status != {USER_STATUS.INTERNAL}) " \
                  f"AND DATE(date_joined) >= CAST('{start_date}' AS DATE) AND DATE(date_joined) <= CAST('{end_date}' AS DATE) " \
                  f"GROUP BY DATE_FORMAT(date_joined, '%b %e, %Y') ORDER BY id"
            cursor.execute(sql)
            rows = cursor.fetchall()

            new = 0
            max_y = 0
            user_series = series.copy()
            for row in rows:
                if (datetime.strptime(row[0], '%b %d, %Y').date() >= first_date):
                    new += row[1]
                if row[1] > max_y:
                    max_y = row[1]
                user_series[categories.index(row[0])] = row[1]

            data['user'] = {
                'total': Profile.objects.filter(~Q(payment_status=''), status=USER_STATUS.VERIFIED).count(),
                'new': new,
            }
            chart_data['user'] = {
                'max_y': max_y if max_y > 1000 else int(max_y * 1.2),
                'categories': categories,
                'series': user_series
            }

            sql = f"SELECT DATE_FORMAT(created_at, '%b %e, %Y'), COUNT(*) FROM back_history, user_profile " \
                  f"WHERE action = 'Log In' AND back_history.user_id = user_profile.user_id AND user_profile.status != {USER_STATUS.INTERNAL} AND " \
                  f"DATE(created_at) >= CAST('{start_date}' AS DATE) AND DATE(created_at) <= CAST('{end_date}' AS DATE) " \
                  f"GROUP BY DATE_FORMAT(created_at, '%b %e') ORDER BY back_history.id"
            cursor.execute(sql)
            rows = cursor.fetchall()

            new = 0
            max_y = 0
            login_series = series.copy()
            today = today.date()
            for row in rows:
                if (datetime.strptime(row[0], '%b %d, %Y').date() == today):
                    new = row[1]
                if row[1] > max_y:
                    max_y = row[1]
                login_series[categories.index(row[0])] = row[1]

            # total = History.objects.filter(action='Log In').count()
            sql = f"SELECT COUNT(*) FROM back_history, user_profile " \
                  f"WHERE action = 'Log In' AND back_history.user_id = user_profile.user_id AND user_profile.status != {USER_STATUS.INTERNAL}"
            cursor.execute(sql)
            row = cursor.fetchone()
            total = row[0]

            data['login'] = {
                'total': total,
                'new': new
            }
            chart_data['login'] = {
                'max_y': max_y if max_y > 1000 else int(max_y * 1.2),
                'categories': categories,
                'series': login_series
            }

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

        return render(request, self.template_name, {'permissions': permissions, 'data': data, 'chart_data': json.dumps(chart_data)})
