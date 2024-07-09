# -*- coding: utf-8 -*-
# from odoo import http


# class ThemeHak(http.Controller):
#     @http.route('/theme_hak/theme_hak', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/theme_hak/theme_hak/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('theme_hak.listing', {
#             'root': '/theme_hak/theme_hak',
#             'objects': http.request.env['theme_hak.theme_hak'].search([]),
#         })

#     @http.route('/theme_hak/theme_hak/objects/<model("theme_hak.theme_hak"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('theme_hak.object', {
#             'object': obj
#         })

