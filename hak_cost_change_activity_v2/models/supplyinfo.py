import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    min_qty = fields.Float(
        'Min Qty', default=0.0, required=True, digits="Product Unit Of Measure",
        help="The quantity to purchase from this vendor to benefit from the price, expressed in the vendor Product Unit of Measure if not any, in the default unit of measure of the product otherwise.")
    max_qty = fields.Float('Max Qty', default=0.0, required=True, digits="Product Unit Of Measure")

    @api.constrains('partner_id', 'product_tmpl_id', 'min_qty', 'max_qty', 'date_start', 'date_end', 'price')
    def check_duplicate_supplier_info(self):
        for record in self:
            existing_supplier_info = self.env['product.supplierinfo'].search([
                ('partner_id', '=', record.partner_id.id),
                ('product_tmpl_id', '=', record.product_tmpl_id.id),
                ('date_start', '=', record.date_start),
                ('date_end', '=', record.date_end),
                ('min_qty', '=', record.min_qty),
                ('max_qty', '=', record.max_qty),
                ('price', '=', record.price),
                ('id', '!=', record.id),  # Exclude current record
            ])
            if existing_supplier_info:
                raise ValidationError("Supplier info already exists for this combination.")
