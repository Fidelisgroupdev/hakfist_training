# Part of Odoo. See LICENSE file for full copyright and licensing details.

import psycopg2
import re

from odoo import _, api, fields, models, registry, Command, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class PackagingMethod(models.Model):
    _name = 'packaging.method'
    _description = "Packaging Methods"

    name = fields.Char('Packaging Method', required=True, translate=True)
    active = fields.Boolean(default=True)
    package_type_id = fields.Many2one('stock.package.type', string='Package Type', ondelete='restrict')
    product_id = fields.Many2one('product.product', string='Packaging Product', required=True, ondelete='restrict')
    currency_id = fields.Many2one(related='product_id.currency_id')
    amount = fields.Float(
        string="Amount",
        default=0,
        help="Amount",
    )


