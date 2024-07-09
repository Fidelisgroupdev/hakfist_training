from odoo import models, fields, _


class MrRejectionWizard(models.TransientModel):
    _name = "mr.rejection.wizard"

    rejection_reason = fields.Char(string="Rejection Reason")

    def action_department_cancel(self):
        active_id = self.env.context.get('active_id')
        mr_id = self.env['employee.purchase.requisition'].browse(active_id)
        # mr_id.cancel_reason_ids = [(0, 0, {'requisition_product_id': mr_id.id, 'cancel_reason': self.rejection_reason})]
        mr_id.cancel_reason = self.rejection_reason
        mr_id.write({'state': 'rejected'})
        mr_id.rejected_user_id = self.env.uid
        mr_id.reject_date = fields.Date.today()
