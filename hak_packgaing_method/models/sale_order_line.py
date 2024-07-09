# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_package = fields.Boolean(string="Is a Package", default=False)

    def _is_not_sellable_line(self):
        return self.is_package or super()._is_not_sellable_line()

    def unlink(self):
        self.filtered('is_package').order_id.filtered('package_id').carrier_id = False
        return super().unlink()

    def _is_package(self):
        self.ensure_one()
        return self.is_package
