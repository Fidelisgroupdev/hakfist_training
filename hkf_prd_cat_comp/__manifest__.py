# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Product Category Company",
    "summary": "Product categories as company dependent",
    "version": "17.0.1.0.0",
    "category": "Product",
    "website": "hakfist.com",
    "author": "jsa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "product",
    ],
    "data": [
        "views/product_category.xml",
        "views/product_template_view.xml",
        "security/ir_rule.xml",
    ],
}
