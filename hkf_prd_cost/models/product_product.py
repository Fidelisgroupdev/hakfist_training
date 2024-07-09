# Copyright 2018 Sergio Teruel - Tecnativa <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    standard_price = fields.Float(groups="hkf_prd_cost.group_product_cost")
    lst_price = fields.Float(groups="hkf_prd_cost.group_product_sales_price")
