# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import osv, fields


class pos_details(osv.osv_memory):
    _inherit = 'pos.details'


    _columns = {
        'grouped': fields.boolean('Grouped')
    }
