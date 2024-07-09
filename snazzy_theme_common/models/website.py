# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.http import request

class PWAshortcuts(models.Model):
    _name = 'pwa.shortcuts'
    _description = "PWA Shortcuts"

    name = fields.Char("Name", required=True)
    short_name = fields.Char("Short Name", required=True)
    url = fields.Char("URL", required=True, default='/')
    description = fields.Char("Description", required=True)
    image_192_shortcut = fields.Binary('Image 192px', readonly=False)

class Website(models.Model):
    _inherit = "website"

    @staticmethod
    def _get_product_sort_mapping():
        website = request.env['website'].get_current_website()

        if website.is_view_active('theme_snazzy.snazzy_b2b_mode') and request.env.user._is_public():
            return [
                ('website_sequence asc', ('Featured')),
                ('create_date desc', ('Newest Arrivals')),
                ('name asc', ('Name (A-Z)')),
            ]
        else:
            return [
                ('website_sequence asc', ('Featured')),
                ('create_date desc', ('Newest Arrivals')),
                ('name asc', ('Name (A-Z)')),
                ('list_price asc', ('Price - Low to High')),
                ('list_price desc', ('Price - High to Low')),
            ]

    @api.model
    def get_categories(self):
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        category_ids = self.env['product.public.category'].search(
            categs_domain)
        res = {
            'categories': category_ids,
        }
        return res
    
    @api.model
    def get_product_category_data_menu(self):
        website_domain = request.website.website_domain()
        category_ids = self.env['product.public.category'].sudo().search(
            [('quick_categ', '=', True)] + website_domain)
        return category_ids

    @api.model
    def get_auto_assign_category(self):
        website_domain = request.website.website_domain()
        auto_assign_categ_ids = self.env['product.public.category'].search(
            [('auto_assign', '=', True)] + website_domain)

        return auto_assign_categ_ids

    @api.model
    def get_categories_in_header(self, categ_id):
        child_categ = self.env['product.public.category'].search(
            [('parent_id', '=', categ_id),('category_in_header','=',True)])

        return child_categ

    @api.model
    def get_brand_data(self):
        brand_ids = self.env['product.brand'].sudo().search(
            [('visible_snippet', '=', True)])
        return brand_ids

    def get_product_brands(self, category, **post):
        domain = []
        if category:
            cat_id = []
            if category != None:
                for ids in category:
                    cat_id.append(ids.id)
                domain += ['|', ('public_categ_ids.id', 'in', cat_id),
                           ('public_categ_ids.parent_id', 'in', cat_id)]
        else:
            domain = []
        product_ids = self.env["product.template"].sudo().search(domain)
        domain_brand = [
            ('product_ids', 'in', product_ids.ids or []), ('product_ids', '!=', False)]
        brands = self.env['product.brand'].sudo().search(domain_brand)
        return brands

    def get_product_count_snazzy(self):
        prod_per_page = self.env['product.per.page.bizople'].search([])
        prod_per_page_no = self.env['product.per.page.count.bizople'].search([
        ])
        values = {
            'name': prod_per_page.name,
            'page_no': prod_per_page_no,
        }
        return values

    def get_current_pager_selection(self):
        page_no = request.env['product.per.page.count.bizople'].sudo().search(
            [('default_active_count', '=', True)])
        if request.session.get('default_paging_no'):
            return int(request.session.get('default_paging_no'))
        elif page_no:
            return int(page_no.name)

    enable_pwa = fields.Boolean(string='Enable PWA', readonly=False)
    app_name_pwa = fields.Char('App Name', readonly=False, default='PWA Name')
    short_name_pwa = fields.Char(
        'Short Name', readonly=False, default='Short Name')
    description_pwa = fields.Char(
        'App Description', readonly=False, default='PWA Desciprtion')
    image_192_pwa = fields.Binary('Image 192px', readonly=False)
    image_512_pwa = fields.Binary('Image 512px', readonly=False, store=True)
    start_url_pwa = fields.Char('App Start Url', readonly=False, default='/')
    background_color_pwa = fields.Char(
        'Background Color', readonly=False, default='#ffbd27')
    theme_color_pwa = fields.Char(
        'Theme Color', readonly=False, default='#ffbd27')
    pwa_shortcuts_ids = fields.Many2many(
        'pwa.shortcuts', string='PWA Shortcuts')