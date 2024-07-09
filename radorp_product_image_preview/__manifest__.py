# -*- coding: utf-8 -*-
{
    'name': "Product Image Preview",
    'version': '17.0',
    "summary": """  Preview the branding image of a product. """,
    "description": """ Preview the branding image of a product. """,
    'license': 'LGPL-3',
    'price': 0,
    'currency': 'EUR',
    'author': "Radorp Pvt Ltd",
    'website': "https://radorp.com/",
    'category': 'Tools',
    'depends': ['base', 'web', 'website', 'website_sale', 'product'],
    'data': [
        "views/preview_views.xml",
        "views/branding.xml",
        "views/preview_carousel.xml",
    ],
    'assets': {
        "web.assets_frontend": [
            "radorp_product_image_preview/static/src/js/preview.js",
            "radorp_product_image_preview/static/src/js/carousel_preview.js",

        ],
    },
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "auto_install": False,
    "installable": True,
}
