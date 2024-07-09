# -*- coding: utf-8 -*-
from odoo import models, api, _
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
import dateutil.relativedelta


class CustomProductReport(models.AbstractModel):
    _name = "report.hak_product_catalog.report_product_catalog"

    def _get_report_values(self, docids, data=None):
        print("_get_report_values", data)
        partner = False
        crm = False
        product_domain = []
        product_category_ids = False
        if data['view_type'] == 'crm':
            if data['product_category_ids']:
                product_domain += [('categ_id', 'in', data['product_category_ids'])]
            else:
                product_category_ids = self.env['product.category'].search(
                    [('personalization_applicable', '=', True), ('type', '=', 'normal')])
                print("product_category_ids", product_category_ids)
                product_domain += [('categ_id', 'in', product_category_ids.ids)]
        else:
            product_domain += [('id', 'in', data['products_list'])]

        print("product_domain", product_domain)

        if data['price_range']:
            if data['price_range'] == 'greater':
                product_domain += [('list_price', '>', data['value'])]
            elif data['price_range'] == 'lesser':
                product_domain += [('list_price', '<', data['value'])]
            else:
                product_domain += [('list_price', '<', data['ending_price']),
                                   ('list_price', '>', data['starting_price'])]

        if data['product_type'] == 'template':
            print("data['stock_range']", data['stock_range'])
            if data['pdt_with_qty']:
                product_domain += [('free_qty', '>', 0)]
            if data['stock_range']:
                if data['stock_range'] == 'greater':
                    print("111111111111111")
                    product_domain += [('free_qty', '>', data['stock_qty'])]
                elif data['stock_range'] == 'lesser':
                    print("222222222222222222")
                    product_domain += [('free_qty', '<', data['stock_qty'])]
                else:
                    print("333333333333333333")
                    product_domain += [('free_qty', '<', data['ending_qty']),
                                       ('free_qty', '>', data['starting_qty'])]

        if data['product_type'] == 'variant':
            print("data['stock_range']", data['stock_range'])
            if data['pdt_with_qty']:
                product_domain += [('qty_available', '>', 0)]
            if data['stock_range']:
                if data['stock_range'] == 'greater':
                    print("111111111111111")
                    product_domain += [('qty_available', '>', data['stock_qty'])]
                elif data['stock_range'] == 'lesser':
                    print("222222222222222222")
                    product_domain += [('qty_available', '<', data['stock_qty'])]
                else:
                    print("333333333333333333")
                    product_domain += [('qty_available', '<', data['ending_qty']),
                                       ('qty_available', '>', data['starting_qty'])]

        print("product_domain 33333333333", product_domain)
        products = False
        if data['product_type'] == 'template':
            products = self.env['product.template'].search(product_domain)
        if data['product_type'] == 'variant':
            products = self.env['product.product'].search(product_domain)

        print("products", products)
        if data['partner_id']:
            partner = self.env['res.partner'].browse(int(data['partner_id']))
        if data['crm_id']:
            crm = self.env['crm.lead'].browse(int(data['crm_id']))
        print("products", products)
        # hhh
        product_dict = {}
        product_list = []
        if products:
            for product in products:
                attribute_list = []
                color_attribute_list = []
                package_list = []
                if data['product_type'] == 'template':
                    if product.attribute_line_ids:
                        for attribute in product.attribute_line_ids:
                            if attribute.attribute_id.display_type == 'color':
                                print("if attribute.displaye_type == 'color':")
                                if attribute.value_ids:
                                    color_list = []
                                    for value in attribute.value_ids:
                                        color_list.append(value.html_color)
                                    print("color_list", color_list)
                                    color_attribute_list = [color_list[i:i + 5] for i in range(0, len(color_list), 5)]
                            else:
                                if attribute.value_ids:
                                    my_list = []
                                    for value in attribute.value_ids:
                                        my_list.append(value.name)
                                    delimiter = ', '
                                    my_string = delimiter.join(my_list)
                                    print(my_string)
                                joint_string = attribute.attribute_id.name + ":" + my_string
                                print("joint_string", joint_string)
                                attribute_list.append(joint_string)

                    print("attribute_list, ", attribute_list)
                    print("color_attribute_list, ", color_attribute_list)
                    # hhh
                    print("product$$$$$$$$$$$$$$$$$$", product)
                    print("product.packaging_ids", product.packaging_ids)

                    if product.attribute_line_ids:
                        products = self.env['product.product'].search([('product_tmpl_id', '=', product.id)])
                        print("products products products", products)
                        for pdt in products:
                            print("pdt.packaging_ids", pdt.packaging_ids)
                            if pdt.packaging_ids:
                                print("***********8888888888888888888888888")
                                for package in pdt.packaging_ids:
                                    package_data = {
                                        'name': package.name,
                                        'qty': package.qty,
                                        'uom': package.product_uom_id.name,
                                        'weight': package.package_type_id.base_weight,
                                        'size': str(package.package_type_id.packaging_length) + "*" + str(
                                            package.package_type_id.width) + "*" + str(package.package_type_id.height),
                                    }
                                    print("package_data", package_data)
                                    package_list.append(package_data)
                    else:
                        if product.packaging_ids:
                            print("***********99999999999999999")
                            for package in product.packaging_ids:
                                package_data = {
                                    'name': package.name,
                                    'qty': package.qty,
                                    'uom': package.product_uom_id.name,
                                    'weight': package.package_type_id.base_weight,
                                    'size': str(package.package_type_id.packaging_length) + "*" + str(
                                        package.package_type_id.width) + "*" + str(package.package_type_id.height),
                                }
                                print("package_data", package_data)
                                package_list.append(package_data)

                    print("package_list, ", package_list)
                    print("product temp product.hs_code", product, product.hs_code)

                    product_dict = {
                        'family_code': product.family_code_ext,
                        'hs_code': product.hs_code,
                        'origin': product.country_of_origin.name,
                        'spec': product.specs,
                        'name': product.name,
                        'uom': product.uom_id.name,
                        'image': product.image_512 if product.image_512 else False,
                        'varients': attribute_list,
                        'colors_list': color_attribute_list,
                        'packages': package_list,
                        'price': product.list_price,
                        'qty': product.free_qty,
                    }
                    # print("product_dict", product_dict)
                if data['product_type'] == 'variant':
                    package_list = []
                    if product.packaging_ids:
                        for package in product.packaging_ids:
                            package_data = {
                                'name': package.name,
                                'qty': package.qty,
                                'uom': package.product_uom_id.name,
                                'weight': package.package_type_id.base_weight,
                                'size': str(package.package_type_id.packaging_length) + "*" + str(
                                    package.package_type_id.width) + "*" + str(package.package_type_id.height),
                            }
                            print("package_data", package_data)
                            package_list.append(package_data)

                    print("package_list, ", package_list)
                    product_dict = {
                        'family_code': product.default_code,
                        'name': product.name,
                        'hs_code': product.hs_code,
                        'origin': product.country_of_origin.name,
                        'spec': product.specs,
                        'uom': product.uom_id.name,
                        'image': product.image_128 if product.image_128 else False,
                        'varients': attribute_list,
                        'colors_list': color_attribute_list,
                        'packages': package_list,
                        'price': product.list_price,
                        'qty': product.free_qty,
                    }
                    # print("product_dict", product_dict)
                product_list.append(product_dict)
        # print("product_list", len(product_list), product_list)
        pair_list = []
        tota_pair_list = []
        if product_list:
            pair = 1
            last_index = len(product_list) - 1
            print("last_index", last_index)
            for i_product in product_list:

                pair_list.append(i_product)
                pair = pair + 1
                index = product_list.index(i_product)
                print("index", index)
                if pair > 2:
                    tota_pair_list.append(pair_list)
                    pair_list = []
                    pair = 1
                if index == last_index:
                    tota_pair_list.append(pair_list)
            print("pair_list", pair_list)
        # mmm
        # print("tota_pair_list", len(tota_pair_list), tota_pair_list)

        # nnn

        other_details = ({

            'show_price': data['show_price'],
            'show_stock': data['show_stock'],
            'products': tota_pair_list,
            'partner': partner if partner else False,
        })
        if crm:
            msg = _("Dynamic catalog has been downloaded on  by %s", self.env.user.name)
            crm.message_post(body=msg)
        return {
            'other': other_details,
        }
