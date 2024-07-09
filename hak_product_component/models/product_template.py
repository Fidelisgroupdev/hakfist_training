import json

from odoo import fields, models, api
from datetime import date


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    components_created = fields.Boolean(string="Components Created")
    is_component = fields.Boolean(string="Is Component")
    component_id = fields.Many2one('product.component', string="Component")


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    component_id = fields.Many2one('product.component', string="Component")
