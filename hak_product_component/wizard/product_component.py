# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
from datetime import date
from datetime import date
import json
import base64


class ProductComponentWizard(models.TransientModel):
    _name = 'product.component.wizard'
    _description = 'Product Component Wizard'

    product_id = fields.Many2one('product.template', string="Product")
    product_component_type_ids = fields.One2many('product.component.type', 'wizard_id', string="Components Type")

    def action_create_component(self):
        print("action_create_component")
        if not self.product_component_type_ids:
            raise UserError(_("Please add atleast one component type"))
        component_category = self.product_id.categ_id.component_category_id
        attribute_list = []
        if self.product_id.attribute_line_ids:
            for attr in self.product_id.attribute_line_ids:
                attr_line = (0, 0, {'attribute_id': attr.attribute_id.id, 'value_ids': attr.value_ids.ids})
                attribute_list.append(attr_line)

        main_product = self.env["product.template"].create({
            'name': "Unpacked " + self.product_id.name,
            'categ_id': component_category.id,
            'detailed_type': 'product',
            'sale_ok': False,
            'purchase_ok': False,
            'attribute_line_ids': attribute_list,
        })
        by_products_list = []
        if self.product_component_type_ids:
            for line in self.product_component_type_ids:
                # name = dict(line._fields['component_type'].selection).get(line.component_type)
                by_product = self.env["product.template"].create({
                    'name': line.name,
                    'categ_id': component_category.id,
                    'detailed_type': 'product',
                    'sale_ok': False,
                    'purchase_ok': False,
                })
                by_products_list.append(by_product)
        if self.product_id:
            bom = self.env['mrp.bom'].create({

                # 'product_id': main_product.id,
                'product_tmpl_id': main_product.id,
                'type': 'normal',
                'product_qty': 1,

            })

            products = self.env["product.product"].search(
                [('product_tmpl_id', '=', self.product_id.id), ('name', '=', self.product_id.name)])
            for product in products:
                lines = self.env['mrp.bom.line'].create({
                    'product_id': product.id,
                    'product_qty': 1,
                    'bom_id': bom.id,
                    'bom_product_template_attribute_value_ids': product.product_template_variant_value_ids.ids,
                })
            if by_products_list:
                for by_pdt in by_products_list:
                    by_product = self.env["product.product"].search([('product_tmpl_id', '=', by_pdt.id)])
                    by_product_line = self.env['mrp.bom.byproduct'].create({
                        'product_id': by_product.id,
                        'product_qty': 1,
                        'bom_id': bom.id,
                    })

            if bom:
                self.product_id.write({
                    'components_created': True
                })


class ProductComponentType(models.TransientModel):
    _name = 'product.component.type'
    _description = 'Product Component Type'

    wizard_id = fields.Many2one("product.component.wizard", 'Wizard')
    name = fields.Char(string='Description')
    component_type = fields.Selection([
        ('box', 'Box'), ('pouch', 'Pouch'),
        ('lid', 'Lid'), ('plastic_cover', 'Plastic Cover'), ('accessories', 'Accessories')], string='Type')
    printing_possible = fields.Boolean('Printing Possible')

    @api.onchange('component_type')
    def onchange_component_type(self):
        for line in self:
            if self.component_type:
                name = dict(line._fields['component_type'].selection).get(line.component_type)
                line.name = name + " Of " + line.wizard_id.product_id.name
