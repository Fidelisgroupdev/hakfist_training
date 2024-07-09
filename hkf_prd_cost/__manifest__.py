# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Product Cost Security",
    "summary": "Product cost security restriction view",
    "version": "17.0.1.0.1",
    "development_status": "Production/Stable",
    "maintainers": ["jsa"],
    "category": "Product",
    "website": "www.hakfist.com",
    "author": "HAKFIST",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["product"],
    "data": ["security/hkf_prd_cost.xml", "views/product_views.xml"],
}
