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

from openerp import models, fields

_logger = logging.getLogger(__name__)


class HotelRoomMaintenance(models.Model):

    _name = "hotel.room.maintenance"
    _description = "Room Maintenance"

    room_no = fields.Many2one('hotel.room', 'Room No', required=True)
    block_start_time = fields.Datetime('Clean Start Time',
                                       required=True)
    block_end_time = fields.Datetime('Clean End Time', required=True)
    description = fields.Text('Description')