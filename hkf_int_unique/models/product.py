# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"

    _sql_constraints = [
        (
            "default_code_uniq",
            "unique(default_code)",
            "Internal Reference must be unique across the database!",
        )
    ]

    @api.constrains('default_code')
    def _check_no_space_in_code(self):
        for record in self:
            print("record", record)
            print("record.code", record.code)
            if record.code and ' ' in record.code:
                raise UserError("Internal reference  field cannot contain spaces!")
