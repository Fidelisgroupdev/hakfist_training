from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()
        for rec in self:
            if rec.move_ids_without_package:
                for line in rec.move_ids_without_package:
                    if line.quantity < 0:
                        raise ValidationError(_(
                            'Quantity should be greater than zero'
                        ))
        return res
