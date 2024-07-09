from odoo import fields, models, api
from datetime import date


class ProductCategory(models.Model):
    _inherit = 'product.category'

    component_category_id = fields.Many2one("product.category", 'Unpacked Component Category')
    byproduct_component_category_id = fields.Many2one("product.category", 'Byproduct Component Category')
