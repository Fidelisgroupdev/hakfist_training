import logging
from datetime import datetime
from odoo import http
from odoo.http import request, route
import unicodedata

_logger = logging.getLogger(__name__)


class ProductConfiguratorController(http.Controller):
    @http.route(['/hak_product_configurator/configure'], type='json', auth="user", methods=['POST'])
    def configure(self, product_template_id, pricelist_id, mode, **kw):
        print("dffffffffffffffffff")
        add_qty = float(kw.get('add_qty', 1))
        product_template = request.env['product.template'].browse(int(product_template_id))
        if mode == 'edit' and product_template.hak_master_product_id:

            product_template = product_template.hak_master_product_id.product_tmpl_id

            pricelist = self._get_pricelist(pricelist_id)

            product_combination = False
            attribute_value_ids = set(kw.get('product_template_attribute_value_ids', []))
            attribute_value_ids |= set(kw.get('product_no_variant_attribute_value_ids', []))
            if attribute_value_ids:
                product_combination = request.env['product.template.attribute.value'].browse(
                    attribute_value_ids
                ).filtered(
                    lambda ptav: ptav.product_tmpl_id == product_template
                )  # Filter out ptavs not belonging to the given template
                # It happens when you change the template on an already configured line
                # receiving the configured attributes data from the previous template configuration.

            if pricelist:
                product_template = product_template.with_context(pricelist=pricelist.id,
                                                                 partner=request.env.user.partner_id)

            return request.env['ir.ui.view']._render_template(
                "hak_product_configurator.configure",
                {
                    'product': product_template,
                    'pricelist': pricelist,
                    'add_qty': add_qty,
                    'product_combination': product_combination
                },
            )
        else:

            product_template = request.env['product.template'].browse(int(product_template_id))
            pricelist = self._get_pricelist(pricelist_id)

            product_combination = False
            attribute_value_ids = set(kw.get('product_template_attribute_value_ids', []))
            attribute_value_ids |= set(kw.get('product_no_variant_attribute_value_ids', []))
            if attribute_value_ids:
                product_combination = request.env['product.template.attribute.value'].browse(
                    attribute_value_ids
                ).filtered(
                    lambda ptav: ptav.product_tmpl_id == product_template
                )  # Filter out ptavs not belonging to the given template
                # It happens when you change the template on an already configured line
                # receiving the configured attributes data from the previous template configuration.

            if pricelist:
                product_template = product_template.with_context(pricelist=pricelist.id,
                                                                 partner=request.env.user.partner_id)

            return request.env['ir.ui.view']._render_template(
                "hak_product_configurator.configure",
                {
                    'product': product_template,
                    'pricelist': pricelist,
                    'add_qty': add_qty,
                    'product_combination': product_combination
                },
            )

    @http.route(['/hak_product_configurator/limit_variants_selection'], type='json', auth="user", methods=['POST'])
    def action_limit_variants_selections(self, product_id, combination):
        print("dkfzdzczx", product_id, combination)
        prod_temp = request.env['product.template'].search([('id', '=', int(product_id))])

        prod_temp_attr_val = request.env['product.template.attribute.value'].search(
            [('product_tmpl_id', '=', int(product_id))])
        print("prod_temp_attr_val", prod_temp_attr_val)
        side_lines = request.env['printing.side.line'].search([('product_temp_id', '=', int(product_id))])
        var_line = []
        if side_lines:
            limit_lines = side_lines.filtered(lambda x: x.limit_variants == True)
            if limit_lines:
                for rec in limit_lines:
                    for items in rec.attribute_value_ids:

                        check2 = request.env['product.template.attribute.value'].search(
                            [('product_tmpl_id', '=', int(product_id)),
                             ('attribute_id', '=', int(items.attribute_id.id)), ('name', '=', items.name)])
                        # prod_temp.attribute_line_ids.filtered(lambda x:x.attribute_id.id == items.attribute_id.id).filtered(lambda y:y.name == prod_temp_attr_val.name))
                        print("sdjasjsdsd", check2, check2.id in combination)
                        if check2.id in combination:
                            var_line.append(rec.id)

        print("sadhsajhdkahsdiuwerrer", var_line)
        return var_line

    @http.route(['/hak_product_configurator/limit_variants'], type='json', auth="user", methods=['POST'])
    def action_limit_variants(self, product_id, attribute, attribute_val):
        print("slkdjsa", product_id, attribute, attribute_val)
        side_lines = request.env['printing.side.line'].search([('product_temp_id', '=', int(product_id))])
        prod_temp = request.env['product.template'].search([('id', '=', int(product_id))])
        prod_temp_attr_val = request.env['product.template.attribute.value'].search([('id', '=', int(attribute_val))])
        vals_list = []
        if side_lines:
            limit_lines = side_lines.filtered(lambda x: x.limit_variants == True)
            if limit_lines:
                print("dd", limit_lines)
                for rec in limit_lines:
                    for items in rec.attribute_value_ids:
                        print("skdku879832", items, items.attribute_id, items.name)

                        check1 = prod_temp.attribute_line_ids.filtered(
                            lambda x: x.attribute_id.id == items.attribute_id.id).value_ids.filtered(
                            lambda y: y.name == prod_temp_attr_val.name)
                        check2 = request.env['product.template.attribute.value'].search(
                            [('product_tmpl_id', '=', int(product_id)),
                             ('attribute_id', '=', int(items.attribute_id.id)), ('name', '=', items.name)])
                        # prod_temp.attribute_line_ids.filtered(lambda x:x.attribute_id.id == items.attribute_id.id).filtered(lambda y:y.name == prod_temp_attr_val.name))
                        vals = {}
                        print("fkljdkf", items, items.name, attribute_val, check1, check2)

                        vals['side_line_id'] = rec.id
                        vals['side_line_name'] = rec.name
                        vals['visible'] = False

                        vals['attribute'] = items.attribute_id.id
                        vals['value'] = check2.id
                        vals['value_name'] = items.name
                        print("check2", check2)
                        print("attribute_val", attribute_val)
                        if check2.id == int(attribute_val):
                            print("if check2.id == int(attribute_val):")
                            vals['visible'] = True
                            # vals['value_name'] = items.name
                            # vals['side_line_id'] = rec.id
                            # vals['side_line_name'] = rec.name

                        vals_list.append(vals)
                        print("skjdlkasdffff", vals_list)
        print("skjdlkasd", vals_list)
        return vals_list

    @http.route(['/hak_product_configurator/map_logo'], type='json', auth="user", methods=['POST'])
    def map_logo_product(self, file, product_id, **kw):
        product_tmpl_id = request.env['product.template'].browse(int(product_id))

        article = file
        article_1 = unicodedata.normalize('NFKD', '/' + article.lstrip('data:image/png;base64,')).encode('ascii',
                                                                                                         'ignore')
        product_tmpl_id.sudo().write({
            'logo': file.replace('data:image/png;base64,', ''),

        })

    @http.route(['/hak_product_configurator/map_personal_logo'], type='json', auth="user", methods=['POST'])
    def map_personal_logo(self, logos_detail, product_id, partner, crm, header_logo=False, **kw):
        print("def map_personal_logo", crm)
        print("skjdkjshfsd", partner, logos_detail, product_id)
        product_tmpl_id = request.env['product.template'].browse(int(product_id))
        new_vals = product_tmpl_id.personalisation_details
        print("kjjgdfg", new_vals)
        # new_vals['printing_details'] = logos_detail
        head_main_logo = request.env['partner.logo'].search([('id', '=', int(header_logo))])

        print("ldkfld")
        for rec in logos_detail:
            print("dskjfnskjdnfs8ui98787", rec, type(rec))
            if rec.get('print_type_checked'):
                # print("lkjjgjgjhghjvkdx", rec)
                # if not rec.get('spcl_logo'):
                #     print("xcvlkmffhgfxclkvmxcv")
                #     rec.update({
                #         'spcl_header_logo':head_main_logo.logo,
                #     })
                # print("lkdlkfjsf", rec)
                article = rec.get('spcl_logo')
                if article:
                    # article_1 = unicodedata.normalize('NFKD', '/' + article.lstrip('data:image/png;base64,')).encode('ascii',
                    #                                                                                              'ignore')
                    # product_tmpl_id.write({
                    #     'logo': file.replace('data:image/png;base64,', ''),
                    #
                    # })

                    attachment = request.env['ir.attachment'].sudo().create({
                        'name': "Personalized for" + rec.get('print_attr_name'),
                        'type': 'binary',
                        'datas': article.replace('data:image/png;base64,',
                                                 '') if 'data:image/png;base64,' in article else article.replace(
                            'data:application/pdf;base64,', ''),
                        'res_model': 'crm.lead',
                        'res_id': crm,
                        'mimetype': 'application/x-pdf' if 'data:application/pdf;base64,' in article else 'image/png'
                    })

                    folder_owner = request.env.ref('hak_product_configurator.attachment_workspace_for_personalisation')

                    request.env['documents.document'].sudo().create({
                        'name': "Personalized for" + rec.get('print_attr_name'),
                        'folder_id': folder_owner.id,
                        'attachment_id': attachment.id,
                        'datas': article.replace('data:image/png;base64,',
                                                 '') if 'data:image/png;base64,' in article else article.replace(
                            'data:application/pdf;base64,', ''),
                    })

                    request.env["partner.logo"].sudo().create({
                        'name': "Personalized for" + rec.get('print_attr_name'),
                        'partner_id': partner,
                        'logo': article.replace('data:image/png;base64,',
                                                '') if 'data:image/png;base64,' in article else article.replace(
                            'data:application/pdf;base64,', ''),
                        'product_id': product_tmpl_id.id,
                        'details': new_vals,
                        'crm_id': crm,

                    })
                # if rec.get('main_header_logo'):
                #     # article_1 = unicodedata.normalize('NFKD', '/' + article.lstrip('data:image/png;base64,')).encode('ascii',
                #     #                                                                                              'ignore')
                #     # product_tmpl_id.write({
                #     #     'logo': file.replace('data:image/png;base64,', ''),
                #     #
                #     # })
                #
                #     attachment = request.env['ir.attachment'].sudo().create({
                #         'name': "Personalized for" + rec.get('print_attr_name'),
                #         'type': 'binary',
                #         'datas': head_main_logo.logo,
                #         'res_model': 'crm.lead',
                #         'res_id': crm,
                #         # 'mimetype': 'application/x-pdf' if 'data:application/pdf;base64,' in article else 'image/png'
                #     })
                #
                #     folder_owner = request.env.ref('hak_product_configurator.attachment_workspace_for_personalisation')
                #
                #     request.env['documents.document'].sudo().create({
                #         'name': "Personalized for" + rec.get('print_attr_name'),
                #         'folder_id': folder_owner.id,
                #         'attachment_id': attachment.id,
                #         'datas': head_main_logo.logo,
                #     })
                #
                #     request.env["partner.logo"].sudo().create({
                #         'name': "Personalized for" + rec.get('print_attr_name'),
                #         'partner_id': partner,
                #         'logo': head_main_logo.logo,
                #         'product_id': product_tmpl_id.id,
                #         'details': new_vals,
                #         'crm_id': crm,
                #
                #     })

        print("logos_detail ooooopppppppp", logos_detail)
        new_vals['printing_details'] = logos_detail
        product_tmpl_id.sudo().personalisation_details = new_vals

    @http.route(['/hak_product_configurator/check_product_customised'], type='json', auth="user", methods=['POST'])
    def cehck_product_is_already(self, product_tmpl_id):
        product_tmpl_id = request.env['product.template'].browse(int(product_tmpl_id))
        list_sides = []
        print("jhkjhjhfch yyyyiiiiiiiiii")
        if product_tmpl_id.hak_master_product_id:
            list_sides.append(product_tmpl_id.hak_master_product_id.product_tmpl_id.id)
            list_sides.append(product_tmpl_id.personalisation_details['printing_details'])
            delta = []
            for ptav in product_tmpl_id.selected_ids:
                vals = {
                    'printing_side_line_id': ptav.id,
                    'selected_width': ptav.selected_width,
                    'selected_height': ptav.selected_height,
                    'printing_side_type_id': ptav.printing_side_type_id.id,
                    'selected_color': ptav.selected_color,
                    'side_name': ptav.printing_side_line_id.name,

                }
                delta.append(vals)

            list_sides.append(delta)

            return list_sides

            # return product_tmpl_id.hak_master_product_id.product_tmpl_id.id
        else:
            return False

    @http.route(['/hak_product_configurator/create_configuration_product'], type='json', auth="user", methods=['POST'])
    def create_configuration_product(self, products_print_vals, products_side_color, product_tmpl_id,
                                     personalised_product_product, personalised_product_template, product_id, quantity,
                                     attachment, **kw):
        details = {}

        print("saaaaaaa", products_print_vals)
        print("products_side_color", products_side_color)

        details['quantity'] = quantity

        product_tmpl_id = request.env['product.template'].browse(int(product_tmpl_id))
        product_main_id = request.env['product.product'].browse(int(product_id))

        sc = 0
        pc = 0

        side_details = []

        detail_side_vals = []

        # head_main_logo = request.env['partner.logo'].search([('id', '=', int(head_logo))])
        # main_attach =
        for recw in products_print_vals:

            if recw.get('print_type_checked'):
                v1 = {}
                for col in products_side_color:
                    print("col", col)

                    if col.get('print_attr_id') == recw.get('print_attr_id'):
                        print("recw", recw)
                        print("recw.get('print_attr_name')", recw.get('print_attr_name'))
                        v1['printing_side_line_id'] = recw.get('print_attr_id')
                        v1['parent_product_id'] = product_main_id.id
                        v1['selected_width'] = col.get('width')
                        v1['selected_height'] = col.get('height')
                        v1['quantity'] = quantity
                        if recw.get('print_type_checked'):
                            v1['printing_side_type_id'] = recw.get('print_type_checked')
                            if col.get('print_side_color') and len(col.get('print_side_color')) > 0:
                                print_pass = False
                                for col_mat in col.get('print_side_color'):
                                    print("sdkjfhskjdhfuu7898we", col_mat)
                                    print("sdkjfhskjdhfuu789sdsds8we", col_mat.get('id'),
                                          recw.get('print_type_checked'))

                                    if int(col_mat.get('id')) == int(recw.get('print_type_checked')):
                                        print("dfkjsldjflsjd")
                                        v1['selected_color'] = col_mat.get('value')
                                        print_pass = True

                                    else:
                                        print("ijijijydxfgchhjk")

                                if not print_pass:
                                    v1['selected_color'] = 0
                            else:
                                v1['selected_color'] = False

                        else:
                            v1['printing_side_type_id'] = False
                            v1['selected_color'] = False
                        print("skjdkk 8898print", v1)

                        select_rec = request.env['selected.printing.side.line'].sudo().create(v1)
                        detail_side_vals.append(select_rec)

                print("lkjvkdx", recw)
                # if not rec.get('spcl_logo'):
                #     print("xcvlkmxclkvmxcv")
                #     rec.update({
                #         'spcl_logo':head_main_logo.logo,
                #     })
                #     # rec['spcl_logo'] = head_main_logo.logo

                side_details.append(recw)

                pt_sc_line = product_tmpl_id.printing_side_line_ids.filtered(
                    lambda x: x.id == int(recw.get('print_attr_id')))
                pt_sc = pt_sc_line.printing_type_ids.filtered(lambda x: x.id == int(recw.get('print_type_checked'))).sc
                pst_sc = pt_sc_line.printing_side_type_id.sc
                prd_temp_sc = product_tmpl_id.sc
                ps_sc = pt_sc_line.sc

                sc += pt_sc * pst_sc * prd_temp_sc * ps_sc

                pt_pc = pt_sc_line.printing_type_ids.filtered(lambda x: x.id == int(recw.get('print_type_checked'))).pc
                pst_pc = pt_sc_line.printing_side_type_id.pc
                prd_temp_pc = product_tmpl_id.pc
                ps_pc = pt_sc_line.pc

                pc += pt_pc * pst_pc * prd_temp_pc * ps_pc
            print("klkklka jsdnasdsadasd", recw)

        person_unit_price = round((sc + (pc * quantity)) / quantity, 2)

        product_main_id = request.env['product.product'].browse(int(product_id))
        details['main_product_id'] = product_main_id.id

        details['printing_details'] = side_details

        print("details['printing_details'] = side_details", details)

        personalized_category = product_tmpl_id.categ_id.personalized_category_id

        if personalised_product_product > 0 and personalised_product_template > 0:
            personalized_product = request.env["product.template"].sudo().search(
                [('id', '=', int(personalised_product_template))])

            personalized_product.sudo().write({
                # 'name': "Personalized" + product_tmpl_id.name,
                # 'categ_id': personalized_category.id,
                # 'detailed_type': 'product',
                'hak_master_product_id': product_main_id.id,
                # 'list_price': person_unit_price,
                'personalisation_details': details,
                # 'family_code': 'P-' + product_tmpl_id.default_code if product_tmpl_id.default_code else 'P-False',
            })

            personalized_product.sudo().selected_ids = False

            for kit in detail_side_vals:
                kit.sudo().product_temp_id = personalized_product.id

            json_det = personalized_product.personalisation_details.get('printing_details')
            descrip = str(personalized_product.name) + 'printing side:-'
            for rec in json_det:
                print("dsfkjhjdskf", rec)

                if rec.get('print_type_checked') and rec.get('print_type_checked'):
                    print("dsfkjhjdsk4444444f", rec)

                    type = request.env['printing.type'].search([('id', '=', int(rec.get('print_type_checked')))])

                    if type.max_color_label == '0':
                        descrip += str(rec.get('print_attr_name') + ':') + str(type.name) + '- Full Color,'


                    else:

                        descrip += str(rec.get('print_attr_name') + ':-') + str(
                            type.name) + '- Max Color' + str(
                            type.max_color_label) + ','

            print("lidjfkd descrip", descrip)
            personalized_product.sudo().specs = descrip
            # personalized_product.onchange_product_template_id_description()
            product = request.env["product.product"].search([('id', '=', int(personalised_product_product))])

        else:
            personalized_product = request.env["product.template"].sudo().create({
                'name': "Personalized" + product_tmpl_id.name,
                'categ_id': personalized_category.id,
                'detailed_type': 'product',
                'hak_master_product_id': product_main_id.id,
                'list_price': person_unit_price,
                'personalisation_details': details,
                'family_code': 'P-' + product_tmpl_id.family_code_ext if product_tmpl_id.family_code_ext else 'P-False',
            })
            # semi_fg_personalized_product = request.env["product.template"].sudo().create({
            #     'name': "Unpacked PSP " + product_tmpl_id.name,
            #     'categ_id': personalized_category.semi_fg_category_id.id,
            #     'detailed_type': 'product',
            #     'hak_master_product_id': product_main_id.id,
            #     'list_price': person_unit_price,
            #     'personalisation_details': details,
            #     'family_code': 'SFGP-' + product_tmpl_id.family_code_ext if product_tmpl_id.family_code_ext else 'SFGPP-False',
            # })
            for kit in detail_side_vals:
                kit.sudo().product_temp_id = personalized_product.id

            if personalized_product:
                print("personalized_product", personalized_product)
                json_det = personalized_product.personalisation_details.get('printing_details')
                descrip = str(personalized_product.name) + 'printing side:-'
                for rec in json_det:
                    print("dsfkjhjdskf", rec)

                    if rec.get('print_type_checked') and rec.get('print_type_checked'):
                        print("dsfkjhjdsk4444444f", rec)

                        type = request.env['printing.type'].search([('id', '=', int(rec.get('print_type_checked')))])

                        if type.max_color_label == '0':
                            descrip += str(rec.get('print_attr_name') + ':') + str(type.name) + '- Full Color,'


                        else:

                            descrip += str(rec.get('print_attr_name') + ':-') + str(
                                type.name) + '- Max Color' + str(
                                type.max_color_label) + ','

                print("lidjfkd descrip", descrip)
                personalized_product.sudo().specs = descrip
            product = request.env["product.product"].sudo().search([('product_tmpl_id', '=', personalized_product.id)])
            # semi_fg_product = request.env["product.product"].sudo().search(
            #     [('product_tmpl_id', '=', semi_fg_personalized_product.id)])
            if product:
                printing_company = request.env["res.company"].sudo().search([('is_printing', '=', True)])
                trading_company = request.env["res.company"].sudo().search([('is_trading', '=', True)])
                # semi_fg_bom = request.env['mrp.bom'].sudo().create({
                bom1 = request.env['mrp.bom'].sudo().create({
                    'product_id': product.id,
                    'product_tmpl_id': personalized_product.id,
                    # 'product_id': semi_fg_product.id,
                    # 'product_tmpl_id': semi_fg_personalized_product.id,
                    'type': 'normal',
                    'product_qty': 1,
                    'company_id': printing_company.id if printing_company else False,

                })
                # print("semi_fg_bom", semi_fg_bom)
                print("bom1", bom1)
                for side in personalized_product.selected_ids:
                    if side.printing_side_line_id.component_product_id:
                        component_product = request.env["product.product"].sudo().search(
                            [('product_tmpl_id', '=', side.printing_side_line_id.component_product_id.id)])
                        if component_product:
                            create_bom_line = True
                            if bom1.bom_line_ids:
                                for bom_line in bom1.bom_line_ids:
                                    # if semi_fg_bom.bom_line_ids:
                                    #     for bom_line in semi_fg_bom.bom_line_ids:
                                    if bom_line.product_id.id == component_product.id:
                                        create_bom_line = False
                            if create_bom_line:
                                lines = request.env['mrp.bom.line'].sudo().create({
                                    'product_id': component_product.id,
                                    'product_qty': 1,
                                    'bom_id': bom1.id,
                                    # 'bom_id': semi_fg_bom.id,
                                })
                    else:
                        lines = request.env['mrp.bom.line'].sudo().create({
                            'product_id': product_main_id.id,
                            'product_qty': 1,
                            'bom_id': bom1.id,
                            # 'bom_id': semi_fg_bom.id,
                        })

                # fg_bom = request.env['mrp.bom'].sudo().create({
                #
                #     'product_id': product.id,
                #     'product_tmpl_id': personalized_product.id,
                #     'type': 'normal',
                #     'product_qty': 1,
                #     'company_id': printing_company.id if printing_company else False,
                #
                # })
                # print("fg_bom", fg_bom)
                # fg_bom_lines = request.env['mrp.bom.line'].sudo().create({
                #     'product_id': semi_fg_product.id,
                #     'product_qty': 1,
                #     'bom_id': fg_bom.id,
                # })
                #
                # byproducts_list = []
                #
                # # print("semi_fg_bom", semi_fg_bom)
                #
                # # if semi_fg_bom:
                # #     for sfg_line in semi_fg_bom.bom_line_ids:
                # #         component_id = sfg_line.product_id.product_tmpl_id.component_id
                # #         component_bom = request.env["mrp.bom"].sudo().search(
                # #             [('component_id', '=', component_id.id)])
                # #         print("component_bom", component_bom)
                # #         if component_bom:
                # #             print("component_bom.byproduct_ids", component_bom.byproduct_ids)
                # #             for byproduct_line in component_bom.byproduct_ids:
                # #                 byproducts_list.append(byproduct_line.product_id.id)
                #
                # print("byproducts_list", byproducts_list)
                # if byproducts_list:
                #     for byproduct in byproducts_list:
                #         print("byproduct", byproduct)
                #         fg_bom_lines = request.env['mrp.bom.line'].sudo().create({
                #             'product_id': byproduct,
                #             'product_qty': 1,
                #             'bom_id': fg_bom.id,
                #         })

                bom2 = request.env['mrp.bom'].sudo().create({

                    'product_id': product.id,
                    'product_tmpl_id': personalized_product.id,
                    'type': 'subcontract',
                    'product_qty': 1,
                    'subcontractor_ids': [(4, printing_company.partner_id.id)],
                    'company_id': trading_company.id if trading_company else False,

                })
                lines = request.env['mrp.bom.line'].sudo().create({
                    'product_id': product_main_id.id,
                    'product_qty': 1,
                    'bom_id': bom2.id,
                })
                # fg_bom.sudo().write({
                bom1.sudo().write({
                    'product_tmpl_id': personalized_product.id,
                })
                if personalized_product:
                    personalized_product.sudo().write({
                        'seller_ids': [(0, 0, {
                            'partner_id': printing_company.partner_id.id,
                            'company_id': trading_company.id,
                            # 'price': 1.0,
                        })]
                    })
        if product:
            # bom = request.env['mrp.bom'].create({
            #
            #     'product_id': product.id,
            #     'product_tmpl_id': personalized_product.id,
            #     'type': 'normal',
            #     'product_qty': 1,
            #
            #
            #
            # })
            #
            # lines = request.env['mrp.bom.line'].create({
            #     'product_id': product_main_id.id,
            #     'product_qty': 1,
            #     'bom_id': bom.id,
            # })

            # ------------------------------

            finals = {
                'new_prod_id': product.id,
                'new_prod_tmpl_id': personalized_product.id,
                'name': product.display_name,

            }

            vv = {'products': [
                {'product_tmpl_id': personalized_product.id,
                 'id': product.id,
                 'description_sale': False,
                 'display_name': personalized_product.display_name,
                 'price': personalized_product.list_price,
                 'personalization_applicable': False,
                 'customized_product': False,
                 'fully_customized_product': False,
                 'printing_side_line_ids': [],
                 'quantity': quantity,
                 'attribute_lines': [],

                 'exclusions': {},
                 'archived_combinations': [],
                 'parent_exclusions': {},
                 'parent_product_tmpl_ids': []

                 }],
                'optional_products': []
            }

            print("return", finals)
            return vv

    @http.route(['/hak_product_configurator/show_advanced_configurator'], type='json', auth="user", methods=['POST'])
    def show_advanced_configurator(self, product_id, variant_values, pricelist_id, **kw):
        pricelist = self._get_pricelist(pricelist_id)
        return self._show_advanced_configurator(product_id, variant_values, pricelist, False, **kw)

    @http.route(['/hak_product_configurator/optional_product_items'], type='json', auth="user", methods=['POST'])
    def optional_product_items(self, product_id, pricelist_id, **kw):
        pricelist = self._get_pricelist(pricelist_id)
        return self._optional_product_items(product_id, pricelist, **kw)

    def _optional_product_items(self, product_id, pricelist, **kw):
        add_qty = float(kw.get('add_qty', 1))
        product = request.env['product.product'].browse(int(product_id))

        parent_combination = product.product_template_attribute_value_ids
        if product.env.context.get('no_variant_attribute_values'):
            # Add "no_variant" attribute values' exclusions
            # They are kept in the context since they are not linked to this product variant
            parent_combination |= product.env.context.get('no_variant_attribute_values')

        return request.env['ir.ui.view']._render_template("hak_product_configurator.optional_product_items", {
            'product': product,
            'parent_name': product.name,
            'parent_combination': parent_combination,
            'pricelist': pricelist,
            'add_qty': add_qty,
        })

    def _show_advanced_configurator(self, product_id, variant_values, pricelist, handle_stock, **kw):
        product = request.env['product.product'].browse(int(product_id))
        combination = request.env['product.template.attribute.value'].browse(variant_values)
        add_qty = float(kw.get('add_qty', 1))

        no_variant_attribute_values = combination.filtered(
            lambda
                product_template_attribute_value: product_template_attribute_value.attribute_id.create_variant == 'no_variant'
        )
        if no_variant_attribute_values:
            product = product.with_context(no_variant_attribute_values=no_variant_attribute_values)

        return request.env['ir.ui.view']._render_template("hak_product_configurator.optional_products_modal", {
            'product': product,
            'combination': combination,
            'add_qty': add_qty,
            'parent_name': product.name,
            'variant_values': variant_values,
            'pricelist': pricelist,
            'handle_stock': handle_stock,
            'already_configured': kw.get("already_configured", False),
            'mode': kw.get('mode', 'add'),
            'product_custom_attribute_values': kw.get('product_custom_attribute_values', None),
            'no_attribute': kw.get('no_attribute', False),
            'custom_attribute': kw.get('custom_attribute', False)
        })

    def _get_pricelist(self, pricelist_id, pricelist_fallback=False):
        return request.env['product.pricelist'].browse(int(pricelist_id or 0))


class CrmProductConfiguratorController(http.Controller):

    @route('/hak_product_configurator/get_values', type='json', auth='user')
    def get_product_configurator_values(
            self,
            product_template_id,
            quantity,
            currency_id,
            so_date,
            product_uom_id=None,
            company_id=None,
            pricelist_id=None,
            ptav_ids=None,
            only_main_product=False,
    ):
        """ Return all product information needed for the product configurator.

        :param int product_template_id: The product for which to seek information, as a
                                        `product.template` id.
        :param int quantity: The quantity of the product.
        :param int currency_id: The currency of the transaction, as a `res.currency` id.
        :param str so_date: The date of the `sale.order`, to compute the price at the right rate.
        :param int|None product_uom_id: The unit of measure of the product, as a `uom.uom` id.
        :param int|None company_id: The company to use, as a `res.company` id.
        :param int|None pricelist_id:  The pricelist to use, as a `product.pricelist` id.
        :param recordset|None product_template_attribute_value_ids: The combination of the product,
                                                                    as a `product.template.attribute
                                                                    .value` recordset.
        :param bool only_main_product: Whether the optional products should be included or not.
        :rtype: dict
        :return: A dict containing a list of products and a list of optional products information,
                 generated by :meth:`_get_product_information`.
        """

        if company_id:
            request.update_context(allowed_company_ids=[company_id])
        product_template = request.env['product.template'].browse(product_template_id)

        combination = request.env['product.template.attribute.value']
        if ptav_ids:
            combination = request.env['product.template.attribute.value'].browse(ptav_ids).filtered(
                lambda ptav: ptav.product_tmpl_id.id == product_template_id)
        if not combination:
            combination = product_template._get_first_possible_combination()

        print("jcombination", combination)

        test = dict(
            products=[
                dict(
                    **self._get_product_information(
                        product_template,
                        combination,
                        currency_id,
                        so_date,
                        quantity=quantity,
                        product_uom_id=product_uom_id,
                        pricelist_id=pricelist_id,
                    ),
                    parent_product_tmpl_ids=[],
                    combination=combination.ids,
                )
            ],
            optional_products=[
                dict(
                    **self._get_product_information(
                        optional_product_template,
                        optional_product_template._get_first_possible_combination(
                            parent_combination=combination
                        ),
                        currency_id,
                        so_date,
                        # giving all the ptav of the parent product to get all the exclusions
                        parent_combination=product_template.attribute_line_ids. \
                            product_template_value_ids,
                        pricelist_id=pricelist_id,
                    ),
                    parent_product_tmpl_ids=[product_template.id],
                ) for optional_product_template in product_template.optional_product_ids
            ] if not only_main_product else []
        )
        print("test", test)
        return test

    @route('/hak_product_configurator/create_product', type='json', auth='user')
    def sale_product_configurator_create_product(self, product_template_id, combination):
        """ Create the product when there is a dynamic attribute in the combination.

        :param int product_template_id: The product for which to seek information, as a
                                        `product.template` id.
        :param recordset combination: The combination of the product, as a
                                      `product.template.attribute.value` recordset.
        :rtype: int
        :return: The product created, as a `product.product` id.
        """
        product_template = request.env['product.template'].browse(product_template_id)
        combination = request.env['product.template.attribute.value'].browse(combination)
        product = product_template.sudo()._create_product_variant(combination)
        return product.id

    @route('/hak_product_configurator/update_combination', type='json', auth='user')
    def sale_product_configurator_update_combination(
            self,
            product_template_id,
            combination,
            currency_id,
            so_date,
            quantity,
            product_uom_id=None,
            company_id=None,
            pricelist_id=None,
    ):
        """ Return the updated combination information.

        :param int product_template_id: The product for which to seek information, as a
                                        `product.template` id.
        :param recordset combination: The combination of the product, as a
                                      `product.template.attribute.value` recordset.
        :param int currency_id: The currency of the transaction, as a `res.currency` id.
        :param str so_date: The date of the `sale.order`, to compute the price at the right rate.
        :param int quantity: The quantity of the product.
        :param int|None product_uom_id: The unit of measure of the product, as a `uom.uom` id.
        :param int|None company_id: The company to use, as a `res.company` id.
        :param int|None pricelist_id:  The pricelist to use, as a `product.pricelist` id.
        :rtype: dict
        :return: Basic informations about a product, generated by
                 :meth:`_get_basic_product_information`.
        """
        if company_id:
            request.update_context(allowed_company_ids=[company_id])
        product_template = request.env['product.template'].browse(product_template_id)
        pricelist = request.env['product.pricelist'].browse(pricelist_id)
        product_uom = request.env['uom.uom'].browse(product_uom_id)
        currency = request.env['res.currency'].browse(currency_id)
        combination = request.env['product.template.attribute.value'].browse(combination)
        product = product_template._get_variant_for_combination(combination)

        return self._get_basic_product_information(
            product or product_template,
            pricelist,
            combination,
            quantity=quantity or 0.0,
            uom=product_uom,
            currency=currency,
            date=datetime.fromisoformat(so_date),
        )

    @route('/hak_product_configurator/get_optional_products_onhand', type='json', auth='user')
    def get_product_available(self, product_template_id, product_id):
        print("sdkjfnkjdsnkjvdsnkjvnuuuuusssss", product_id, product_template_id)

        main_product_id = request.env['product.product'].browse(product_id)
        print("salkdfsa", main_product_id)
        stock_quant_availablility = sum(
            request.env['stock.quant'].search([('product_id', '=', main_product_id.id), ('on_hand', '=', True)]).mapped(
                'available_quantity'))
        print("jfjdsf uuupp", str(stock_quant_availablility) + '' + str(main_product_id.uom_id.name) + ' Available')
        return str(stock_quant_availablility) + ' ' + str(main_product_id.uom_id.name) + ' Available'

    @route('/hak_product_configurator/get_optional_products', type='json', auth='user')
    def sale_product_configurator_get_optional_products(
            self,
            product_template_id,
            combination,
            parent_combination,
            currency_id,
            so_date,
            company_id=None,
            pricelist_id=None,
    ):
        """ Return information about optional products for the given `product.template`.

        :param int product_template_id: The product for which to seek information, as a
                                        `product.template` id.
        :param recordset combination: The combination of the product, as a
                                      `product.template.attribute.value` recordset.
        :param recordset parent_combination: The combination of the parent product, as a
                                             `product.template.attribute.value` recordset.
        :param int currency_id: The currency of the transaction, as a `res.currency` id.
        :param str so_date: The date of the `sale.order`, to compute the price at the right rate.
        :param int|None company_id: The company to use, as a `res.company` id.
        :param int|None pricelist_id:  The pricelist to use, as a `product.pricelist` id.
        :rtype: [dict]
        :return: A list of optional products information, generated by
                 :meth:`_get_product_information`.
        """
        if company_id:
            request.update_context(allowed_company_ids=[company_id])
        product_template = request.env['product.template'].browse(product_template_id)
        parent_combination = request.env['product.template.attribute.value'].browse(
            parent_combination + combination
        )
        return [
            dict(
                **self._get_product_information(
                    optional_product_template,
                    optional_product_template._get_first_possible_combination(
                        parent_combination=parent_combination
                    ),
                    currency_id,
                    so_date,
                    parent_combination=parent_combination,
                    pricelist_id=pricelist_id,
                ),
                parent_product_tmpl_ids=[product_template.id],
            ) for optional_product_template in product_template.optional_product_ids
        ]

    def _get_product_information(
            self,
            product_template,
            combination,
            currency_id,
            so_date,
            quantity=1,
            product_uom_id=None,
            pricelist_id=None,
            parent_combination=None,
    ):
        """ Return complete information about a product.

        :param recordset product_template: The product for which to seek information, as a
                                           `product.template` record.
        :param recordset combination: The combination of the product, as a
                                      `product.template.attribute.value` recordset.
        :param int currency_id: The currency of the transaction, as a `res.currency` id.
        :param str so_date: The date of the `sale.order`, to compute the price at the right rate.
        :param int quantity: The quantity of the product.
        :param int|None product_uom_id: The unit of measure of the product, as a `uom.uom` id.
        :param int|None pricelist_id:  The pricelist to use, as a `product.pricelist` id.
        :param recordset|None parent_combination: The combination of the parent product, as a
                                                  `product.template.attribute.value` recordset.
        :rtype: dict
        :return: A dict with the following structure:
            {
                'product_tmpl_id': int,
                'id': int,
                'description_sale': str|False,
                'display_name': str,
                'price': float,
                'quantity': int
                'attribute_line': [{
                    'id': int
                    'attribute': {
                        'id': int
                        'name': str
                        'display_type': str
                    },
                    'attribute_value': [{
                        'id': int,
                        'name': str,
                        'price_extra': float,
                        'html_color': str|False,
                        'image': str|False,
                        'is_custom': bool
                    }],
                    'selected_attribute_id': int,
                }],
                'exclusions': dict,
                'archived_combination': dict,
                'parent_exclusions': dict,
            }
        """

        print("slkjlkjdasd uuuuu", combination)
        pricelist = request.env['product.pricelist'].browse(pricelist_id)
        product_uom = request.env['uom.uom'].browse(product_uom_id)
        currency = request.env['res.currency'].browse(currency_id)
        product = product_template._get_variant_for_combination(combination)
        attribute_exclusions = product_template._get_attribute_exclusions(
            parent_combination=parent_combination
        )

        return dict(
            product_tmpl_id=product_template.id,
            **self._get_basic_product_information(
                product or product_template,
                pricelist,
                combination,
                quantity=quantity,
                uom=product_uom,
                currency=currency,
                date=datetime.fromisoformat(so_date),
            ),
            personalization_applicable=product_template.personalization_applicable,
            customized_product=product_template.customized_product,
            fully_customized_product=product_template.fully_customized_product,
            psc_product=product_template.psc_product,

            # printing_side_line_ids = product_template.printing_side_line_ids,
            printing_side_line_ids=[dict(
                id=ptal.id,
                state=ptal.state,
                name=ptal.name,
                image_1920=ptal.image_1920,
                max_width=ptal.max_width,
                max_height=ptal.max_height,
                printing_type_ids=[
                    dict(
                        **ptav.read(['name', 'id', 'max_color_label'])[0],

                    ) for ptav in ptal.printing_type_ids

                ],

            ) for ptal in product_template.printing_side_line_ids],

            quantity=quantity,
            attribute_lines=[dict(
                id=ptal.id,
                attribute=dict(**ptal.attribute_id.read(['id', 'name', 'display_type'])[0]),
                attribute_values=[
                    dict(
                        **ptav.read(['name', 'html_color', 'image', 'is_custom'])[0],
                        price_extra=ptav.currency_id._convert(
                            ptav.price_extra,
                            currency,
                            request.env.company,
                            datetime.fromisoformat(so_date).date(),
                        ),
                    ) for ptav in ptal.product_template_value_ids
                    if ptav.ptav_active
                ],
                selected_attribute_value_ids=combination.filtered(
                    lambda c: ptal in c.attribute_line_id
                ).ids,
                create_variant=ptal.attribute_id.create_variant,
            ) for ptal in product_template.attribute_line_ids],
            exclusions=attribute_exclusions['exclusions'],
            archived_combinations=attribute_exclusions['archived_combinations'],
            parent_exclusions=attribute_exclusions['parent_exclusions'],
        )

    def _get_basic_product_information(self, product_or_template, pricelist, combination, **kwargs):
        """ Return basic information about a product

        :param recordset product_or_template: The product for which to seek information, as a
                                              `product.product` or `product.template` record.
        :param recordset|None pricelist: The pricelist to use, as a `product.pricelist` record.
        :param recordset combination: The combination of the product, as a
                                      `product.template.attribute.value` recordset.
        :param dict kwargs: Locally unused data passed to `_get_product_price`
        :rtype: dict
        :return: A dict with the following structure::
            {
                'id': int,  # if product_or_template is a record of `product.product`.
                'description_sale': str|False,
                'display_name': str,
                'price': float,
                'quantity': int,
            }
        """
        basic_information = dict(
            **product_or_template.read(['description_sale', 'display_name'])[0]
        )
        # If the product is a template, check the combination to compute the name to take dynamic
        # and no_variant attributes into account. Also, drop the id which was auto-included by the
        # search but isn't relevant since it is supposed to be the id of a `product.product` record.
        if not product_or_template.is_product_variant:
            basic_information['id'] = False
            combination_name = combination._get_combination_name()
            if combination_name:
                basic_information.update(
                    display_name=f"{basic_information['display_name']} ({combination_name})"
                )
        return dict(
            **basic_information,
            price=pricelist._get_product_price(
                product_or_template.with_context(
                    **product_or_template._get_product_price_context(combination)
                ),
                **kwargs,
            ),
        )
