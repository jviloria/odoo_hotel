# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import osv, fields
import logging

_logger = logging.getLogger(__name__)

class posDetails(osv.osv_memory):
    _inherit = 'pos.details'


    _columns = {
        'grouped': fields.boolean('Grouped')
    }

    def print_report(self, cr, uid, ids, context=None):
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
        res = self.read(cr, uid, ids, ['date_start', 'date_end', 'user_ids', 'grouped'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return self.pool['report'].get_action(cr, uid, [], 'point_of_sale.report_detailsofsales', data=datas, context=context)
