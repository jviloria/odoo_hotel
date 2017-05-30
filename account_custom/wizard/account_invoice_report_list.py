# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from openerp import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class accountWizard(models.TransientModel):
    _name = 'account.invoice.list'
    _description = 'Invoices Report List'


    date_start = fields.Date('Date Start', required=True, default=fields.Datetime.now)
    date_end = fields.Date('Date End', required=True, default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string='User', required=True)

    @api.multi
    def print_report(self, datas=None):
        _logger.critical('REPORT INVOICE PRINTING')
        """
         To get the date and print the report
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return : retrun report
        """
        if self._context is None:
            self._context = {}
        datas = {'ids': self._context.get('active_ids', [])}
        res = self.search_read([], ['date_start', 'date_end', 'user_id'])
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        _logger.critical('HASTA ACA MONOCUCO')
        return self.env['report'].get_action(self, 'account.report_invoice_list', data=datas)
