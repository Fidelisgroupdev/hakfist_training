# -*- coding: utf-8 -*-

from odoo import api, models, fields


class ProductPreviewTemplate(models.Model):
    _inherit = 'product.template'

    branding_image = fields.Image("Branding Image")
