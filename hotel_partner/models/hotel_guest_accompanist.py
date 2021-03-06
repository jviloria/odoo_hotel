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

from openerp import models, fields


class HotelGuestAccompanist(models.Model):
    '''
    Accompanying the guest.
    '''
    _name = 'hotel.guest.accompanist'

    accompanist_id = fields.Many2one('res.partner', 
        string='Guest Accompanist')
    reservation_id = fields.Many2one('hotel.reservation', 
        string='Reservation ID')
    date = fields.Date(string='Date', 
        help='Date')
