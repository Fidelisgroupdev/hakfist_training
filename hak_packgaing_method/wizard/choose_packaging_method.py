# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ChooseDeliveryCarrier(models.TransientModel):
    _name = 'choose.packaging.method'
    _description = 'Delivery Carrier Selection Wizard'

    order_id = fields.Many2one('sale.order', required=True, ondelete="cascade")
    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', required=True)
    packing_id = fields.Many2one(
        'packaging.method',
        string="Packaging Method",
        required=True,
    )
    currency_id = fields.Many2one('res.currency', related='order_id.currency_id')
    company_id = fields.Many2one('res.company', related='order_id.company_id')

    def button_confirm(self):
        self.order_id.set_package_line(self.packing_id, self.packing_id.amount)
        # self.order_id.write({
        #     'recompute_delivery_price': False,
        #     'delivery_message': self.delivery_message,
        # })
