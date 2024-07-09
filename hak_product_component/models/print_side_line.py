import json

from odoo import fields, models, api
from datetime import date


class PrintSideLine(models.Model):
    _inherit = 'printing.side.line'

    component_product_id = fields.Many2one('product.template', string="Component")
    component_id = fields.Many2one('product.component', string="Component", related='product_temp_id.component_id')


