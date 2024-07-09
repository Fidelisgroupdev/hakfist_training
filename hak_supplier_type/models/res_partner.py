# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree


# import simplejson


class Partner(models.Model):
    _inherit = "res.partner"

    supplier_type_id = fields.Many2one("supplier.type", 'Supplier Type')
