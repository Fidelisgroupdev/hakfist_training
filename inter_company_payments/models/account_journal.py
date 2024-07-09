# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_inter_company = fields.Boolean(string='Inter Company', default=False)
