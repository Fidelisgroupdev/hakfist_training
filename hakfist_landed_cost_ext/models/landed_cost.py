# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    def get_valuation_lines(self):
        lines = super().get_valuation_lines()
        print("lines", lines)
        for val in lines:
            print("val", val)
            move = self.env['stock.move'].browse(val['move_id'])
            print("move", move)
            print("move.purchase_order_id", move.purchase_order_id)
            if move.purchase_order_id:
                val['purchase_order_id'] = move.purchase_order_id.id
                val['po_currency_id'] = move.purchase_order_id.currency_id.id
            if move.purchase_line_id:
                val['purchase_unit_price'] = move.purchase_line_id.price_unit
                val['purchase_total_price'] = move.purchase_line_id.price_unit * val['quantity']
            # val['new_unit_price'] = val['final_cost'] / val['quantity']
        return lines


class StockLandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'

    @api.onchange('product_id')
    def onchange_product_id(self):
        super().onchange_product_id()
        print("_get_default_account")
        for line in self:
            print("line.product_id.property_account_expense_id", line.product_id.property_account_expense_id)
            if line.product_id and line.product_id.property_account_expense_id:
                line.account_id = line.product_id.property_account_expense_id.id
            print("line.account_id", line.account_id)


class AdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'

    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order')
    po_currency_id = fields.Many2one('res.currency')
    purchase_unit_price = fields.Monetary(
        'Purchase Unit Price',currency_field='po_currency_id')
    purchase_total_price = fields.Monetary(
        'Purchase Total Price',currency_field='po_currency_id')
    new_unit_price = fields.Monetary(
        'New Unit Price', compute='_compute_new_unit_price',
        store=True)


    @api.depends('final_cost', 'quantity')
    def _compute_new_unit_price(self):
        for line in self:
            line.new_unit_price = line.final_cost / line.quantity
