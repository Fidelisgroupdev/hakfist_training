# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order')


class StockMove(models.Model):
    _inherit = 'stock.move'

    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order', compute='_compute_po', store=True)

    @api.depends('picking_id')
    def _compute_po(self):
        for move in self:
            purchase_order_id = False
            if move.picking_id:
                if move.picking_id.purchase_order_id:
                    purchase_order_id = move.picking_id.purchase_order_id.id
            move.purchase_order_id = purchase_order_id


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order', compute='_compute_po', store=True)

    @api.depends('picking_id')
    def _compute_po(self):
        for move_line in self:
            purchase_order_id = False
            if move_line.move_id:
                if move_line.move_id.picking_id:
                    if move_line.move_id.picking_id.purchase_order_id:
                        purchase_order_id = move_line.move_id.picking_id.purchase_order_id.id
            move_line.purchase_order_id = purchase_order_id


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order', compute='_compute_po', store=True)

    @api.depends('stock_move_id')
    def _compute_po(self):
        for line in self:
            purchase_order_id = False
            if line.stock_move_id:
                if line.stock_move_id.picking_id:
                    if line.stock_move_id.picking_id.purchase_order_id:
                        purchase_order_id = line.stock_move_id.picking_id.purchase_order_id.id
            line.purchase_order_id = purchase_order_id