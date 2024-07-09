# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class InterCompanyPayment(models.Model):
    _name = 'inter.company.payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Inter Company Payment'

    name = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner', string="Partner")
    source_payment_id = fields.Many2one('account.payment', string="Source Payment")
    source_partner_id = fields.Many2one('res.partner', string="Source Partner ID")
    destination_payment_id = fields.Many2one('account.payment', string="Destination Payment")
    payment_method_line_id = fields.Many2one('account.payment.method.line', string="Payment Method")
    source_journal_id = fields.Many2one('account.journal', string="Source Journal")
    destination_journal_id = fields.Many2one('account.journal', string="Destination Journal")
    payment_type = fields.Selection([
        ('outbound', 'Send'),
        ('inbound', 'Receive'),
    ], string='Payment Type', default='inbound', required=True, tracking=True)
    date = fields.Date(string="Date")
    amount = fields.Float(string="Amount")
    ref = fields.Char(string="Memo")
    company_id = fields.Many2one('res.company', string="Inter Company", compute='_compute_company_id', store=False)
    state = fields.Selection(([('draft', 'Draft'), ('confirm', 'Confirmed'), ('post', 'Posted')]), string='State',
                             default='draft')
    payment_inter_order_count = fields.Integer(compute='_compute_payment_inter_order_count')
    source_payment_order_count = fields.Integer(compute='_compute_payment_inter_order_count')

    def _compute_payment_inter_order_count(self):
        for rec in self:
            orders_count = self.env['account.payment'].sudo().search_count(
                [('id', '=', self.destination_payment_id.id)])
            rec.payment_inter_order_count = orders_count
            source_orders_count = self.env['account.payment'].sudo().search_count(
                [('id', '=', self.source_payment_id.id)])
            rec.source_payment_order_count = source_orders_count

    def _compute_company_id(self):
        if self.partner_id:
            company_id = self.env['res.company'].search([('partner_id', '=', self.partner_id.id)], limit=1)
            if company_id:
                self.company_id = company_id.id
            else:
                self.company_id = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New') or 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('inter.company.payment') or _('New')
        source_payment_id = self._context.get('context_source_payment_id')
        destination_payment_id = self._context.get('context_destination_payment_id')
        res = super(InterCompanyPayment, self).create(vals_list)
        if destination_payment_id:
            res.update({"destination_payment_id": destination_payment_id})
        if source_payment_id:
            res.update({"source_payment_id": source_payment_id})
        return res

    def open_set_destination_journal_wiz(self):
        return {
            'name': _('Create Inter Company Payment'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'inter.company.payment.wiz',
            'target': 'new',
            'view_id': self.env.ref('inter_company_payments.create_inter_company_transaction_wiz_views').id,
        }

    def action_view_intercompany_payment(self):
        action = self.env.ref('account.action_account_payments')
        domain = [('id', '=', self.destination_payment_id.id)]
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_mode': action.view_mode,
            'target': action.target,
            'domain': domain,
            'context': {'context_destination_payment_id': self.id},
            'res_model': action.res_model,
        }
        return result

    def action_view_source_payment(self):
        action = self.env.ref('account.action_account_payments')
        domain = [('id', '=', self.source_payment_id.id)]
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
