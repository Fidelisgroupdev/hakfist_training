# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import http,_
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.http import request
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_users import SignupError
from werkzeug.urls import url_encode

import werkzeug

class CustomAuthSignupHome(AuthSignupHome):

    # def _prepare_signup_values(self, qcontext):
    #     values = {key: qcontext.get(key) for key in ('login', 'name', 'password','vat')}
    #     if not values:
    #         raise UserError(_("The form was not properly filled in."))
    #     if values.get('password') != qcontext.get('confirm_password'):
    #         raise UserError(_("Passwords do not match; please retype them."))
    #     supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
    #     lang = request.context.get('lang', '')
    #     if lang in supported_lang_codes:
    #         values['lang'] = lang
    #     return values
    # @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    # def web_auth_signup(self, *args, **kw):
    #     qcontext = self.get_auth_signup_qcontext()
    #
    #     if not qcontext.get('token') and not qcontext.get('signup_enabled'):
    #         raise werkzeug.exceptions.NotFound()
    #     self.do_signup(qcontext)
    #     # return http.request.render('hakfist_partner_reg.thank_you_page')
    #     return """
    #                        <script>
    #                            alert("Thank you for expressing your interest. We will inform you once the procedures have been completed.");
    #                            window.location.href = "/thank_you";  // Redirect to the thank you page
    #                        </script>
    #                    """

        # if 'error' not in qcontext and request.httprequest.method == 'POST':
        #     try:
        #         self.do_signup(qcontext)
        #         # Send an account creation confirmation email
        #         User = request.env['res.users']
        #         user_sudo = User.sudo().search(
        #             User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
        #         )
        #         template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
        #                                    raise_if_not_found=False)
        #         if user_sudo and template:
        #             template.sudo().send_mail(user_sudo.id, force_send=True)
        #         return self.web_login(*args, **kw)
        #     except UserError as e:
        #         qcontext['error'] = e.args[0]
        #     except (SignupError, AssertionError) as e:
        #         if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
        #             qcontext["error"] = _("Another user is already registered using this email address.")
        #         else:
        #             _logger.warning("%s", e)
        #             qcontext['error'] = _("Could not create a new account.") + "\n" + str(e)
    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = self._prepare_signup_values(qcontext)
        self._signup_with_values(qcontext.get('token'), values)
        # request.env.cr.commit()
        return """
                           <script>
                               alert("Thank you for expressing your interest. We will inform you once the procedures have been completed.");
                               window.location.href = "/thank_you";  // Redirect to the thank you page
                           </script>
                       """


    def _signup_with_values(self, token, values):
        print(values, type(values),values.get('vat'))
        temp_partner = request.env['temp.partner'].sudo().create({
            'name': values.get('name'),
            'email': values.get('login'),
            # 'password': values.get('password'),
            # 'company_name': values.get('company_name'),
            'street': values.get('street'),
            'street2': values.get('street2'),
            'city': values.get('city'),
            'state_id': values.get('state_id'),
            'zip': values.get('zip'),
            'country_id': values.get('country_id'),
            'phone': values.get('phone'),
            'mobile': values.get('mobile'),
            # 'website': values.get('website'),
            'trn_number': values.get('vat'),
            # 'customer_header': values.get('customer_header'),
            # 'trade_license': values.get('trade_license'),
            # 'customer_footer': values.get('customer_footer'),
            # 'trn_certificate': values.get('trn_certificate'),
            # 'tags': values.get('tags'),
            # 'licence_expiry_date': values.get('licence_expiry_date'),
            # Add other fields as needed
        })
        print(temp_partner, 'temp partner')
        # response = request.render('hakfist_partner_reg.success_reg')
        # window.location.href = "/thank_you";

        # return http.local_redirect('/home')
        # return response
        # response = request.render('auth_signup.reset_password')
        # response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        # response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        # return response
        # return
        # return http.request.render('hakfist_partner_reg.thank_you_page')

    # login, password = request.env['res.users'].sudo().signup(values, token)
    # request.env.cr.commit()     # as authenticate will use its own cursor we need to commit the current transaction
    # pre_uid = request.session.authenticate(request.db, login, password)
    # if not pre_uid:
    #     raise SignupError(_('Thank you for expressing your interest. We will inform you once the procedures have been completed'))
