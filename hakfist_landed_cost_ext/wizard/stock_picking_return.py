from odoo import fields, models, api


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _prepare_picking_default_values(self):
        res = super()._prepare_picking_default_values()
        print("res", res)
        purchase_order_id = False
        if self.picking_id.purchase_order_id:
            purchase_order_id = self.picking_id.purchase_order_id.id
        res.update({'purchase_order_id': purchase_order_id})
        return res
