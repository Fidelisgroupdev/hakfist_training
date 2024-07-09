# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _prepare_picking(self):
        res = super()._prepare_picking()
        print("res", res)
        res.update({'purchase_order_id': self.id})
        return  res

