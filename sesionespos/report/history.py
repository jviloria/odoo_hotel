# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import xlwt
from datetime import datetime
from openerp.osv import orm
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.tools.translate import translate, _
import logging
import locale
import pytz
_logger = logging.getLogger(__name__)

_ir_translation_name = 'pos.session.xls'


class pos_session_xls_parser(report_sxw.rml_parse):

	def __init__(self, cr, uid, name, context):
		super(pos_session_xls_parser, self).__init__(cr, uid, name, context=context)
		history_obj = self.pool.get('pos.session')
		self.context = context
		self.cr=cr
		self.uid=uid
		wanted_list = ['product','quantity']
		template_changes = {}
		self.localcontext.update({
			'datetime': datetime,
			'wanted_list': wanted_list,
			'template_changes': template_changes,
			'_': self._,
		})

	def _(self, src):
		lang = self.context.get('lang', 'en_US')
		return translate(self.cr, _ir_translation_name, 'report', lang, src) or src


class pos_session_xls(report_xls):
	def __init__(self, name, table, rml=False, parser=False, header=True,store=False):
		super(pos_session_xls, self).__init__(name, table, rml, parser, header, store)
		# Cell Styles
		_xs = self.xls_styles
		# header
		rh_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
		self.rh_cell_style = xlwt.easyxf(rh_cell_format)
		self.rh_cell_style_center = xlwt.easyxf(rh_cell_format + _xs['center'])
		self.rh_cell_style_right = xlwt.easyxf(rh_cell_format + _xs['right'])
		# lines
		aml_cell_format = _xs['borders_all']
		self.aml_cell_style = xlwt.easyxf(aml_cell_format)
		self.aml_cell_style_center = xlwt.easyxf(aml_cell_format + _xs['center'])
		self.aml_cell_style_date = xlwt.easyxf(aml_cell_format + _xs['left'],num_format_str=report_xls.date_format)
		self.aml_cell_style_decimal = xlwt.easyxf(aml_cell_format + _xs['right'],num_format_str=report_xls.decimal_format)
		# totals
		rt_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
		self.rt_cell_style = xlwt.easyxf(rt_cell_format)
		self.rt_cell_style_right = xlwt.easyxf(rt_cell_format + _xs['right'])
		self.rt_cell_style_decimal = xlwt.easyxf(rt_cell_format + _xs['right'],num_format_str=report_xls.decimal_format)
		# XLS Template
		self.col_specs_template = {
			'location': {
			'header': [1, 20, 'text', _render("_('Location')")],
			'lines': [1, 0, 'text', _render("line['location']")],
			'totals': [1, 0, 'text', None]},
			'product': {
			'header': [1, 42, 'text', _render("_('Product')")],
			'lines': [1, 0, 'text', _render("line['name']+line['description']")],
			'totals': [1, 0, 'text', None]},
			'item_code': {
			'header': [1, 42, 'text', _render("_('Item Code')")],
			'lines': [1, 0, 'text', _render("line['item_code']")],
			'totals': [1, 0, 'text', None]},
			'qty': {
			'header': [1, 42, 'text', _render("_('Quantity')")],
			'lines': [1, 0, 'number', _render("line['qty']")],
			'totals': [1, 0, 'text', None]},
			'total_cost': {
			'header': [1, 42, 'text', _render("_('Total Cost')")],
			'lines': [1, 0, 'number', _render("line['total_cost']")],
			'totals': [1, 0, 'text', None]},
			'location_id': {
			'header': [1, 20, 'text', _render("_('Location')")],
			'lines': [1, 0, 'text', _render("line.location_id.name or ''")],
			'totals': [1, 0, 'text', None]},
			'product_id': {
			'header': [1, 42, 'text', _render("_('Product')")],
			'lines': [1, 0, 'text', _render("line.product_id.name or ''")],
			'totals': [1, 0, 'text', None]},
			'quantity': {
			'header': [1, 42, 'text', _render("_('Quantity')")],
			'lines': [1, 0, 'number', _render("line.quantity")],
			'totals': [1, 0, 'text', None]},
			'progress': {
			'header': [1, 42, 'text', _render("_('Progress')")],
			'lines': [1, 0, 'number', _render("a")],
			'totals': [1, 0, 'text', None]},
		}

	def generate_xls_report(self, _p, _xs, data, objects, wb):
		wanted_list = _p.wanted_list
		self.col_specs_template.update(_p.template_changes)
		_ = _p._
		cr=self.cr
		uid=self.uid
		context=self.context
		# report_name = objects[0]._description or objects[0]._name
		report_name = _("product sales")
		ws = wb.add_sheet(report_name[:31])
		ws.panes_frozen = True
		ws.remove_splits = True
		ws.portrait = 0  # Landscape
		ws.fit_width_to_pages = 1
		row_pos = 0
		fechas=self._fechas(cr,uid,objects,context)

		# set print header/footer
		ws.header_str = self.xls_headers['standard']
		ws.footer_str = self.xls_footers['standard']
		plist=['qty','product']
		# Title
		cell_style = xlwt.easyxf(_xs['xls_title'])
		c_specs = [ ('report_name', 1, 0, 'text', report_name),]
		row_data = self.xls_row_template(c_specs, ['report_name'])
		row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
		row_pos += 1
		
		cell_style = xlwt.easyxf(_xs['xls_title'])
		c_specs = [ ('date', 2, 0, 'text', fechas),]
		row_data = self.xls_row_template(c_specs, ['date'])
		row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
		row_pos += 1
		
		# Column headers
		c_specs = map(lambda x: self.render(x, self.col_specs_template, 'header', render_space={'_': _p._}),plist)
		row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
		row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rh_cell_style,set_column_size=True)
		ws.set_horz_split_pos(row_pos)
		a=0
		# account move lines
		history_ids=[]
		history_data=[]
		
		productos=self._productos(cr,uid,objects,context)
		for line in productos:
			c_specs = map(lambda x: self.render(x, self.col_specs_template, 'lines'),plist)
			row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])	
			row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.aml_cell_style)	
		c_specs = map(lambda x: self.render(x, self.col_specs_template, 'totals'),wanted_list)
		row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
		row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rt_cell_style_right)
	def _fechas(self,cr,uid,ids,context):
		res = {}
		text = " "
		inc=1
		fechas = []
		efechas=[]
		primero = None
		for sesiones in ids:
			d = self._get_fecha(sesiones.start_at)			
		
			day_string = d.strftime('%d-%m-%Y')
			fechas.append(day_string)
			if sesiones.stop_at:
				b = self._get_fecha(sesiones.stop_at)		
				day_string2 = b.strftime('%d-%m-%Y')
				fechas.append(day_string2)
			if sesiones == ids[len(ids)-1]:
				tam = len(fechas)
				for inc in range(1,tam,inc*3+1):
					while inc>0:
						for i in range(inc,tam):
							j=i
							temp=fechas[i]
							fechaini=datetime.strptime(fechas[j-inc], '%d-%m-%Y')
							fechafin=datetime.strptime(temp, '%d-%m-%Y')
							diferencia=fechaini-fechafin
							
							while j>=inc and diferencia.days<0:
						    		fechas[j]=fechas[j-inc]
						    		j=j-inc
							fechas[j]=temp
					    	inc=inc/2
				if len(fechas) > 0:
					if len(fechas)>1:
						text =" Fechas desde: "+fechas[len(fechas)-1]+" hasta "+fechas[0]
					else:
						text = "Fechas desde: "+fechas[0]
				else:
					text = "En Esta Sesion no hay Productos que mostrar"
		return text

	def _get_fecha(self,date):
		local_tz = pytz.timezone("America/Tegucigalpa")
		utc_dt = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
		local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
		return local_dt
	def _productos(self,cr,uid,ids,context):
		res = {}
		text = " "
		inc=1
		productos = []
		primero = None
		for sesiones in ids:
			if primero:
				primero = sesiones.id
			for order in sesiones.order_ids:
				for p in order.lines:
					flag = True
					for i in range(0,len(productos)):
						if p.product_id.id == productos[i]["id"]:
							flag = False
							productos[i]["qty"]= float(productos[i]["qty"]+p.qty)
							i = len(productos)
					if flag:
						if p.product_id.attribute_value_ids.name:
							nombre = " ("+p.product_id.attribute_value_ids.name[0:11]+")"
						else :
							nombre = " "
						productos.append({'id':p.product_id.id,'qty':p.qty,'name':p.product_id.name,'description':nombre})

				
			if sesiones == ids[len(ids)-1]:
				tam = len(productos)
				for inc in range(1,tam,inc*3+1):
					while inc>0:
						for i in range(inc,tam):
							j=i
							temp=productos[i]
							while j>=inc and productos[j-inc]["qty"]<temp["qty"]:
						    		productos[j]=productos[j-inc]
						    		j=j-inc
							productos[j]=temp
					    	inc=inc/2
				if len(productos) > 0:
					for a in productos:
						peso = 23
						combo = 14
						fill = len(str(int(productos[0]["qty"])))
						text= text+ str(str(int(a["qty"])).zfill(fill)+" ").ljust(6, " ") +a["name"][0:peso]+a["description"][0:combo]  + "\n"
				else:
					text = "En Esta Sesion no hay Productos que mostrar"
				
		return productos
	def _user(self,cr,uid,ids,context):
		res = {}
		text = " "
		inc=1
		users = []
		primero = None
		for sesiones in ids:
			temp = [sesiones.user_id.id,sesiones.user_id.name]
			if not temp in users:
				users.append([sesiones.user_id.id,sesiones.user_id.name])
			
		return users
pos_session_xls('report.pos.session.xls','pos.session',parser=pos_session_xls_parser)
