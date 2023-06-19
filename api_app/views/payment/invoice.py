import json
import mimetypes
import os.path
import pdfkit

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


def create_invoice(user_id, total, tax, tier_name, tier_number, donation, billing_details):
    now = timezone.now()
    invoice_number = 'OR-IN-' + str(now.timestamp()).replace('.', '')
    invoice_dir = settings.BASE_DIR.joinpath('invoice', str(user_id))
    invoice_path = os.path.join(invoice_dir, invoice_number + '.pdf')
    if not os.path.exists(invoice_dir):
        os.makedirs(invoice_dir)

    user = User.objects.get(id=user_id)

    tier_checked = False
    tiers = json.loads(API_Meta.objects.get(meta_key='tier-cost').meta_value)
    for tier in tiers:
        if tier['value'] == tier_name:
            if tier['price'] * tier_number + donation == total:
                tier_checked = True
                break
            else:
                raise Exception(f"Total does not match. Total: {total}, Tier Name: {tier_name}, Tier Number: {tier_number}, Donation: {donation}")
    if not tier_checked:
        raise Exception(f"Total does not match. Total: {total}, Tier Name: {tier_name}, Tier Number: {tier_number}, Donation: {donation}")

    data = {}
    data['tax'] = '%.2f' % tax
    data['tier_name'] = tier_name
    data['tier_price'] = tier['price']
    data['tier_number'] = tier_number
    if donation > 0:
        data['donation'] = '{0:,.2f}'.format(donation)
    data['total'] = '{0:,.2f}'.format(total)

    data['payer'] = {
        'full_name': billing_details['name'],
        'address_line1': billing_details['address']['line1'] + (' #' + billing_details['address']['line2'] if billing_details['address']['line2'] else ''),
        'address_line2': (billing_details['address']['city'] + ', ' if billing_details['address']['city'] else '')
                         + (billing_details['address']['state'] + ' ' if billing_details['address']['state'] else '')
                         + billing_details['address']['postal_code'] + ' ' + billing_details['address']['country'],
    }
    data['invoice_number'] = invoice_number
    data['date'] = now.strftime('%B %#d, %Y')

    if os.path.exists('/usr/local/bin/wkhtmltopdf'):
        configuration = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
    else:
        configuration = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

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

    subject = 'One World Family Invoice'
    send_mail(GMAIL_HOST_USER, user.email, subject, sourceHtml, 'html')

    # send_mail(GMAIL_HOST_USER, LOG_RECIPIENT_ADDRESS, subject, sourceHtml, 'html')

    return invoice_number, invoice_path
