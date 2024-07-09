from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    return_notes = fields.Text(string="Notes", store=True, related='move_ids_without_package.return_notes')
    move_ids_without_package = fields.One2many(
        'stock.move', 'picking_id', string="Stock move", domain=['|', ('package_level_id', '=', False), ('picking_type_entire_packs', '=', False)])
