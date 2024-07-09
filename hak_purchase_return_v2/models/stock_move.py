from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    reason_for_return = fields.Many2one(comodel_name='purchase.return.reason', string='Reasons', readonly=True)
    return_notes = fields.Text(string="Return Notes", store=True)
