from odoo import models, fields, api, exceptions, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def update_product_cost(self):
        action = self.env.ref('hakfist_cost_updation.action_window_product_cost_wizard').sudo()
        result =action.read()[0]
        return result
