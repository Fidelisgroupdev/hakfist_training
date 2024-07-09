from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class MailActivityType(models.Model):
    _inherit = 'mail.activity.type'

    to_grant_po_approval = fields.Boolean(string='To Grant PO Approval')
    # granted_po_approval = fields.Boolean(string='Granted PO Approval')
