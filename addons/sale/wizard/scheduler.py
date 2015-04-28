from openerp import models


class procurement_compute_all(models.TransientModel):
    _inherit = 'procurement.order.compute.all'

    def procure_calculation(self, cr, uid, ids, context=None):
        ctx = context or {}
        sale_obj = self.pool.get('sale.order')
        # should not allow scheduler to run for SOs with no active procurements, cos it would switch to
        # normal mode (non-selective) and would run for all existing procurements
        if sale_obj._is_running_scheduler_for_SO(cr, uid, ctx) and not sale_obj._has_active_procurements(cr, uid, [], ctx):
            return {'type': 'ir.actions.act_window_close'}
        return super(procurement_compute_all, self).procure_calculation(cr, uid, ids, context=ctx)
