from openerp.osv import osv


class reporte(osv.AbstractModel):
    _name = 'report.sesionespos.report_caja'
    def render_html(self, cr, uid, ids, data=None, context=None):
        report_obj = self.pool['report']
        report = report_obj._get_report_from_name(
            cr, uid, 'sesionespos.report_caja'
        )
        docargs = {
            'doc_ids': ids,
            'doc_model': report.model,
            'docs': self.pool[report.model].browse(
                cr, uid, ids, context=context
            ),
        }
        return report_obj.render(
            cr, uid, ids, 'sesionespos.report_caja',
            docargs, context=context
        )
