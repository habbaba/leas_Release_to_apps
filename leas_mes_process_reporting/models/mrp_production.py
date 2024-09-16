from odoo import models, fields

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    qty_operation_wip = fields.Float('In-Process Quantity', default=0.0)
    qty_operation_comp = fields.Float('Completed Quantity', default=0.0)