from odoo import models, fields, api

class MrpReportingOperationWizard(models.TransientModel):
    _name = 'mrp.reporting.operation.wizard'
    _description = 'MRP Reporting Operation Wizard'

    workorder_id = fields.Many2one('mrp.workorder', string='Work Order', required=True)
    qty_done = fields.Float('Done Quantity', required=True)

    def button_submit(self):
        self.ensure_one()
        workorder = self.workorder_id
        workorder.qty_operation_comp += self.qty_done
        workorder.qty_operation_wip -= self.qty_done
        if workorder.qty_operation_wip < 0:
            workorder.qty_operation_wip = 0
        return {'type': 'ir.actions.act_window_close'}