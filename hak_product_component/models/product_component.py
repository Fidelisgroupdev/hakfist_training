# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
from datetime import date
from datetime import date
import json
import base64


class ProductComponent(models.Model):
    _name = 'product.component'
    _description = 'Product Component'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.template', string="Product")
    family_code = fields.Char(string='Family Suffix', related='product_id.family_code_ext')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('review', 'Under Review'),
            ('approved', 'Approved'),
            ('cancel', 'Cancelled'),
        ], string='Status', tracking=True, default='draft')
    product_component_type_ids = fields.One2many('product.component.type', 'component_id', string="Components Type")

    def action_request_for_approval(self):
        for rec in self:
            rec.state = "review"

    def action_create_component(self):
        print("action_create_component")
        if not self.product_component_type_ids:
            raise UserError(_("Please add atleast one component type"))
        unpacked_component_category = self.product_id.categ_id.component_category_id
        byproduct_component_category = self.product_id.categ_id.byproduct_component_category_id
        attribute_list = []
        if self.product_id.attribute_line_ids:
            for attr in self.product_id.attribute_line_ids:
                attr_line = (0, 0, {'attribute_id': attr.attribute_id.id, 'value_ids': attr.value_ids.ids})
                attribute_list.append(attr_line)

        main_product = self.env["product.template"].create({
            'name': "Unpacked " + self.product_id.name,
            'component_id': self.id,
            'categ_id': unpacked_component_category.id,
            'detailed_type': 'product',
            'sale_ok': False,
            'purchase_ok': False,
            'is_component': True,
            'attribute_line_ids': attribute_list,
        })
        by_products_list = []
        if self.product_component_type_ids:
            for line in self.product_component_type_ids:
                # name = dict(line._fields['component_type'].selection).get(line.component_type)
                by_product = self.env["product.template"].create({
                    'name': line.name,
                    'component_id': self.id,
                    'categ_id': byproduct_component_category.id,
                    'detailed_type': 'product',
                    'is_component': True,
                    'sale_ok': False,
                    'purchase_ok': False,
                })
                by_products_list.append(by_product)
        if self.product_id:
            bom = self.env['mrp.bom'].create({

                # 'product_id': main_product.id,
                'product_tmpl_id': main_product.id,
                'component_id': self.id,
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
                self.state = "approved"
                self.product_id.write({
                    'components_created': True,
                    'component_id': self.id,
                })

    def action_cancel_component(self):
        print("action_cancel_component")
        component_bom = self.env['mrp.bom'].sudo().search(
            [('component_id', '=', self.id)])
        if component_bom:
            component_bom.write({
                'active': False
            })
        component_products = self.env['product.template'].sudo().search(
            [('component_id', '=', self.id),('is_component', '=', True)])
        if component_products:
            component_products.write({
                'active': False
            })
        self.state = "cancel"
        self.product_id.write({
            'components_created': False
        })

    def action_view_bom(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_bom_form_action")
        action['domain'] = [('component_id', '=', self.id)]
        # components = self.env['mrp.bom'].sudo().search(
        #     [('component_id', '=', self.id)])
        # if len(components) == 1:
        #     action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        #     action['res_id'] = components.id
        return action



    def action_view_products(self):
        print("action_view_products")
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.product_template_action_product")
        action['domain'] = [('component_id', '=', self.id)]
        # components = self.env['mrp.bom'].sudo().search(
        #     [('component_id', '=', self.id)])
        # if len(components) == 1:
        #     action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        #     action['res_id'] = components.id
        return action


class ProductComponentType(models.Model):
    _name = 'product.component.type'
    _description = 'Product Component Type'

    component_id = fields.Many2one("product.component", 'Component')
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
                line.name = name + " Of " + line.component_id.product_id.name
