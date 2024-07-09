# Copyright 2018 Sergio Teruel - Tecnativa <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    standard_price = fields.Float(groups="hkf_prd_cost.group_product_cost")
    user_can_update_cost = fields.Boolean(compute="_compute_user_can_update_cost")

    list_price = fields.Float(groups="hkf_prd_cost.group_product_sales_price")
    user_can_update_sales_price = fields.Boolean(compute="_compute_user_can_update_sales_price")

    @api.depends_context("uid")
    def _compute_user_can_update_cost(self):
        """A user could have full cost permissions but no product edition permissions.
        We want to prevent those from updating costs."""
        for product in self:
            product.user_can_update_cost = self.env.user.has_group(
                "hkf_prd_cost.group_product_edit_cost"
            )

    @api.depends_context("uid")
    def _compute_user_can_update_sales_price(self):
        """A user could have full cost permissions but no product edition permissions.
        We want to prevent those from updating Sales Price."""
        for product in self:
            print("CHECK__", self.env.user.has_group(
                "hkf_prd_cost.group_product_edit_sales_price"
            ))
            product.user_can_update_sales_price = self.env.user.has_group(
                "hkf_prd_cost.group_product_edit_sales_price"
            )
