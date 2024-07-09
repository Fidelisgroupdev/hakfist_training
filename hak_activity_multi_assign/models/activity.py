import logging
import pytz

from collections import defaultdict, Counter
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, exceptions, fields, models, _, Command
from odoo.osv import expression
from odoo.tools import is_html_empty
from odoo.tools.misc import clean_context, get_lang, groupby

_logger = logging.getLogger(__name__)


class MailActivityType(models.Model):
    _inherit = 'mail.activity'

    cc_user_ids = fields.Many2many('res.users', string='CC Users')

    def action_notify(self):
        print("action_notify")
        if not self:
            return
        for activity in self:
            if activity.user_id.lang:
                # Send the notification in the assigned user's language
                activity = activity.with_context(lang=activity.user_id.lang)

            model_description = activity.env['ir.model']._get(activity.res_model).display_name
            body = activity.env['ir.qweb']._render(
                'mail.message_activity_assigned',
                {
                    'activity': activity,
                    'model_description': model_description,
                    'is_html_empty': is_html_empty,
                },
                minimal_qcontext=True
            )
            record = activity.env[activity.res_model].browse(activity.res_id)
            if activity.user_id:
                record.message_notify(
                    partner_ids=activity.user_id.partner_id.ids,
                    body=body,
                    record_name=activity.res_name,
                    model_description=model_description,
                    email_layout_xmlid='mail.mail_notification_layout',
                    subject=_('"%(activity_name)s: %(summary)s" assigned to you',
                              activity_name=activity.res_name,
                              summary=activity.summary or activity.activity_type_id.name),
                    subtitles=[_('Activity: %s', activity.activity_type_id.name),
                               _('Deadline: %s', activity.date_deadline.strftime(get_lang(activity.env).date_format))]
                )
            print("activity.cc_user_ids", activity.cc_user_ids)
            if activity.cc_user_ids:
                for cc_user in activity.cc_user_ids:
                    record.message_notify(
                        partner_ids=cc_user.partner_id.ids,
                        body=body,
                        record_name=activity.res_name,
                        model_description=model_description,
                        email_layout_xmlid='mail.mail_notification_layout',
                        subject=_('"%(activity_name)s: %(summary)s"',
                                  activity_name=activity.res_name,
                                  summary=activity.summary or activity.activity_type_id.name),
                        subtitles=[_('Activity: %s', activity.activity_type_id.name),
                                   _('Deadline: %s',
                                     activity.date_deadline.strftime(get_lang(activity.env).date_format))]
                    )

    @api.model_create_multi
    def create(self, vals_list):
        print("vals_list@@@@@@@@@@", vals_list)
        records = super().create(vals_list)
        print("activity create 44444444444444444", records)
        for rec in records:
            print("rec.cc_user_ids", rec.cc_user_ids)
            if rec.cc_user_ids:
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                notification_ids = [(0, 0,
                                     {
                                         'res_partner_id': user.partner_id.id,
                                         'notification_type': 'inbox'
                                     }
                                     ) for user in rec.cc_user_ids if rec.cc_user_ids]

                message = self.env['mail.message'].create({
                    'message_type': "notification",
                    'body': _('"%(summary)s"', summary=rec.summary or rec.activity_type_id.name),
                    'subject': "Your Subject",
                    'partner_ids': [(4, user.partner_id.id) for user in rec.cc_user_ids if rec.cc_user_ids],
                    'model': self._name,
                    'res_id': self.id,
                    'notification_ids': notification_ids,
                    'author_id': self.env.user.partner_id and self.env.user.partner_id.id
                })
                print("message", message)
        return records
