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
import logging

_logger= logging.getLogger(__name__)

class HotelReservation(models.Model):

    _inherit = ['hotel.reservation']
	
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                              ('cancel', 'Cancel'), ('done', 'Checked')],
                             'State', readonly=True,
                             default=lambda *a: 'draft') 
    checkin = fields.Datetime('Expected-Date-Arrival', required=True,
                              readonly=True,
                              states={'draft': [('readonly', False)],
                                            'confirm': [('readonly', False)]})
    checkout = fields.Datetime('Expected-Date-Departure', required=True,
                               readonly=True,
                               states={'draft': [('readonly', False)],
                                            'confirm': [('readonly', False)]}) 

    @api.depends('reservation_line')
    def _get_room_lines(self):
        for record in self:
            rooms = []
            for room in record.reservation_line:
            	if room.name:
                	rooms.append(room.name)
            if rooms:
                record.room_number = ','.join(rooms)

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
        res = super(HotelReservation, self).default_get(fields)
        if self._context:
            keys = self._context.keys()
            if 'checkin_date' in keys:
                res.update({'checkin': self._context['checkin_date']})
            if 'room_id' in keys:   #Se crean datos de la habitacion
                roomid = self._context['room_id']
                room = self.env['hotel.room'].search(
                            [('id','=',roomid)])
                if room:
                    product = room.product_id
                    product_uom = product.product_tmpl_id.uom_id.id
                    res['reservation_line'] = [(0,0,{
                        'categ_id': room.categ_id.id,
                        'reserve':[(6,0,[room.id])],
                        'name':product.name,
                        })]
        return res

    room_number = fields.Char('Room No', compute='_get_room_lines')
    accompanist_ids = fields.One2many('hotel.guest.accompanist', 
        'reservation_id', 'Guest Accompanist')


class HotelReservationLine(models.Model):

    _inherit = "hotel_reservation.line"

    @api.onchange('categ_id')
    def on_change_categ(self):
        '''
        When you change categ_id it check checkin and checkout are
        filled or not if not then raise warning
        -----------------------------------------------------------
        @param self: object pointer
        '''
        hotel_room_obj = self.env['hotel.room']
        hotel_room_ids = hotel_room_obj.search([('categ_id', '=',
                                                 self.categ_id.id)])
        assigned = False
        room_ids = []
        if not self.line_id.checkin:
            raise except_orm(_('Warning'),
                             _('Before choosing a room,\n You have to select \
                             a Check in date or a Check out date in \
                             the reservation form.'))
        for room in hotel_room_ids:
            assigned = False
            for line in room.room_reservation_line_ids:
                if(line.check_in >= self.line_id.checkin and
                   line.check_in <= self.line_id.checkout or
                   line.check_out <= self.line_id.checkout and
                   line.check_out >= self.line_id.checkin):
                    assigned = True
            if not assigned:
                room_ids.append(room.id)

        domain = {'reserve': [('id', 'in', room_ids)]}
        return {'domain': domain}

    @api.model
    def create(self, vals):
        _logger.critical('VALS: %s'%vals)
        keys = vals.keys()
        if 'reserve' in keys:
            reserve = eval(vals['reserve']) if type(vals['reserve']) \
                                        == 'str' else vals['reserve']
            if len(reserve[0][2]) >= 2:
                for room_id in reserve[0][2]:
                    line = {}
                    for key in keys:
                        if key == 'reserve':
                            line[key] = [(6,0,[room_id])]
                        else:
                            line[key] = vals[key]
                    line['name'] = self.env['hotel.room'].search(
                                    [('id','=',room_id)]).name
                    reservation_line = super(HotelReservationLine, \
                                            self).create(line)
            else:
                room_id = reserve[0][2]
                vals['name'] = self.env['hotel.room'].search([('id','=',room_id)]).name
                reservation_line = super(HotelReservationLine, self).create(vals)
        for record in reservation_line:
            _logger.critical('RESERVE: %s'%record.reserve)
        return reservation_line