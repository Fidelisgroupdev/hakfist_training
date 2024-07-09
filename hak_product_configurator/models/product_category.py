from odoo import fields, models, api
from datetime import date


class ProductCategory(models.Model):
    _inherit = 'product.category'

    personalization_applicable = fields.Boolean(string="Personalization Applicable")
    personalized_product = fields.Boolean(string="Personalized Product")
    customized_product = fields.Boolean(string="Readymade")
    psc_product = fields.Boolean(string="PSC")
    fully_customized_product = fields.Boolean(string="Customized Product")
    personalized_category_id = fields.Many2one("product.category", 'Personalized Category')
    hak_margin = fields.Float(string='Margin %')
    printing_category_id = fields.Many2one('printing.category', string="Printing Category")
    semi_fg_category_id = fields.Many2one("product.category", 'Semi FG Category')

    @api.onchange('personalization_applicable')
    def _onchange_personalization_applicable(self):
        for rec in self:
            if rec.personalization_applicable:
                rec.personalized_product = False
                rec.customized_product = False
                rec.fully_customized_product = False
            # else:
            #     rec.personalization_applicable = False

    @api.onchange('customized_product')
    def _onchange_customized_product(self):
        if self.customized_product:
            self.personalization_applicable = False
            self.personalized_product = False
            self.fully_customized_product = False

    @api.onchange('fully_customized_product')
    def _onchange_fully_customized_product(self):
        if self.fully_customized_product:
            self.personalization_applicable = False
            self.personalized_product = False
            self.customized_product = False

    @api.onchange('personalized_product')
    def _onchange_personalized_product(self):
        for rec in self:
            if rec.personalized_product:
                rec.personalization_applicable = False
                rec.customized_product = False
                rec.fully_customized_product = False