# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree


# import simplejson


class Partner(models.Model):
    _inherit = "res.users"

    supplier_type_id = fields.Many2one("supplier.type", 'Default Supplier Type')
    supplier_type_ids = fields.Many2many('supplier.type', 'supplier_type_rel', 'user_id', 'type_id',
                                         string='Allowed Supplier Types')
