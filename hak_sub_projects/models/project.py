# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from lxml import etree
# import simplejson

_logger = logging.getLogger(__name__)


class Project(models.Model):
    _inherit = "project.project"

    parent_project_id = fields.Many2one("project.project", 'Parent Project')
    sub_project_ids = fields.One2many('project.project', 'parent_project_id', string="Parent Project")


    def action_view_sub_projects(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("project.open_view_project_all_config")
        action['domain'] = [('parent_project_id', '=', self.id)]
        # components = self.env['mrp.bom'].sudo().search(
        #     [('component_id', '=', self.id)])
        # if len(components) == 1:
        #     action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        #     action['res_id'] = components.id
        return action

    def unlink(self):
        for rec in self:
            sub_projects = self.env['project.project'].search([('parent_project_id', '=', rec.id)])
            if sub_projects:
                raise UserError(_("Sorry!!! You cannot delete this project, because it has sub projects"))
        return super().unlink()






