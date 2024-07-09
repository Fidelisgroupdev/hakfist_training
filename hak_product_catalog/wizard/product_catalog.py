# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import datetime
from datetime import date
from datetime import date
import json
import base64


class ProductCatalogWizard(models.TransientModel):
    _name = 'product.catalog.wizard'
    _description = 'Product Catalog Wizard'

    product_category_ids = fields.Many2many(comodel_name='product.category', string="Product Category")
    price_range = fields.Selection(string='Price Range',
                                   selection=[('greater', 'Greater'), ('lesser', 'Lesser'), ('between', 'Between')])
    view_type = fields.Selection(string='View Type',
                                 selection=[('crm', 'CRM'), ('product', 'Product')])
    starting_price = fields.Float(string="From", default=0)
    ending_price = fields.Float(string="To", default=0)
    value = fields.Float(string="Value", default=0)
    show_price = fields.Boolean(string="Show Price")
    show_stock = fields.Boolean(string="Show Stock")
    pdt_with_qty = fields.Boolean(string="Show Products Only With Available Qty", default=True)
    partner_id = fields.Many2one('res.partner', string="Customer")
    crm_id = fields.Many2one('crm.lead', string="CRM")
    stock_range = fields.Selection(string='Stock Range',
                                   selection=[('greater', 'Greater'), ('lesser', 'Lesser'), ('between', 'Between')])
    product_type = fields.Selection(string='Product Type',
                                    selection=[('template', 'Template'), ('variant', 'Variant')], default='template')
    starting_qty = fields.Float(string="From", default=0)
    ending_qty = fields.Float(string="To", default=0)
    stock_qty = fields.Float(string="Qty", default=0)

    def action_print_product_catalog(self):
        print("action_print_product_catalog")
        print("self._context action_print_product_catalog", self._context)
        products_list = []
        if self.view_type == 'product':
            products = self.env['product.template'].browse(self._context.get('active_ids', []))
            products_list = products.ids
        # hh
        data = {

            'model_id': self.id,
            'partner_id': self.partner_id.id,
            'crm_id': self.crm_id.id,
            'product_category_ids': self.product_category_ids.ids if self.product_category_ids else False,
            'price_range': self.price_range if self.price_range else False,
            'view_type': self.view_type if self.view_type else False,
            'starting_price': self.starting_price if self.starting_price else False,
            'ending_price': self.ending_price if self.ending_price else False,
            'value': self.value if self.value else False,
            'stock_range': self.stock_range if self.stock_range else False,
            'product_type': self.product_type if self.product_type else False,
            'starting_qty': self.starting_qty if self.starting_qty else False,
            'ending_qty': self.ending_qty if self.ending_qty else False,
            'stock_qty': self.stock_qty if self.stock_qty else False,
            'show_price': self.show_price if self.show_price else False,
            'show_stock': self.show_stock if self.show_stock else False,
            'pdt_with_qty': self.pdt_with_qty if self.pdt_with_qty else False,
            'products_list': products_list,
        }
        return self.env.ref('hak_product_catalog.action_report_product_catalog').report_action(None, data=data)

    def action_send_by_email(self):
        """ Opens a wizard to compose an email, with relevant mail template loaded by default """
        attachment_id = self.action_get_attachment()
        print("attachment_id", attachment_id)
        ctx = {
            'default_subject': 'Product Catalog',
            'default_attachment_ids': [attachment_id.id],
            'default_partner_ids': [self.partner_id.id] if self.partner_id else False,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def action_get_attachment(self):
        print("action_get_attachment")
        products_list = []
        if self.view_type == 'product':
            products = self.env['product.template'].browse(self._context.get('active_ids', []))
            products_list = products.ids
        data = {

            'model_id': self.id,
            'partner_id': self.partner_id.id,
            'crm_id': self.crm_id.id,
            'product_category_ids': self.product_category_ids.ids if self.product_category_ids else False,
            'price_range': self.price_range if self.price_range else False,
            'view_type': self.view_type if self.view_type else False,
            'starting_price': self.starting_price if self.starting_price else False,
            'ending_price': self.ending_price if self.ending_price else False,
            'value': self.value if self.value else False,
            'stock_range': self.stock_range if self.stock_range else False,
            'product_type': self.product_type if self.product_type else False,
            'starting_qty': self.starting_qty if self.starting_qty else False,
            'ending_qty': self.ending_qty if self.ending_qty else False,
            'stock_qty': self.stock_qty if self.stock_qty else False,
            'show_price': self.show_price if self.show_price else False,
            'show_stock': self.show_stock if self.show_stock else False,
            'pdt_with_qty': self.pdt_with_qty if self.pdt_with_qty else False,
            'products_list': products_list,
        }
        # """ this method called from button action in view xml ""”
        report = self.env['ir.actions.report']._render_qweb_pdf("hak_product_catalog.action_report_product_catalog",
                                                                self.id, data=data)
        print("report", report)
        # save pdf as attachment
        name = "Product Catalog"
        filename = name + '.pdf'

        return self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(report[0]),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })
