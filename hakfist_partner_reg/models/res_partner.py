from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    image_header = fields.Binary(string='Customer Header Image')
    file_name_header = fields.Char('File Name')
    image_footer = fields.Binary(string='Customer Footer Image')
    file_name_image_footer = fields.Char('File Name')
    customer_logo = fields.Binary(string='Customer Logo')
    file_name_customer_logo = fields.Char('Customer Logo File Name')
    license_att_ids = fields.Many2many(
        'ir.attachment', string='Trade License')
    trn_att_ids = fields.Many2many(
        'ir.attachment', 'partner_reg_attachment_rel', 'partner_reg_id', string='TRN Certificate')
    trade_licence_expiry_date = fields.Date(string='Licence Expiry Date')
