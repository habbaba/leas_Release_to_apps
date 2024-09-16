from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    qty_equal = fields.Boolean(string='Qty Equal', compute='_compute_qty_equal')
    qty_consuming = fields.Float(string="Partial Qty", digits='Product Unit of Measure', compute='_compute_qty_consuming', store=True)
    over_prod_qty = fields.Float(string="Total Produce Qty", digits='Product Unit of Measure', compute='_compute_over_production_qty')

    @api.depends('move_finished_ids')
    def _compute_over_production_qty(self):
        for production in self:
            finish_moves = production.move_finished_ids.filtered(lambda m: m.product_id == production.product_id and m.state in ('done'))
            qty_consuming = sum(finish_moves.mapped('quantity_done'))
            production.over_prod_qty = qty_consuming

    @api.depends('move_finished_ids', 'over_prod_qty', 'workorder_ids.qty_produced')
    def _compute_qty_consuming(self):
        for production in self:
            last_work_order = self.env['mrp.workorder'].search([('production_id', '=', production.id)], order='id desc',limit=1)
            completed_qty = sum(last_work_order.mapped('qty_operation_comp'))
            production.qty_consuming = completed_qty - production.over_prod_qty

    @api.depends('qty_produced', 'product_qty')
    def _compute_qty_equal(self):
        self.qty_equal = False
        for record in self:
            if record.qty_produced == record.product_qty:
                record.qty_equal = True
            else:
                record.qty_equal = False

    def action_produced_continue(self):
        for production in self:
            if not production.qty_consuming:
                raise ValidationError(_("Please enter partial production quantity in order."))

            for rec in production.move_raw_ids:
                if not rec.quantity_done:
                    raise ValidationError(_("Please enter done quantity in components."))

            finish_moves = production.move_finished_ids.filtered(lambda m: m.product_id == production.product_id and m.state not in ('done', 'cancel'))

            for move in finish_moves:
                if move.quantity_done:
                    continue

                move._set_quantity_done(float_round(production.qty_consuming, precision_rounding=production.product_uom_id.rounding, rounding_method='HALF-UP'))

                # move.move_line_ids.lot_id = production.lot_producing_id

            for move in production.move_raw_ids | production.move_finished_ids:
                move._action_done()

            production.qty_consuming = 0.0

        return True