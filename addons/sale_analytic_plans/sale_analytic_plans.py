# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import api
from openerp.osv import fields, osv


class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'analytics_id': fields.many2one('account.analytic.plan.instance', 'Analytic Distribution'),
    }


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _columns = {
        'analytics_id': fields.many2one('account.analytic.plan.instance', 'Analytic Distribution'),
    }
    def invoice_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        line_obj = self.pool.get('account.invoice.line')
        create_ids = super(sale_order_line, self).invoice_line_create(cr, uid, ids, context=context)
        i = 0
        for line in self.browse(cr, uid, ids, context=context):
            analytics = line.analytics_id or line.order_id.analytics_id
            if analytics:
                line_obj.write(cr, uid, [create_ids[i]], {'analytics_id': analytics.id})
            i = i + 1
        return create_ids

    @api.multi
    def get_analytics(self):
        return self.analytics_id or self.order_id.analytics_id or self.analytics_default().analytics_id


class stock_move(osv.Model):
    _inherit = 'stock.move'

    def _create_invoice_line_from_vals(self, cr, uid, move, invoice_line_vals, context=None):
        """ set sale line's / sale's analytics distribution on the invoice line, overriding the default distribution """
        sale_line = move.procurement_id.sale_line_id
        analytics = sale_line.analytics_id or sale_line.order_id.analytics_id
        if analytics:
            invoice_line_vals['analytics_id'] = analytics.id
        return super(stock_move, self)._create_invoice_line_from_vals(cr, uid, move, invoice_line_vals, context=context)


class account_analytic_plan_instance(osv.osv):
    _inherit = "account.analytic.plan.instance"

    @api.model
    def default_get(self, fields_list):
        res = super(account_analytic_plan_instance, self).default_get(fields_list)
        self._load_default_journal_data(fields_list, res)
        return res

    def _load_default_journal_data(self, fields_list, res):
        if self._context.get('load_default_journal_data'):
            journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
            if journal_id:
                journal = self.env['account.journal'].browse(journal_id)
                if 'journal_id' in fields_list and journal.analytic_journal_id:
                    res['journal_id'] = journal.analytic_journal_id.id
                if 'plan_id' in fields_list and journal.plan_id:
                    res['plan_id'] = journal.plan_id.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
