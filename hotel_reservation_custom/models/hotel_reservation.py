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

from openerp import api, models, fields


class HotelReservation(models.Model):

    _inherit = ['hotel.reservation']

    @api.depends('reservation_line')
    def _get_room_lines(self):
        for record in self:
            rooms = []
            for room in record.reservation_line:
            	if room.name:
                	rooms.append(room.name)
            if rooms:
                record.room_number = ','.join(rooms)

    room_number = fields.Char('Room No', compute='_get_room_lines')
    accompanist_ids = fields.One2many('hotel.guest.accompanist', 
        'reservation_id', 'Guest Accompanist')