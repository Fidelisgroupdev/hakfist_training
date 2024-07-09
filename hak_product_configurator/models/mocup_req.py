import json
from odoo import fields, Command, models, api, _
from odoo.osv import expression
from odoo.exceptions import UserError


class MockRequest(models.Model):
    _name = 'mockup.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Mockup Request'

    name = fields.Char("Name")
    ref = fields.Char("Reference")
    crm_id = fields.Many2one('crm.lead', 'CRM')
    crm_line_id = fields.Many2one('crm.product.line', 'CRM Line')
    partner_logo_id = fields.Many2one('partner.logo', related='crm_id.partner_logo')
    mock_doc_id = fields.Many2one('documents.document')
    task_user_id = fields.Many2one('res.users', string='Assignee')
    active = fields.Boolean(string='Active')

    product_cust_id = fields.Many2one('product.template', 'Customised Product')
    product_ids = fields.Many2many('product.template', compute='_compute_cust_product_domain')
    product_parent_id = fields.Many2one('product.product', 'Main Product')
    task_ids = fields.One2many('project.task', 'mockup_id')
    # sla_ids = fields.Many2many('helpdesk.sla', 'helpdesk_mock', 'ticket_id', 'sla_id', string="SLAs", copy=False)
    # child_ticket_ids = fields.One2many('mockup.request', 'parent_id', string='Child Tickets')
    # parent_id = fields.Many2one('mockup.request', string='Parent Ticket')
    # hide_fetch_details = fields.Boolean(string='Hide Fetch Details', compute='_compute_hide_fetch_details')
    cust_product_domain = fields.Char(

        readonly=True,
        store=False,

    )
    task_count = fields.Integer(compute='_compute_task_count', string="Task Count")
    state = fields.Selection(
        [('new', 'New'),
         ('assigned', 'Assigned'),
         ('in_progress', 'In Progress'),
         ('waiting_customer_approval', 'Waiting Customer Approval'),
         ('approved', 'Approved'),
         ('rejected', 'Rejected'),
         ('canceled', 'Canceled'),
         ], string='Status', default='new')
    count_task_draft = fields.Integer(compute='_compute_picking_count')
    count_task_assigned = fields.Integer(compute='_compute_picking_count')
    count_task_in_progress = fields.Integer(compute='_compute_picking_count')
    count_task_waiting_cus_approval = fields.Integer(compute='_compute_picking_count')
    count_task_approved = fields.Integer(compute='_compute_picking_count')
    count_task_rejected = fields.Integer(compute='_compute_picking_count')
    count_task_canceled = fields.Integer(compute='_compute_picking_count')

    # rev_mockup_id = fields.Many2one('mockup.request', string="Revision Of", copy=False)
    # rev_mockup_ids = fields.One2many('mockup.request', 'rev_mockup_id', string="Mockup History", copy=False

    def _compute_task_count(self):
        for rec in self:
            project_task_count = self.env['project.task'].sudo().search_count([('mockup_id', '=', rec.id)])
            rec.task_count = project_task_count

    @api.onchange('task_user_id')
    def onchange_task_user_id(self):
        for rec in self:
            print("rec", rec)
            if rec.task_user_id:
                print("rec.task_user_id", rec.task_user_id)
                print("rec._origin.task_user_id", rec._origin.task_user_id)
                if rec.task_ids:
                    print("rec.task_ids", rec.task_ids)
                    for task in rec._origin.task_ids:
                        print("task", task)
                        task.user_ids = False
                        task.write({
                            'user_ids': [(4, rec.task_user_id.id)],
                        })

    def get_mock_req_action(self):
        return self._get_action('hak_product_configurator.action_mock_request_form')

    def _get_action(self, action_xmlid):
        action = self.env["ir.actions.actions"]._for_xml_id(action_xmlid)
        action['res_id'] = self.id
        return action

    def _compute_picking_count(self):
        draft_stage_id = self.env['project.task.type'].search([('is_mockup', '=', True), ('name', '=', 'New')])
        assigned_stage_id = self.env['project.task.type'].search([('is_mockup', '=', True), ('name', '=', 'Assigned')])
        in_progress_stage_id = self.env['project.task.type'].search(
            [('is_mockup', '=', True), ('name', '=', 'In Progress')])
        cus_approval_stage_id = self.env['project.task.type'].search(
            [('is_mockup', '=', True), ('name', '=', 'Waiting Customer Approval')])
        approved_stage_id = self.env['project.task.type'].search([('is_mockup', '=', True), ('name', '=', 'Approved')])
        rejected_stage_id = self.env['project.task.type'].search([('is_mockup', '=', True), ('name', '=', 'Rejected')])
        canceled_stage_id = self.env['project.task.type'].search([('is_mockup', '=', True), ('name', '=', 'Canceled')])
        domains = {
            'count_task_draft': [('stage_id', '=', draft_stage_id.id)],
            'count_task_assigned': [('stage_id', '=', assigned_stage_id.id)],
            'count_task_in_progress': [('stage_id', '=', in_progress_stage_id.id)],
            'count_task_waiting_cus_approval': [('stage_id', '=', cus_approval_stage_id.id)],
            'count_task_approved': [('stage_id', '=', approved_stage_id.id)],
            'count_task_rejected': [('stage_id', '=', rejected_stage_id.id)],
            'count_task_canceled': [('stage_id', '=', canceled_stage_id.id)],
        }
        for rec in self:
            for field_name, domain in domains.items():
                data = self.env['project.task']._read_group(domain +
                                                            [('is_mockup', '=', True),
                                                             ('mockup_id', '=', rec.id)],
                                                            ['mockup_id'], ['__count'])
                count = {mockup.id: count for mockup, count in data}
                for record in rec:
                    record[field_name] = count.get(record.id, 0)

    def get_action_task_tree_new(self):
        action = self._get_action('hak_product_configurator.action_view_all_task_inherit')
        draft_stage_id = self.env['project.task.type'].search([('is_mockup', '=', True), ('name', '=', 'New')])
        action['domain'] = [('stage_id', '=', draft_stage_id.id), ('mockup_id', '=', self.id)]
        return action

    def get_action_task_tree_in_progress(self):
        action = self._get_action('hak_product_configurator.action_view_all_task_inherit')
        in_progress_stage_id = self.env['project.task.type'].search(
            [('is_mockup', '=', True), ('name', '=', 'In Progress')])
        action['domain'] = [('stage_id', '=', in_progress_stage_id.id), ('mockup_id', '=', self.id)]
        return action

    def get_action_task_tree_assigned(self):
        action = self._get_action('hak_product_configurator.action_view_all_task_inherit')
        assigned_stage_id = self.env['project.task.type'].search([('is_mockup', '=', True), ('name', '=', 'Assigned')])
        action['domain'] = [('stage_id', '=', assigned_stage_id.id), ('mockup_id', '=', self.id)]
        return action

    def get_action_task_tree_wc_approval(self):
        action = self._get_action('hak_product_configurator.action_view_all_task_inherit')
        cus_approval_stage_id = self.env['project.task.type'].search(
            [('is_mockup', '=', True), ('name', '=', 'Waiting Customer Approval')])
        action['domain'] = [('stage_id', '=', cus_approval_stage_id.id), ('mockup_id', '=', self.id)]
        return action

    def get_action_task_tree_approved(self):
        action = self._get_action('hak_product_configurator.action_view_all_task_inherit')
        approved_stage_id = self.env['project.task.type'].search([('is_mockup', '=', True), ('name', '=', 'Approved')])
        action['domain'] = [('stage_id', '=', approved_stage_id.id), ('mockup_id', '=', self.id)]
        return action

    def get_action_task_tree_rejected(self):
        action = self._get_action('hak_product_configurator.action_view_all_task_inherit')
        rejected_stage_id = self.env['project.task.type'].search([('is_mockup', '=', True), ('name', '=', 'Rejected')])
        action['domain'] = [('stage_id', '=', rejected_stage_id.id), ('mockup_id', '=', self.id)]
        return action

    def get_action_task_tree_canceled(self):
        action = self._get_action('hak_product_configurator.action_view_all_task_inherit')
        canceled_stage_id = self.env['project.task.type'].search([('is_mockup', '=', True), ('name', '=', 'Canceled')])
        action['domain'] = [('stage_id', '=', canceled_stage_id.id), ('mockup_id', '=', self.id)]
        return action

    def action_view_tasks(self):
        action = self.env['ir.actions.act_window'].sudo()._for_xml_id(
            'hak_product_configurator.action_view_all_task_inherit')
        action['domain'] = [('mockup_id', '=', self.id)]
        return action

    @api.model
    def create(self, vals):
        print("Mockup create", vals)
        record = super(MockRequest, self).create(vals)
        mock_req_seq = self.env['ir.sequence'].next_by_code('mock.request')
        print("mock_req_seq", mock_req_seq)
        record.name = mock_req_seq or 'New'
        print("record.name", record.name)
        return record

    def add_mock_doc(self):
        return {
            'name': _("Add Mockup Doc"),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('hak_product_configurator.add_mockup_doc_form_view').id,
            'res_model': 'add.mockup.doc',
            'context': {
                'default_mockup_id': self.id if self else False,
            },
            'target': 'new',
        }

    # def action_fetch_details(self):
    #     # self.write({'product_parent_id': self.product_cust_id.hak_master_product_id.id})
    #     self.line_ids = False
    #
    #     # line_products = self.crm_id.product_line_ids.filtered(
    #     #     lambda x: x.hak_type in ['std_with_p', 'psc', 'fully_cus_with', 'cust_with_p'])
    #     # for line_product in line_products:
    #     if self.crm_line_id:
    #         for lines in self.crm_line_id.product_template_id.personalisation_details.get('printing_details'):
    #             if lines.get('print_type_checked'):
    #                 # product_side_details = self.product_cust_id.hak_master_product_id.product_tmpl_id.printing_side_line_ids.filtered(lambda x:x.id == int(lines.get('print_attr_id')))
    #                 product_side_details = self.env['printing.side.line'].search(
    #                     [('id', '=', int(lines.get('print_attr_id')))])
    #                 print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", product_side_details)
    #                 print("lines *****************", lines)
    #                 print("lines.get('print_attr_id') 3333333333333333", lines.get('print_attr_id'))
    #                 # ppp
    #                 data_vals = {
    #                     'request_id': self.id,
    #                     'crm_line_id': self.crm_line_id.id,
    #                     'product_cust_id': self.crm_line_id.product_template_id.id,
    #                     'product_parent_id': self.crm_line_id.product_template_id.hak_master_product_id.id,
    #                     'side': lines.get('print_attr_name'),
    #                     'printing_side_line_id': lines.get('print_attr_id'),
    #                     'printing_side_type_id': product_side_details.printing_side_type_id.id,
    #                     'image': product_side_details.image_1920,
    #                     'image_variant': self.crm_line_id.product_template_id.hak_master_product_id.image_1920,
    #                 }
    #
    #                 if lines.get('spcl_logo'):
    #                     data_vals.update({'logo': lines.get('spcl_logo').replace('data:image/png;base64,',
    #                                                                              '') if 'data:image/png;base64,' in lines.get(
    #                         'spcl_logo') else lines.get('spcl_logo').replace('data:application/pdf;base64,',
    #                                                                          '') or self.product_cust_id.logo})
    #
    #                 else:
    #                     print("ines.get('header_logo')ddddddddd", lines.get('main_header_logo'))
    #                     if lines.get('main_header_logo'):
    #                         data_vals.update({
    #                             'logo': self.env['partner.logo'].search(
    #                                 [('id', '=', int(lines.get('main_header_logo')))]).logo
    #
    #                         })
    #
    #                 mock_line = self.env['mockup.lines'].create(data_vals)
    #
    #                 attachment = self.env['ir.attachment'].create({
    #                     'name': str(self.name) + str(mock_line.side),
    #                     'type': 'binary',
    #                     'datas': mock_line.logo,
    #                     'res_model': 'mockup.lines',
    #                     'res_id': mock_line.id,
    #                     # 'mimetype': 'application/x-pdf' if 'data:application/pdf;base64,' in article else 'image/png'
    #                 })
    #                 mock_line.attachment_id = attachment.id

    @api.onchange('product_cust_id')
    def onchange_product_cust_id(self):
        self.write({'product_parent_id': self.product_cust_id.hak_master_product_id.id})

    @api.depends('crm_id')
    def _compute_cust_product_domain(self):
        product = self.env['product.template']
        for rec in self:
            if not rec.crm_id:
                # rec.cust_product_domain = json.dumps(
                #     []
                # )
                rec.product_ids = [Command.set(product.ids)]
            else:
                if self.crm_id:
                    print("dfdsfsdfdscrrrrrrrrrr")
                    jj = self.crm_id.product_line_ids.filtered(
                        lambda x: x.hak_type in ['std_with_p', 'psc', 'fully_cus_with', 'cust_with_p']).mapped(
                        'product_template_id')
                    print("dfdsfsdfdsssssedescrrrrrrrrrr")
                    # rec.cust_product_domain = json.dumps(
                    #     [('id', 'in', self.crm_id.product_line_ids.mapped('product_template_id').ids)]
                    # )

                    rec.product_ids = [Command.set(jj.ids)]


class Mocklogo(models.Model):
    _name = 'mockup.logo'
    _description = 'Mock Logo'

    name = fields.Char("Reference")
    logo = fields.Binary('Document')
    revision = fields.Integer('Revision', default=0)
    request_id = fields.Many2one('mockup.request', 'Mockup Request')
    # request_line_id = fields.Many2one('mockup.lines', 'Mockup Line ID')
    attachment_id = fields.Many2one('ir.attachment', 'Attachments')

    def write(self, vals):
        if vals.get('logo'):
            attachment = self.env['ir.attachment'].create({
                'name': vals.get('name') or self.name,
                'type': 'binary',
                'datas': vals.get('logo'),
                'res_model': 'mockup.logo',
                'res_id': self.id,
                # 'mimetype': 'application/x-pdf' if 'data:application/pdf;base64,' in article else 'image/png'
            })
            vals['attachment_id'] = attachment.id

        res = super().write(vals)

        return res
