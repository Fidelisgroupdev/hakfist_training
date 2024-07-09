# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PackageType(models.Model):
    _inherit = 'stock.package.type'

    @api.onchange('packaging_length', 'width', 'height')
    def onchange_size_dimensions(self):
        for vals in self:
            if vals.packaging_length or vals.width or vals.height:
                type = self.env['stock.package.type'].sudo().search(
                    [('packaging_length', '=', vals.packaging_length), ('width', '=', vals.width),
                     ('height', '=', vals.height),('id', '!=', vals.id)])
                if type:
                    raise ValidationError("Same dimensions already exists for another Packaging Type.")

    # @api.constrains('packaging_length', 'width', 'height')
    # def check_size_dimensions(self):
    #     for vals in self:
    #         if vals.packaging_length or vals.width or vals.height:
    #             type = self.env['stock.package.type'].sudo().search(
    #                 [('packaging_length', '=', vals.packaging_length), ('width', '=', vals.width),
    #                  ('height', '=', vals.height), ('id', '!=', vals.id)])
    #             if type:
    #                 raise ValidationError("Same dimensions already exists for another Packaging Type.")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if 'detailed_type' in res and res['detailed_type'] == 'product':
            res['tracking'] = 'lot'
        return res

    @api.onchange('detailed_type')
    def onchange_detailed_type(self):
        for vals in self:
            if vals.detailed_type == 'product':
                vals.tracking = 'lot'
            else:
                vals.tracking = 'none'

    @api.onchange('tracking')
    def onchange_product_tracking(self):
        for vals in self:
            if vals.tracking != 'lot':
                if vals.detailed_type == 'product':
                    raise ValidationError("Storable product type must have tracking By lots.")


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def action_apply_inventory(self):
        for quants in self:
            if quants.product_id:
                if quants.product_id.tracking == 'lot':
                    if not quants.lot_id:
                        raise ValidationError("Please add Lot/Serial Number for product %s" % quants.product_id.name)
        return super(StockQuant, self).action_apply_inventory()
