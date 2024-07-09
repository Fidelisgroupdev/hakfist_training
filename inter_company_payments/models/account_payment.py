# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_inter_company_transfer = fields.Boolean(string='Is Inter Company')
    is_payment_auto_created = fields.Boolean(string="Is Payment Auto Created")
    inter_payment_order_count = fields.Integer(compute='_compute_inter_payment_order_count')

    def _compute_inter_payment_order_count(self):
        for rec in self:
            orders_count = self.env['inter.company.payment'].sudo().search_count(
                [('source_payment_id', '=', rec.id)])
            rec.inter_payment_order_count = orders_count

    @api.onchange('partner_id')
    def _onchange_partner_id_company(self):
        if self.partner_id.is_inter_company:
            company_id = self.env['res.company'].search([('partner_id', '=', self.partner_id.id)], limit=1)
            if company_id:
                self.is_inter_company_transfer = True
            else:
                self.is_inter_company_transfer = False

    def action_post(self):
        res = super(AccountPayment, self).action_post()
        if not self.is_payment_auto_created and self.partner_id.is_inter_company == True and self.is_internal_transfer == False:
            self.create_inter_company_payment()
        return res

    def create_inter_company_payment(self):
        self.env['inter.company.payment'].create({
            'name': _('New'),
            'source_payment_id': self.id,
            'source_journal_id': self.journal_id.id,
            'partner_id': self.partner_id.id,
            'source_partner_id': self.env.user.partner_id.id,
            'payment_type': self.payment_type,
            'date': self.date,
            'amount': self.amount,
            'ref': self.ref,
            'state': 'confirm',
        })

    def button_open_inter_company_payment(self):
        action = self.env.ref('inter_company_payments.inter_company_payment_action')
        domain = [('source_payment_id', '=', self.id)]
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_mode': action.view_mode,
            'target': action.target,
            'domain': domain,
            'context': {'context_source_payment_id': self.id},
            'res_model': action.res_model,
        }
        return result
