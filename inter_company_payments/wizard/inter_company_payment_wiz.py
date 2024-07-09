# -*- coding:utf-8 -*-

from odoo import models, fields, api
import json


class InterCompanyPayment(models.TransientModel):
    _name = 'inter.company.payment.wiz'
    _description = 'Inter Company Payment Wiz'

    def _default_source_payment_id(self):
        active_id = self._context.get('active_id')
        source_payment_id = self.env['inter.company.payment'].browse(active_id)
        return source_payment_id

    def _default_source_journal_id(self):
        active_id = self._context.get('active_id')
        source_payment_id = self.env['inter.company.payment'].browse(active_id)
        if source_payment_id:
            return source_payment_id.source_journal_id
        else:
            return None

    source_payment_id = fields.Many2one('inter.company.payment', string='Source Payment',
                                        default=_default_source_payment_id)
    source_journal_id = fields.Many2one('account.journal', string='Source Journal', default=_default_source_journal_id)
    destination_journal_id = fields.Many2one('account.journal', string='Destination Journal', domain="[('id', 'in', journal_ids)]")
    # destination_journal_id_domain = fields.Char(compute="_compute_destination_journal_id_domain", readonly=True, store=False)
    payment_method_id = fields.Many2one('account.payment.method.line',domain="[('id', 'in', available_payment_method_line_ids)]",
                                        string='Payment Method')
    # payment_method_id_domain = fields.Char(readonly=True, store=False)
    available_payment_method_line_ids = fields.Many2many('account.payment.method.line')
    journal_ids = fields.Many2many('account.journal', string='Journals', compute='_compute_journal_ids')

    def _get_payment_method_codes_to_exclude(self):
        # can be overriden to exclude payment methods based on the payment characteristics
        self.ensure_one()
        return []

    @api.onchange('destination_journal_id')
    def onchange_payment_method_line_fields(self):
        for pay in self:
            if pay.destination_journal_id:
                pay.payment_method_id = False
                payment_type = False
                icp_id = self.source_payment_id
                if icp_id:
                    if icp_id.payment_type == 'inbound':
                        payment_type = 'outbound'
                    if icp_id.payment_type == 'outbound':
                        payment_type = 'inbound'
                pay.available_payment_method_line_ids = pay.destination_journal_id._get_available_payment_method_lines(payment_type)
                to_exclude = pay._get_payment_method_codes_to_exclude()
                if to_exclude:
                    pay.available_payment_method_line_ids = pay.available_payment_method_line_ids.filtered(
                        lambda x: x.code not in to_exclude)

    @api.depends('source_payment_id.company_id')
    def _compute_journal_ids(self):
        for rec in self:
            destination_journal_id_list = []
            icp_id = self.source_payment_id
            icp_company_id = self.env['res.company'].search([('partner_id', '=', icp_id.partner_id.id)])
            if rec.source_payment_id.company_id:
                accounts = self.env['account.journal'].sudo().search([('company_id', '=', icp_company_id.id)])
                for account in accounts:
                    print('cpm[any', account.company_id.name, '==', rec.source_payment_id.company_id.name)
                    if account.company_id.id == icp_company_id.id:
                        destination_journal_id_list.append(account.id)
                rec.journal_ids = destination_journal_id_list
            else:
                rec.journal_ids = False

    def create_internal_payment(self):
        if self.source_payment_id and self.destination_journal_id:
            payment_type = False
            company_id = False
            icp_id = self.source_payment_id
            if icp_id:
                if icp_id.payment_type == 'inbound':
                    payment_type = 'outbound'
                if icp_id.payment_type == 'outbound':
                    payment_type = 'inbound'
                company_id = self.env['res.company'].search([('partner_id', '=', icp_id.partner_id.id)])
                payment_id = self.env['account.payment'].create({
                    'journal_id': self.destination_journal_id.id,
                    'is_inter_company_transfer': True,
                    'outstanding_account_id': self.payment_method_id.payment_account_id.id,
                    'payment_method_line_id': self.payment_method_id.id or False,
                    'company_id': company_id.id,
                    'partner_id': company_id.partner_id.id,
                    'payment_type': payment_type,
                    'date': icp_id.date or False,
                    'amount': icp_id.amount or False,
                    'is_payment_auto_created': True,
                    'ref': icp_id.ref or False,
                })

                payment_id.action_post()
                self.source_payment_id.write({'destination_journal_id': self.destination_journal_id.id,
                                              'payment_method_line_id': self.payment_method_id.id,
                                              'state': 'post',
                                              'destination_payment_id': payment_id.id})
