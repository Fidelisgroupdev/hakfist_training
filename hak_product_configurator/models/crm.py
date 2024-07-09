from odoo import fields, Command, models, api, _
from datetime import date
from odoo.exceptions import UserError


class CRM(models.Model):
    _inherit = 'crm.lead'
    _rec_name = 'crm_sequence'

    product_line_ids = fields.One2many('crm.product.line', 'crm_id', string="Product Lines")
    partner_logo = fields.Many2one('partner.logo')

    partner_mock_ids = fields.Many2many('mockup.request', compute='_compute_partner_mock_count',
                                        string="Partner Mockup Request")

    partner_mock_count = fields.Integer('Number of other Mockup req from the same partner',
                                        compute='_compute_partner_mock_count')

    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        compute='_compute_pricelist_id',
        store=True, readonly=False, precompute=True, check_company=True,  # Unrequired company
        tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.")

    date_order = fields.Datetime('Order Date', default=lambda self: fields.Datetime.now())

    sequence = fields.Char('Sequence', readonly=1)
    crm_sequence = fields.Char('Sequence')
    show_update_quotation = fields.Boolean(compute='_compute_show_update_quotation',
                                           string="Show Update Quotation")

    partner_invoice_id = fields.Many2one(
        comodel_name='res.partner',
        string="Invoice Address",
        compute='_compute_partner_invoice_id',
        store=True, readonly=False, required=True, precompute=True,
    )
    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string="Delivery Address",
        compute='_compute_partner_shipping_id',
        store=True, readonly=False, required=True, precompute=True,
    )
    contact_person_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact Person',
    )

    @api.depends('partner_id')
    def _compute_partner_invoice_id(self):
        for order in self:
            order.partner_invoice_id = order.partner_id.address_get(['invoice'])[
                'invoice'] if order.partner_id else False

    @api.depends('partner_id')
    def _compute_partner_shipping_id(self):
        for order in self:
            order.partner_shipping_id = order.partner_id.address_get(['delivery'])[
                'delivery'] if order.partner_id else False

    @api.depends('order_ids.state', 'order_ids.currency_id', 'order_ids.amount_untaxed', 'order_ids.date_order',
                 'order_ids.company_id')
    def _compute_show_update_quotation(self):
        for lead in self:
            do_not_show_update_quotation = True
            quotation_count = len(lead.order_ids.filtered_domain(
                [('state', '!=', 'cancel'), ('is_sample_order', '=', False)]))
            quotations = lead.order_ids.filtered_domain(
                [('is_sample_order', '=', False)])
            if quotations:
                if quotation_count > 0:
                    do_not_show_update_quotation = True
                else:
                    do_not_show_update_quotation = False
            else:
                do_not_show_update_quotation = True
            lead.show_update_quotation = do_not_show_update_quotation

    @api.model_create_multi
    def create(self, vals_list):
        print("create 2222222222222222222", vals_list)
        for vals in vals_list:
            tick_sequence = self.env["ir.sequence"].next_by_code('crm.seq')
            print("tick_sequence", tick_sequence)
            vals['crm_sequence'] = tick_sequence
            # if vals.get('partner_id'):
            #     partner_id = self.env['res.partner'].browse(vals.get('partner_id', False))
            #     print("partner_id", partner_id)
            #     print("partner_id.company_id.id", partner_id.company_id.id)
            # if partner_id:
            #     vals['company_id'] = partner_id.company_id.id
        tick = super().create(vals_list)
        print("tick", tick)
        # tick.crm_sequence = tick_sequence
        return tick

    # currency_id = fields.Many2one(
    #     comodel_name='res.currency',
    #     compute='_compute_currency_id',
    #     store=True,
    #     precompute=True,
    #     ondelete='restrict'
    # )
    #
    # company_id = fields.Many2one(
    #     comodel_name='res.company',
    #     required=True, index=True,
    #     default=lambda self: self.env.company)

    # @api.depends('pricelist_id', 'company_id')
    # def _compute_currency_id(self):
    #     for order in self:
    #         order.currency_id = order.pricelist_id.currency_id or order.company_id.currency_id

    @api.depends('partner_id', 'company_id')
    def _compute_pricelist_id(self):
        for order in self:
            # if order.state != 'draft':
            #     continue
            if not order.partner_id:
                order.pricelist_id = False
                continue
            order = order.with_company(order.company_id)
            order.pricelist_id = order.partner_id.property_product_pricelist

    # c = fields.Integer('Number of other open mock from the same partner',
    #                                            compute='_compute_partner_mock_count')

    def _compute_partner_mock_count(self):
        for ticket in self:
            partner_ticket = self.env['mockup.request'].sudo().search(
                [('crm_id', '=', ticket.id)])
            ticket.partner_mock_ids = partner_ticket
            ticket.partner_mock_count = len(partner_ticket) if partner_ticket else 0
            # open_ticket = partner_ticket.filtered(lambda ticket: not ticket.stage_id.fold)
            # ticket.partner_open_mock_count = len(open_ticket) if open_ticket else 0

    def action_open_mock_ticket(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("hak_product_configurator.action_mock_request")
        action.update({
            'domain': [('crm_id', '=', self.id)],
            'context': {'create': False},
        })
        return action

    def action_create_request(self):

        if not self.partner_logo:
            raise UserError('Please add LOGO!')
        current = self.env['ir.model'].sudo().search([('model', '=', self._name)])

        team = self.env['helpdesk.team'].search([('name', '=', 'Mockup Team'), ('applicability_ids', 'in', current.id)])
        context = {
            'default_crm_id': self.id,
            'default_created_from': current.id,
            'default_team_id': team.id,
        }

        line_products = self.product_line_ids.filtered(
            lambda x: x.hak_type in ['std_with_p', 'psc', 'fully_cus_with', 'cust_with_p'])
        if not line_products:
            raise UserError(_("There is no lines to create mockup request"))

        return {
            'name': _('Mockup Request'),
            'res_model': 'mock.wizard',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'view_mode': 'form',
            'target': 'new',
            'context': context,
        }

    def add_partner_logo(self):
        print("$$$$$$$$$$$$$$")
        if self.partner_id:
            return {
                'name': _('Add Logo'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_model': 'partner.logo',
                'target': 'new',
                'context': {'default_partner_id': self.partner_id.id, 'default_crm_id': self.id},
            }
        else:
            raise UserError('Please add the customer')

    # @api.onchange('partner_logo')
    # def onchange_partner_logo(self):
    #     print("###########")
    #     print("self", self)
    #     print("self.partner_id", self._origin.partner_id)
    #     if not self.partner_id:
    #         raise UserError('Please add the customer')

    def open_product_configurator(self):
        return {
            'name': _('Product Configurator'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'product.configurator.wizard',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': self.env.context,
        }

    def action_sale_revise(self):
        print("sldka")
        sale = self.env['sale.order'].search(
            [('state', 'in', ('draft', 'sent', 'review', 'approve')), ('opportunity_id', '=', self.id)])
        if len(sale) > 1:
            raise UserError('Multiple Qoute Found')
        else:
            sample_orders = self.env['sale.order'].search(
                [('opportunity_id', '=', self.id), ('is_sample_order', '=', True)])
            if sample_orders:
                for sample in sample_orders:
                    if sample.state in ['sale', 'done']:
                        raise UserError(
                            _('You are not allowed to revise this enquiry, since there is a sample order in Confirmed State'))
                    else:
                        sale.action_cancel()
                        self.write({
                            'sample_order_created': False,
                            'sample_order_id': False,
                        })

            vals = []
            for rec in self.product_line_ids:
                order_line_obj = {
                    'product_template_id': rec.product_template_id.id,

                    # 'product_uom': rec.,

                    'price_unit': rec.net_unit_price,
                    'product_id': rec.product_id.id,
                    'product_uom_qty': rec.product_uom_qty,
                }
                vals.append((0, 0, order_line_obj))

            print("sadasdaasad", sale, sale.state)

            # if sale.state == 'sent':
            #     print("dfkmsd")
            #     revised = sale.revise_quotation()
            #     new_sale = self.env['sale.order'].search([('id', '=', int(revised.get('res_id')))])
            #     new_sale.order_line = False
            #     new_sale.write({'order_line': vals})
            #     print("skaldksalkda", revised)
            #     return revised
            #
            # else:
            if sale.state not in ['sale', 'done', 'cancel']:
                # sale.order_line = False
                # sale.write({'state': 'cancel'})
                sale.action_cancel()

                return_vals = {'type': 'ir.actions.act_window',
                               'view_mode': 'form',
                               'res_model': 'sale.order',
                               'views': [(False, 'form')],
                               'res_id': sale.id}
                return return_vals

    def action_update_quotation(self):
        print("action_update_quotation")
        vals = []
        create_sample_order = False
        for rec in self.product_line_ids:
            if rec.sample_qty > 0:
                create_sample_order = True
        if create_sample_order:
            if not self.sample_order_created or self.sample_order_id.state not in ['sale', 'done']:
                raise UserError(
                    _('You are allowed to create quotation without creating and validating the sample order.'))

        print("self._context", self._context)
        from_wizard = self._context.get('from_wizard')
        delivery_date = self._context.get('delivery_date')
        warehouse_id = self._context.get('warehouse_id')

        if not from_wizard:
            return {
                'name': _("Set Delivery Details"),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_id': self.env.ref('hak_sample_order.set_delivery_details_form_view').id,
                'res_model': 'set.delivery.details',
                'context': {
                    'default_crm_id': self.id if self else False,
                    'default_order_type': 'normal',
                },
                'target': 'new',
            }

        for rec in self.product_line_ids:
            order_line_obj = {
                'product_template_id': rec.product_template_id.id,

                # 'product_uom': rec.,

                'price_unit': rec.net_unit_price,
                'product_id': rec.product_id.id,
                'product_uom_qty': rec.product_uom_qty,
            }
            vals.append((0, 0, order_line_obj))
        # revised = sale.revise_quotation()
        quotations = self.env['sale.order'].search(
            [('state', '=', 'cancel'), ('opportunity_id', '=', self.id), ('is_sample_order', '=', False)],
            order="id desc", limit=1)
        print("quotations", quotations)
        revised = quotations.revise_quotation()
        new_sale = self.env['sale.order'].search([('id', '=', int(revised.get('res_id')))])
        new_sale.order_line = False
        new_sale.write({
            'order_line': vals,
            'commitment_date': delivery_date if delivery_date else False,
        })
        print("skaldksalkda", revised)
        return revised

    def _get_lead_quotation_domain(self):
        return [('state', 'in', ('draft', 'sent', 'review', 'approve'))]

    def _get_lead_sale_order_domain(self):
        return [('state', 'not in', ('draft', 'sent', 'cancel', 'review', 'approve'))]

    def write(self, vals):
        print("write ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,sadsankhjhbhjlkdsa", vals)
        result = super(CRM, self).write(vals)
        for rec in self.product_line_ids:
            rec.onchange_product_template_id_description()
        return result

    def action_sale_quotations_lines(self):
        print("klmjkclvxsssssss")

        vals = []

        for rec in self.product_line_ids:
            order_line_obj = {
                'product_template_id': rec.product_template_id.id,

                # 'product_uom': rec.,

                'price_unit': rec.net_unit_price,
                'product_id': rec.product_id.id,
                'product_uom_qty': rec.product_uom_qty,
                'company_id': self.company_id.id,
            }
            vals.append((0, 0, order_line_obj))
        if not self.partner_id:
            return self.env["ir.actions.actions"]._for_xml_id("sale_crm.crm_quotation_partner_action")
        else:
            sale_lines = self.action_new_quotation()
            print("sdkjsad", sale_lines)
            if sale_lines.get('context'):
                sale_lines.get('context')['default_order_line'] = vals
                # sale_lines.get('context')['default_company_id'] = self.company_id.id
            sale = self.env['sale.order'].with_context(sale_lines.get('context')).create({})
            print("sakjdjashdjasd", sale_lines)

            return {
                'name': _("Quotation"),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                # 'view_id': self.env.ref('account_batch_payment.view_batch_payment_form').id,
                'res_model': 'sale.order',
                'res_id': sale.id,
                # 'context': {
                #     'create': False,
                #     'delete': False,
                # },
                'target': 'current',
            }
            # return sale_lines

    # def action_sale_quotations_new(self):
    #     # res = super(CRM, self).action_sale_quotations_new()
    #     # res = super(CRM, self).action_sale_quotations_new()
    #     print("uuuuuuuuaaaaawww",)
    #
    #     # return res
    #     # if not self.partner_id:
    #     #     return self.env["ir.actions.actions"]._for_xml_id("sale_crm.crm_quotation_partner_action")
    #     # else:
    #     #     return self.action_new_quotation()


class Ticket(models.Model):
    _inherit = "helpdesk.ticket"

    psc_line_id = fields.Many2one('crm.product.line')
    psc_product_tmpl_id = fields.Many2one('product.template', string='PSC Product')


class CustomVariant(models.Model):
    _inherit = "product.attribute.custom.value"

    crm_line_id = fields.Many2one('crm.product.line', string="CRM")


class CrmProductLine(models.Model):
    _name = 'crm.product.line'
    _description = 'CRM Product Line'
    _inherit = "mail.thread", "mail.activity.mixin"
    _rec_name = 'product_template_id'

    crm_id = fields.Many2one("crm.lead", 'CRM')
    # product_id = fields.Many2one("product.product", 'Product')
    # product_template_id = fields.Many2one("product.template", 'Product')
    pdt_default_code = fields.Char("Internal Ref")
    product_uom_qty = fields.Float(string="Qty")
    base_unit_price = fields.Float(string="Base Unit Price")
    personalized_unit_price = fields.Float(string="Personalized Unit Price")
    net_unit_price = fields.Float(string="Net Unit Price", compute='_update_sub_fields_values')
    total_base_price = fields.Float(string="Total Base Price", compute='_update_sub_fields_values')
    total_personalized_price = fields.Float(string="Total Personalized Price", compute='_update_sub_fields_values')
    net_total_price = fields.Float(string="Net Total Price", compute='_update_sub_fields_values')

    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        change_default=True, ondelete='restrict', index='btree_not_null',
        domain="[('sale_ok', '=', True)]")
    product_template_id = fields.Many2one(
        string="Product Template",
        comodel_name='product.template',
        compute='_compute_product_template_id',
        readonly=False,
        search='_search_product_template_id',
        # previously related='product_id.product_tmpl_id'
        # not anymore since the field must be considered editable for product configurator logic
        # without modifying the related product_id when updated.
        domain=[('sale_ok', '=', True)])

    description_details = fields.Char('Description')

    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string="Unit of Measure",
        compute='_compute_product_uom',
        store=True, readonly=False, precompute=True, ondelete='restrict',
        domain="[('category_id', '=', product_uom_category_id)]")

    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', depends=['product_id'])

    # is_configurable_product = fields.Boolean(
    #     string="Is the product configurable?",
    #     related='product_template_id.has_configurable_attributes',
    #     depends=['product_id'])

    is_configurable_product = fields.Boolean(
        string="Is the product configurable?", compute='_compute_is_configurable_product')

    product_template_attribute_value_ids = fields.Many2many(
        related='product_template_id.hak_master_product_id.product_template_attribute_value_ids',
        depends=['product_id'])
    product_no_variant_attribute_value_ids = fields.Many2many(
        comodel_name='product.template.attribute.value',
        string="Extra Values",
        compute='_compute_no_variant_attribute_values',
        store=True, readonly=False, precompute=True, ondelete='restrict')

    product_custom_attribute_value_ids = fields.One2many(
        comodel_name='product.attribute.custom.value', inverse_name='crm_line_id',
        string="Custom Values",
        compute='_compute_custom_attribute_values',
        store=True, readonly=False, precompute=True, copy=True)

    currency_id = fields.Many2one(
        related='crm_id.company_currency',
        depends=['crm_id.company_currency'],
        store=True, precompute=True)

    # hak_type = fields.Selection(
    #     [('std_with_p', 'Standard product with personalization'),
    #      ('std', 'Standard products only'),
    #      ('psc', 'PSC'),
    #      ('fully_cus', 'Customized'),
    #      ('fully_cus_with', 'Customized with personalization'),
    #      ('cust', 'Ready made'),
    #      ('cust_with_p', 'Ready made with personalization'),
    #      ('out', 'Standard product with outsourcing')
    #
    #      ], string='Type', default='std_with_p')

    hak_type = fields.Selection(
        [('std_with_p', 'HAK items w/p'),
         ('std', 'HAK Items only'),
         ('psc', 'PSC'),
         ('fully_cus', 'Customized'),
         ('fully_cus_with', 'Customized w/p'),
         ('cust', 'Ready made'),
         ('cust_with_p', 'Ready made w/p')
         ], string='Type', default='std_with_p')

    state = fields.Selection(
        [('in_crm', 'In CRM'),
         ('quotation_created', 'Quotation Created'),
         ('quotation_sent', 'Quotation Sent'),
         ('order_confirmed_and_waiting', 'Order Confirmed Waiting For Payment'),
         ('order_confirmed', 'Order Confirmed'),
         ('ready_for_delivery', 'Items Picked Ready For Delivery'),
         ('delivered', 'Delivered'),
         ('on_hold', 'On Hold')
         ], string='Status', default='in_crm')

    hak_type_sub = fields.Selection(
        [('personalization_applicable', 'HAK items'),
         ('customized_product', 'Ready made'),
         ('psc', 'PSC'),
         ('fully_customized_product', 'Customized'),
         ], string='Type Sub', compute='_compute_hak_type_sub', )

    hak_type_visible = fields.Boolean(default=False)
    product_template_domain_ids = fields.Many2many('product.template', string='Products Domain')
    product_not_availability = fields.Boolean(compute='_compute_product_not_availability',
                                              store=True, string="Availability")

    sc = fields.Float('SC', store=True, compute='_compute_sc_and_pc')
    pc = fields.Float('PC', store=True, compute='_compute_sc_and_pc')

    @api.depends('product_template_id', 'product_template_id.selected_ids')
    def _compute_sc_and_pc(self):
        for rec in self:
            sc = 0.0
            pc = 0.0
            if rec.product_template_id and rec.product_template_id.selected_ids:
                for line in rec.product_template_id.selected_ids:
                    sc = sc + line.sc
                    pc = pc + line.pc
            rec.sc = sc
            rec.pc = pc

    @api.depends('hak_type')
    def _compute_hak_type_sub(self):
        print("_compute_hak_type_sub")
        for line in self:
            product_template_ids = []
            line_sudo = line.sudo()
            hak_type_sub = False
            if line_sudo.hak_type in ['std_with_p', 'std']:
                hak_type_sub = 'personalization_applicable'
            elif line_sudo.hak_type in ['fully_cus', 'fully_cus_with']:
                hak_type_sub = 'fully_customized_product'
            elif line_sudo.hak_type in ['cust', 'cust_with_p']:
                hak_type_sub = 'customized_product'
            else:
                hak_type_sub = 'psc'
            line.hak_type_sub = hak_type_sub

    # @api.depends('hak_type')
    # def _compute_domain_product_template_id(self):
    #     print("_compute_domain_product_template_id")
    #     for line in self:
    #         product_template_ids = []
    #         line_sudo = line.sudo()
    #         products = False
    #         if line_sudo.hak_type in ['std_with_p', 'std']:
    #             products = self.env['product.template'].search([('personalization_applicable', '=', True)])
    #         elif line_sudo.hak_type in ['fully_cus', 'fully_cus_with']:
    #             products = self.env['product.template'].search([('fully_customized_product', '=', True)])
    #         elif line_sudo.hak_type in ['cust', 'cust_with_p']:
    #             products = self.env['product.template'].search([('customized_product', '=', True)])
    #         else:
    #             products = False
    #         # print("products", len(products), products)
    #         if products:
    #             product_template_ids = products.ids
    #         print("product_template_ids", product_template_ids)
    #         line.product_template_domain_ids = [Command.set(product_template_ids)]

    @api.onchange('product_template_id')
    def onchange_product_template_id_description(self):
        print("dfsf")
        if self.product_template_id:
            print("onchange_product_template_id_description")
            # ff
            if self.product_template_id.hak_master_product_id:
                json_det = self.product_template_id.personalisation_details.get('printing_details')
                print("dlijfdsijfjson_det", json_det)
                variant_color = False
                if json_det:
                    print("self.product_template_id.hak_master_product_id",
                          self.product_template_id.hak_master_product_id)
                    print("self.product_template_id.hak_master_product_id.product_template_variant_value_ids",
                          self.product_template_id.hak_master_product_id.product_template_variant_value_ids)
                    for variant in self.product_template_id.hak_master_product_id.product_template_variant_value_ids:
                        if variant.attribute_id and variant.attribute_id.display_type == 'color':
                            print("variant.product_attribute_value_id.display_name:",
                                  variant.product_attribute_value_id.display_name)
                            variant_color = variant.product_attribute_value_id.display_name
                    if variant_color:
                        descrip = str(self.product_template_id.name) + ', ' + variant_color + ', ' + 'printing side:-'
                    else:
                        descrip = str(self.product_template_id.name) + 'printing side:-'
                    for rec in json_det:
                        print("dsfkjhjdskf", rec)

                        if rec.get('print_type_checked') and rec.get('print_type_checked'):
                            print("dsfkjhjdsk4444444f", rec)

                            type = self.sudo().env['printing.type'].search(
                                [('id', '=', int(rec.get('print_type_checked')))])

                            if type.max_color_label == '0':
                                descrip += str(rec.get('print_attr_name') + ':') + str(type.name) + '- Full Color,'


                            else:

                                descrip += str(rec.get('print_attr_name') + ':-') + str(
                                    type.name) + '- Max Color' + str(
                                    type.max_color_label) + ','

                    print("lidjfkd descrip", descrip)
                    self.sudo().description_details = descrip
                    # self.product_template_id.specs = descrip

                else:
                    self.sudo().description_details = self.product_template_id.name
                    # self.product_template_id.specs = self.product_template_id.name
            else:
                self.sudo().description_details = self.product_template_id.name
                # self.product_template_id.specs = self.product_template_id.name

            # mockup = self.env['mockup.request'].sudo().search(
            #     [('crm_line_id', '=', self.id), ('stage_id.name', 'not in', ['Close','Cancelled'])], limit=1)
            # print("mockups ############", mockup)
            #
            # # n = 0
            # if mockup:
            #     cancel_stage = self.env['helpdesk.stage'].sudo().search([('name', '=', 'Cancelled')])
            #     print("cancel_stage", cancel_stage)
            #
            #     # for mockup in mockups:
            #     print("mockup.name", mockup.name)
            #     # if n < 1:
            #     if mockup.stage_id.name != 'Cancelled':
            #         # new_mockup = mockup.copy()
            #         if cancel_stage:
            #             mockup.sudo().write({
            #                 'stage_id': cancel_stage.id
            #             })
            #         new_mockup = self.env['mockup.request'].sudo().create({
            #             'description': mockup.description,
            #             'team_id': mockup.team_id.id,
            #             'priority': mockup.priority,
            #             'ref': mockup.ref,
            #             'name': mockup.ref,
            #             'partner_id': mockup.partner_id.id,
            #             'created_from': mockup.created_from.id,
            #             'crm_id': mockup.crm_id.id,
            #             'crm_line_id': mockup.crm_line_id.id,
            #             'product_cust_id': mockup.product_cust_id.id,
            #         })
            #         if new_mockup:
            #             n = 1
            #         print("new_mockup 11111111", new_mockup)
            #         mockup.sudo().rev_mockup_id = new_mockup.id
            #         # new_mockup.rev_mockup_ids = new_mockup.rev_mockup_ids.ids + mockup.rev_mockup_ids.ids
            #         new_mockup.sudo().action_fetch_details()
            #         new_mockup.sudo().rev_mockup_ids = mockup.ids
            # fff
        else:
            self.sudo().description_details = False
            # self.product_template_id.specs = False

    @api.onchange('hak_type')
    def onchange_hak_type_psc(self):
        for rec in self:
            rec.product_template_id = False
            rec.product_id = False
            rec.description_details = False
            rec.product_uom_qty = False
            rec.base_unit_price = False
            if rec.hak_type == 'psc':
                rec.hak_type_visible = True
            else:
                rec.hak_type_visible = False

    def view_psc_ticket(self):
        print("dfs")
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("hak_product_configurator.action_mock_request")
        action.update({
            'domain': ['|', ('psc_line_id', '=', self.id), ('crm_line_id', '=', self.id)],
            'context': {'create': False},
        })
        return action

    def view_product_line(self):
        print("view_product_line")
        # self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("hak_product_configurator.action_crm_product_line")
        print("action", action)
        # ff
        action.update({
            # 'domain': ['|', ('psc_line_id', '=', self.id), ('crm_line_id', '=', self.id),
            #            ('stage_id.name', '!=', 'Cancelled')],
            'context': {'create': False},
            'res_id': self.id,
        })
        return action

    def create_psc_ticket(self):
        print("dcd")
        context = {
            'default_crm_id': self.crm_id.id,
            'default_psc_line_id': self.id,
            'default_psc_product_tmpl_id': self.product_template_id.id,
            # 'default_created_from': current.id,
            # 'default_customer': self.env.user.id,
        }

        if self.hak_type == 'psc':
            return {
                'name': _('Tickets'),
                'res_model': 'helpdesk.ticket',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'view_mode': 'form',
                'target': 'new',
                'context': context,
            }

    # @api.model
    # def create(self, vals):
    #     # record = super(MockRequest, self).create(vals)
    #     record = super().create(vals)
    #     if record.hak_type == 'psc':
    #         product_lines = self.env['crm.product.line'].sudo().search(
    #             [('crm_id', '=', record.crm_id.id), ('hak_type', '!=', 'psc')])
    #         if product_lines:
    #             raise UserError(_('You are not allowed to add PSC type with Others'))
    #     else:
    #         product_lines = self.env['crm.product.line'].sudo().search(
    #             [('crm_id', '=', record.crm_id.id), ('hak_type', '=', 'psc')])
    #         if product_lines:
    #             raise UserError(_('You are not allowed to add PSC type with other types'))
    #     return record

    def write(self, vals):
        result = super(CrmProductLine, self).write(vals)
        return result

    def action_add_psc(self):
        if self.hak_type == 'psc':
            print("sdkjhs", self)
            current = self.env['ir.model'].sudo().search([('model', '=', 'crm.lead')])

            context = {
                'default_crm_id': self.crm_id.id,
                'default_crm_product_line_id': self.id,
                # 'default_created_from': current.id,
                # 'default_customer': self.env.user.id,
            }

            return {
                'name': _('PSC'),
                'res_model': 'type.hak.psc',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'view_mode': 'form',
                'target': 'new',
                'context': context,
            }

    @api.depends('product_id')
    def _compute_product_uom(self):
        for line in self:
            if not line.product_uom or (line.product_id.uom_id.id != line.product_uom.id):
                line.product_uom = line.product_id.uom_id

    @api.depends('product_id', 'product_template_id', 'product_uom_qty')
    def _compute_product_not_availability(self):
        for line in self:
            if line.product_template_id:
                if line.product_template_id.hak_master_product_id:
                    print("!!!")
                    if line.product_uom_qty > line.product_template_id.hak_master_product_id.free_qty:
                        line.product_not_availability = True
                    else:
                        line.product_not_availability = False
                else:
                    print("222222222")
                    if line.product_uom_qty > line.product_id.free_qty:
                        line.product_not_availability = True
                    else:
                        line.product_not_availability = False
            else:
                line.product_not_availability = False
            # if not line.product_uom or (line.product_id.uom_id.id != line.product_uom.id):
            #     line.product_uom = line.product_id.uom_id

    @api.depends('product_id')
    def _compute_is_configurable_product(self):
        for rec in self:
            if rec.product_template_id:
                if rec.product_template_id.has_configurable_attributes or rec.product_template_id.hak_master_product_id:
                    rec.is_configurable_product = True
                elif rec.product_template_id.categ_id.personalization_applicable or rec.product_template_id.categ_id.fully_customized_product or rec.product_template_id.categ_id.psc_product or rec.product_template_id.categ_id.customized_product and rec.product_template_id.printing_side_line_ids:
                    rec.is_configurable_product = True

                else:
                    rec.is_configurable_product = False
            else:
                rec.is_configurable_product = False

    @api.depends('personalized_unit_price', 'base_unit_price')
    def _update_sub_fields_values(self):
        for rec in self:
            rec.net_unit_price = rec.personalized_unit_price + rec.base_unit_price
            rec.total_base_price = rec.base_unit_price * rec.product_uom_qty
            rec.total_personalized_price = rec.personalized_unit_price * rec.product_uom_qty
            rec.net_total_price = rec.total_base_price + rec.total_personalized_price

    @api.onchange('product_template_id')
    def onchage_product_template_id(self):
        if self.product_template_id:

            if self.product_template_id.hak_master_product_id:
                self.base_unit_price = self.product_template_id.hak_master_product_id.lst_price
                self.personalized_unit_price = self.product_template_id.list_price
                self.pdt_default_code = self.product_template_id.default_code

            else:
                self.base_unit_price = self.product_template_id.list_price
                self.personalized_unit_price = 0
                self.pdt_default_code = self.product_template_id.default_code

    @api.depends('product_id')
    def _compute_product_template_id(self):
        for line in self:
            line.product_template_id = line.product_id.product_tmpl_id

    def _search_product_template_id(self, operator, value):
        return [('product_id.product_tmpl_id', operator, value)]

    @api.depends('product_id')
    def _compute_custom_attribute_values(self):
        for line in self:
            if not line.product_id:
                line.product_custom_attribute_value_ids = False
                continue
            if not line.product_custom_attribute_value_ids:
                continue
            valid_values = line.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
            # remove the is_custom values that don't belong to this template
            for pacv in line.product_custom_attribute_value_ids:
                if pacv.custom_product_template_attribute_value_id not in valid_values:
                    line.product_custom_attribute_value_ids -= pacv

    @api.depends('product_id')
    def _compute_no_variant_attribute_values(self):
        for line in self:
            if not line.product_id:
                line.product_no_variant_attribute_value_ids = False
                continue
            if not line.product_no_variant_attribute_value_ids:
                continue
            valid_values = line.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
            # remove the no_variant attributes that don't belong to this template
            for ptav in line.product_no_variant_attribute_value_ids:
                if ptav._origin not in valid_values:
                    line.product_no_variant_attribute_value_ids -= ptav
