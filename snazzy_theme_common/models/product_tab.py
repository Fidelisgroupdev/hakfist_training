# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class ProductTab(models.Model):
    _name = 'product.tab'
    _description = 'Product Tab'
    _rec_name = 'name'

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence", default=1)
    content = fields.Html(string="Content")
    product_ids = fields.Many2many('product.template','product_tab_table','product_ids','tab_ids', string="product")
