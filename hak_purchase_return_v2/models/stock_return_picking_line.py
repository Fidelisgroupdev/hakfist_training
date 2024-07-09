from odoo import models, fields, api, _


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    # Old fields
    product_id = fields.Many2one('product.product', string="Product", required=True, domain="[('id', '=', product_id)]")
    quantity = fields.Float("Quantity", digits='Product Unit of Measure', required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id')
    wizard_id = fields.Many2one('stock.return.picking', string="Wizard")
    move_id = fields.Many2one('stock.move', "Move")
    # New field
    reason_for_return = fields.Many2one(comodel_name='purchase.return.reason', string='Reason For Return', store=True,
                                        domain="[('department', '=', user_department)]")
    return_notes = fields.Text(string="Notes", store=True)

    @api.model
    def _get_user_department(self):
        return self.env.user.department_id.id

    user_department = fields.Many2one(comodel_name='hr.department', string='Department',
                                      default=_get_user_department)






