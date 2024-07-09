from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[('approved', 'Approved'), ('purchase',)])

    def action_send_for_approval(self):
        for po in self:
            for line in po.order_line:
                if line.product_qty < 0:
                    raise ValidationError(_(
                        'Quantity should be greater than zero'
                    ))
                if line.price_unit < 0:
                    raise ValidationError(_(
                        'price should not be negative'
                    ))
            po.write({'state': 'to approve'})
            activity_type = self.env['mail.activity.type'].sudo().search([('to_grant_po_approval', '=', True)],
                                                                         limit=1)
            if activity_type:
                todos = {
                    'res_id': po.id,
                    'res_model_id': self.env['ir.model'].search([('model', '=', 'purchase.order')]).id,
                    'user_id': activity_type.default_user_id.id,
                    'note': activity_type.default_note,
                    'activity_type_id': activity_type.id,
                    # 'date_deadline': datetime.date.today(),
                }
                activity = self.env['mail.activity'].create(todos)
                print("activity", activity)
        return {}

    def action_approve(self):
        for po in self:
            po.write({'state': 'approved'})
            purchase_model = self.env['ir.model'].search([('model', '=', 'purchase.order')])
            activity = self.env['mail.activity'].sudo().search(
                [('res_id', '=', po.id), ('res_model_id', '=', purchase_model.id)],
                limit=1)
            if activity:
                activity.action_feedback("Approved, You can confirm this order", None)
        return {}

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'approved']:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True
