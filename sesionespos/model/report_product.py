from openerp.osv import osv
from datetime import datetime
import locale
import pytz

class reporte(osv.AbstractModel):
	_name = 'report.sesionespos.report_product'
	def render_html(self, cr, uid, ids, data=None, context=None):
		report_obj = self.pool['report']
		report = report_obj._get_report_from_name(cr, uid, 'sesionespos.report_product')
		fechas=self._fechas(cr,uid,ids,context)
		productos=self._productos(cr,uid,ids,context)
		users=self._user(cr,uid,ids,context)
		docargs = {
		'doc_ids': ids,
		'doc_model': report.model,
		'docs': self.pool[report.model].browse(cr, uid, ids, context=context),
		'products':productos,
		'fecha':fechas,
		'users':users,
		}
		return report_obj.render(cr, uid, ids, 'sesionespos.report_product',docargs, context=context)
        
	def _fechas(self,cr,uid,ids,context):
		res = {}
		text = " "
		inc=1
		fechas = []
		efechas=[]
		primero = None
		for sesiones in self.pool.get('pos.session').browse(cr,uid,ids,context=context):
			
			
			d = self._get_fecha(sesiones.start_at)			
		
			day_string = d.strftime('%d-%m-%Y')
			fechas.append(day_string)
			if sesiones.stop_at:
				b = self._get_fecha(sesiones.stop_at)		
				day_string2 = b.strftime('%d-%m-%Y')
				fechas.append(day_string2)
			if sesiones == self.pool.get('pos.session').browse(cr,uid,ids,context=context)[len(self.browse(cr,uid,ids,context=context))-1]:
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
		for sesiones in self.pool.get('pos.session').browse(cr,uid,ids,context=context):
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

				
			if sesiones == self.pool.get('pos.session').browse(cr,uid,ids,context=context)[len(self.browse(cr,uid,ids,context=context))-1]:
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
		for sesiones in self.pool.get('pos.session').browse(cr,uid,ids,context=context):
			temp = [sesiones.user_id.id,sesiones.user_id.name]
			if not temp in users:
				users.append([sesiones.user_id.id,sesiones.user_id.name])
			
		return users
