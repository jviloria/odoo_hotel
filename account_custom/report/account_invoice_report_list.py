# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
import pytz
from openerp import api, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF, \
    DEFAULT_SERVER_DATETIME_FORMAT as DTF
import logging

_logger = logging.getLogger(__name__)

class ParticularReport(models.AbstractModel):
    _name = 'report.account.report_invoice_list'

    def _get_current_datetime(self):
        now = datetime.now(pytz.timezone('UTC'))
        user = self.env['res.users'].browse(self._uid)
        tz_name = user.tz or self.localcontext.get('tz') or 'UTC'
        user_tz = pytz.timezone(tz_name)
        now = now.astimezone(user_tz)
        return now.strftime(DTF)

    @api.multi
    def render_html(self, data=None):
        _logger.critical(self._ids)

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('account.report_invoice_list')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'data': data,
            'get_current_datetime': self._get_current_datetime,
        }
        return report_obj.render('account.report_invoice_list', docargs)



# from datetime import datetime
# import pytz
# import time
# from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF, \
#     DEFAULT_SERVER_DATETIME_FORMAT as DTF
# from openerp.osv import osv
# from openerp.report import report_sxw
# import logging

# _logger = logging.getLogger(__name__)

# class AccountInvoiceList(report_sxw.rml_parse):

#     def _get_account_invoices(self, form):
#         inv_obj = self.pool.get('account.invoice')
#         user_obj = self.pool.get('res.users')
#         data = []
#         result = {}
#         company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
#         user = self.pool['res.users'].browse(self.cr, self.uid, self.uid)
#         tz_name = user.tz or self.localcontext.get('tz') or 'UTC'
#         user_tz = pytz.timezone(tz_name)
#         between_dates = {}
#         timestamp = datetime.strptime(form['date_start'], DF)
#         timestamp = user_tz.localize(timestamp).astimezone(pytz.utc)
#         date_start = timestamp.strftime(DF)
#         timestamp = datetime.strptime(form['date_end'], DF)
#         timestamp = user_tz.localize(timestamp).astimezone(pytz.utc)
#         date_end = timestamp.strftime(DF)
#         invoice_user = form['user_id'][0]

#         inv_ids = inv_obj.search(self.cr, self.uid, [
#             ('date_invoice', '>=', date_start),
#             ('date_invoice', '<=', date_end),
#             ('state', 'in', ['paid']),
#             ('company_id', '=', company_id),
#             ('user_id', '=', invoice_user)
#             ])
#         invoices = inv_obj.browse(self.cr, self.uid, inv_ids)
#         return invoices

#     def _sum_total_payments(self):
#         keys = []
#         total = {}
#         for payment in self.payments:
#             for key in payment:
#                 if not key in keys:
#                     try:
#                         value = float(payment[key])
#                         keys.append(key)
#                     except:
#                         pass
#         total['Tarjeta'] = 0.0
#         total['Efectivo'] = 0.0
#         for key in keys:
#             total[key] = 0.0
#             for payment in self.payments:
#                 if key in payment:
#                     total[key] += payment[key]
#         return [total]

#     def _get_header(self, form):
#         return ['Partner Name','Folio','Room Number','Cash','Credit Card',
#             'Enterprise','Receipt','Detail','Credit Card Brand']

#     def _get_folio(self, inv):
#         folio = False
#         folio_obj = self.pool.get('hotel.folio')
#         folio_ids = folio_obj.search(self.cr, self.uid, \
#                     [('invoice_status','=','invoiced'), \
#                      ('order_id.name','=',inv.origin)])
#         if folio_ids:
#             folio = folio_obj.browse(self.cr, self.uid, folio_ids)[0]
#         return folio

#     def _get_payments(self, inv):   #Just for one invoice
#         payments = {}
#         for payment in inv.payment_ids:
#             try:
#                 payments[unicode.capitalize(payment.journal_id.name)] += payment.amount
#                 payments['receipts'] = payment.name
#             except:
#                 payments[unicode.capitalize(payment.journal_id.name)] = payment.amount
#                 payments['receipts'] = payment.name
#         cash = payments['Efectivo'] if 'Efectivo' in payments else 0.0
#         bank = payments['Tarjeta'] if 'Tarjeta' in payments else 0.0
#         self.payments.append(payments)
#         return cash, bank, payments['receipts']

#     def _get_cashier_name(self, form):
#         return unicode.capitalize(form['user_id'][1])

#     def _get_cashier_id(self, form):
#         return form['user_id'][0]

#     def _get_current_datetime(self):
#         now = datetime.now(pytz.timezone('UTC'))
#         user = self.pool['res.users'].browse(self.cr, self.uid, self.uid)
#         tz_name = user.tz or self.localcontext.get('tz') or 'UTC'
#         user_tz = pytz.timezone(tz_name)
#         now = now.astimezone(user_tz)
#         return now.strftime(DTF)

#     def _compute_orders(self, form):
#         invoices = self._get_account_invoices(form)
#         inv_list = []
#         for inv in invoices:
#             folio = self._get_folio(inv)
#             if folio:
#                 cash, bank, receipt = self._get_payments(inv)
#                 data = {
#                     'partner': inv.partner_id.name,
#                     'folio': folio.name,
#                     'room_number': folio.room_number,
#                     'cash': cash,
#                     'bank': bank,
#                     'receipt': receipt,
#                     }
#                 inv_list.append(data)
#         return inv_list

#     def __init__(self, cr, uid, name, context):
#         super(AccountInvoiceList, self).__init__(cr, uid, name, context=context)
#         self.payments = []
#         self.cashier = False
#         self.localcontext.update({
#             #'time': time,
#             'compute_orders': self._compute_orders,
#             'get_header': self._get_header,
#             'sum_total_payments': self._sum_total_payments,
#             'get_cashier_id': self._get_cashier_id,
#             'get_cashier_name': self._get_cashier_name,
#             'get_current_datetime': self._get_current_datetime,
#         })


# class report_AccountInvoiceList(osv.AbstractModel):
#     _name = 'report.account.report_invoice_list'
#     _inherit = 'report.abstract_report'
#     _template = 'account.report_invoice_list'
#     _wrapped_report_class = AccountInvoiceList
