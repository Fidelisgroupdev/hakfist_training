# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    # Theme information
    'name': 'Snazzy Theme Common',
    'category': 'Website',
    'version': '17.0.0.0',
    'author': 'Bizople Solutions Pvt. Ltd.',
    'website': 'https://www.bizople.com',
    'summary': 'Snazzy Theme Common',
    'description': """Snazzy Theme Common""",
    'depends': [
        'website',
        'portal',
        'web_editor',
        'website_blog',
        'sale_management',
        'website_sale',
        'website_sale_wishlist',
        'website_sale_comparison',
        'website_sale_stock',
        'stock',
    ],

    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/category_template.xml',
        'views/brand_template.xml',
        'views/manifest.xml',
        'views/pwa_offline.xml',
        #Megamenus
        'views/megamenus/megamenu_one_snippet.xml',
        'views/megamenus/megamenu_two_snippet.xml',
        'views/megamenus/megamenu_three_snippet.xml',
        'views/megamenus/dynamic_megamenu_snippet.xml',
        'views/megamenus/megamenu_four_snippet.xml',
        'views/megamenus/megamenu_five_snippet.xml',
    ],
    'images': [
       'static/description/banner.jpg'
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
    'price': 25,
    'currency': 'EUR',
}
