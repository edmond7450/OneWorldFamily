import calendar
import json
import mimetypes
import os.path
import pdfkit

from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse
from django.template.loader import get_template, render_to_string
from django.utils import timezone
from rest_framework.views import APIView
from wsgiref.util import FileWrapper

from my_settings import GMAIL_HOST_USER, LOG_RECIPIENT_ADDRESS
from api_app.models.api_meta import API_Meta
from api_app.models.invoice import Invoice
from user_app.views.send_email import send_mail


class InvoiceView(APIView):
    def get(self, request):
        data = []
        rows = Invoice.objects.filter(user_id=request.user.id).order_by('-id')
        if Invoice.objects.filter(user_id=request.user.id, total=0).count() == 0:
            for row in rows:
                item = {}
                item['id'] = row.id
                item['invoiceNumber'] = row.invoice_number
                item['total'] = '${0:,.2f}'.format(row.total)
                item['createdAt'] = row.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                data.append(item)

            return JsonResponse({'status': 200, 'success': True, 'message': 'Successfully Loaded', 'data': data})

        else:
            balance = 0.0
            for row in rows:
                item = {}
                item['id'] = row.id
                item['invoiceNumber'] = row.invoice_number
                if row.total:
                    balance += row.total
                    item['total'] = '${0:,.2f}'.format(row.total)
                else:
                    balance -= float(row.description.replace(',', ''))
                    item['total'] = f'(${row.description})'
                item['createdAt'] = row.created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                data.append(item)

            if balance >= 0:
                balance = '${0:,.2f}'.format(balance)
            else:
                balance = '-${0:,.2f}'.format(-balance)

            return JsonResponse({'status': 200, 'success': True, 'message': 'Successfully Loaded', 'data': data, 'balance': balance})

    def post(self, request):
        try:
            invoice_path = Invoice.objects.get(id=request.data['id'], user_id=request.user.id).invoice_path

            mime_type, _ = mimetypes.guess_type(invoice_path)
            response = FileResponse(FileWrapper(open(invoice_path, 'rb')), content_type=mime_type)
            response['Content-Disposition'] = "attachment; filename=%s" % os.path.basename(invoice_path)
            return response
        except:
            raise Http404


def get_invoice_data(user, current_date=timezone.now().date()):
    profile = user.profile

    data = {}
    cost_value = json.loads(API_Meta.objects.get(meta_key='estimated-cost').meta_value)
    data['baseCost'] = '%.2f' % cost_value['baseCost']
    data['feedCost'] = '%.2f' % cost_value['feedCost']

    arrears = {}
    arrears_startDate, arrears_endDate, advance_startDate, advance_endDate = get_cycle(profile.membership_date, current_date)

    advance = {}
    advance['periodStartDate'] = advance_startDate.strftime('%B %#d, %Y')
    advance['periodEndDate'] = advance_endDate.strftime('%B %#d, %Y')

    feeds = {}
    numberFeeds = 0
    for account_id in feeds:
        if feeds[account_id][0] and feeds[account_id][1] is None:
            numberFeeds += 1

    advance['numberFeeds'] = numberFeeds  # len(Account.objects.filter(user=user, date_closed=None))
    advance['archivingCost'] = '%.2f' % (float(data['feedCost']) * advance['numberFeeds'])
    advance['advanceTotalCost'] = '%.2f' % (float(data['baseCost']) + float(advance['archivingCost']))
    data['advance'] = advance

    data['subtotal'] = '%.2f' % (float(advance['advanceTotalCost']) + (float(arrears['arrearsTotalCost']) if 'arrearsTotalCost' in arrears else 0))

    if profile.membership_date == arrears_startDate:
        data['isSecondInvoice'] = True

    return data


# If a month doesn't have the anchor day, the subscription will be billed on the last day of the month.
def get_cycle(membership_date, current_date=timezone.now().date()):
    current_month_last_day = calendar.monthrange(current_date.year, current_date.month)[1]
    diff_months = (current_date.year - membership_date.year) * 12 + current_date.month - membership_date.month
    if membership_date.day <= current_date.day or current_date.day == current_month_last_day:
        diff_months += 1

    current_periodStartDate = membership_date + relativedelta(months=diff_months - 1)
    current_periodEndDate = membership_date + relativedelta(months=diff_months) - relativedelta(days=1)

    past_periodStartDate = membership_date + relativedelta(months=diff_months - 2)
    past_periodEndDate = current_periodStartDate - relativedelta(days=1)

    return past_periodStartDate, past_periodEndDate, current_periodStartDate, current_periodEndDate


# If a month doesn't have the anchor day, the subscription will be billed on the first day of the next month.
def get_cycle1(membership_start_day, current_date):
    this_month_start_date = datetime(current_date.year, current_date.month, 1)
    this_month_last_day = calendar.monthrange(this_month_start_date.year, this_month_start_date.month)[1]
    past_month_start_date = this_month_start_date - relativedelta(months=1)
    past_month_last_day = calendar.monthrange(past_month_start_date.year, past_month_start_date.month)[1]

    if current_date.day < membership_start_day:
        past2_month_start_date = past_month_start_date - relativedelta(months=1)
        past2_month_last_day = calendar.monthrange(past2_month_start_date.year, past2_month_start_date.month)[1]

        if past2_month_last_day < membership_start_day - 1:
            past_periodStartDate = past_month_start_date
        else:
            past_periodStartDate = past2_month_start_date.replace(day=membership_start_day)

        if past_month_last_day < membership_start_day - 1:
            past_periodEndDate = past_month_start_date.replace(day=past_month_last_day)
            current_periodStartDate = this_month_start_date
        else:
            past_periodEndDate = past_month_start_date.replace(day=membership_start_day) - relativedelta(days=1)
            current_periodStartDate = past_month_start_date.replace(day=membership_start_day)

        if this_month_last_day < membership_start_day - 1:
            current_periodEndDate = this_month_start_date.replace(day=this_month_last_day)
        else:
            current_periodEndDate = this_month_start_date.replace(day=membership_start_day) - relativedelta(days=1)
    else:
        next_month_start_date = this_month_start_date + relativedelta(months=1)
        next_month_last_day = calendar.monthrange(next_month_start_date.year, next_month_start_date.month)[1]

        if past_month_last_day < membership_start_day - 1:
            past_periodStartDate = this_month_start_date
        else:
            past_periodStartDate = past_month_start_date.replace(day=membership_start_day)

        past_periodEndDate = this_month_start_date.replace(day=membership_start_day) - relativedelta(days=1)
        current_periodStartDate = this_month_start_date.replace(day=membership_start_day)

        if next_month_last_day < membership_start_day - 1:
            current_periodEndDate = next_month_start_date.replace(day=next_month_last_day)
        else:
            current_periodEndDate = next_month_start_date.replace(day=membership_start_day) - relativedelta(days=1)

    return past_periodStartDate, past_periodEndDate, current_periodStartDate, current_periodEndDate


def create_invoice(user_id, subtotal, tax, current_date, billing_details, is_due=False):
    now = timezone.now()
    invoice_number = 'SA-IN-' + str(now.timestamp()).replace('.', '')
    invoice_dir = settings.ARCHIVE_DIR.joinpath('invoice', str(user_id))
    invoice_path = os.path.join(invoice_dir, invoice_number + '.pdf')
    if not os.path.exists(invoice_dir):
        os.makedirs(invoice_dir)

    user = User.objects.get(id=user_id)

    data = get_invoice_data(user, current_date)

    if float(data['subtotal']) != subtotal:
        raise Exception(f"Subtotal does not match. Old: {subtotal}, Current: {data['subtotal']}")

    data['tax'] = '%.2f' % tax
    data['total'] = '{0:,.2f}'.format(subtotal + tax)

    data['payer'] = {
        'full_name': billing_details['name'],
        'address_line1': billing_details['address']['line1'] + (' #' + billing_details['address']['line2'] if billing_details['address']['line2'] else ''),
        'address_line2': (billing_details['address']['city'] + ', ' if billing_details['address']['city'] else '')
                         + (billing_details['address']['state'] + ' ' if billing_details['address']['state'] else '')
                         + billing_details['address']['postal_code'] + ' ' + billing_details['address']['country'],
    }
    data['invoice_number'] = invoice_number
    data['date'] = now.strftime('%B %#d, %Y')  # data['advance']['periodStartDate']

    if os.path.exists('/usr/local/bin/wkhtmltopdf'):
        configuration = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
    else:
        configuration = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    if not is_due:
        sourceHtml = render_to_string('user/email/invoice_content.html', {'data': data})
        options = {
            'encoding': 'utf-8',
            'page-size': 'Letter',
            'margin-left': '0',
            'margin-right': '0',
            'margin-top': '48',
            'header-html': get_template('user/email/invoice_header.html').origin,
            'footer-html': get_template('user/email/invoice_footer.html').origin
        }
        pdfkit.from_string(sourceHtml, invoice_path, configuration=configuration, options=options)

        sourceHtml = render_to_string('user/email/invoice.html', {'data': data})
    else:
        data['due_date'] = (datetime.strptime(data['date'], '%B %d, %Y') + relativedelta(days=10)).strftime('%B %#d, %Y')
        sourceHtml = render_to_string('user/email/invoice-due_content.html', {'data': data})
        options = {
            'encoding': 'utf-8',
            'page-size': 'Letter',
            'margin-left': '0',
            'margin-right': '0',
            'margin-top': '48',
            'header-html': get_template('user/email/invoice_header.html').origin,
            'footer-html': get_template('user/email/invoice-due_footer.html').origin
        }
        pdfkit.from_string(sourceHtml, invoice_path, configuration=configuration, options=options)

        sourceHtml = render_to_string('user/email/invoice-due.html', {'data': data})

    subject = 'Sharp Archive Invoice'
    send_mail(GMAIL_HOST_USER, user.email, subject, sourceHtml, 'html')

    send_mail(GMAIL_HOST_USER, LOG_RECIPIENT_ADDRESS, subject, sourceHtml, 'html')

    return invoice_number, invoice_path


def create_refund(user_id, stripe_payment_intent_id, total, forced=False):
    now = timezone.now()
    invoice_number = 'SA-RE-' + str(now.timestamp()).replace('.', '')
    invoice_dir = settings.ARCHIVE_DIR.joinpath('invoice', str(user_id))
    invoice_path = os.path.join(invoice_dir, invoice_number + '.pdf')

    user = User.objects.get(id=user_id)

    invoice_data = get_invoice_data(user)
    invoice = Invoice.objects.filter(stripe_payment_intent_id=stripe_payment_intent_id).first()

    daysCycle = (datetime.strptime(invoice_data['advance']['periodEndDate'], '%B %d, %Y') - datetime.strptime(invoice_data['advance']['periodStartDate'], '%B %d, %Y')).days + 1
    daysLeft = (datetime.strptime(invoice_data['advance']['periodEndDate'], '%B %d, %Y').date() - now.date()).days

    data = {}
    data['invoice_number'] = invoice_number
    data['date'] = now.strftime('%B %#d, %Y')
    data['periodStartDate'] = invoice_data['advance']['periodStartDate']
    data['periodEndDate'] = invoice_data['advance']['periodEndDate']
    data['daysCycle'] = daysCycle
    data['feedCost'] = invoice_data['feedCost']
    data['dailyCostPerFeed'] = '%.3f' % (float(data['feedCost']) / daysCycle)
    data['daysLeft'] = daysLeft
    data['numberFeeds'] = invoice_data['advance']['numberFeeds']
    subtotal = round(float(data['dailyCostPerFeed']) * data['daysLeft'] * data['numberFeeds'], 2)
    tax = round(subtotal / invoice.subtotal * invoice.tax, 2)

    if forced:
        subtotal = invoice.subtotal
        tax = invoice.tax

    data['subtotal'] = '{0:,.2f}'.format(subtotal)
    data['tax'] = '%.2f' % (tax)
    data['total'] = '{0:,.2f}'.format(subtotal + tax)

    if subtotal + tax != total:
        raise Exception(f"Total does not match. Old: {total}, Current: {data['total']}")

    profile = user.profile
    address_components = json.loads(profile.address_components)
    data['payer'] = {
        'full_name': user.get_full_name(),
        'address_line1': address_components['street_number'] + ' ' + address_components['route'],
        'address_line2': address_components['city'] + (', ' + address_components['state'] if address_components['state'] else ',') + ' ' + address_components['postal_code'] + ' ' + address_components['country'],
    }

    sourceHtml = render_to_string('user/email/refund.html', {'data': data})
    if os.path.exists('/usr/local/bin/wkhtmltopdf'):
        configuration = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
    else:
        configuration = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    options = {
        'encoding': 'utf-8',
        'page-size': 'Letter'
    }
    pdfkit.from_string(sourceHtml, invoice_path, configuration=configuration, options=options)

    subject = 'Sharp Archive Refund'
    send_mail(GMAIL_HOST_USER, user.email, subject, sourceHtml, 'html')

    # send to manager too
    send_mail(GMAIL_HOST_USER, LOG_RECIPIENT_ADDRESS, subject, sourceHtml, 'html')

    return invoice_number, invoice_path, subtotal, tax
