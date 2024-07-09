"""field  requisition order in stock location """
from odoo import models, fields


class Picking(models.Model):
    """ inherit stock.location model """

    _inherit = 'stock.location'

    is_material_requisition = fields.Boolean(string='Is MR Location')
