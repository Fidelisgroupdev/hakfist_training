import pytz
import datetime
from lxml import etree

from odoo import api, fields, models
from odoo.exceptions import UserError
from markupsafe import Markup

# Global variables used for the warning fields declared on the res.partner
# in the following modules : sale, purchase, account, stock
WARNING_MESSAGE = [
    ('no-message', 'No Message'),
    ('warning', 'Warning'),
    ('block', 'Blocking Message')
]
WARNING_HELP = 'Selecting the "Warning" option will notify user with the message, Selecting "Blocking Message" will throw an exception with the message and block the flow. The Message has to be written in the next field.'

ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id')


@api.model
def _lang_get(self):
    return self.env['res.lang'].get_installed()


# put POSIX 'Etc/*' entries at the end to avoid confusing users - see bug 1086728
_tzs = [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]


def _tz_get(self):
    return _tzs


from odoo import api, fields, models, _, tools


class TempPartner(models.Model):
    _name = "temp.partner"
    _inherit = ['format.address.mixin', 'avatar.mixin', 'mail.thread']
    _description = "Temp Partner"

    is_reg_user = fields.Boolean(string='Is Registration User')

    @api.depends('tz')
    def _compute_tz_offset(self):
        for partner in self:
            partner.tz_offset = datetime.datetime.now(pytz.timezone(partner.tz or 'GMT')).strftime('%z')

    @api.depends('vat', 'company_id', 'company_registry')
    def _compute_same_vat_partner_id(self):

        for partner in self:
            # use _origin to deal with onchange()
            partner_id = partner._origin.id
            # active_test = False because if a partner has been deactivated you still want to raise the error,
            # so that you can reactivate it instead of creating a new one, which would loose its history.
            Partner = self.with_context(active_test=False).sudo()
            domain = [
                ('vat', '=', partner.vat),
            ]
            if partner.company_id:
                domain += [('company_id', 'in', [False, partner.company_id.id])]
            if partner_id:
                domain += [('id', '!=', partner_id), '!', ('id', 'child_of', partner_id)]
            # For VAT number being only one character, we will skip the check just like the regular check_vat
            should_check_vat = partner.vat and len(partner.vat) != 1
            partner.same_vat_partner_id = should_check_vat and not partner.parent_id and Partner.search(domain, limit=1)
            # check company_registry
            domain = [
                ('company_registry', '=', partner.company_registry),
                ('company_id', 'in', [False, partner.company_id.id]),
            ]
            if partner_id:
                domain += [('id', '!=', partner_id), '!', ('id', 'child_of', partner_id)]
            partner.same_company_registry_partner_id = bool(
                partner.company_registry) and not partner.parent_id and Partner.search(domain, limit=1)

    # @api.model
    # def get_views(self, views, options=None):
    #     res = super().get_views(views, options)
    #     views_types = ['list', 'form']
    #     for view_type in views_types:
    #         arch = res['views'].get(view_type, {}).get('arch')
    #         if view_type == 'list':
    #             view_type = 'tree'
    #         if arch:
    #             if not self.user_has_groups(
    #                     'hakfist_partner_reg.group_customer_review'):
    #                 tree = etree.fromstring(arch)
    #
    #                 for node in tree.xpath('//' + view_type):
    #                     node.set('domain',
    #                              "[('create_uid', '=', 'self.env.user.id')")
    #                     print(self.env.user.id,)
    #
    #                 arch = etree.tostring(tree, encoding='unicode')
    #                 if view_type == 'tree':
    #                     view_type = 'list'
    #             res['views'].setdefault(view_type, {})['arch'] = arch
    #     return res

    def _compute_company_registry(self):
        # exists to allow overrides
        for company in self:
            company.company_registry = company.company_registry

    @api.depends('lang')
    def _compute_active_lang_count(self):
        lang_count = len(self.env['res.lang'].get_installed())
        for partner in self:
            partner.active_lang_count = lang_count

    name = fields.Char(index=True, default_export_compatible=True)
    display_name = fields.Char(compute='_compute_display_name', recursive=True, store=True, index=True)
    date = fields.Date(index=True)
    title = fields.Many2one('res.partner.title')
    parent_id = fields.Many2one('temp.partner', string='Related Company', index=True)
    parent_name = fields.Char(related='parent_id.name', readonly=True, string='Parent name')
    child_ids = fields.One2many('temp.partner', 'parent_id', string='Contact', domain=[
        ('active', '=', True)])  # force "active_test" domain to bypass _search() override
    ref = fields.Char(string='Reference', index=True)
    lang = fields.Selection(_lang_get, string='Language',
                            help="All the emails and documents sent to this contact will be translated in this language.")
    active_lang_count = fields.Integer(compute='_compute_active_lang_count')
    tz = fields.Selection(_tz_get, string='Timezone', default=lambda self: self._context.get('tz'),
                          help="When printing documents and exporting/importing data, time values are computed according to this timezone.\n"
                               "If the timezone is not set, UTC (Coordinated Universal Time) is used.\n"
                               "Anywhere else, time values are computed according to the time offset of your web client.")

    tz_offset = fields.Char(compute='_compute_tz_offset', string='Timezone offset', invisible=True)
    vat = fields.Char(string='Tax ID', index=True,
                      help="The Tax Identification Number. Values here will be validated based on the country format. You can use '/' to indicate that the partner is not subject to tax.")
    same_vat_partner_id = fields.Many2one('temp.partner', string='Partner with same Tax ID',
                                          compute='_compute_same_vat_partner_id', store=False)
    same_company_registry_partner_id = fields.Many2one('temp.partner', string='Partner with same Company Registry',
                                                       compute='_compute_same_vat_partner_id', store=False)
    # company_registry = fields.Char(string="Company ID", compute='_compute_company_registry', store=True, readonly=False,
    #                                help="The registry number of the company. Use it if it is different from the Tax ID. It must be unique across all partners of a same country")
    website = fields.Char('Website Link')
    comment = fields.Html(string='Notes')
    category_id = fields.Many2many('res.partner.category', column1='partner_id',
                                   column2='category_id', string='Tags')
    active = fields.Boolean(default=True)
    employee = fields.Boolean(help="Check this box if this contact is an Employee.")
    function = fields.Char(string='Job Position')
    current_user_id = fields.Many2one('res.users', string='Current User')
    company_registry = fields.Char(string='License Number')
    trn_number = fields.Char(string='TRN Number')
    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Invoice Address'),
         ('delivery', 'Delivery Address'),
         ('private', 'Private Address'),
         ('other', 'Other Address'),
         ], string='Address Type',
        default='contact')
    # address fields
    street = fields.Char(states={'review': [('readonly', True)]})
    street2 = fields.Char(readonly=1, states={'draft': [('readonly', False)]})
    zip = fields.Char(change_default=True, readonly=1, states={'draft': [('readonly', False)]})
    city = fields.Char(readonly=1, states={'draft': [('readonly', False)]})
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]", readonly=1,
                               states={'draft': [('readonly', False)]})
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',
                                 readonly=1, states={'draft': [('readonly', False)]})
    country_code = fields.Char(related='country_id.code', string="Country Code",
                               readonly=1, states={'draft': [('readonly', False)]})
    partner_latitude = fields.Float(string='Geo Latitude', digits=(10, 7))
    partner_longitude = fields.Float(string='Geo Longitude', digits=(10, 7))
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    mobile = fields.Char(string="Mobile")
    is_company = fields.Boolean(string='Is a Company', default=False,
                                help="Check if the contact is a company, otherwise it is a person")
    industry_id = fields.Many2one('res.partner.industry', 'Industry')
    company_type = fields.Selection(string='Company Type',
                                    selection=[('person', 'Individual'), ('company', 'Company')], default='company')
    # company_id = fields.Many2one('res.company', 'Company', index=True)
    company_id = fields.Many2one('res.company', 'Company', index=True, compute='check_group')
    color = fields.Integer(string='Color Index', default=0)
    company_name = fields.Char('Company Name')
    barcode = fields.Char(help="Use a barcode to identify this contact.", copy=False, company_dependent=True)
    team_id = fields.Many2one('crm.team', string='Sales Team')
    sale_person_id = fields.Many2one('res.users', string='Sales Person', default=lambda self: self.env.user)
    request_user_id = fields.Many2one('res.users', string='Request User')
    review_user_id = fields.Many2one('res.users', string='Request User')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('review', 'Under Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('cancel', 'Cancelled'),
        ], string='Status', required=True, readonly=True, tracking=True, default='draft')
    customer_id = fields.Many2one("res.partner", string="Customer Reference")
    trade_licence_expiry_date = fields.Date(string='Licence Expiry Date')
    # trn_expiry_date = fields.Date(string='TRN Expiry Date')
    image_header = fields.Binary(string='Customer Header Image', help='Upload images with .png,jpg,.jpeg')
    file_name_header = fields.Char('File Name')
    image_footer = fields.Binary(string='Customer Footer Image')
    file_name_image_footer = fields.Char('File Name')
    customer_logo = fields.Binary(string='Customer Logo')
    file_name_customer_logo = fields.Char('Customer Logo File Name')
    license_att_ids = fields.Many2many(
        'ir.attachment', string='TRADE license')
    trn_att_ids = fields.Many2many(
        'ir.attachment', 'reg_attachment_rel', 'reg_id', string='TRN registration')
    contact_line_ids = fields.One2many('contact.contact', 'cust_reg_id', string='Contact Line ids')
    reject_reason_id = fields.Many2one('reject.reason', string='Reject Reason')
    rejection_description = fields.Char('Description')

    def check_group(self):
        print('ss')
        for rec in self:
            rec.company_id = rec.company_id
            if not rec.user_has_groups(
                    'hakfist_partner_reg.group_customer_review'):
                rec.is_reg_user = True
            rec.current_user_id = rec.env.user.id
            print('UUU', rec.current_user_id, rec.env.user, rec.is_reg_user)

    def create_partner(self):
        print("create_partner")
        partner_obj = self.env['res.partner'].sudo()
        self.sudo().review_user_id = self.env.user.id
        self.sudo().message_post(
            body='Contact created from customer registration form, Request by %s and reviewed by %s' % (
                self.request_user_id.name, self.review_user_id.name), partner_ids=[], attachment_ids=[])

        vals = {
            'name': self.name,
            'date': self.date,
            'title': self.title.id if self.title else False,
            'ref': self.ref,
            'lang': self.lang,
            'tz': self.tz,
            'tz_offset': self.tz_offset,
            'company_registry': self.company_registry,
            'vat': self.trn_number,
            'website': self.website,
            'comment': self.comment,
            'employee': self.employee,
            'function': self.function,
            'type': self.type,
            'street': self.street,
            'street2': self.street2,
            'zip': self.zip,
            'city': self.city,
            'state_id': self.state_id.id if self.state_id else False,
            'country_id': self.country_id.id if self.country_id else False,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'is_company': self.is_company,
            'industry_id': self.industry_id.id if self.industry_id else False,
            'company_type': self.company_type,
            'color': self.color,
            'company_name': self.company_name,
            'barcode': self.barcode,
            # 'image_header': self.image_header,
            # 'image_footer': self.image_footer,
            'customer_logo': self.customer_logo,
            'license_att_ids': self.license_att_ids,
            'trn_att_ids': self.trn_att_ids,
            'trade_licence_expiry_date': self.trade_licence_expiry_date,
            'user_id': self.sale_person_id.id if self.sale_person_id else False,
            'team_id': self.team_id.id if self.team_id else False,
            'customer_rank': 1,
        }
        print("valspppppppppppppp", vals)
        partner = partner_obj.create(vals)
        print("partner", partner)
        if self.sudo().contact_line_ids:
            for contact in self.contact_line_ids:
                contact_vals = {'name': contact.name,
                                'function': contact.function,
                                'mobile': contact.mobile,
                                'email': contact.email,
                                'parent_id': partner.id if partner else False,
                                'type': 'contact'
                                }
                contact = partner_obj.create(contact_vals)

        self.sudo().customer_id = partner
        self.sudo().state = 'approved'
        if self.sudo().customer_id:
            message = self.get_message_body(self, 'cancelled')
            print("message444", message)

            outgoing_mailserver = self.sudo().env.company.parent_id
            print("outgoing_mailserver", outgoing_mailserver)
            if outgoing_mailserver:
                mail_values = {
                    'subject': 'Request For Customer Registration Approved',
                    'body_html': message,
                    'auto_delete': False,
                    'email_from': outgoing_mailserver.email,
                    'email_to': '%s' % self.customer_id.email,
                }
                mail_id = self.env['mail.mail'].sudo().create(mail_values)
                mail_id.sudo().send()
        return

    def get_message_body(self, temp, type):
        if type == 'request':
            base_url = self.sudo().env['ir.config_parameter'].sudo().get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=%s' % (temp.id, self._name)
            url = base_url
            body = Markup(
                "{greeting} <br/> {msg} <br/> <a href='{url}' class='btn btn-link'>Customer</a>").format(
                greeting='Dear Concerned,',
                msg=_(
                    'Kindly note the following request has been received from the  %s for your approval.provide a button for the link to redirect to the said customer registration record.' % (
                        temp.sale_person_id.name)),
                url=_(url),

            )
        elif type == 'approve':
            print("elif type == 'approve':")
            body = Markup(
                "{greeting} <br/> {msg} <br/>").format(
                greeting='Dear Concerned,',
                msg=_('Kindly note that your customer registration request is approved'),
            )
        else:
            print("reject")
            body = Markup(
                "{greeting} <br/> {msg} <br/>").format(
                greeting='Dear Concerned,',
                msg=_('Kindly note that your customer registration request is rejected'),
            )
        print("body", body)
        # oooo
        return body

    def request_for_review(self):
        for rec in self:
            rec.sudo().state = "review"
            rec.sudo().request_user_id = self.sudo().env.user.id
            message = self.sudo().get_message_body(rec, 'request')
            print("message444", message)

            outgoing_mailserver = self.sudo().env.company.parent_id
            print("outgoing_mailserver", outgoing_mailserver)
            # jjj
            if outgoing_mailserver:
                mail_values = {
                    'subject': 'Request For Customer Registration Approval',
                    'body_html': message,
                    'auto_delete': False,
                    'email_from': outgoing_mailserver.email,
                    'email_to': '%s' % rec.team_id.user_id.login,
                    # 'email_cc': '%s' % self.customer_id.user_id.login,
                }
                mail_id = self.env['mail.mail'].sudo().create(mail_values)
                mail_id.sudo().send()
            rec.sudo().message_post(body=message)
            # print(rec.request_user_id, 'll')

    def action_reject(self):
        return {
            'name': "Reject Customer",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'reject.wizard',
            'view_id': self.env.ref('hakfist_partner_reg.reject_wizard_view').id,
            'target': 'new',
        }

    def action_cancel(self):
        for rec in self:
            rec.sudo().state = "draft"

    def unlink(self):
        for rec in self:
            if rec.sudo().state != "draft":
                raise UserError(_('Records can be deleted only in Draft state'))
        return super().unlink()

    @api.onchange('sale_person_id')
    def onchange_sale_person_id(self):
        for rec in self:
            team_id = False
            if rec.sudo().sale_person_id:
                teams = self.env['crm.team'].sudo().search([])
                if teams:
                    for team in teams:
                        if rec.sale_person_id.id in team.member_ids.ids:
                            team_id = team
            if team_id:
                rec.sudo().team_id = team_id.id
            else:
                rec.sudo().team_id = team_id

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.sudo().license_att_ids or res.trn_att_ids:
            attachments_license = []
            attachments_registration = []
            for attachment in res.sudo().license_att_ids:
                attachments_license.append(attachment.id)
            res.sudo().message_post(body='TRADE Licence attachments', partner_ids=[],
                                    attachment_ids=attachments_license)
            for attachment in res.trn_att_ids:
                attachments_registration.append(attachment.id)
            res.sudo().message_post(body='TRN Registration attachments', partner_ids=[],
                                    attachment_ids=attachments_registration)
        return res


class ContactContact(models.Model):
    _name = 'contact.contact'

    cust_reg_id = fields.Many2one('temp.partner', string='Customer Registration Id')
    name = fields.Char(string='Name')
    function = fields.Char(string='Job Position')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')
