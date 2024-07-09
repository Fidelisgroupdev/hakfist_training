# -*- coding: utf-8 -*-

import tempfile
import binascii
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, exceptions, api, _
from odoo.modules.module import get_module_resource

import logging

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class Inherit_Stock_Picking(models.Model):
    _inherit = 'stock.picking'

    is_import = fields.Boolean("import records", default=False)


class ImportPicking(models.TransientModel):
    _name = "import.picking1"
    _description = "Import Picking"

    def _get_transfer_template(self):
        file = get_module_resource('hkf_mat_trf_upload', 'sample_file', 'import_picking.xlsx')
        self.transfer_template = base64.b64encode(open(file, "rb").read())

    seq = fields.Char(string="Name")
    file = fields.Binary('File')
    # import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='xls')
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type')
    location_id = fields.Many2one(
        'stock.location', "Source Location Zone",
        default=lambda self: self.env['stock.picking.type'].browse(
            self._context.get('default_picking_type_id')).default_location_src_id,
        required=True,
    )
    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location Zone",
        default=lambda self: self.env['stock.picking.type'].browse(
            self._context.get('default_picking_type_id')).default_location_dest_id,
    )
    transfer_template = fields.Binary('Template', compute="_get_transfer_template")

    def download_sample_file(self):
        return {
            'type': 'ir.actions.act_url',
            'name': 'Transfer',
            'url': '/web/content/import.picking1/%s/transfer_template/import_picking.xlsx?download=true' % (self.id),
        }

    @api.onchange('picking_type_id')
    def onchange_picking_type_id(self):
        """
        it is used to set the location and destination location from picking type.
        """
        if self.picking_type_id:
            self.location_id = self.picking_type_id.default_location_src_id.id
            self.location_dest_id = self.picking_type_id.default_location_dest_id.id
            rcode = _('%s') % self.picking_type_id.sequence_id.name
            self.seq = self.env['ir.sequence'].next_by_code(rcode)

    def create_picking(self, values):
        """
        create a picking from data.
        """
        picking_obj = self.env['stock.picking']
        pickings_created = {}
        picking = picking_obj.search([('name', '=', values.get('seq'))])
        if picking:
            lines = self.make_picking_line(values, picking)
            return lines
        else:
            # pick_date = self._get_date(values.get('date'))
            vals = {
                'name': values.get('seq'),
                'partner_id': False,
                'picking_type_id': values.get('picking_type_id'),
                'location_id': values.get('location_id'),
                'location_dest_id': values.get('location_dest_id'),
                'origin': values.get('origin'),
                'is_import': True
            }
            print(values.get('seq'))
            pick_id = picking_obj.create(vals)
            pickings_created[pick_id] = values.get('location_dest_id')

            lines = self.make_picking_line(values, pick_id)
        # return pick_id

    def make_picking_line(self, values, pick_id):
        print('Values..', values)
        """
        it is used to create stock move and stock move line from data.
        """
        product_obj = self.env['product.product'].sudo()
        tmpl_obj = self.env['product.template'].sudo()
        stock_lot_obj = self.env['stock.lot'].sudo()
        stock_move_obj = self.env['stock.move'].sudo()
        stock_move_line_obj = self.env['stock.move.line'].sudo()
        expiry_date = False
        lot_id = False

        product_id = product_obj.search(
            [('default_code', '=', values.get('default_code'))])

        # if not product_id:
        #     tmpl_id = tmpl_obj.search(
        #         [('mgo_code', '=', values.get('mgo_code'))])
        #     print(values.get('mgo_code'),tmpl_id)
        #
        #     product_id = product_obj.search([('product_tmpl_id', '=', tmpl_id.id)])
        #     print(product_id)
        if not product_id:
            raise ValidationError(
                _('Product is not available "%s" .') % values.get('default_code'))

        if product_id.use_expiration_date and not values.get('expiry_date') == '':
            expiry_date = self._get_date(values.get('expiry_date'))
        if values.get('lot') != '':
            if values.get('lot'):
                # prdtmpl_obj = self.env['']
                lot_id = stock_lot_obj.search(
                    [('company_id', '=', pick_id.company_id.id), ('name', '=', values.get('lot')),
                     ('product_id', '=', product_id.id)])
                lot_id.expiration_date = expiry_date
                if not lot_id:
                    lot_vals = {
                        'name': values.get('lot'),
                        'product_id': product_id.id,
                        'company_id': pick_id.company_id.id,
                        'expiration_date': expiry_date,
                        'use_date': expiry_date,
                        'removal_date': expiry_date,
                        'alert_date': expiry_date
                    }
                    lot_id = stock_lot_obj.create(lot_vals)

        move = stock_move_obj.create({
            'product_id': product_id.id,
            'name': product_id.name,
            'product_uom_qty': values.get('quantity'),
            # 'reserved_availability': values.get('quantity'),
            'picking_id': pick_id.id,
            'location_id': pick_id.location_id.id,
            'date': pick_id.scheduled_date,
            'location_dest_id': pick_id.location_dest_id.id,
            'product_uom': values.get('product_uom') if values.get('product_uom') else product_id.uom_id.id,
            'picking_type_id': self.picking_type_id.id,
            'state': 'confirmed',

        })

        move_line = stock_move_line_obj.create({
            'picking_id': pick_id.id,
            'location_id': pick_id.location_id.id,
            'location_dest_id': pick_id.location_dest_id.id,
            'quantity': values.get('quantity'),
            # 'product_uom_qty':values.get('quantity'),
            'product_id': product_id.id,
            'move_id': move.id,
            'lot_id': lot_id.id if lot_id else False,
            'lot_name': lot_id.name if lot_id else False,
            'expiration_date': lot_id.expiration_date if lot_id else False,
            'product_uom_id': values.get('product_uom') if values.get('product_uom') else product_id.uom_id.id,
        })
        move_line._onchange_lot_id()
        # return True

    def _get_date(self, date):
        """
        it is used to check the dateformat
        """
        DATETIME_FORMAT = "%Y-%m-%d"
        if date:
            try:
                i_date = datetime.strptime(date, DATETIME_FORMAT).date()
            except Exception:
                raise ValidationError(
                    _('Wrong Date Format. Date Should be in format YYYY-MM-DD.'))
            return i_date
        else:
            raise ValidationError(
                _('Date field is blank in sheet Please add the date.'))

    def import_picking(self):
        """
        it is used to check the file format and preapre values for create picking.
        """
        if not self.file:
            raise ValidationError(_("Please select a file first then proceed"))
        else:
            try:
                fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.file))
                fp.seek(0)
                values = {}
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:
                raise ValidationError(_("Not a valid file!"))
            list_col = ['INTERNAL REFERENCE', 'LOT NUMBER', 'EXPIRY DATE', 'QUANTITY', 'UNIT', 'LOCATION']
            pickings_created = {}
            pickings_ids = []
            for row_no in range(sheet.nrows):
                current_row = row_no + 1  # Adding 1 to convert from zero-based to one-based row numbers

                if row_no <= 0:
                    line_fields = list(
                        map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value),
                            sheet.row(row_no)))

                    for col in line_fields:
                        if not col in list_col:
                            raise ValidationError(
                                _('Error in row %s: Wrong Column name %s.' % (current_row, col)))
                else:
                    line = list(map(lambda row: isinstance(row.value, bytes) and row.value.encode(
                        'utf-8') or str(row.value), sheet.row(row_no)))

                    if line[0] == '':
                        raise ValidationError(
                            _('Error in row %s: INTERNAL REFERENCE is missing' % current_row))

                    if line[3] == '':
                        raise ValidationError(_('Error in row %s: QUANTITY Not Available' % current_row))
                    if line[5] == '':
                        raise ValidationError(_('Error in row %s: Destination Location not Available' % current_row))
                    if line[4] == '':
                        raise ValidationError(_('Error in row %s: UNIT not Available' % current_row))
                    else:
                        uom_id = self.env['uom.uom'].search([('name', '=', line[4])], limit=1)
                        if not uom_id:
                            raise ValidationError(
                                _('Error in row %s: Unit of Measure not present in the system' % current_row))

                    if line[2] != '':
                        expiry_date_float = int(float(line[2]))
                        expiry_date = datetime(
                            *xlrd.xldate_as_tuple(expiry_date_float, workbook.datemode))
                        expiry_date_string = expiry_date.date().strftime('%Y-%m-%d')
                    else:
                        expiry_date_string = False
                    destination_location = self.env['stock.location'].search([('name', '=', line[5])], limit=1)
                    if not destination_location:
                        raise ValidationError(_('Error in row %s: Destination Location not present in the system' % current_row))
                    values.update({
                        'default_code': line[0],
                        'lot': line[1],
                        'expiry_date': expiry_date_string,
                        'quantity': line[3],
                        'picking_type_id': self.picking_type_id.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': destination_location.id,
                        'seq': self.seq,
                        'product_uom': uom_id.id,
                    })

                    picking_obj = self.env['stock.picking']
                    picking = picking_obj.search([('name', '=', values.get('seq'))])
                    # if picking:
                    #     lines = self.make_picking_line(values, picking)
                    #     return lines
                    # pick_date = self._get_date(values.get('date'))
                    if values.get('location_dest_id') not in pickings_created:
                        vals = {
                            # 'name': self.env['ir.sequence'].next_by_code('stock.picking'),
                            'partner_id': False,
                            'picking_type_id': values.get('picking_type_id'),
                            'location_id': values.get('location_id'),
                            'location_dest_id': values.get('location_dest_id'),
                            'origin': values.get('origin'),
                            'is_import': True
                        }
                        print(values.get('seq'))
                        pick_id = picking_obj.create(vals)
                        pickings_ids.append(pick_id.id)
                        pickings_created[values.get('location_dest_id')] = pick_id
                        lines = self.make_picking_line(values, pick_id)

                    else:
                        lines = self.make_picking_line(values, pickings_created[values.get('location_dest_id')])
        action = {
            'name': _('Transfers'),
            'view_mode': 'list',
            'view_type': 'list',
            'views': [[False, 'list'], [False, 'form']],
            'view_id': self.env.ref('stock.vpicktree').id,
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', pickings_ids)]}

        return action
