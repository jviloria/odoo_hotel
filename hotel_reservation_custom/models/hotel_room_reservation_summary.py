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
from dateutil.relativedelta import relativedelta
from openerp import api, models, fields

_logger = logging.getLogger(__name__)

class RoomReservationSummary(models.Model):

    _inherit = 'room.reservation.summary'

    date_from = fields.Datetime('Date From', default=datetime.today())
    date_to = fields.Datetime('Date To', default=datetime.today()
                              + relativedelta(days=14))

class HotelSelectorWizard(models.TransientModel):
    _name = 'hotel.selector.wizard'

    check_in = fields.Datetime('Date', required=True)
    room_id = fields.Many2one('hotel.room', 'Room', required=True)

    @api.multi
    def new_reservation(self):
        _logger.critical("NEW RESERVATION RAISED")
        _logger.critical("ROOM ID: %s"%self.room_id)
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'quick.room.reservation',
                'view_type': 'form',
                'view_mode': 'form',
                #'res_id': 'quick_room_reservation_form_view',
                'target': 'new',
            }

    @api.multi
    def new_checkin(self):
        _logger.critical("NEW CHECKIN RAISED")
        room_id = self.room_id.id
        checkin_date = self.check_in
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'hotel.folio',
                'view_type': 'form',
                'view_mode': 'form',
                #'res_id': 'quick_room_reservation_form_view',
                'context': {'room_id': room_id,
                            'checkin_date': checkin_date},
                'target': 'new',
            }

    @api.model
    def default_get(self, fields):
        """
        To get default values for the object.
        @param self: The object pointer.
        @param fields: List of fields for which we want default values
        @return: A dictionary which of fields with values.
        """
        _logger.critical(self._context)
        if self._context is None:
            self._context = {}
        res = super(HotelSelectorWizard, self).default_get(fields)
        if self._context:
            keys = self._context.keys()
            if 'date' in keys:
                res.update({'check_in': self._context['date']})
            if 'room_id' in keys:
                _logger.critical("ROOM ID: %s"%self._context['room_id'])
                roomid = self._context['room_id']
                res.update({'room_id': int(roomid)})
        return res

class QuickRoomReservation(models.TransientModel):
    _inherit = 'quick.room.reservation'

    @api.model
    def default_get(self, fields):
        """
        To get default values for the object.
        @param self: The object pointer.
        @param fields: List of fields for which we want default values
        @return: A dictionary which of fields with values.
        """
        _logger.critical(self._context)
        if self._context is None:
            self._context = {}
        res = super(QuickRoomReservation, self).default_get(fields)
        if self._context:
            keys = self._context.keys()
            if 'date' in keys:
                res.update({'check_in': self._context['date']})
            if 'room_id' in keys:
                _logger.critical("ROOM ID: %s"%self._context['room_id'])
                roomid = self._context['room_id']
                res.update({'room_id': int(roomid)})
        return res

