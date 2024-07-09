# -*- coding: utf-8 -*-

from odoo import fields, Command, models, api, _
from odoo.exceptions import UserError
from odoo.tools import html_escape


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[('review', 'Under Review'), ('approve', 'Reviewed'), ('sent',)])
    rev_sale_id = fields.Many2one('sale.order', string="Revision Of", copy=False)
    src_sale_id = fields.Many2one('sale.order', string="Source", copy=False)
    rev_sale_ids = fields.One2many('sale.order', 'rev_sale_id', string="Sale History", copy=False)
    rev_count = fields.Integer(string="Reverse Orders", compute="reversed_order_count", copy=False)
    src_sale_ids = fields.One2many('sale.order', 'src_sale_id', string="Sale History", copy=False)
    org_sale_id = fields.Many2one('sale.order', string="Origin", copy=False, )
    src_count = fields.Integer(string="src Orders", compute="src_order_count", copy=False)
    is_revised = fields.Boolean(string="Is Revised", copy=False)
    reviewed_by = fields.Many2one('res.users', string="Reviewed By", track_visibility='onchange')
    confirm_seq = fields.Char(string="Order Number")
    contact_person_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact Person',
    )

    def action_sent_review(self):
        self.state = 'review'

    def action_order_approve(self):
        self.state = 'approve'
        self.reviewed_by = self.env.user.id

    def revise_quotation(self):
        new_quote = self.copy()
        self.is_revised = True

        if self.org_sale_id:
            new_quote.org_sale_id = self.org_sale_id.id
        else:
            new_quote.org_sale_id = self.id
        self.src_sale_id = new_quote.id
        self.rev_sale_id = new_quote.id
        new_quote.rev_sale_ids = new_quote.rev_sale_ids + self.rev_sale_ids
        new_quote.name = new_quote.org_sale_id.name + "/Rev" + str(len(new_quote.rev_sale_ids))
        self.state = 'cancel'
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'views': [(False, 'form')],
            'res_id': new_quote.id,
        }

    @api.depends('rev_sale_ids')
    def reversed_order_count(self):
        self.rev_count = len(self.rev_sale_ids)

    @api.depends('src_sale_ids')
    def src_order_count(self):
        self.src_count = len(self.src_sale_ids)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.state == 'approve':
            self.state = 'draft'
        return super(SaleOrder, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    # def action_confirm(self):
    #     res = super(SaleOrder, self).action_confirm()
    #     initial = self.env['hr.employee'].search([('id', '=', self.sales_person.id)]).employee_initial
    #     split_seq = self.env['ir.sequence'].next_by_code('conf.sale.seq')
    #     split_seq_1 = split_seq.split('/')[2]
    #     initial_split_concat = initial + "-" + split_seq_1 if initial else split_seq_1
    #     split = split_seq[0:-4]
    #     seq = split + initial_split_concat + "/" + str(fields.Date.today().year)
    #     self.write({
    #         'confirm_seq': seq or _('New')
    #
    #     })
    #     return res

    def action_quotation_sent_new(self):
        if self.filtered(lambda so: so.state != 'approve'):
            raise UserError(_('Only Approved orders can be marked as sent directly.'))
        for order in self:
            order.message_subscribe(partner_ids=order.partner_id.ids)
        self.write({'state': 'sent'})


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    printing_type_id = fields.Many2one('printing.type', string="Printing Type", copy=False)
