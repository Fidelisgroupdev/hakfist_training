from odoo import models, api, fields, _
from datetime import datetime
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def supplier_pricelist(self):
        product_details = []
        for order in self:
            for order_line in order.order_line:
                supplierinfos = self.env['product.supplierinfo'].search([
                    ('partner_id', '=', order.partner_id.id),
                    ('product_tmpl_id', '=', order_line.product_id.product_tmpl_id.id)
                ])
                for supplierinfo in supplierinfos:
                    if (supplierinfo.min_qty == order_line.product_qty and
                            supplierinfo.price != order_line.price_unit):
                        product_details.append({
                            'supplier_name': supplierinfo.partner_id.name,
                            'product_name': order_line.product_id.name,
                            'qty': order_line.product_qty,
                            'standard_price': supplierinfo.price,
                            'purchase_price': order_line.price_unit,
                        })
                    elif supplierinfo.min_qty != order_line.product_qty and supplierinfo.price != order_line.price_unit:
                        product_details.append({
                            'supplier_name': supplierinfo.partner_id.name,
                            'product_name': order_line.product_id.name,
                            'qty': order_line.product_qty,
                            'standard_price': supplierinfo.price,
                            'purchase_price': order_line.price_unit,
                        })
        return product_details

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        for order in self:
            if 'state' in vals and vals['state'] == 'to approve':
                product_details = self.supplier_pricelist()
                email_to = self.get_email_to()
                if product_details:
                    temp_vals = {
                        'email_to': email_to,
                        'reply_to': email_to,
                    }
                    mail_template = self.env['mail.template'].browse(
                        self.env.ref('hak_cost_change_activity_v2.email_template_cost_change_purchase').id)
                    mail_template.send_mail(order.id, email_values=temp_vals, force_send=True,
                                            email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature")
        return res

    @api.model
    def get_email_to(self):
        account_group = self.env.ref("account.group_account_manager")
        account_users = self.env['res.users'].search([('groups_id', 'in', account_group.ids)])
        email_list = [usr.partner_id.email for usr in account_users if usr.partner_id.email]
        return ",".join(email_list)
