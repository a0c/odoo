from openerp import models


class procurement_compute_all(models.TransientModel):
    _inherit = 'procurement.order.compute.all'

    def procure_calculation(self, cr, uid, ids, context=None):
        ctx = context or {}
        if ctx.get('active_model') == 'sale.order' and 'active_ids' in ctx:
            ctx = self.pool.get('sale.order')._scheduler_context(cr, uid, ctx.get('active_ids', []), ctx)
            if not ctx:
                return {'type': 'ir.actions.act_window_close'}
        return super(procurement_compute_all, self).procure_calculation(cr, uid, ids, context=ctx)
