# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.tools.mail import is_html_empty
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from datetime import date, timedelta

class RejectWizard(models.TransientModel):
    _name = "reject.wizard"
    _description = 'Reject Wizard'

    reject_reason_id = fields.Many2one('reject.reason', string='Reject Reason')
    rejection_description = fields.Char('Description')

    def action_reject(self):
        partner = self.env['temp.partner'].browse(self._context.get('active_ids', []))
        for rec in partner:
            rec.sudo().write({
                'state': "rejected",
                'reject_reason_id': self.reject_reason_id.id,
                'rejection_description': self.rejection_description,
            })
            message = rec.sudo().get_message_body(rec, 'rejected')
            print("message444", message)

            outgoing_mailserver = rec.sudo().env.company.parent_id
            print("outgoing_mailserver", outgoing_mailserver)
            if outgoing_mailserver:
                mail_values = {
                    'subject': 'Customer Registration Rejected',
                    'body_html': message,
                    'auto_delete': False,
                    'email_from': outgoing_mailserver.email,
                    'email_to': '%s' % rec.sudo().email,
                }
                mail_id = self.sudo().env['mail.mail'].sudo().create(mail_values)
                mail_id.sudo().send()
            rec.sudo().message_post(body=message)
