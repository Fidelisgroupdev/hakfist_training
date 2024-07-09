from datetime import date
from odoo import api, fields, models, addons, modules, tools, Command, _
from odoo.exceptions import UserError, ValidationError


class Task(models.Model):
    _inherit = 'project.task'

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, order="fold, sequence, id")

    is_mockup = fields.Boolean("Is Mockup")
    crm_id = fields.Many2one("crm.lead", 'CRM')
    salesperson_id = fields.Many2one("res.users", 'Salesperson', related='crm_id.user_id')
    partner_logo_id = fields.Many2one('partner.logo', related='crm_id.partner_logo')
    side = fields.Char('Side')
    mockup_id = fields.Many2one('mockup.request', 'Mockup')
    printing_side_line_id = fields.Many2one('printing.side.line', 'Side')
    printing_side_type_id = fields.Many2one('printing.side.type', 'Side Type')
    logo = fields.Binary('Logo', related='partner_logo_id.logo')
    image = fields.Binary('Side Line Image')
    image_variant = fields.Binary('Variant Image')
    selected_width = fields.Float(string="Width (mm)")
    selected_height = fields.Float(string="Height (mm)")
    selected_color = fields.Integer('Color')
    mockup_file = fields.Binary('Mockup Image')
    mock_logo_ids = fields.Many2many('mockup.logo', string='Documents')
    attachment_id = fields.Many2one('ir.attachment', 'Attachments')
    crm_line_id = fields.Many2one('crm.product.line', 'CRM Line')
    product_cust_id = fields.Many2one('product.template', 'Customised Product')
    product_parent_id = fields.Many2one('product.product', 'Main Product')
    product_ids = fields.Many2many('product.template', compute='_compute_cust_product_domain')
    mockup_image_history_ids = fields.One2many('mockup.image.history', 'task_id', string='Image History')
    stage_id = fields.Many2one('project.task.type', string='Stage', compute='_compute_stage_id',
                               store=True, readonly=False, ondelete='restrict', tracking=True, index=True,
                               default=_get_default_stage_id, group_expand='_read_group_stage_ids',
                               )
    # domain="['|', ('project_ids', '=', project_id), ('is_mockup', '=', 'is_mockup')]")
    # crm_line_ids = fields.One2many('crm.product.line', 'project_id', string="CRM Lines")
    default_stage_ids = fields.Many2many('project.task.type', string='Default Stages',
                                         compute="_compute_default_stage_ids_domain")
    revision = fields.Integer("Revision", default=-2)
    revision_starter = fields.Integer("Revision", default=1)
    updated_date = fields.Datetime('Date')

    @api.onchange('stage_id')
    def onchange_stage_id_check(self):
        for rec in self:
            print("rec._origin.stage_id", rec._origin.stage_id)
            print("rec.stage_id", rec.stage_id)
            if rec.is_mockup:
                stage_id = self.env['project.task.type'].search([('name', '=', 'In Progress')], limit=1)
                print("stage_id", stage_id)
                if stage_id.id == rec.stage_id.id:
                    user_list = [self.env.user.id]
                    user_tasks = self.env['project.task'].search(
                        [('user_ids', 'in', user_list), ('is_mockup', '=', True)])
                    print("user_tasks", user_tasks)
                    for task in user_tasks:
                        if task.stage_id.id == stage_id.id:
                            raise UserError(_('You cannot start this task while another task is in progress.'))

    @api.onchange('mockup_file')
    def onchange_mockup_file(self):
        for rec in self:
            rec.revision = rec.revision + 1
            if rec.revision_starter > 1:
                history = self.env['mockup.image.history'].sudo().create({
                    'task_id': rec._origin.id,
                    'previous_image': rec._origin.mockup_file,
                    'revision': rec.revision,
                    'updated_date': rec._origin.updated_date,
                })

            rec.revision_starter = 2
            rec.updated_date = fields.Datetime.now()

    @api.depends('project_id')
    def _compute_default_stage_ids_domain(self):
        for rec in self:
            if rec.is_mockup:
                domain = ['|', ('project_ids', '=', rec.project_id.id), ('is_mockup', '=', 'is_mockup')]
            else:
                domain = [('project_ids', '=', rec.project_id.id)]
            stages = self.env['project.task.type'].search(domain)
            if stages:
                rec.default_stage_ids = [Command.set(stages.ids)]
            else:
                rec.default_stage_ids = [Command.set([])]

    def action_timer_start(self):
        print("action_timer_start")
        super().action_timer_start()
        if self.is_mockup:
            stage_id = self.env['project.task.type'].search([('name', '=', 'In Progress')], limit=1)
            print("stage_id", stage_id)
            user_list = [self.env.user.id]
            user_tasks = self.env['project.task'].search([('user_ids', 'in', user_list), ('is_mockup', '=', True)])
            print("user_tasks", user_tasks)
            for task in user_tasks:
                if task.stage_id.id == stage_id.id:
                    raise UserError(_('You cannot start this task while another task is in progress.'))
            self.stage_id = stage_id.id

    def write(self, vals):
        print("self", self)
        if self.is_mockup:
            if vals.get('stage_id'):
                stage_rec = self.env['project.task.type'].search([('id', '=', vals.get('stage_id'))], limit=1)
                print("stage_rec", stage_rec)
                stage_id = self.env['project.task.type'].search([('name', '=', 'In Progress')], limit=1)
                print("stage_id", stage_id)
                if stage_id.id == stage_rec.id:
                    user_list = [self.env.user.id]
                    user_tasks = self.env['project.task'].search(
                        [('user_ids', 'in', user_list), ('is_mockup', '=', True)])
                    print("user_tasks", user_tasks)
                    for task in user_tasks:
                        if task.stage_id.id == stage_id.id:
                            raise UserError(_('You cannot start this task while another task is in progress.'))
        result = super().write(vals)
        print("result", result)
        return result


class ProjectStage(models.Model):
    _inherit = 'project.task.type'

    is_mockup = fields.Boolean("Is Mockup")

    @api.model_create_multi
    def create(self, vals_list):
        stages = super().create(vals_list)
        for stage in stages:
            if stage.is_mockup:
                project = self.env['project.project'].search([('name', '=', 'Internal')], limit=1)
                print("project", project)
                if project:
                    stage.project_ids = [(4, project.id)]
        return stages
