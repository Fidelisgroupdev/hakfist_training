from odoo import models, fields, api, _


class PurchaseReturnReason(models.Model):
    _name = 'purchase.return.reason'

    name = fields.Char(related='reason_name')
    reason_name = fields.Char(string='Reason', store=True)
    created_by = fields.Char(string='Created By', compute='_compute_created_by', store=True)
    created_date = fields.Datetime(string='Created Date', store=True, default=fields.Date.today)
    active = fields.Boolean(string='Active', default=True)
    department = fields.Many2one(comodel_name='hr.department', string='Department', required=True)

    @api.depends('create_uid')
    def _compute_created_by(self):
        for record in self:
            record.created_by = record.create_uid.name

    def archive(self):
        """Archive the record(s)."""
        self.write({'active': False})

    def unarchive(self):
        """Unarchive the record(s)."""
        self.write({'active': True})
