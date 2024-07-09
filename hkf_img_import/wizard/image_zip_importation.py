# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

from io import BytesIO
from zipfile import ZipFile, BadZipFile
import base64
import os

import logging
_logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = ('.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG', '.bmp',
                    '.BMP')


class ImageZipImportation(models.TransientModel):
    _name = 'image.zip.importation'
    _description = 'Image Zip Importation'

    img_zip_file = fields.Binary(
        string='Image Zip File',
        attachment=False,
        required=True,
    )

    filename = fields.Char(
        string='File Name',
        readonly=False,
    )

    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Model',
        required=True,
    )

    id_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Identity Field',
        required=True,
        domain="""[
            ('ttype', '=', 'char'),
            ('model_id', '=', model_id),
        ]""",
    )

    img_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Image Field',
        required=True,
        domain="""[
            ('ttype', '=', 'binary'),
            ('model_id', '=', model_id),
        ]""",
    )

    result_info = fields.Html(
        string='Results Information',
        readonly=True,
    )

    state = fields.Selection(
        selection=[
            ('import', 'Importation'),
            ('result', 'Results'),
        ],
        string='State',
        default='import',
    )

    def import_images(self):
        img_zip_file = base64.decodebytes(self.img_zip_file)
        try:
            img_files = ZipFile(BytesIO(img_zip_file))
        except BadZipFile:
            raise ValidationError(_(
                'You must select a ZIP file in order to load its content.'
            ))
        result_info = _('''
            <table style="width:100%%; border-collapse: collapse; table-layout: fixed;">
                <tr style="border-bottom: 1px solid;">
                    <th style="width:25%%;">File</th>
                    <th style="width:25%%;">%s</th>
                    <th style="width:25%%;">%s</th>
                    <th style="width:25%%;">Result</th>
                </tr>
        ''') % (
            self.model_id.name,
            self.id_field_id.name,
        )
        for img_filename_path in img_files.namelist():
            row_info = _('''
                <tr style="border-bottom: 1px solid;">
                    <td>%s</td>
            ''') % (
                img_filename_path,
            )
            img_filename = os.path.basename(img_filename_path)
            try:
                value, extension = os.path.splitext(img_filename)
            except Exception:
                row_info += _('''
                        <td>-</td>
                        <td>-</td>
                        <td style="color: red;">Invalid file.</td>
                    </tr>
                ''')
                result_info += row_info
                continue
            else:
                if extension not in IMAGE_EXTENSIONS:
                    row_info += _('''
                            <td>-</td>
                            <td>-</td>
                            <td style="color: red;">The file is not an image.</td>
                        </tr>
                    ''')
                    result_info += row_info
                    continue
            img_file_content = img_files.read(img_filename_path)
            encoded_string = base64.b64encode(img_file_content).decode()
            records_to_update = self.env[self.model_id.model].search([
                (self.id_field_id.name, '=', value),
            ])
            update = records_to_update.write({
                self.img_field_id.name: encoded_string,
            })
            if len(records_to_update) > 0 and update:
                row_info += _('''
                        <td>%s</td>
                        <td>%s</td>
                        <td style="color: green;">Image updated.</td>
                    </tr>
                ''') % (
                    records_to_update.mapped('display_name'), value
                )
            elif len(records_to_update) == 0:
                row_info += _('''
                        <td>-</td>
                        <td>%s</td>
                        <td style="color: red;">Identification not found.</td>
                    </tr>
                ''') % (
                    value
                )
            else:
                row_info += _('''
                        <td>%s</td>
                        <td>%s</td>
                        <td style="color: red;">Image not updated.</td>
                    </tr>
                ''') % (
                    records_to_update.mapped('display_name'), value
                )
            result_info += row_info
        result_info += _('''
            </table>
        ''')
        self.write({
            'result_info': result_info,
            'state': 'result',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'image.zip.importation',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
