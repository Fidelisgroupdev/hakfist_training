from odoo import fields, models, api, _
from datetime import date
from odoo.exceptions import UserError


class CRM(models.Model):
    _inherit = 'crm.lead'

    def action_open_product_catalog(self):
        print("self._context action_open_product_catalog", self._context)
        if self.partner_id or self.email_from or self.phone:
            return {
                'name': _('Product Catalog'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'product.catalog.wizard',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': {
                    'default_partner_id': self.partner_id.id if self.partner_id else False,
                    'default_crm_id': self.id if self else False,
                    'default_view_type': 'crm',
                }
            }
        else:
            raise UserError(_("You need to provide either the customer's email or phone number to access the product catalog."))

