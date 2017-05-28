# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
import pytz
import time
from openerp import tools
from openerp.osv import osv
from openerp.report import report_sxw
import logging

_logger = logging.getLogger(__name__)

class AccountInvoiceList(report_sxw.rml_parse):

    def _get_account_invoices(self, form):
        inv_obj = self.pool.get('account.invoice')
        user_obj = self.pool.get('res.users')
        data = []
        result = {}
        company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
        user = self.pool['res.users'].browse(self.cr, self.uid, self.uid)
        tz_name = user.tz or self.localcontext.get('tz') or 'UTC'
        user_tz = pytz.timezone(tz_name)
        between_dates = {}
        timestamp = datetime.datetime.strptime(form['date_start'], tools.DEFAULT_SERVER_DATETIME_FORMAT)
        timestamp = user_tz.localize(timestamp).astimezone(pytz.utc)
        date_start = timestamp.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        timestamp = datetime.datetime.strptime(form['date_end'], tools.DEFAULT_SERVER_DATETIME_FORMAT)
        timestamp = user_tz.localize(timestamp).astimezone(pytz.utc)
        date_end = timestamp.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)

        inv_ids = inv_obj.search(self.cr, self.uid, [
            ('date_invoice', '>=', date_start),
            ('date_invoice', '<', date_end),
            ('state', 'in', ['paid']),
            ('company_id', '=', company_id)
        ])
        invoices = inv_obj.browse(self.cr, self.uid, inv_ids)
        return invoices

    # def _get_product_ids(self, orders):
    #     product_ids = []
    #     proccesed = []
    #     for order in orders:
    #         for line in order.order_line:
    #             if line.product_id.id not in proccesed:
    #                 product_ids.append({
    #                     'id': line.product_id.id,
    #                     'product_name': line.name,
    #                     'qty': 0
    #                 })
    #                 proccesed.append(line.product_id.id)
    #     return product_ids

    # def _clear_product_ids(self, product_ids):
    #     for product in product_ids:
    #         product['qty'] = 0

    # def _get_customers(self, orders):
    #     customers = []
    #     proccesed = []
    #     for order in orders:
    #         if order.partner_id.id not in proccesed:
    #             customers.append((order.partner_id.id, order.partner_id.name))
    #             proccesed.append(order.partner_id.id)
    #     return customers

    # def _sum_total_product_qty(self):
    #     orders = self._get_orders()
    #     footer = ['Total']
    #     for product_id in self._get_product_list():
    #         total_qty = 0
    #         for order in orders:
    #             for line in order.order_line:
    #                 if line.product_id.id == product_id:
    #                     total_qty += line.product_uom_qty
    #         footer.append(total_qty)
    #     self.total_product_qty = footer
    #     return footer

    # def _get_orders(self):
    #     return self.orders

    # def _get_product_list(self):
    #     return self.product_list

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
        for key in keys:
            total[key] = 0.0
            for payment in self.payments:
                if key in payment:
                    total[key] += payment[key]
        return [total]

    def _get_header(self, form):
        return ['Partner Name','Folio','Room Number','Cash','Credit Card',
            'Enterprise','Receipt','Detail','Credit Card Brand']

    def _get_folio(self, inv):
        folio = False
        folio_obj = self.pool.get('hotel.folio')
        folio_ids = folio_obj.search(self.cr, self.uid, \
                    [('invoice_status','=','invoiced'), \
                     ('order_id.name','=',inv.origin)])
        if folio_ids:
            folio = folio_obj.browse(self.cr, self.uid, folio_ids)[0]
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

    # def _get_date_start(self, form):
    #     user_obj = self.pool.get('res.users')
    #     data = []
    #     result = {}
    #     company_id = user_obj.browse(self.cr, self.uid, self.uid).company_id.id
    #     user = self.pool['res.users'].browse(self.cr, self.uid, self.uid)
    #     tz_name = user.tz or self.localcontext.get('tz') or 'UTC'
    #     user_tz = pytz.timezone(tz_name)
    #     between_dates = {}
    #     timestamp = datetime.datetime.strptime(form['date_start'], tools.DEFAULT_SERVER_DATETIME_FORMAT)
    #     timestamp = user_tz.localize(timestamp).astimezone(pytz.utc)
    #     date_start = timestamp.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)

    def __init__(self, cr, uid, name, context):
        super(AccountInvoiceList, self).__init__(cr, uid, name, context=context)
        self.payments = []
        self.localcontext.update({
            #'time': time,
            'compute_orders': self._compute_orders,
            'get_header': self._get_header,
            'sum_total_payments': self._sum_total_payments,
        })


class report_AccountInvoiceList(osv.AbstractModel):
    _name = 'report.account.report_invoice_list'
    _inherit = 'report.abstract_report'
    _template = 'account.report_invoice_list'
    _wrapped_report_class = AccountInvoiceList
