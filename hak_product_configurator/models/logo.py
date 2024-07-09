from odoo import fields, models, api
from datetime import date


class PartnerLogo(models.Model):
    _name = 'partner.logo'
    _description = 'Printing Type'

    name = fields.Char("Reference")
    partner_id = fields.Many2one('res.partner', 'Partner')
    product_id = fields.Many2one('product.template', 'Product')
    logo = fields.Binary('Logo')
    crm_id = fields.Many2one('crm.lead', 'CRM ID')
    crm_sequence = fields.Char(related='crm_id.crm_sequence', string='CRM Ref')
    crm_line_id = fields.Many2one('crm.product.line', 'CRM Line ID')

    details = fields.Text('Details')
    attachment_id = fields.Many2one('ir.attachment', 'Attachments')

    @api.model_create_multi
    def create(self, vals_list):
        records = super(PartnerLogo, self).create(vals_list)
        for record in records:
            if record.crm_id:
                records.crm_id.partner_logo = records.id
            if record.logo:
                attachment = self.env['ir.attachment'].sudo().create({
                    'name': record.name,
                    'type': 'binary',
                    'datas': record.logo,
                    'res_model': 'partner.logo',
                    'res_id': record.id,
                    # 'mimetype': 'application/x-pdf' if 'data:application/pdf;base64,' in article else 'image/png'
                })
                record.attachment_id = attachment.id

                folder_owner = self.env.ref('hak_product_configurator.attachment_workspace_for_personalisation')

                self.env['documents.document'].sudo().create({
                    'name': "Main logo for CRM-" + record.name +'-'+ record.crm_id.crm_sequence,
                    'folder_id': folder_owner.id,
                    'attachment_id': attachment.id,
                    'datas': record.logo,
                })
        return records

    def write(self, vals):

        if vals.get('logo'):
            attachment = self.env['ir.attachment'].sudo().create({
                'name': vals.get('name') or self.name,
                'type': 'binary',
                'datas': vals.get('logo'),
                'res_model': 'partner.logo',
                'res_id': self.id,
                # 'mimetype': 'application/x-pdf' if 'data:application/pdf;base64,' in article else 'image/png'
            })
            vals['attachment_id'] = attachment.id

            folder_owner = self.env.ref('hak_product_configurator.attachment_workspace_for_personalisation')

            print("dflksd", vals)
            self.env['documents.document'].sudo().create({
                'name': "Main logo for CRM-" + self.name +'-'+ self.crm_id.name,
                'folder_id': folder_owner.id,
                'attachment_id': attachment.id,
                'datas': self.logo,
            })

        res = super().write(vals)
        if self.crm_id:
            print("dkfjlkdjf uuid")
            self.crm_id.partner_logo = self.id

        return res

    @api.depends('product_id')
    def _compute_details(self):
        print("sadj", self)
        for rec in self:
            details = rec.product_id.personalisation_details




class Partner(models.Model):
    _inherit = 'res.partner'

    partner_logo_ids = fields.One2many('partner.logo', 'partner_id')

