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

from openerp import api, models, fields

_logger = logging.getLogger(__name__)


class HotelRoomMaintenance(models.Model):

    _name = "hotel.room.maintenance"
    _description = "Room Maintenance"

    @api.model
    def default_get(self, fields):
        """
        To get default values for the object.
        @param self: The object pointer.
        @param fields: List of fields for which we want default values
        @return: A dictionary which of fields with values.
        """
        if self._context is None:
            self._context = {}
        res = super(HotelRoomMaintenance, self).default_get(fields)
        if self._context:
            keys = self._context.keys()
            if 'date' in keys:
                res.update({'block_start_time': self._context['date']})
            if 'room_no' in keys:
                room_no = self._context['room_no']
                res.update({'room_no': int(room_no)})
        return res

    room_no = fields.Many2one('hotel.room', 'Room No', required=True)
    block_start_time = fields.Datetime('Clean Start Time',
                                       required=True)
    block_end_time = fields.Datetime('Clean End Time', required=True)
    description = fields.Text('Description', default='Maintenance',
    							required=True)