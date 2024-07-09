import json

from odoo import fields, models, api, Command, _
from datetime import date
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _default_hak_margin(self):
        for rec in self:
            if rec.categ_id:
                return rec.categ_id.hak_margin
            else:
                return 0

    personalization_applicable = fields.Boolean(string="Personalization Applicable",
                                                related='categ_id.personalization_applicable')
    customized_product = fields.Boolean(string="Customized Product", related='categ_id.customized_product', )
    fully_customized_product = fields.Boolean(string="Fully Customized Product",
                                              related='categ_id.fully_customized_product')
    psc_product = fields.Boolean(string="PSC", related='categ_id.psc_product')
    printing_side_line_ids = fields.One2many('printing.side.line', 'product_temp_id', string="Printing Sides")
    selected_ids = fields.One2many('selected.printing.side.line', 'product_temp_id', string="Selected Values")
    family_code_ext = fields.Char(string='Family Code', compute='_compute_family_code_ext', store=True)
    hak_margin = fields.Float(default=_default_hak_margin, readonly=False)
    is_margin_fixed = fields.Boolean('Is Fixed?', default=False)
    sc = fields.Float('Mulitplier(SC)', default=1)
    pc = fields.Float('Mulitplier(PC)', default=1)
    hak_master_product_id = fields.Many2one('product.product', string='Master Product')
    logo = fields.Binary(
        string='Global Product Image',

        help='Use as the global image for all product default images. '
             'Limited to 1024x1024.',
    )

    personalisation_details = fields.Json('Details', copy=False, readonly=False)
    personalized_product = fields.Boolean(string="Personalized Product", related='categ_id.personalized_product')
    hak_type_sub = fields.Selection(
        [('personalization_applicable', 'HAK items'),
         ('customized_product', 'Ready made'),
         ('psc', 'PSC'),
         ('fully_customized_product', 'Customized'),
         ], string='Type Sub', compute='_compute_hak_type_sub', store=True)

    final_mockup_file = fields.Binary('Final Mockup File')
    customer_logo = fields.Binary('Customer Logo')
    finalisation_file = fields.Binary('Finalisation File')
    mockup_id = fields.Many2one('mockup.request', 'Mockup')

    @api.depends('personalization_applicable', 'fully_customized_product', 'customized_product', 'psc_product')
    def _compute_hak_type_sub(self):
        print("_compute_hak_type_sub")
        for line in self:
            product_template_ids = []
            line_sudo = line.sudo()
            hak_type_sub = False
            if line_sudo.personalization_applicable:
                hak_type_sub = 'personalization_applicable'
            elif line_sudo.fully_customized_product:
                hak_type_sub = 'fully_customized_product'
            elif line_sudo.customized_product:
                hak_type_sub = 'customized_product'
            elif line_sudo.psc_product:
                hak_type_sub = 'psc'
            line.hak_type_sub = hak_type_sub

    def check_json(self):
        print("dshfdskjhfkjdsnhcheck_jsonf", self.personalisation_details)

        descrip = 'printing side:-'

        for rec in self.personalisation_details['printing_details']:
            print("dsfkjhjdskf", rec)

            if rec.get('print_type_checked'):
                print("dsfkjhjdsk4444444f", rec)

                type = self.env['printing.type'].search([('id', '=', int(rec.get('print_type_checked')))])

                if type.max_color_label == '0':
                    descrip += str(rec.get('print_attr_name') + ':') + str(type.name) + '- Full Color,'


                else:

                    descrip += str(rec.get('print_attr_name') + ':-') + str(type.name) + '- Max Color' + str(
                        type.max_color_label) + ','

        print("sdjlskj", descrip)

    def write(self, vals):
        """ Sanitize bounce_alias / catchall_alias """
        res = super().write(vals)
        return res

        # if self.categ_id.personalization_applicable or self.categ_id.customized_product or self.categ_id.fully_customized_product:
        #     if not self.printing_side_line_ids:
        #         raise UserError('Please add the printing sides')
        #     else:
        #         return res
        # else:
        #     return res

    @api.onchange('categ_id')
    def _onchange_hak_product_categ_id(self):
        for rec in self:
            if rec.categ_id:
                rec.hak_margin = rec.categ_id.hak_margin

            else:
                rec.hak_margin = 0


class Product(models.Model):
    _inherit = 'product.product'

    @api.model
    def _build_attributes_domain(self, product_template, product_attributes):
        domain = []
        cont = 0
        attributes_ids = []
        if product_template:
            for attr_line in product_attributes:
                if isinstance(attr_line, dict):
                    attributes_ids.append(attr_line.get("attribute_id"))
                else:
                    attributes_ids.append(attr_line.attribute_id.id)
            domain.append(("product_tmpl_id", "=", product_template.id))
            for attr_line in product_attributes:
                if isinstance(attr_line, dict):
                    value_id = attr_line.get("value_id")
                else:
                    value_id = attr_line.value_id.id
                if value_id:
                    ptav = self.env["product.template.attribute.value"].search(
                        [
                            ("product_tmpl_id", "=", product_template.id),
                            ("attribute_id", "in", attributes_ids),
                            ("product_attribute_value_id", "=", value_id),
                        ]
                    )
                    if ptav:
                        domain.append(
                            ("product_template_attribute_value_ids", "=", ptav.id)
                        )
                        cont += 1
        return domain, cont

    @api.model
    def _product_find(self, product_template, product_attributes):
        if product_template:
            domain, cont = self._build_attributes_domain(
                product_template, product_attributes
            )
            products = self.search(domain)
            # Filter the product with the exact number of attributes values
            for product in products:
                if len(product.product_template_attribute_value_ids) == cont:
                    return product
        return False


class PrintingSideLine(models.Model):
    _name = 'printing.side.line'
    _description = 'Printing Side Line'

    name = fields.Char(string="Side Name", required=1)
    product_temp_id = fields.Many2one("product.template", 'Product Template', required=1)
    side_code = fields.Char(string="Side Code")
    image_group = fields.Char(string="Image Group")
    max_width = fields.Float(string="Max Width (mm)", required=1)
    max_height = fields.Float(string="Max Height (mm)", required=1)
    limit_variants = fields.Boolean(string="Limit Variants")
    attribute_value_ids = fields.Many2many('product.attribute.value', string='Values')
    product_image_line_ids = fields.One2many('product.image.line', 'side_line_id', string='Values')
    printing_type_ids = fields.Many2many('printing.type', string="Printing Types", required=1)

    sc = fields.Float('Mulitplier(SC)', default=1)
    pc = fields.Float('Mulitplier(PC)', default=1)
    image_1920 = fields.Image("Variant Image", max_width=1920, max_height=1920)

    printing_side_type_id = fields.Many2one('printing.side.type', string="Printing Side Types")
    cust_attribute_value_domain = fields.Many2many('product.attribute.value', 'name', 'id',
                                                   compute="_compute_cust_attribute_value_domain",

                                                   )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('review', 'Under Review'),
            ('approved', 'Approved'),
            ('cancel', 'Cancelled'),
        ], string='Status', tracking=True, default='draft')

    @api.constrains('max_width', 'max_height')
    def _check_max_height(self):
        for record in self:
            if record.max_width <= 0 or record.max_height <= 0:
                raise UserError(_('Max width and max height should be greater than zero.'))

    @api.model_create_multi
    def create(self, vals_list):
        # for vals in vals_list:
        #     sequence = self.env["ir.sequence"].next_by_code("printing.line.seq")
        #     vals["side_code"] = side_code
        res = super().create(vals_list)
        sequence = self.env["ir.sequence"].next_by_code("printing.line.seq")
        if res.product_temp_id.family_code:
            res.side_code = res.product_temp_id.categ_id.prefix + str(res.product_temp_id.family_code) + sequence
        else:
            if res.product_temp_id.default_code:
                res.side_code = res.product_temp_id.default_code + sequence
            elif res.product_temp_id.categ_id.prefix:
                res.side_code = res.product_temp_id.categ_id.prefix + sequence
            else:
                res.side_code = sequence
        if not res.product_temp_id.categ_id.prefix:
            raise UserError('Category Prefix Missing')
        return res

    def create_record(self):
        for rec in self:
            if rec.product_temp_id:
                products = self.env['product.product'].search([('product_tmpl_id', '=', rec.product_temp_id.id)])
                if len(products) > 1:
                    if rec.limit_variants:
                        product_template_attribute_value_ids = self.env['product.template.attribute.value'].search(
                            [('product_attribute_value_id', 'in', rec.attribute_value_ids.ids)])
                        d_pdts = []
                        for pdt in products:
                            for value in pdt.product_template_attribute_value_ids:
                                if value.id in product_template_attribute_value_ids.ids:
                                    d_pdts.append(pdt.id)
                        products = self.env['product.product'].browse(d_pdts)
                    if products:
                        for product in products:
                            code = rec.side_code + "_" + product.default_code
                            print(
                                "code", code
                            )
                            product_side_code = self.env['product.image.line'].search_count(
                                [('product_side_code', '=', code)])
                            print("product_side_code", product_side_code)
                            line = False
                            if not product_side_code:
                                line = self.env['product.image.line'].create({
                                    'side_line_id': rec.id,
                                    'product_id': product.id,
                                })
                            if line:
                                line._compute_product_side_code()

    @api.depends('product_temp_id')
    def _compute_cust_attribute_value_domain(self):
        print("_compute_cust_attribute_value_domain")
        for rec in self:
            if not rec.product_temp_id:
                rec.cust_attribute_value_domain = [Command.set([])]
            else:
                if self.product_temp_id:
                    dom = []
                    for rec_line in self.product_temp_id.attribute_line_ids:
                        for item in rec_line.value_ids:
                            dom.append(item._origin.id)
                    rec.cust_attribute_value_domain = [Command.set(dom)]

    def action_request_for_approval(self):
        for rec in self:
            rec.state = "review"

    def action_approve_side_line(self):
        for rec in self:
            rec.state = "approved"

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = "draft"

    def action_cancel_side_line(self):
        for rec in self:
            rec.state = "cancel"


class ProductImageLine(models.Model):
    _name = 'product.image.line'
    _description = 'Product Image Line'

    side_line_id = fields.Many2one("printing.side.line", 'Side Line')
    product_temp_id = fields.Many2one("product.template", 'Product Template', related='side_line_id.product_temp_id',
                                      store=True)
    product_id = fields.Many2one("product.product", 'Product', required=1)
    image = fields.Image("Image")
    product_side_code = fields.Char(string='Code', compute="_compute_product_side_code", copy=False, store=True)
    product_ids = fields.Many2many('product.product', string='Products', compute='_compute_products_domain')

    @api.constrains('product_side_code')
    def _check_unique_product_side_code(self):
        for record in self:
            product_side_code = self.env['product.image.line'].search_count(
                [('product_side_code', '=', record.product_side_code)])
            if product_side_code > 1:
                raise UserError("There is already a record with the same code.")

    @api.depends('product_id', 'side_line_id')
    def _compute_product_side_code(self):
        for rec in self:
            if rec.product_id:
                rec.product_side_code = rec.side_line_id.side_code + "_" + rec.product_id.default_code

    @api.depends('side_line_id', 'side_line_id.limit_variants', 'side_line_id.attribute_value_ids')
    def _compute_products_domain(self):
        for rec in self:
            products = self.env['product.product'].search([('product_tmpl_id', '=', rec.product_temp_id.id)])
            print("products 111111111", products)
            print("rec.side_line_id.limit_variants", rec.side_line_id.limit_variants)
            if rec.side_line_id.limit_variants:
                print("side_line_id.attribute_value_ids", rec.side_line_id.attribute_value_ids)
                product_template_attribute_value_ids = self.env['product.template.attribute.value'].search(
                    [('product_attribute_value_id', 'in', rec.side_line_id.attribute_value_ids.ids)])
                print("product_template_attribute_value_ids", product_template_attribute_value_ids)
                d_pdts = []
                for pdt in products:
                    print("pdt.product_template_attribute_value_ids", pdt.product_template_attribute_value_ids)
                    for value in pdt.product_template_attribute_value_ids:
                        if value.id in product_template_attribute_value_ids.ids:
                            d_pdts.append(pdt.id)
                            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("d_pdts", d_pdts)
                rec.product_ids = [Command.set(d_pdts)]
            else:
                rec.product_ids = [Command.set(products.ids)]


class SelectedPrintingSideLine(models.Model):
    _name = 'selected.printing.side.line'
    _description = 'Selected Printing Side Line'

    name = fields.Char(string=" Name")
    product_temp_id = fields.Many2one("product.template", 'Product Template')
    parent_product_id = fields.Many2one("product.product", 'Parent Product')
    side_code = fields.Char(string="Side Code")
    printing_side_line_id = fields.Many2one('printing.side.line', string="Side Name")
    selected_width = fields.Float(string="Width (mm)")
    selected_height = fields.Float(string="Height (mm)")
    quantity = fields.Float(string="Quantity")
    attachment = fields.Binary('Attachment')
    printing_side_type_id = fields.Many2one('printing.type', string="Printing Types")
    selected_color = fields.Float('Color')
    printing_category_id = fields.Many2one('printing.category', string="Printing Category", store=True,
                                           compute='_compute_printing_category_id')
    side_type_id = fields.Many2one('printing.side.type', string="Side Type", store=True,
                                   compute='_compute_side_type_id')
    sc = fields.Float('SC', store=True, compute='_compute_sc_and_pc')
    pc = fields.Float('PC', store=True, compute='_compute_sc_and_pc')

    @api.depends('parent_product_id')
    def _compute_printing_category_id(self):
        for rec in self:
            if rec.parent_product_id.categ_id and rec.parent_product_id.categ_id.printing_category_id:
                rec.printing_category_id = rec.parent_product_id.categ_id.printing_category_id.id
            else:
                rec.printing_category_id = False

    @api.depends('printing_side_line_id')
    def _compute_side_type_id(self):
        for rec in self:
            if rec.printing_side_line_id:
                rec.side_type_id = rec.printing_side_line_id.printing_side_type_id.id
            else:
                rec.side_type_id = False

    @api.depends('side_type_id', 'printing_category_id', 'parent_product_id', 'selected_color', 'printing_side_type_id')
    def _compute_sc_and_pc(self):
        for rec in self:
            details = False
            if rec.side_type_id and rec.printing_category_id and rec.printing_side_type_id:
                for line in rec.printing_side_type_id.printing_details_ids:
                    if line.printing_side_type_id.id == rec.side_type_id.id and line.printing_category_id.id == rec.printing_category_id.id and line.color == rec.selected_color:
                        # details = self.env['printing.details'].search(
                        #     [('printing_type_id', '=', rec.printing_side_type_id.id),
                        #      ('printing_side_type_id', '=', rec.side_type_id.id),
                        #      ('printing_category_id', '=', rec.printing_category_id.id),
                        #      ('color', '=', rec.selected_color)
                        #      ])
                        details = line
            if details:
                rec.sc = details.sc
                rec.pc = details.pc
            else:
                rec.sc = 0
                rec.pc = 0
