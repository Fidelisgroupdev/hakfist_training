from odoo import fields, models, api
from datetime import date

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_amount_in_words = fields.Char(string="Amount in Words", compute='_compute_total_amount_in_words')

    def _compute_total_amount_in_words(self):
        for rec in self:
            if rec.amount_total:
                rec.total_amount_in_words = False
                rec.total_amount_in_words = rec.currency_id.amount_to_text(rec.amount_total)
            else:
                rec.total_amount_in_words = False


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    total_amount_in_words = fields.Char(string="Amount in Words", compute='_compute_total_amount_in_words')
    payment_term_id = fields.Many2one('account.payment.term','Payment Terms')
    validity_days = fields.Char("Validity")
    ref_contact_name = fields.Char(string="Ref Contact Name")
    ref_email = fields.Char(string="Ref Email")
    ref_phone = fields.Char(string="Ref Phone")

    @api.onchange('date_order')
    def onchange_validity_date(self):
        if self.date_order:
            date_order = self.date_order.date()
            days = str((date_order - date.today()).days + 1)
            self.validity_days = days + '\n' + 'Days'
        else:
            self.validity_days = False

    def _compute_total_amount_in_words(self):
        for rec in self:
            if rec.amount_total:
                rec.total_amount_in_words = False
                rec.total_amount_in_words = rec.currency_id.amount_to_text(rec.amount_total)
            else:
                rec.total_amount_in_words = False


class AccountMove(models.Model):
    _inherit = 'account.move'

    total_amount_in_words = fields.Char(string="Amount in Words", compute='_compute_total_amount_in_words')

    def _compute_total_amount_in_words(self):
        for rec in self:
            if rec.amount_total:
                rec.total_amount_in_words = False
                rec.total_amount_in_words = rec.currency_id.amount_to_text(rec.amount_total)
            else:
                rec.total_amount_in_words = False
