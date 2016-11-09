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


class ResPartner(models.Model):
    _inherit = ['res.partner']

    ref_type = fields.Selection([
        ('CC','CEDULA DE CIUDADANIA'),
        ('TI','TARJETA DE IDENTIDAD'),
        ('CE','CEDULA DE EXTRANJERIA'),
        ('RC','REGISTRO CIVIL'),
        ('PA','PASAPORTE'),
        ('AS','ADULTO SIN IDENTIFICACION'),
        ('MS','MENOR SIN IDENTIFICACION'),
        ('NU','NUMERO UNICO DE IDENTIFICACION'),
        ], string='Reference Type',required=True, default='CC')
    ref = fields.Char('Internal Reference', select=1, required=True)