# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.http import request
import base64

class res_config(models.TransientModel):
    _inherit = "res.config.settings"

    enable_pwa = fields.Boolean(
        string='Enable PWA', related='website_id.enable_pwa', readonly=False,)
    app_name_pwa = fields.Char(
        'App Name', related='website_id.app_name_pwa', readonly=False)
    short_name_pwa = fields.Char(
        'Short Name', related='website_id.short_name_pwa', readonly=False)
    description_pwa = fields.Char(
        'App Description', related='website_id.description_pwa', readonly=False)
    image_192_pwa = fields.Binary(
        'Image 192px', related='website_id.image_192_pwa', readonly=False)
    image_512_pwa = fields.Binary(
        'Image 512px', related='website_id.image_512_pwa', readonly=False)
    start_url_pwa = fields.Char(
        'App Start Url', related='website_id.start_url_pwa', readonly=False)
    background_color_pwa = fields.Char(
        'Background Color', related='website_id.background_color_pwa', readonly=False)
    theme_color_pwa = fields.Char(
        'Theme Color', related='website_id.theme_color_pwa', readonly=False)
    pwa_shortcuts_ids = fields.Many2many(
        related='website_id.pwa_shortcuts_ids', readonly=False)