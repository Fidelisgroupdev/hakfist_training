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
""" add field requisition_order in purchase order"""
from odoo import models, fields


class PurchaseOrder(models.Model):
    """ inherit purchase.order model """

    _inherit = 'purchase.order'

    requisition_order = fields.Char(string='Requisition Order',
                                    help='Requisition Order')
    # product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
    #                              change_default=True, index=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 change_default=True, index='btree_not_null')
    requisition_product_id = fields.Many2one(
        'employee.purchase.requisition', help='Requisition product.')

    def button_confirm(self):
        res = super().button_confirm()
        # self.picking_ids.requisition_product_id = self.requisition_product_id.id
        for picking_id in self.picking_ids:
            if self.requisition_product_id:
                new_picking_id = picking_id.copy({
                    'location_id': picking_id.location_dest_id.id,
                    'location_dest_id': self.requisition_product_id.destination_location_id.id,
                    'related_picking_id': picking_id.id,
                    'requisition_product_id': self.requisition_product_id.id
                })
                new_picking_id.action_confirm()
                new_picking_id.state = 'waiting'
        return res

