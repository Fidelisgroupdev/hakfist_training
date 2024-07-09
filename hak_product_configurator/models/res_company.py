# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import html_escape

class ResCompany(models.Model):
    _inherit = 'res.company'

    is_printing = fields.Boolean(string="Is Printing", copy=False)
    is_trading = fields.Boolean(string="Is Trading", copy=False)
