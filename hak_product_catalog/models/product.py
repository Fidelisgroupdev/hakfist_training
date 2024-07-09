from odoo import fields, models, api, _
from datetime import date
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    free_qty = fields.Float('Free To Use Quantity ', compute='_compute_free_qty', digits='Product Unit of Measure',
                            store=True)

    from_crm = fields.Boolean(string='From CRM', default=False)

    @api.depends('family_code', 'categ_id')
    def _compute_family_code_ext(self):
        for rec in self:
            if rec.categ_id and rec.family_code:
                rec.family_code_ext = rec.categ_id.prefix + rec.family_code

    @api.depends('qty_available')
    def _compute_free_qty(self):
        for rec in self:
            print("_compute_free_qty")
            total_free_qty = 0
            product_domain = [('product_tmpl_id', '=', rec.id)]
            products = self.env['product.product'].search(product_domain)
            print("products", products)
            total_free_qty = sum(products.mapped("free_qty"))
            print("total_free_qty", total_free_qty)
            rec.free_qty = total_free_qty

    def action_open_product_catalog(self):
        print("self._context action_open_product_catalog", self._context)
        crm_id = self.env['crm.lead'].browse(int(self._context.get('active_id')))
        return {
            'name': _('Product Catalog'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'product.catalog.wizard',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': {
                'default_view_type': 'product',
                'default_crm_id': crm_id.id if crm_id else False,
                'default_partner_id': crm_id.partner_id.id if crm_id.partner_id else False,
                'default_product_type': 'template',
            }
        }


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def action_open_product_catalog(self):
        print("self._context action_open_product_catalog product.product", self._context)
        print("self._context.get('params')", self._context.get('params'))
        crm_id = self.env['crm.lead'].browse(int(self._context.get('active_id')))
        return {
            'name': _('Product Catalog'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'product.catalog.wizard',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': {
                'default_view_type': 'product',
                'default_crm_id': crm_id.id if crm_id else False,
                'default_partner_id': crm_id.partner_id.id if crm_id.partner_id else False,
                'default_product_type': 'variant',
            }
        }
