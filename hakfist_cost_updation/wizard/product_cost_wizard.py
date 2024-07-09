from odoo import api, fields, models, _


class ProductCostWizard(models.TransientModel):
    _name = "product.cost.wiz"
    _description = "Product Cost Wizard"

    product_cost = fields.Float(string='Product Cost')
    reason_for_change = fields.Text('Reason', tracking=True)

    def cost_confirm(self):
        product_ids = self.env['product.template'].browse(self._context.get('active_ids', []))
        for rec in product_ids:
            b = rec.standard_price
            rec.standard_price = self.product_cost
            message = 'Product cost changed from %s to %s Due to %s' % (b, self.product_cost, self.reason_for_change)
            rec.message_post(body=message, subjcet="reason")
