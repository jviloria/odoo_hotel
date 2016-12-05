# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    John W. Viloria Amaris <john.viloria.amaris@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from datetime import datetime

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp import api, models, fields


_logger = logging.getLogger(__name__)

class HotelFolio(models.Model):
    _inherit = 'hotel.folio'

    @api.depends('room_lines')
    def _get_room_lines(self):
        for record in self:
            rooms = []
            for room in record.room_lines:
                rooms.append(room.product_id.name)
            if rooms:
                record.room_number = ','.join(rooms)

    room_number = fields.Char('Room No', compute='_get_room_lines')
    
    @api.model
    def default_get(self, fields):
        """
        To get default values for the object.
        @param self: The object pointer.
        @param fields: List of fields for which we want default values
        @return: A dictionary which of fields with values.
        """
        _logger.critical(self._context)
        _logger.critical("FIELDS: %s"%fields)
        if self._context is None:
            self._context = {}
        res = super(HotelFolio, self).default_get(fields)
        if self._context:
            keys = self._context.keys()
            if 'checkin_date' in keys:
                res.update({'checkin_date': self._context['checkin_date']})
            if 'room_id' in keys:   #Se crean datos de la habitacion
                _logger.critical("ROOM ID: %s"%self._context['room_id'])
                roomid = self._context['room_id']
                room = self.env['hotel.room'].search(
                            [('id','=',roomid)])
                if room:
                    product = room.product_id
                    product_uom = product.product_tmpl_id.uom_id.id
                    _logger.critical('PRODUCT UOM:%s'%product_uom)
                    res['room_lines'] = [(0,0,{
                        'product_id':product.id,
                        'product_uom':product_uom,
                        'checkin_date':self._context['checkin_date'],
                        'checkout_date':self._context['checkin_date'],
                        'name':product.name,
                        'price_unit': product.lst_price,
                        })]
        return res
		
    @api.onchange('checkout_date', 'checkin_date')
    def onchange_dates(self):
        '''
        This mathod gives the duration between check in and checkout
        if customer will leave only for some hour it would be considers
        as a whole day.If customer will check in checkout for more or equal
        hours, which configured in company as additional hours than it would
        be consider as full days
        --------------------------------------------------------------------
        @param self: object pointer
        @return: Duration and checkout_date
        '''
        company_obj = self.env['res.company']
        configured_addition_hours = 0
        company_ids = company_obj.search([])
        if company_ids.ids:
            configured_addition_hours = company_ids[0].additional_hours
        myduration = 0
        chckin = self.checkin_date
        chckout = self.checkout_date
        if chckin and chckout:
            server_dt = DTF
            chkin_dt = datetime.strptime(chckin, server_dt)
            chkout_dt = datetime.strptime(chckout, server_dt)
            dur = chkout_dt - chkin_dt
            sec_dur = dur.seconds
            if (not dur.days and not sec_dur) or (dur.days and not sec_dur):
                myduration = dur.days
            else:
                myduration = dur.days + 1
            if configured_addition_hours > 0:
                additional_hours = abs((dur.seconds / 60) / 60)
                if additional_hours >= configured_addition_hours:
                    myduration += 1
            
            sum = 0
            for room in self.room_lines:
                room.checkin_date = chkin_dt
                room.checkout_date = chckout 
                room.price_subtotal=myduration*room.price_unit
                sum += room.price_subtotal
        
            self.duration = myduration
            self.amount_untaxed = sum
            self.amount_total = self.amount_untaxed + self.amount_tax
