from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    no_edit_access = fields.Boolean(string='No Edit Access', compute='_compute_no_edit_access', copy=False)

    # @api.depends('employee_id')
    def _compute_no_edit_access(self):
        print("_compute_no_edit_access")
        for rec in self:
            print("user access", self.user_has_groups('hak_po_price_edit.group_edit_po_price'))
            if not self.user_has_groups('hak_po_price_edit.group_edit_po_price'):
                rec.no_edit_access = True
            else:
                rec.no_edit_access = False

    @api.onchange('product_id')
    def onchange_product_id_compute_po(self):
        print("onchange_product_id_compute_po")
        for line in self:
            print("line", line)
            if self.product_id:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                line._compute_no_edit_access()
