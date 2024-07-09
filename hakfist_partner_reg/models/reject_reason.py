import pytz
import datetime
from lxml import etree

from odoo import api, fields, models
from odoo.exceptions import UserError
from markupsafe import Markup


from odoo import api, fields, models, _, tools


class RejectReason(models.Model):
    _name = "reject.reason"
    _description = "Reject Reason"

    name = fields.Char('Name')
