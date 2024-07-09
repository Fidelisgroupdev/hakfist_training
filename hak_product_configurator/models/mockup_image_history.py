from odoo import fields, models, api
from datetime import date


class MockupImageHistory(models.Model):
    _name = 'mockup.image.history'
    _description = 'Mockup Image History'

    task_id = fields.Many2one('project.task', string="Task")
    previous_image = fields.Binary('Previous Image')
    revision = fields.Integer("Revision")
    updated_date = fields.Datetime('Date')
