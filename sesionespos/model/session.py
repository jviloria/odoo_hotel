# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from datetime import datetime
import locale
import pytz
class sessionpos(osv.Model):
	
	

	def _fun_diferencia(self,cr,uid,ids,fields,args,context=None):
		res={}
		total=0
		totali=0		
		for session in self.browse(cr,uid,ids,context=context):
			totali=session.cash_register_balance_end
			totalf=session.cash_register_balance_end_real
			for order in session.order_ids:
				flag=False
				for producto in order.lines:
					if producto.product_id.expense_pdt:
					    print producto.product_id.name
					    flag=True
				if flag==True:
					totali-=(order.amount_total*2)
			if totali<0:
			   total=(totali+totalf)
			else:
			   total= (totali - totalf)
			res[session.id]=total
			
			if total<0:
				total=-total
			elif totali<0:
				total=total
			else:
			  total=-total

			if session.state!='closed':
			    self.write(cr,uid,session.id,{'diferencia2':total},context=context)
			    self.write(cr,uid,session.id,{'dn_cierre':totali},context=context)
			    self.write(cr,uid,session.id,{'dn_reportado':totalf},context=context)
		return res



	def _calc_vb(self,cr,uid,ids,fields,args,context=None):
		res={}
		total=0
		flag=False
		for session in self.browse(cr,uid,ids,context=context):
		    total=0
		    for order in session.order_ids:
			flag=False
			for producto in order.lines:
				if producto.product_id.expense_pdt or producto.product_id.income_pdt:
				    flag=True
			if flag==False:
		        	total+=order.amount_total
		    res[session.id]=total				 
		return res


	def _calc_isv(self,cr,uid,ids,fields,args,context=None):
		res={}
		total=0
		for session in self.browse(cr,uid,ids,context=context):
		    for order in session.order_ids:
		        total+=order.amount_tax
		    res[session.id]=total				 
		return res  

	def _calc_subtotal(self,cr,uid,ids,fields,args,context=None):
		res={}
		total=0
		for session in self.browse(cr,uid,ids,context=context):
		    total=session.venta_bruta-session.isv
		    res[session.id]=total				 
		return res 

	def _calc_no_facturas(self,cr,uid,ids,fields,args,context=None):
		res={}
		array=[]
		count=0
		for session in self.browse(cr,uid,ids,context=context):
		    for order in session.order_ids:
		    	count+=1
			array.append(order.name)
	            if array:
		    	res[session.id]=str(count) + " facturas "+array[len(array)-1]+" A "+array[0]
		    						 
		return res

	def _calc_descuento(self,cr,uid,ids,fields,args,context=None):
		res={}
		des_total=0
		for session in self.browse(cr,uid,ids,context=context):
		    for order in session.order_ids:
			descuento=0
			for desc in order.lines:
			    descuento+=desc.price_unit*(desc.discount/100)
			des_total+=descuento
		    res[session.id]=des_total	    				 
		return res


	def _calc_dn_entrante(self,cr,uid,ids,fields,args,context=None):
		res={}
		total=0
		counttotal=0
		for session in self.browse(cr,uid,ids,context=context):
		    for order in session.order_ids:
			total2=0
			count=0
		    	for desc in order.lines:
			    
			    if desc.product_id.income_pdt:
				count+=1
				total2+=desc.price_subtotal_incl	
		     	    total+=total2
			    counttotal+=count
		    res[session.id]=str(counttotal) + " Entrada(s) "+" Total Entradas "+ str(total)						 
		return res

	def _calc_dn_saliente(self,cr,uid,ids,fields,args,context=None):
		res={}
		total=0
		counttotal=0
		for session in self.browse(cr,uid,ids,context=context):
		    for order in session.order_ids:
			total2=0
			count=0
		    	for desc in order.lines:
			    
			    if desc.product_id.expense_pdt:
				count+=1
				total2+=desc.price_subtotal_incl	
		     	    total+=total2
			    counttotal+=count
		    res[session.id]=str(counttotal) + " Salida(s) "+"  Total Salidas "+ str(total)						 
		return res


	def _mas_vendido(self,cr,uid,ids,fields,args,context=None):
		res={}
		total=0
		array3=[]
		array2=[]
		array=[]
		identificador=0
		cant=0
		producto=""
		for session in self.browse(cr,uid,ids,context=context):
			for order in session.order_ids:
				for p in order.lines:
					
					array2.append([p.product_id.id,p.qty])


		for a in array2:
			if a[0] not in array:
				array.append(a[0])

		for x in array:
			temp=0
			for a in array2:
				if a[0]==x:
					temp+=a[1]
			array3.append([x,temp])
	
		for n in array3:
			   
			    if n[1]>cant:
				identificador=n[0]
				cant=n[1]
		
				

		for session in self.browse(cr,uid,ids,context=context):
			for order in session.order_ids:
				for p in order.lines:
				    if identificador==p.product_id.id:
				        producto=p.product_id.name	
			res[session.id]=str(cant)+" "+producto
		return res

	def _productos(self,cr,uid,ids,fields,args,context=None):
		res = {}
		text = " "
		inc=1
		productos = []
		primero = None
		for sesiones in self.browse(cr,uid,ids,context=context):
			if primero:
				primero = sesiones.id
			for order in sesiones.order_ids:
				for p in order.lines:
					flag = True
					for i in range(0,len(productos)):
						if p.product_id.id == productos[i][0]:
							flag = False
							productos[i][1]= float(productos[i][1]+p.qty)
							i = len(productos)
					if flag:
						if p.product_id.attribute_value_ids.name:
							nombre = " ("+p.product_id.attribute_value_ids.name[0:11]+")"
						else :
							nombre = " "
						productos.append([p.product_id.id,p.qty,p.product_id.name, nombre])

				
			if sesiones == self.browse(cr,uid,ids,context=context)[len(self.browse(cr,uid,ids,context=context))-1]:
				tam = len(productos)
				for inc in range(1,tam,inc*3+1):
					while inc>0:
						for i in range(inc,tam):
							j=i
							temp=productos[i]
							while j>=inc and productos[j-inc][1]<temp[1]:
						    		productos[j]=productos[j-inc]
						    		j=j-inc
							productos[j]=temp
					    	inc=inc/2
				if len(productos) > 0:
					for a in productos:
						peso = 23
						combo = 14
						fill = len(str(int(productos[0][1])))
						text= text+ str(str(int(a[1])).zfill(fill)+" ").ljust(6, " ") +a[2][0:peso]+a[3][0:combo]  + "\n"
				else:
					text = "En Esta Sesion no hay Productos que mostrar"
				
			
			if sesiones.id:
				res[sesiones.id]=text
		return res


		
	def _fechas(self,cr,uid,ids,fields,args,context=None):
		res = {}
		text = " "
		inc=1
		fechas = []
		primero = None
		for sesiones in self.browse(cr,uid,ids,context=context):
			
			
			d = self._get_fecha(sesiones.start_at)			
			

			day_string = d.strftime('%Y-%m-%d')

			fechas.append(day_string)
			if sesiones.stop_at:
				b = self._get_fecha(sesiones.stop_at)		
				day_string2 = b.strftime('%d-%m-%Y')
				fechas.append(day_string2)
			if sesiones == self.browse(cr,uid,ids,context=context)[len(self.browse(cr,uid,ids,context=context))-1]:
				tam = len(fechas)
				for inc in range(1,tam,inc*3+1):
					while inc>0:
						for i in range(inc,tam):
							j=i
							temp=fechas[i]
							while j>=inc and fechas[j-inc]<temp:
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
				
			
			if sesiones.id:
				res[sesiones.id]=text
		return res

	def _get_fecha(self,date):
		local_tz = pytz.timezone("America/Tegucigalpa")
		utc_dt = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
		local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
		return local_dt

	def _horas(self,cr,uid,ids,fields,args,context=None):
		res = {}
		horas = []
		text = " "
		inc=1
		for sesiones in self.browse(cr,uid,ids,context=context):
			for order in sesiones.order_ids:
				d = self._get_fecha(order.date_order)			
				day_string = d.strftime('%H:00')
				flag = True
				for i in range(0,len(horas)):
					if horas[i][0] == day_string:					
						flag = False
						horas[i][1]+=1
						horas[i][2]+=order.amount_total
						i = len(horas)
				if flag:
					horas.append([day_string,1,order.amount_total])
			if sesiones == self.browse(cr,uid,ids,context=context)[len(self.browse(cr,uid,ids,context=context))-1]:
				tam = len(horas)
				for inc in range(1,tam,inc*3+1):
					while inc>0:
						for i in range(inc,tam):
							j=i
							temp=horas[i]
							while j>=inc and horas[j-inc][1]<temp[1]:
						    		horas[j]=horas[j-inc]
						    		j=j-inc
							horas[j]=temp
					    	inc=inc/2
				if len(horas) > 0:
					for a in horas:
						fill = len(str(int(horas[0][1])))
						text= text+ " Hora: " + a[0] + " "+str(a[1]).zfill(fill)+" L."+str(a[2])+ "\n"
				else:
					text = "En la Sesion No hay producto Vendido"
				


			res[sesiones.id]= text
		return res


	def _user(self,cr,uid,ids,fields,args,context=None):
		res = {}
		text = " "
		inc=1
		users = []
		primero = None
		for sesiones in self.browse(cr,uid,ids,context=context):
			temp = [sesiones.user_id.id,sesiones.user_id.name]
			if not temp in users:
				users.append([sesiones.user_id.id,sesiones.user_id.name])
			if sesiones == self.browse(cr,uid,ids,context=context)[len(self.browse(cr,uid,ids,context=context))-1]:
				text="USUARIOS\n"
				for a in users:
					text= text+" "+a[1]+"\n"
			if sesiones.id:
				res[sesiones.id]=text
		return res
	

	
		  
	_inherit = 'pos.session'
	_columns = {
	   'validar':fields.boolean(string="Validacion",help="validacion"),
	   'diferencia':fields.function(_fun_diferencia,string="Diferencia"),
	   'diferencia2':fields.float('diferencia2'),
	   'venta_bruta':fields.function(_calc_vb,'venta bruta'),
	   'isv':fields.function(_calc_isv,'ISV'),
	   'subtotal':fields.function(_calc_subtotal,'subtotal'),
	   'nro_facturas':fields.function(_calc_no_facturas,'nro facturas',type="char"),
	   'descuento':fields.function(_calc_descuento,'descuento'),
	   'dinero_entrante':fields.function(_calc_dn_entrante,'dinero entrante',type="char"),
	   'dinero_saliente':fields.function(_calc_dn_saliente,'dinero saliente',type="char"),
	   'dn_cierre':fields.float('dinero Cierre'),
	   'dn_reportado':fields.float('dinero Cierre'),
	   'producto_mvendido':fields.function(_mas_vendido,string="producto mas vendido",type="char"),
	   'productos_vendidos':fields.function(_productos,string="Productos vendidos",type="text"),
		   'hora_venta':fields.function(_horas,string="Hora de ventas",type="text"),
	'fechas':fields.function(_fechas,string="Fechas",type="text"),
		'users':fields.function(_user,string="Usuarios",type="text"),
	}

class product_template(osv.osv):
    _inherit = 'product.template'

    _columns = {
        'income_pdt': fields.boolean('Point of Sale Cash In', help="Check if, this is a product you can use to put cash into a statement for the point of sale backend."),
        'expense_pdt': fields.boolean('Point of Sale Cash Out', help="Check if, this is a product you can use to take cash from a statement for the point of sale backend, example: money lost, transfer to bank, etc."),
        'available_in_pos': fields.boolean('Available in the Point of Sale', help='Check if you want this product to appear in the Point of Sale'), 
        'to_weight' : fields.boolean('To Weigh With Scale', help="Check if the product should be weighted using the hardware scale integration"),
        'pos_categ_id': fields.many2one('pos.category','Point of Sale Category', help="Those categories are used to group similar products for point of sale."),
    }

    _defaults = {
        'to_weight' : False,
        'available_in_pos': True,
    }




	
