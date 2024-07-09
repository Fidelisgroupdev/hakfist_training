# -*- coding: utf-8 -*-

from odoo import fields, models, api, Command


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    configurator_id = fields.Integer(string="Configurator ID")
