from odoo import fields, models, api
from datetime import date
from odoo.exceptions import ValidationError


class PrintingType(models.Model):
    _name = 'printing.type'
    _description = 'Printing Type'
    _rec_name = 'rec_name'

    name = fields.Char("Name", required=1)
    rec_name = fields.Char("Name", compute='_compute_rec_name', store=True)
    max_color = fields.Integer(string="Max color", required=1)
    max_color_label = fields.Selection([
        ('0', "Full Color"),
        ('1', "Max Color 1"),
        ('2', "Max Color 2"),
        ('3', "Max Color 3"),
        ('4', "Max Color 4"),
        ('5', "Max Color 5"),
        ('6', "Max Color 6"),
        ('7', "Max Color 7"),
        ('8', "Max Color 8"),
        ('9', "Max Color 9"),
        ('10', "Max Color 10"),
        ('11', "Max Color 11"),
        ('12', "Max Color 12"),
    ], string='Max Color Label', compute='_compute_max_color_label', store=True)

    sc = fields.Float('Mulitplier(SC)', default=1)
    pc = fields.Float('Mulitplier(PC)', default=1)
    sequence = fields.Char('Sequence', readonly=1)
    printing_details_ids = fields.One2many('printing.details', 'printing_type_id', string="Printing Details")

    @api.depends('name', 'max_color')
    def _compute_rec_name(self):
        for rec in self:
            if rec.name and rec.max_color:
                rec.rec_name = rec.name + '-' + str(rec.max_color)

    @api.model
    def create(self, vals):
        record = super(PrintingType, self).create(vals)
        record.sequence = self.env["ir.sequence"].next_by_code("printing.type") or ''
        return record

    @api.depends('max_color')
    def _compute_max_color_label(self):
        for rec in self:
            if rec.max_color:
                rec.max_color_label = str(rec.max_color)
            else:
                rec.max_color_label = str(rec.max_color)

    def name_get(self):
        result = []
        for rec in self:
            if rec.max_color_label:
                name = rec.name + " - " + dict(self._fields['max_color_label'].selection).get(rec.max_color_label)
                result.append((rec.id, name))
            else:
                name = rec.name
                result.append((rec.id, name))
        return result

    def action_create_printing_details_line(self):
        print("action_create_printing_details_line")
        categories = self.env['printing.category'].search([])
        side_line_types = self.env['printing.side.type'].search([])
        for category in categories:
            for side_line_type in side_line_types:
                if self.max_color <= 1:
                    # If max_colour is 0 or 1, create a single record
                    self.env['printing.details'].sudo().create({
                        'printing_type_id': self.id,
                        'printing_side_type_id': side_line_type.id,
                        'printing_category_id': category.id,
                        'color': self.max_color,
                    })
                else:
                    # If max_colour is greater than 1, create records for each colour
                    for colour in range(1, self.max_color + 1):
                        self.env['printing.details'].sudo().create({
                            'printing_type_id': self.id,
                            'printing_side_type_id': side_line_type.id,
                            'printing_category_id': category.id,
                            'color': colour,
                        })


class PrintingSideType(models.Model):
    _name = 'printing.side.type'
    _description = 'Printing Side Type'
    _rec_name = 'side_name'

    side_name = fields.Char('Side Name')

    sc = fields.Float('Mulitplier(SC)', default=1)
    pc = fields.Float('Mulitplier(PC)', default=1)


class PrintingCategory(models.Model):
    _name = 'printing.category'
    _description = 'Printing Category'
    _rec_name = 'code'

    name = fields.Char('Name')
    code = fields.Char('Code')


class PrintingDetails(models.Model):
    _name = 'printing.details'
    _description = 'Printing Details'

    printing_type_id = fields.Many2one("printing.type", 'Printing Type')
    printing_side_type_id = fields.Many2one("printing.side.type", 'Printing Side Type')
    printing_category_id = fields.Many2one("printing.category", 'Printing Category')
    color = fields.Float('Color')
    sc = fields.Float('SC')
    pc = fields.Float('PC')

    @api.constrains('printing_type_id', 'printing_side_type_id', 'printing_category_id', 'color')
    def onchange_print(self):
        for vals in self:
            if vals.printing_type_id or vals.printing_side_type_id or vals.printing_category_id or vals.color:
                type = self.env['printing.details'].sudo().search(
                    [('printing_type_id', '=', vals._origin.printing_type_id.id),
                     ('printing_side_type_id', '=', vals._origin.printing_side_type_id.id),
                     ('printing_category_id', '=', vals._origin.printing_category_id.id), ('color', '=', vals.color),
                     ('id', '!=', vals._origin.id)])
                if type:
                    raise ValidationError("Same combination already exists.")
