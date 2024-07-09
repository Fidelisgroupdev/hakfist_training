from odoo import models, fields, api, _
from lxml import etree
from odoo.exceptions import UserError


class Location(models.Model):
    _inherit = 'stock.location'

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        views_types = ['list', 'form']
        for view_type in views_types:
            arch = res['views'].get(view_type, {}).get('arch')
            if view_type == 'list':
                view_type = 'tree'
            if arch:
                if not self.user_has_groups(
                        'jsa_warehouse_access_control.group_warehouse_access'):
                    tree = etree.fromstring(arch)
                    for node in tree.xpath('//' + view_type):
                        node.set('create', '0')
                        node.set('edit', '0')
                        node.set('delete', '0')
                    arch = etree.tostring(tree, encoding='unicode')
                    if view_type == 'tree':
                        view_type = 'list'
                res['views'].setdefault(view_type, {})['arch'] = arch
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if not self.user_has_groups(
                'jsa_warehouse_access_control.group_warehouse_access'):
            raise UserError(_('Only Warehouse Super User can Create/Edit Location'))
        return res

    def write(self, values):
        res = super().write(values)
        if not self.user_has_groups(
                'jsa_warehouse_access_control.group_warehouse_access'):
            raise UserError(_('Only Warehouse Super User can Create/Edit Location'))
        return res


