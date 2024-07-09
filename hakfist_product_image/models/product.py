# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api
from odoo.osv import expression



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    specs = fields.Char(string="Specification")

    @api.model_create_multi
    def create(self, vals_list):
        print("product.template create !222222222222222")
        for vals in vals_list:
            if "specs" in vals and vals["specs"]:
                desc = vals["description_sale"] if "description_sale" in vals and vals["description_sale"] else ""
                vals["description_sale"] = vals["specs"] + desc
        res = super(ProductTemplate, self).create(vals_list)
        return res

    def write(self, vals):
        # print("product.template write !11111111111111111", vals)
        # pppp
        res = super(ProductTemplate, self).write(vals)
        if "specs" in vals and vals["specs"]:
            self.sudo().description_sale = self.specs + (self.description_sale if self.description_sale else "")
        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            product_ids = []
            if operator in positive_operators:
                product_ids = list(self._search([('default_code', '=', name)] + domain, limit=limit, order=order))
                if not product_ids:
                    product_ids = list(self._search([('barcode', '=', name)] + domain, limit=limit, order=order))
                    if not product_ids:
                        product_ids = list(self._search([('specs', '=', name)] + domain, limit=limit, order=order))
                        print("PRODUCT IDSDSDSD", product_ids)

            if not product_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                product_ids = list(self._search(domain + ['|', ('default_code', operator, name), ('specs', operator, name)], limit=limit, order=order))
                if not limit or len(product_ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(product_ids)) if limit else False
                    product2_ids = self._search(domain + [('name', operator, name), ('id', 'not in', product_ids)], limit=limit2, order=order)
                    product_ids.extend(product2_ids)
            elif not product_ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                domain2 = expression.OR([
                    ['&', ('default_code', operator, name), ('name', operator, name)],
                    ['&', ('default_code', '=', False), ('name', operator, name)],
                ])
                domain2 = expression.AND([domain, domain2])
                product_ids = list(self._search(domain2, limit=limit, order=order))
            if not product_ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    product_ids = list(self._search([('default_code', '=', res.group(2))] + domain, limit=limit, order=order))
            # still no results, partner in context: search on supplier info as last hope to find something
            if not product_ids and self._context.get('partner_id'):
                suppliers_ids = self.env['product.supplierinfo']._search([
                    ('partner_id', '=', self._context.get('partner_id')),
                    '|',
                    ('product_code', operator, name),
                    ('product_name', operator, name)])
                if suppliers_ids:
                    product_ids = self._search([('product_tmpl_id.seller_ids', 'in', suppliers_ids)], limit=limit, order=order)
        else:
            product_ids = self._search(domain, limit=limit, order=order)
        return product_ids

