# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def get_landed_cost_summary_data(self):
        for rec in self:
            landed_costs_ids = self.env['stock.valuation.adjustment.lines'].read_group(
                domain=[('purchase_order_id', '=', self.id), ('cost_id.state', '=', 'done')],
                fields=['cost_line_id', 'additional_landed_cost:sum'], groupby=['cost_line_id'])
            total_dict = []
            for line in landed_costs_ids:
                cost_line_id = line['cost_line_id']
                final_cost = line['additional_landed_cost']
                cost_line = self.env['stock.landed.cost.lines'].browse(cost_line_id[0])
                service_product = cost_line.product_id
                description = cost_line.name
                if any(d['description'] == description for d in total_dict):
                    for rec in total_dict:
                        if rec['description'] == description:
                            amount = rec['amount']
                            cost = amount + final_cost
                            rec['amount'] = cost
                else:
                    total_dict.append({
                        'cost_line_id': service_product.name,
                        'description': description,
                        'amount': final_cost
                    })
            report_data = total_dict
            return report_data

    def get_landed_cost_detailed_data(self):
        dict = []
        for rec in self.order_line:
            stock_layer = self.env['stock.valuation.layer'].search(
                [('product_id', '=', rec.product_id.id), ('purchase_order_id', '=', rec.order_id.id)])
            qty = 0
            total_cost_lcy = 0
            total_charges = 0
            cost_per_unit_lcy = 0
            total_cost = 0
            total_cost_fcy = 0
            effective_unit_price = 0
            landed_cost = 0
            for stock in stock_layer:
                qty += stock.quantity
                total_cost_fcy = rec.price_unit * rec.product_qty
                if not stock.quantity == 0:
                    total_cost_lcy += stock.value
                if stock.quantity == 0:
                    total_charges += stock.value
                total_cost = total_charges + total_cost_lcy
                if qty != 0:
                    cost_per_unit_lcy = total_cost_lcy / qty
                    effective_unit_price = total_cost / qty
                    landed_cost = total_charges / qty

            dict.append({
                'item_code': rec.product_id.default_code,
                'description': rec.product_id,
                'quantity': qty,
                'cost_per_unit': rec.price_unit,
                'total_cost_fcy': total_cost_fcy,
                'total_cost_lcy': total_cost_lcy,
                'total_charges': total_charges,
                'cost_per_unit_lcy': cost_per_unit_lcy,
                'total_cost': total_cost,
                'effective_unit_price': effective_unit_price,
                'landed_cost': landed_cost

            })

        report_data = dict
        return report_data
