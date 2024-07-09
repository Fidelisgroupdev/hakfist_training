from odoo import api, models, fields, _
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    reference_type = fields.Selection(
        [('family_code', 'Family Code'), ('sl_no', 'Serial Number'), ('manual', 'Manual')], default='manual')
    prefix = fields.Char(string='Prefix')
    sequence_id = fields.Many2one('ir.sequence', string='Sequence Number')

    @api.onchange('reference_type')
    def onchange_reference_type(self):
        if self.product_count > 0:
            raise UserError(
                _('You are not allowed to change reference type as already some products are linked to this category'))

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for categ in res:
            sequence = self.env['ir.sequence'].create(
                {'name': categ.name, 'implementation': 'standard',
                 'number_next_actual': 1, 'padding': 4, 'number_increment': 1,
                 'code': 'product.category_%s' % categ.id,
    'company_id': False})
            categ.sequence_id = sequence

            if categ.reference_type == 'sl_no' and not categ.prefix:
                raise UserError(_('Please set prefix for the category %s') % categ.name)
        return res
