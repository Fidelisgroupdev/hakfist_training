from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _po_dept_manager_domain(self):
        return [('id', 'in', self.env.ref('purchase.group_purchase_manager').users.ids)]

    def _po_finance_manager_domain(self):
        return [('id', 'in', self.env.ref('hakfist_po_three_levels_approval.group_purchase_finance_manager').users.ids)]

    def _po_director_domain(self):
        return [('id', 'in', self.env.ref('hakfist_po_three_levels_approval.group_purchase_director').users.ids)]

    state = fields.Selection(
        selection_add=[('finance_approve', 'Finance Approval'), ('director_approve', 'Director Approval'),
                       ('refuse', 'Refuse')])
    user_group_type = fields.Selection(
        [('user', 'User'),
         ('admin', "Admin"),
         ('finance', 'Finance'),
         ('director', 'Director')],
        string="User Group", compute='check_user_group_type', )
    # state = fields.Selection([('draft', 'RFQ'), ('sent', 'RFQ Sent'), ('to approve', 'To Approve'),
    #                           ('finance_approve', 'Finance Approval'), ('director_approve', 'Director Approval'),
    #                           ('purchase', 'Purchase Order'), ('done', 'Locked'), ('refuse', 'Refuse'), ('cancel', 'Cancelled')
    #                           ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    make_form_readonly = fields.Boolean(compute='compute_make_form_readonly')
    dept_manager_approval_required = fields.Boolean(compute='check_approval_required')
    dept_manager_id = fields.Many2one('res.users', string='Approval Department Manager', domain=_po_dept_manager_domain,
                                      copy=False)
    dept_manager_approve_date = fields.Datetime('Department Manager Approval Date', readonly=True, copy=False)

    finance_approval_required = fields.Boolean(compute='check_approval_required')
    finance_approval_id = fields.Many2one('res.users', string='Approval Finance Manager',
                                          domain=_po_finance_manager_domain, copy=False)
    finance_manager_approve_date = fields.Datetime('Finance Manager Approval Date', readonly=True, copy=False)

    director_approval_required = fields.Boolean(compute='check_approval_required')
    director_approval_id = fields.Many2one('res.users', string='Approval Director', domain=_po_director_domain,
                                           copy=False)
    director_approve_date = fields.Datetime('Director Approval Date', readonly=True, copy=False)

    refused_user_id = fields.Many2one('res.users', string='Refused By', copy=False)
    refused_date = fields.Date('Refused Date', readonly=True, copy=False)
    refused_reason = fields.Text('Refused Reason', readonly=True, copy=False)

    last_approval_id = fields.Many2one('res.users', string='Last Approver', copy=False)

    @api.depends('amount_total')
    def check_approval_required(self):
        for po in self:
            vals = {'finance_approval_required': False, 'director_approval_required': False,
                    'dept_manager_approval_required': False}
            if po.company_id and po.company_id.three_step_approval and po.company_id.set_approval_user_required:
                if po.amount_total > po.company_id.finance_approve_limit:
                    vals.update({'finance_approval_required': True})
                if po.amount_total > po.company_id.director_approve_limit:
                    vals.update({'director_approval_required': True})
                if po.amount_total > po.company_id.dept_manager_approve_limit:
                    vals.update({'dept_manager_approval_required': True})
            po.write(vals)

    @api.depends('state')
    def compute_make_form_readonly(self):
        for po in self:
            if po.state not in ['draft','sent']:
                po.make_form_readonly = True
            else:
                po.make_form_readonly = False

    @api.depends('last_approval_id')
    def check_user_group_type(self):
        for po in self:
            if po.last_approval_id:
                groups_ids = po.last_approval_id.groups_id.ids
                if self.env.ref('hakfist_po_three_levels_approval.group_purchase_director').id in groups_ids:
                    po.user_group_type = 'director'
                elif self.env.ref('hakfist_po_three_levels_approval.group_purchase_finance_manager').id in groups_ids:
                    po.user_group_type = 'finance'
                elif self.env.ref('purchase.group_purchase_manager').id in groups_ids:
                    po.user_group_type = 'admin'
                else:
                    po.user_group_type = 'user'
            else:
                po.user_group_type = 'user'

    def button_confirm(self):
        # Regular Confirm Override Base Method And Added Three Step Approval
        for po in self:
            if po.state not in ['draft', 'sent']:
                continue
            po._add_supplier_to_product()
            if not po.company_id.three_step_approval == True or po.amount_total < self.env.user.company_id.currency_id._convert(
                    po.company_id.dept_manager_approve_limit, po.currency_id):
                po.button_approve(force=True)
            else:
                po.write({'state': 'to approve'})  # Call For Manager Approval
        return True

    def button_approve(self, force=False):
        # Regular Approve Override Base Method And Added Three Step Approval
        for po in self:
            company = po.company_id
            if not company.three_step_approval or (
                    company.dept_manager_approve_limit <= 0 or company.finance_approve_limit <= 0 or company.director_approve_limit <= 0):
                return super(PurchaseOrder, self).button_approve(force=force)
            if po.dept_manager_id and self.env.user != po.dept_manager_id and not force:
                raise UserError(_("Only %s User Can Approve This Order." % (po.dept_manager_id.name)))
            if po.amount_total < self.env.user.company_id.currency_id._convert(po.company_id.finance_approve_limit,
                                                                              po.currency_id):
                if force:
                    po.write({'state': 'purchase'})
                else:
                    po.write({'state': 'purchase', 'dept_manager_id': self.env.uid, 'last_approval_id': self.env.uid,
                              'dept_manager_approve_date': fields.Datetime.now()})
                po._create_picking()
                po.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
            else:
                company.approve_mail_template.send_mail(po.id)
                po.write({'state': 'finance_approve', 'dept_manager_id': self.env.uid, 'last_approval_id': self.env.uid,
                          'dept_manager_approve_date': fields.Datetime.now()})
        return {}

    def purchase_finance_manager_approve(self):
        print("purchase_finance_manager_approve")
        for po in self:
            company = po.company_id
            if po.finance_approval_id and self.env.user != po.finance_approval_id:
                raise UserError(_("Only %s User Can Approve This Order." % (po.finance_approval_id)))
            if po.amount_total < self.env.user.company_id.currency_id._convert(po.company_id.director_approve_limit,
                                                                              po.currency_id):
                print("##################", po.amount_total,self.env.user.company_id.currency_id._convert(po.company_id.director_approve_limit,po.currency_id))
                po.write({'state': 'purchase', 'date_approve': fields.Date.context_today(self), 'finance_approval_id': self.env.uid, 'last_approval_id': self.env.uid,
                     'finance_manager_approve_date': fields.Datetime.now()})
                po._create_picking()
                po.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
            else:
                print("!!!!!!!!!!!!!!!!!!")
                company.approve_mail_template.send_mail(po.id)
                po.write(
                    {'state': 'director_approve', 'finance_approval_id': self.env.uid, 'last_approval_id': self.env.uid,
                     'finance_manager_approve_date': fields.Datetime.now()})
        return {}

    def purchase_director_approve(self):
        for po in self:
            company = po.company_id
            if po.director_approval_id and self.env.user != po.director_approval_id:
                raise UserError(_("Only %s User Can Approve This Order." % (po.director_approval_id)))
            company.approve_mail_template.send_mail(po.id)
            po.write({'state': 'purchase', 'director_approval_id': self.env.uid, 'last_approval_id': self.env.uid,
                      'director_approve_date': fields.Datetime.now(), 'date_approve': fields.Date.context_today(self)})
            po._create_picking()
            po.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
        return {}

    def refused_order(self):
        # Check User Access
        groups_ids = self.env.user.groups_id.ids
        access = ''
        if self.env.ref('hakfist_po_three_levels_approval.group_purchase_director').id in groups_ids:
            access = 'purchase_director'
        elif self.env.ref('hakfist_po_three_levels_approval.group_purchase_finance_manager').id in groups_ids:
            access = 'finance_manager'
        elif self.env.ref('purchase.group_purchase_manager').id in groups_ids:
            access = 'purchase_manager'
        for po in self:
            if po.state == 'director_approve' and access != 'purchase_director':
                raise UserError(_('You Can Not Reject This Order'))
            elif po.state == 'finance_approve' and access not in ['finance_manager', 'purchase_director']:
                raise UserError(_('You Can Not Reject This Order'))
            elif po.state == 'to approve' and access not in ['purchase_manager', 'finance_manager',
                                                             'purchase_director']:
                raise UserError(_('You Can Not Reject This Order'))
            return {
                'name': 'Purchase Order Refuse',
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order.refuse',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_purchase_order_id': po.id},
            }

    def button_cancel(self):
        show_warning = True
        groups_ids = self.env.user.groups_id.ids
        access = ''
        if self.env.ref('hakfist_po_three_levels_approval.group_purchase_director').id in groups_ids:
            access = 'director'
        elif self.env.ref('hakfist_po_three_levels_approval.group_purchase_finance_manager').id in groups_ids:
            access = 'finance'
        elif self.env.ref('purchase.group_purchase_manager').id in groups_ids:
            access = 'admin'
        for po in self:
            if po.user_group_type == 'user':
                if access in ['director', 'finance','admin'] or self.env.user.id == po.last_approval_id.id:
                    show_warning = False
            elif po.user_group_type == 'admin':
                if access in ['director', 'finance'] or self.env.user.id == po.last_approval_id.id:
                    show_warning = False
            elif po.user_group_type == 'finance':
                if access == 'director' or self.env.user.id == po.last_approval_id.id:
                    show_warning = False
            else:
                if self.env.user.id == po.last_approval_id.id:
                    show_warning = False
        if show_warning:
            raise UserError(_('You are not allowed to cancel this order'))
        return super().button_cancel()

    def button_draft(self):
        self.write({
            'finance_approval_id': False,
            'last_approval_id': False,
            'director_approval_id': False,
            'dept_manager_id': False,
            'dept_manager_approve_date': False,
            'finance_manager_approve_date': False,
            'director_approve_date': False,
            'refused_user_id': False,
            'refused_date': False,
            'refused_reason': False,
        })
        return super().button_draft()
