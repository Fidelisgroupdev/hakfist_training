from odoo import api, models, fields, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    family_code = fields.Char(string='Family Suffix')
    reference_type = fields.Selection([('family_code', 'Family Code'), ('sl_no', 'Serial Number')],
                                      related='categ_id.reference_type')

    @api.constrains('family_code')
    def _check_family_code_size(self):
        for record in self:
            if record.reference_type == 'family_code':
                if len(record.family_code) < 4:
                    raise UserError(_('Family Code must be at least 4 characters long.'))


class ProductProduct(models.Model):
    _inherit = 'product.product'

    family_code = fields.Char(string='Family Code', related='product_tmpl_id.family_code')
    old_sku = fields.Char(string='Zoho reference')

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for product in res:
            if product.product_tmpl_id.categ_id.reference_type == 'family_code':
                attribute_ids = self.env['product.attribute']
                product_attribute_value_ids = self.env['product.attribute.value']
                for attr_value in product.product_template_attribute_value_ids:
                    attrs = product.product_tmpl_id.attribute_line_ids.filtered(
                        lambda x: x.attribute_id == attr_value.attribute_id)
                    for at in attrs:
                        if at.value_count > 1:
                            if attr_value.attribute_id not in attribute_ids:
                                attribute_ids += attr_value.attribute_id
                            if attr_value.product_attribute_value_id not in product_attribute_value_ids:
                                product_attribute_value_ids += attr_value.product_attribute_value_id
                sorted = attribute_ids.sorted(key=lambda r: r.sl_no)
                code = ''
                for attribute in sorted:
                    attribute_value = product_attribute_value_ids.filtered(
                        lambda x: x.attribute_id == attribute)
                    for attr in attribute_value:
                        if attr.code:
                            code += attr.code + '-'
                        else:
                            raise UserError(_('Code is missing in attribute value %s') % (attribute_value.name))
                code = code[:-1]
                if product.product_tmpl_id.family_code:
                    if product.product_tmpl_id.categ_id.prefix:
                        product.default_code = product.product_tmpl_id.categ_id.prefix + product.product_tmpl_id.family_code + '-' + code if code else product.product_tmpl_id.categ_id.prefix + product.product_tmpl_id.family_code
                    else:
                        product.default_code = product.product_tmpl_id.family_code + '-' + code if code else  product.product_tmpl_id.family_code
            elif product.product_tmpl_id.categ_id.reference_type == 'sl_no':
                seqcode = self.env['ir.sequence'].next_by_code(
                    'product.category_%s' % product.product_tmpl_id.categ_id.id)
                if product.product_tmpl_id.family_code:
                    seqcode = product.product_tmpl_id.family_code + str(seqcode)
                if product.product_tmpl_id.categ_id.prefix:
                    seqcode = product.product_tmpl_id.categ_id.prefix + str(seqcode)
                product.default_code = seqcode
                # 'product.category_%s' % (product.product_tmpl_id.id)
        # res.prodcut_template_variant_value_ids.filtered(lambda x:)
        return res


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    sl_no = fields.Integer(string='Serial Number')
    _sql_constraints = [
        ('sl_no_attribute_uniq', 'unique (sl_no)', 'The Serial Number of the attribute must be unique')
    ]


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'
    _sql_constraints = [
        ('code_attribute_uniq', 'unique (attribute_id, code)', 'The code for each attribute values must be unique')
    ]

    code = fields.Char(string='Code')

    @api.constrains('code')
    def _check_no_space_in_code(self):
        for record in self:
            if ' ' in record.code:
                raise UserError("Code field cannot contain spaces!")


class ProductTemplateAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'

    @api.onchange('attribute_id')
    def onchange_attribute_id(self):
        for attribute in self:
            if not attribute.product_tmpl_id.family_code and attribute.product_tmpl_id.categ_id.reference_type == 'family_code':
                raise UserError(_('Family Code is missing in Product Master'))
