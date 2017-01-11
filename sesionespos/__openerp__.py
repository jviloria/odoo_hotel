# -*- coding: utf-8 -*-
{	
	'name' : 'sesionespos',
	'author': 'Odoo Honduras, Hernan Pinzon',
	'category': 'pos',
	'summary': 'sessiones pos',
	'description': """Modulo para revision de pos """,
	'data':[
	    'views/session_view.xml',
	    'views/sesionespos_report1.xml',
	    'views/reporte1.xml',
	    'views/reporte2.xml',
	    'views/reporte3.xml',
	    'views/layouts.xml',
	    'report/pos_session_xls.xml',
	    ],
	'depends': ['base','point_of_sale','report_xls','sale_stock'],
	'init_xml': [],
    	'update_xml': [],
    	'installable': True,

}
