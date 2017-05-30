# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
import pytz
from openerp import api, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF, \
    DEFAULT_SERVER_DATETIME_FORMAT as DTF

import logging

_logger = logging.getLogger(__name__)

class PaidInvoiceReport(models.AbstractModel):
    _name = 'report.account.report_invoice_list'

    def _formatlang(self, value):
        return formatLang(value, digits=2)

    def _get_account_invoices(self, form):
        inv_obj = self.env['account.invoice']
        user_obj = self.env['res.users']
        data = []
        result = {}
        user = user_obj.browse(self._uid)
        company_id = user.company_id.id
        tz_name = user.tz or self.localcontext.get('tz') or 'UTC'
        user_tz = pytz.timezone(tz_name)
        between_dates = {}
        timestamp = datetime.strptime(form['date_start'], DF)
        timestamp = user_tz.localize(timestamp).astimezone(pytz.utc)
        date_start = timestamp.strftime(DF)
        timestamp = datetime.strptime(form['date_end'], DF)
        timestamp = user_tz.localize(timestamp).astimezone(pytz.utc)
        date_end = timestamp.strftime(DF)
        invoice_user = form['user_id'][0]

        invoices = inv_obj.search([
            ('date_invoice', '>=', date_start),
            ('date_invoice', '<=', date_end),
            ('state', 'in', ['paid']),
            ('company_id', '=', company_id),
            ('user_id', '=', invoice_user)
            ])
        return invoices

    def _get_current_datetime(self):
        now = datetime.now(pytz.timezone('UTC'))
        user = self.env['res.users'].browse(self._uid)
        tz_name = user.tz or self.localcontext.get('tz') or 'UTC'
        user_tz = pytz.timezone(tz_name)
        now = now.astimezone(user_tz)
        return now.strftime(DTF)

    def _get_cashier_name(self, form):
        return unicode.capitalize(form['user_id'][1])

    def _get_header(self, form):
        return ['Nombre','Folio','Hab','Efectivo',u'Tarj. Crédito',
            'Empresa','Recibo','Detalle','Tipo Tarj']

    def _get_folio(self, inv):
        folio = False
        folio_obj = self.env['hotel.folio']
        folio_ids = folio_obj.search(
                    [('invoice_status','=','invoiced'), \
                     ('order_id.name','=',inv.origin)])
        if folio_ids:
            folio = folio_ids[0]
        return folio

    def _get_payments(self, inv):   #Just for one invoice
        payments = {}
        for payment in inv.payment_ids:
            try:
                payments[unicode.capitalize(payment.journal_id.name)] += payment.amount
                payments['receipts'] = payment.name
            except:
                payments[unicode.capitalize(payment.journal_id.name)] = payment.amount
                payments['receipts'] = payment.name
        cash = payments['Efectivo'] if 'Efectivo' in payments else 0.0
        bank = payments['Tarjeta'] if 'Tarjeta' in payments else 0.0
        self.payments.append(payments)
        return cash, bank, payments['receipts']

    def _sum_total_payments(self):
        keys = []
        total = {}
        for payment in self.payments:
            for key in payment:
                if not key in keys:
                    try:
                        value = float(payment[key])
                        keys.append(key)
                    except:
                        pass
        total['Tarjeta'] = 0.0
        total['Efectivo'] = 0.0
        for key in keys:
            total[key] = 0.0
            for payment in self.payments:
                if key in payment:
                    total[key] += payment[key]
        return [total]

    def _compute_orders(self, form):
        invoices = self._get_account_invoices(form)
        inv_list = []
        for inv in invoices:
            folio = self._get_folio(inv)
            if folio:
                cash, bank, receipt = self._get_payments(inv)
                data = {
                    'partner': inv.partner_id.name,
                    'folio': folio.name,
                    'room_number': folio.room_number,
                    'cash': cash,
                    'bank': bank,
                    'receipt': receipt,
                    }
                inv_list.append(data)
        return inv_list

    @api.multi
    def render_html(self, data=None):
        self.payments = []
        self.invoices = self._get_account_invoices(data['form'])
        inv_ids = [inv.id for inv in self.invoices]
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('account.report_invoice_list')
        docargs = {
            'doc_ids': inv_ids[0],
            'doc_model': report.model,
            'docs': self.invoices[0],
            'data': data,
            'get_current_datetime': self._get_current_datetime,
            'get_cashier_name': self._get_cashier_name,
            'get_header': self._get_header,
            'compute_orders': self._compute_orders,
            'sum_total_payments': self._sum_total_payments,
        }
        return report_obj.render('account.report_invoice_list', docargs)
