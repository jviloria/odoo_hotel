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

from openerp import api, models

_logger = logging.getLogger(__name__)

class HotelFolio(models.Model):
    _inherit = 'hotel.folio'

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
                        })]
        return res