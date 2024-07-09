# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Vishnu P(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
""" Purchase Requisition model"""
from odoo import models, fields, api, _
from lxml import etree, html
import json
from odoo.exceptions import UserError


class PurchaseRequisition(models.Model):
    """ Model for storing purchase requisition """
    _name = 'employee.purchase.requisition'
    _description = 'Purchase Requisition'
    _inherit = "mail.thread", "mail.activity.mixin"
    _order = 'id desc'

    name = fields.Char(string="Reference No", readonly=True, copy=False)
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  help='Employee', default=lambda self: self.env.user.sudo().employee_id)
    dept_id = fields.Many2one('hr.department', string='Department', help='Department')
    user_id = fields.Many2one('res.users', string='Requisition Responsible',
                              required=True, readonly=True,
                              help='Requisition responsible user', default=lambda self: self.env.user)
    requisition_date = fields.Date(string="Requisition Date",
                                   default=lambda self: fields.Date.today(),
                                   help='Date of Requisition', readonly=True)
    receive_date = fields.Date(string="Received Date", readonly=True,
                               help='Receive Date')
    requisition_deadline = fields.Date(string="Requisition Deadline",
                                       help="End date of Purchase requisition", required=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company,
                                 help='Company')
    requisition_order_ids = fields.One2many('requisition.order',
                                            'requisition_product_id',
                                            required=True, copy=True)
    confirm_id = fields.Many2one('res.users', string='Confirmed By',
                                 default=lambda self: self.env.uid,
                                 readonly=True,
                                 help='User who Confirmed the requisition.')
    manager_id = fields.Many2one('res.users', string='Department Manager',
                                 readonly=True, help='Department Manager')
    requisition_head_id = fields.Many2one('res.users', string='Approved By',
                                          readonly=True,
                                          help='User who approved the requisition.')
    rejected_user_id = fields.Many2one('res.users', string='Rejected By',
                                       readonly=True,
                                       help='user who rejected the requisition')
    confirmed_date = fields.Date(string='Confirmed Date', readonly=True,
                                 help='Date of Requisition Confirmation')
    department_approval_date = fields.Date(string='Department Approval Date',
                                           readonly=True,
                                           help='Department Approval Date')
    approval_date = fields.Date(string='Approved Date', readonly=True,
                                help='Requisition Approval Date')
    reject_date = fields.Date(string='Rejection Date', readonly=True,
                              help='Requisition Rejected Date')
    source_location_id = fields.Many2one('stock.location',
                                         string='Source Location',
                                         help='Source location of requisition.')
    destination_location_id = fields.Many2one('stock.location',
                                              string="Destination Location",
                                              help='Destination location of requisition.',
                                              compute='_compute_destination_location_id'
                                              )
    delivery_type_id = fields.Many2one('stock.picking.type',
                                       string='Delivery To',
                                       help='Type of Delivery.')
    internal_picking_id = fields.Many2one('stock.picking.type',
                                          string="Internal Picking")
    requisition_description = fields.Text(string="Reason For Requisition")
    purchase_count = fields.Integer(string='Purchase Count',
                                    help='Purchase Count',
                                    compute='_compute_purchase_count')
    internal_transfer_count = fields.Integer(string='Internal Transfer count',
                                             help='Internal Transfer count',
                                             compute='_compute_internal_transfer_count')
    state = fields.Selection(
        [('new', 'New'),
         ('waiting_department_approval', 'Waiting Department Approval'),
         ('under_review', 'Under Review'),
         ('approved', 'Approved'),
         ('purchase_order_created', 'Purchase/Picking Created'),
         ('received', 'Received'),
         ('cancelled', 'Cancelled'),
         ('rejected', 'Rejected')],
        default='new', copy=False, tracking=True)

    is_colleague_dep = fields.Boolean(string='Is Colleague/Dept', compute='_compute_is_colleague_dep', copy=False)
    request_for = fields.Selection([('self', 'Self'), ('colleague', 'Colleague'), ('department', 'Department')],
                                   default='self')

    is_user_readonly = fields.Boolean(string='Is User Readonly', compute='_compute_is_user_editable')
    # cancel_reason_ids = fields.One2many('mr.cancel.reason', 'requisition_product_id')
    # cancel_reason_count = fields.Integer(string='Cancel Count', compute='_compute_cancel_count')
    cancel_reason = fields.Char(string='Cancel Reason')

    @api.depends('request_for', 'employee_id', 'dept_id')
    def _compute_destination_location_id(self):
        for rec in self:
            if rec.sudo().employee_id and rec.sudo().employee_id.employee_location_id:
                rec.destination_location_id = rec.sudo().employee_id.employee_location_id.id
            elif rec.dept_id and rec.dept_id.department_location_id:
                rec.destination_location_id = rec.dept_id.department_location_id.id
            else:
                rec.destination_location_id = False

    @api.depends('cancel_reason_ids')
    def _compute_cancel_count(self):
        for rec in self:
            rec.cancel_reason_count = len(rec.cancel_reason_ids)

    @api.depends('user_id')
    def _compute_is_user_editable(self):
        for rec in self:
            if rec.state in ('cancelled', 'rejected'):
                rec.is_user_readonly = True
            elif rec.state != 'new' and not self.env.user.has_group(
                    'employee_purchase_requisition.employee_requisition_head') and not self.env.user.has_group(
                'employee_purchase_requisition.employee_requisition_manager'):
                rec.is_user_readonly = True
            else:
                rec.is_user_readonly = False

    @api.depends('employee_id')
    def _compute_is_colleague_dep(self):
        print("_compute_is_colleague_dep___", self.user_has_groups(
            'employee_purchase_requisition.employee_requisition_head') or self.user_has_groups(
            'employee_purchase_requisition.employee_requisition_manager'))
        for rec in self:
            if self.user_has_groups(
                    'employee_purchase_requisition.employee_requisition_head') or self.user_has_groups(
                'employee_purchase_requisition.employee_requisition_manager'):
                rec.is_colleague_dep = True
            else:
                rec.is_colleague_dep = False

    def action_cancel(self):
        self.state = 'cancelled'

    def action_reset_to_draft(self):
        self.state = 'new'

    @api.onchange('request_for')
    def onchange_request_for(self):
        if self.request_for == 'self':
            self.employee_id = self.env.user.sudo().employee_id.id
        elif self.request_for == 'department':
            self.employee_id = False

        return {'domain': {'employee_id': [('department_id', '=', self.env.user.sudo().employee_id.department_id.id)]}}

    @api.onchange('employee_id', 'request_for')
    def onchange_employee_id(self):
        if self.employee_id:
            self.dept_id = self.employee_id.department_id.id
        else:
            self.dept_id = False

    @api.model
    def create(self, vals):
        """generate purchase requisition sequence"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'employee.purchase.requisition') or 'New'
        result = super(PurchaseRequisition, self).create(vals)
        return result

    def action_confirm_requisition(self):
        """confirm purchase requisition"""
        if not self.requisition_order_ids:
            raise UserError(_("Requisition Orders should not be empty"))
        self.source_location_id = self.sudo().employee_id.department_id.department_location_id.id
        # self.destination_location_id = self.sudo().employee_id.employee_location_id.id
        self.delivery_type_id = self.source_location_id.warehouse_id.in_type_id.id
        self.internal_picking_id = self.source_location_id.warehouse_id.int_type_id.id
        self.write({'state': 'waiting_department_approval'})
        self.confirm_id = self.env.uid
        self.confirmed_date = fields.Date.today()

    def action_department_approval(self):
        """approval from department"""
        if not self.requisition_order_ids:
            raise UserError(_("Requisition Orders should not be empty"))
        # self.write({'state': 'waiting_head_approval'})
        self.write({'state': 'under_review'})
        self.manager_id = self.env.uid
        self.department_approval_date = fields.Date.today()

    def action_department_cancel(self):
        """cancellation from department """
        # self.write({'state': 'rejected'})
        # self.rejected_user_id = self.env.uid
        # self.reject_date = fields.Date.today()

        return {
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_model': 'mr.rejection.wizard',
            'name': _("MR Rejection Wizard"),
            # 'res_id': w.id,
            'views': [(False, 'form')],
            'context': self.env.context,
        }

    def action_review_approval(self):
        """approval from Reviewer"""
        if not self.requisition_order_ids:
            raise UserError(_("Requisition Orders should not be empty"))
        self.write({'state': 'approved'})
        self.requisition_head_id = self.env.uid
        self.approval_date = fields.Date.today()

    def action_head_cancel(self):
        """cancellation from department head"""
        self.write({'state': 'rejected'})
        self.rejected_user_id = self.env.uid
        self.reject_date = fields.Date.today()

    def action_create_purchase_order(self):
        """create purchase order and internal transfer"""
        if not self.internal_picking_id:
            raise UserError(_("Fill up the Internal Picking inside the Picking Details"))
        source_location_empty = self.requisition_order_ids.filtered(
            lambda x: x.requisition_type == 'internal_transfer' and not x.source_location_id)
        if source_location_empty:
            raise UserError(_("Fill up the Source Location for the Internal Transfers"))
        if not self.destination_location_id:
            raise UserError(_("Configure Destination Location inside the Employee or the Department"))
        for rec in self.requisition_order_ids:
            if rec.requisition_type == 'internal_transfer':
                self.env['stock.picking'].create({
                    'location_id': rec.source_location_id.id if rec.source_location_id else self.source_location_id.id,
                    'location_dest_id': self.destination_location_id.id,
                    'picking_type_id': self.internal_picking_id.id,
                    # 'picking_type_id': self.source_location_id.warehouse_id.int_type_id.id,
                    'requisition_order': self.name,
                    'requisition_product_id': self.id,
                    'move_ids_without_package': [(0, 0, {
                        'name': rec.product_id.name,
                        'product_id': rec.product_id.id,
                        'product_uom': rec.product_id.uom_id.id,
                        'product_uom_qty': rec.quantity,
                        'location_id': rec.source_location_id.id if rec.source_location_id else self.source_location_id.id,
                        'location_dest_id': self.destination_location_id.id,
                    })]
                })
            else:
                purchase_order = self.env['purchase.order']
                print("rec.partner_ids___", rec.partner_ids)
                if not rec.partner_ids:
                    raise UserError(_("Fill up Requisition Type / Vendors in Requisition lines"))
                for partner_id in rec.partner_ids:
                    dummy_product_id = self.env['product.product'].search([('barcode', '=', '000000000000000')])
                    exist_po_order = self.env['purchase.order'].search(
                        [('requisition_product_id', '=', self.id), ('partner_id', '=', partner_id.id),
                         ('state', '=', 'draft')])
                    if not exist_po_order:
                        po_id = self.env['purchase.order'].create({
                            'partner_id': partner_id.id,
                            'requisition_order': self.name,
                            'requisition_product_id': self.id,
                            "order_line": [(0, 0, {
                                'product_id': rec.product_id.id if rec.product_id else dummy_product_id.id,
                                'name': rec.description,
                                'product_qty': rec.quantity,
                            })]})
                        if len(rec.partner_ids) > 1:
                            purchase_order += po_id
                    else:
                        exist_po_order.order_line = [(0, 0, {
                            'product_id': rec.product_id.id if rec.product_id else dummy_product_id.id,
                            'name': rec.description,
                            'product_qty': rec.quantity,
                        })]
                # for po_id in purchase_order:
                #     po_ids = purchase_order.filtered(lambda po: po.id != po_id.id)
                #     print("po_ids___", po_id, po_ids)
                #     # po_id.alternative_po_ids = [(6, 0, po_ids.ids)]
                #     po_id.alternative_po_ids = [(4, po_ids.ids)]
                #     print("po_id.alternative_po_ids", po_id.alternative_po_ids)
                #     # self.write({'state': 'purchase_order_created'})
                print("purchase_order__", purchase_order)
                purchase_order.alternative_po_ids = [(6, 0, purchase_order.ids)]
        self.state = 'purchase_order_created'

    def _compute_internal_transfer_count(self):
        # self.internal_active = 0
        # self.internal_transfer_count = self.env['stock.picking'].search_count([
        #     ('requisition_order', '=', self.name)])
        for rec in self:
            rec.internal_transfer_count = self.sudo().env['stock.picking'].search_count([
                ('requisition_product_id', '=', rec.id)])

    def _compute_purchase_count(self):
        self.purchase_count = self.sudo().env['purchase.order'].search_count([
            ('requisition_order', '=', self.name)])

    def action_receive(self):
        """receive purchase requisition"""
        self.write({'state': 'received'})
        self.receive_date = fields.Date.today()

    def get_purchase_order(self):
        """purchase order smart button view"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Order',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('requisition_order', '=', self.name)],
        }

    def get_internal_transfer(self):
        """internal transfer smart tab view"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Internal Transfers',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            # 'domain': [('requisition_order', '=', self.name)],
            'domain': [('requisition_product_id', '=', self.id)],
        }

    def action_print_report(self):
        """print purchase requisition report"""
        data = {
            'employee': self.sudo().employee_id.name,
            'records': self.read(),
            'order_ids': self.requisition_order_ids.read(),
        }
        return self.env.ref(
            'employee_purchase_requisition.action_report_purchase_requisition').report_action(
            self, data=data)

    def unlink(self):
        for rec in self:
            if rec.state not in ('new', 'waiting_department_approval'):
                raise UserError(_("You can't delete in this state"))
        return super().unlink()

    # @api.model
    # def get_viewsX(self, views, options=None):
    #     res = super().get_views(views, options)
    #     views_types = ['list', 'form']
    #     for view_type in views_types:
    #         arch = res['views'].get(view_type, {}).get('arch')
    #         if view_type == 'list':
    #             view_type = 'tree'
    #         if arch:
    #             print("USER___", self.user_has_groups(
    #                     'employee_purchase_requisition.employee_requisition_user'))
    #             if self.user_has_groups(
    #                     'employee_purchase_requisition.employee_requisition_user'):
    #                 print("employee_requisition_user")
    #                 tree = etree.fromstring(arch)
    #                 # for node in tree.xpath('//' + view_type):
    #                 for node in tree.xpath('//field[@name="employee_id"]'):
    #                     node.set('readonly', '1')
    #                     node.set('create', '0')
    #                     node.set('edit', '0')
    #                     node.set('delete', '0')
    #                 arch = etree.tostring(tree, encoding='unicode')
    #                 if view_type == 'tree':
    #                     view_type = 'list'
    #             res['views'].setdefault(view_type, {})['arch'] = arch
    #     return res
    #
    # @api.model
    # def get_views(self, views, options=None):
    #     res = super().get_views(views, options)
    #     print("res___", res)
    #     views_types = ['list', 'form']
    #     for view_type in views_types:
    #         if view_type == 'form':
    #             if self.user_has_groups(
    #                     'employee_purchase_requisition.employee_requisition_user'):
    #                 print("GROUP", self.user_has_groups(
    #                     'employee_purchase_requisition.employee_requisition_user'))
    #                 doc = etree.XML(res['views'].get(view_type, {}).get('arch'))
    #                 for node in doc.xpath("//field[@name='employee_id']"):
    #                     node.set("readonly", "1")
    #                     modifiers = json.loads(node.get("modifiers"))
    #                     modifiers['readonly'] = True
    #                     node.set("modifiers", json.dumps(modifiers))
    #                 res['arch'] = etree.tostring(doc)
    #     return res


class RequisitionProducts(models.Model):
    _name = 'requisition.order'
    _description = 'Requisition order'

    requisition_product_id = fields.Many2one(
        'employee.purchase.requisition', help='Requisition product.')
    state = fields.Selection(string='State',
                             related='requisition_product_id.state')
    requisition_type = fields.Selection(
        string='Requisition Type',
        selection=[
            ('purchase_order', 'Purchase Order'),
            ('internal_transfer', 'Internal Transfer'),
        ], help='type of requisition')
    product_id = fields.Many2one('product.product', help='Product')
    description = fields.Text(
        string="Description",
        # compute='_compute_name',
        store=True, readonly=False,
        precompute=True, help='Product Description')
    quantity = fields.Integer(string='Quantity', help='Quantity')
    product_qty_available = fields.Float(string='Available Qty', compute='_compute_qty_available',
                                         digits='Product Unit of Measure')
    uom = fields.Char(related='product_id.uom_id.name',
                      string='Unit of Measure', help='Product Uom')
    # partner_id = fields.Many2one('res.partner', string='Vendor',
    #                              help='Vendor for the requisition')
    partner_ids = fields.Many2many('res.partner', string='Vendors',
                                   help='Vendor for the requisition')
    source_location_id = fields.Many2one('stock.location', string='Source Location',
                                         # domain=[('is_material_requisition', '=', True)]
                                         domain=[('usage', '=', 'internal')]
                                         )

    @api.depends('product_id')
    def _compute_qty_available(self):
        for line in self:
            if line.product_id:
                company = self.env.company
                warehouses = self.env['stock.warehouse'].search([('company_id', '=', company.id)])
                total_qty = 0
                for warehouse in warehouses:
                    total_qty = total_qty + line.product_id.with_context(warehouse=warehouse.id).free_qty
                line.product_qty_available = total_qty
            else:
                line.product_qty_available = 0

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.description:
            product_lang = self.product_id.with_context(
                lang=self.requisition_product_id.sudo().employee_id.lang)
            self.description = product_lang.get_product_multiline_description_sale()

    @api.depends('product_id')
    def _compute_name(self):
        """compute product description"""
        for option in self:
            if not option.product_id:
                continue
            product_lang = option.product_id.with_context(
                lang=self.requisition_product_id.sudo().employee_id.lang)
            option.description = product_lang.get_product_multiline_description_sale()

    @api.onchange('requisition_type')
    def _onchange_product(self):
        """fetching product vendors"""
        vendors_list = []
        for data in self.product_id.seller_ids:
            vendors_list.append(data.partner_id.id)
        return {'domain': {'partner_id': [('id', 'in', vendors_list)]}}

    def unlink(self):
        for rec in self:
            if rec.state not in ('new', 'waiting_department_approval'):
                raise UserError(_("You can't delete in this state"))
        return super().unlink()

# class MrCancelReason(models.Model):
#     _name = 'mr.cancel.reason'
#
#     requisition_product_id = fields.Many2one(
#         'employee.purchase.requisition', help='Requisition product')
#     cancel_reason = fields.Char(string='Cancel Reason')
