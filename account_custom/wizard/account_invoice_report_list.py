# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from openerp.osv import osv, fields
import logging

_logger = logging.getLogger(__name__)

class accountWizard(osv.osv_memory):
    _name = 'account.invoice.list'
    _description = 'Invoices Report List'

    _columns = {
        'date_start': fields.datetime('Date Start', required=True),
        'date_end': fields.datetime('Date End', required=True),
    }
    _defaults = {
        'date_start': fields.datetime.now,
        'date_end': fields.datetime.now,
    }

    def print_report(self, cr, uid, ids, context=None):
        _logger.critical('REPORT INVOICE PRINTING')
        """
         To get the date and print the report
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return : retrun report
        """
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['date_start', 'date_end'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return self.pool['report'].get_action(cr, uid, [], 'account.report_invoice_list', data=datas, context=context)
