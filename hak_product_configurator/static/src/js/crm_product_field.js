/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { useEffect } from '@odoo/owl';
import { registry } from "@web/core/registry";
import { Many2OneField, many2OneField } from "@web/views/fields/many2one/many2one_field";
//import { SaleOrderLineProductField } from '@sale/js/sale_product_field';
import { serializeDateTime, serializeDate } from "@web/core/l10n/dates";
import { x2ManyCommands } from "@web/core/orm_service";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
//import { ProductConfiguratorDialog } from "@sale_product_configurator/js/product_configurator_dialog/product_configurator_dialog";

import { CRMProductConfiguratorDialog } from "@hak_product_configurator/js_new/product_configurator_dialog/product_configurator_dialog";

async function applyProductPersonalised(record, product) {
    // handle custom values & no variants
    const contextRecords = [];
//    for (const ptal of product.attribute_lines) {
//        const selectedCustomPTAV = ptal.attribute_values.find(
//            ptav => ptav.is_custom && ptal.selected_attribute_value_ids.includes(ptav.id)
//        );
//        if (selectedCustomPTAV) {
//            contextRecords.push({
//                default_custom_product_template_attribute_value_id: selectedCustomPTAV.id,
//                default_custom_value: ptal.customValue,
//            });
//        };
//    }

    const proms = [];
//    proms.push(record.data.product_custom_attribute_value_ids.createAndReplace(contextRecords));
//
//    const noVariantPTAVIds = product.attribute_lines.filter(
//        ptal => ptal.create_variant === "no_variant" && ptal.attribute_values.length > 1
//    ).flatMap(ptal => ptal.selected_attribute_value_ids);

    await Promise.all(proms);
    await record.update({
        product_id: [product.id, product.display_name],
        product_uom_qty: product.quantity,
        product_no_variant_attribute_value_ids: [],
    });
};



async function applyProduct(record, product) {
    // handle custom values & no variants
    const contextRecords = [];
    for (const ptal of product.attribute_lines) {
        const selectedCustomPTAV = ptal.attribute_values.find(
            ptav => ptav.is_custom && ptal.selected_attribute_value_ids.includes(ptav.id)
        );
        if (selectedCustomPTAV) {
            contextRecords.push({
                default_custom_product_template_attribute_value_id: selectedCustomPTAV.id,
                default_custom_value: ptal.customValue,
            });
        };
    }

    const proms = [];
    proms.push(record.data.product_custom_attribute_value_ids.createAndReplace(contextRecords));

    const noVariantPTAVIds = product.attribute_lines.filter(
        ptal => ptal.create_variant === "no_variant" && ptal.attribute_values.length > 1
    ).flatMap(ptal => ptal.selected_attribute_value_ids);

    await Promise.all(proms);
    await record.update({
        product_id: [product.id, product.display_name],
        product_uom_qty: product.quantity,
        product_no_variant_attribute_value_ids: [x2ManyCommands.set(noVariantPTAVIds)],
    });
};


export class CRMLineProductField extends Many2OneField {
    static props = {
        ...Many2OneField.props,
        readonlyField: { type: Boolean, optional: true },
    };

    setup() {
        super.setup();
        let isMounted = false;
        let isInternalUpdate = false;
        let personalisation = false
        const { updateRecord } = this;
        this.updateRecord = (value) => {
            isInternalUpdate = true;
            return updateRecord.call(this, value);
        };
        useEffect(value => {
            if (!isMounted) {
                isMounted = true;
            } else if (value && isInternalUpdate) {
                // we don't want to trigger product update when update comes from an external sources,
                // such as an onchange, or the product configuration dialog itself
                if (this.relation === "product.template") {
                    this._onProductTemplateUpdate();
                } else {
                    this._onProductUpdate();
                }
            }
            isInternalUpdate = false;
        }, () => [Array.isArray(this.value) && this.value[0]]);


        this.dialog = useService("dialog");
        this.orm = useService("orm");
    }

    get isProductClickable() {
        // product form should be accessible if the widget field is readonly
        // or if the line cannot be edited (e.g. locked SO)
        return (
            this.props.readonlyField ||
            (this.props.record.model.root.activeFields.product_line_ids &&
                this.props.record.model.root._isReadonly("product_line_ids"))
        );
    }
    get hasExternalButton() {
        // Keep external button, even if field is specified as 'no_open' so that the user is not
        // redirected to the product when clicking on the field content
        const res = super.hasExternalButton;
        return res || (!!this.props.record.data[this.props.name] && !this.state.isFloating);
    }
    get hasConfigurationButton() {
        return this.isConfigurableLine || this.isConfigurableTemplate;
    }
    get isConfigurableLine() {
        return false;
    }
    get isConfigurableTemplate() {

        return false || this.props.record.data.is_configurable_product

     }

    get configurationButtonHelp() {
        return _t("Edit Configuration");
    }

    get configurationButtonIcon() {
        return 'btn btn-secondary fa ' + this.configurationButtonFAIcon();
    }

    configurationButtonFAIcon() {
        return 'fa-pencil';
    }

    onClick(ev) {
        // Override to get internal link to products in SOL that cannot be edited
        if (this.props.readonly) {
            ev.stopPropagation();
            this.openAction();
        }
        else {
            super.onClick(ev);
        }
    }

    async _onProductTemplateUpdate() {

            const result = await this.orm.call(
            'product.template',
            'get_single_product_variant',
            [this.props.record.data.product_template_id[0]],
            {
                context: this.context,
            }
        );
        if(result && result.product_id) {
            if (this.props.record.data.product_id != result.product_id.id) {
                if (result.has_optional_products) {
                    this._openProductConfigurator();
                } else {
                    await this.props.record.update({
                        product_id: [result.product_id, result.product_name],
                    });
                    this._onProductUpdate();
                }
            }
        } else {
            if (!result.mode || result.mode === 'configurator') {
                this._openProductConfigurator();
            } else {
                // only triggered when sale_product_matrix is installed.
                this._openGridConfigurator();
            }
        }

    }

//    async _openProductConfigurator(edit=false) {
//        this.context['mode'] = mode
//        const saleOrderRecord = this.props.record.model.root;
//        const pricelistId = saleOrderRecord.data.pricelist_id ? saleOrderRecord.data.pricelist_id[0] : false;
//        const productTemplateId = this.props.record.data.product_template_id[0];
//        const $modal = $(
//            await this.rpc(
//                "/hak_product_configurator/configure",
//                {
//                    product_template_id: productTemplateId,
//                    quantity: this.props.record.data.product_uom_qty || 1,
//                    pricelist_id: pricelistId,
//                    product_template_attribute_value_ids: this.props.record.data.product_template_attribute_value_ids.records.map(
//                        record => record.data.id
//                    ),
//                    product_no_variant_attribute_value_ids: this.props.record.data.product_no_variant_attribute_value_ids.records.map(
//                        record => record.data.id
//                    ),
//                    mode: mode,
//                    context: this.context,
//                },
//            )
//        );
//        const productSelector = `input[type="hidden"][name="product_id"], input[type="radio"][name="product_id"]:checked`;
//        // TODO VFE drop this selectOrCreate and make it so that
//        // get_single_product_variant returns first variant as well.
//        // and use specified product on edition mode.
//        const productId = await selectOrCreateProduct.call(
//            this,
//            $modal,
//            parseInt($modal.find(productSelector).first().val(), 10),
//            productTemplateId,
//            false
//        );
//        $modal.find(productSelector).val(productId);
//        const variantValues = getSelectedVariantValues($modal);
//        const noVariantAttributeValues = getNoVariantAttributeValues($modal);
//        /**
//         *  `product_custom_attribute_value_ids` records are not loaded in the view bc sub templates
//         *  are not loaded in list views. Therefore, we fetch them from the server if the record is
//         *  saved. Else we use the value stored on the line.
//         */
//
//        const customAttributeValueRecords = this.props.record.data.product_custom_attribute_value_ids.records;
//        let customAttributeValues = [];
//        if (customAttributeValueRecords.length > 0) {
//            if (customAttributeValueRecords[0].isNew) {
//                customAttributeValues = customAttributeValueRecords.map(
//                    record => record.data
//                );
//            } else {
//                customAttributeValues = await this.orm.read(
//                    'product.attribute.custom.value',
//                    this.props.record.data.product_custom_attribute_value_ids.currentIds,
//                    ["custom_product_template_attribute_value_id", "custom_value"]
//                );
//            }
//        }
//
//        const formattedCustomAttributeValues = customAttributeValues.map(
//            data => {
//                // NOTE: this dumb formatting is necessary to avoid
//                // modifying the shared code between frontend & backend for now.
//                return {
//                    custom_value: data.custom_value,
//                    custom_product_template_attribute_value_id: {
//                        res_id: data.custom_product_template_attribute_value_id[0],
//                    },
//                };
//            }
//        );
//        this.rootProduct = {
//            product_id: productId,
//            product_template_id: productTemplateId,
//            quantity: parseFloat($modal.find('input[name="add_qty"]').val() || 1),
//            variant_values: variantValues,
//            product_custom_attribute_values: formattedCustomAttributeValues,
//            no_variant_attribute_values: noVariantAttributeValues,
//        };
//        const optionalProductsModal = new OptionalProductsModal(null, {
//            rootProduct: this.rootProduct,
//            pricelistId: pricelistId,
//            okButtonText: this.env._t("Confirm"),
//            cancelButtonText: this.env._t("Back"),
//            title: this.env._t("Configure"),
//            context: this.context,
//            mode: mode,
//        });
//        let modalEl;
//        optionalProductsModal.opened(() => {
//            modalEl = optionalProductsModal.el;
//            this.ui.activateElement(modalEl);
//        });
//        optionalProductsModal.on("closed", null, async () => {
//            // Wait for the event that caused the close to bubble
//            await new Promise(resolve => setTimeout(resolve, 0));
//            this.ui.deactivateElement(modalEl);
//        });
//        optionalProductsModal.open();
//
//        let confirmed = false;
//        optionalProductsModal.on("confirm", null, async () => {
//
//            if (!optionalProductsModal.personalisation){
//
//
//                confirmed = true;
//                const [
//                    mainProduct,
//                    ...optionalProducts
//                ] = await optionalProductsModal.getAndCreateSelectedProducts();
//                await this.props.record.update(await this._convertConfiguratorDataToUpdateData(mainProduct));
//
//
//            }else{
//
//
//                confirmed = true;
//
//                var attachment = document.getElementById('file1').files[0]
//
//
//
//
//                const [
//                    mainProduct,
//                    ...optionalProducts
//                ] = await optionalProductsModal.getAndPrintCustomiseProduct();
//                await this.props.record.update(await this._convertConfiguratorDataToUpdateData(mainProduct));
//
//                if(attachment){
//                    var url = await optionalProductsModal.toBase64(attachment)
//
//
//
//                    const $modal_hak = $(
//                                            await this.rpc(
//                                                "/hak_product_configurator/map_logo",
//                                                {
//                                                    file: url,
//                                                    product_id: mainProduct.product_template_id,
//
//                                                },
//                                            )
//                                        );
//
//               }
//
//               for (var i = 0; i < optionalProductsModal.products_print_vals.length; i++) {
//
//
//                if(optionalProductsModal.products_print_vals[i].spcl_logo){
//
//
//                var url_logo = await optionalProductsModal.toBase64(optionalProductsModal.products_print_vals[i].spcl_logo)
//
//                optionalProductsModal.products_print_vals[i].spcl_logo = url_logo
//
//                }
//
//
//               }
//
//                const $modal_personal_hak = $(
//                                            await this.rpc(
//                                                "/hak_product_configurator/map_personal_logo",
//                                                {
//                                                    logos_detail: optionalProductsModal.products_print_vals,
//                                                    product_id: mainProduct.product_template_id,
//                                                    partner: this.env.model.root.data.partner_id[0]
//
//                                                },
//                                            )
//                                        );
//
//            }
//
//
//
//
//        });
//        optionalProductsModal.on("closed", null, () => {
//            if (confirmed) {
//                return;
//            }
//            if (mode != 'edit') {
//                this.props.record.update({
//                    product_template_id: false,
//                    product_id: false,
//                    product_uom_qty: 1.0,
//                    // TODO reset custom/novariant values (and remove onchange logic?)
//                });
//            }
//        });
//    }

    toBase64 (file){


             return   new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = reject;
        });

     }


    async _openProductConfigurator(edit=false) {

        console.log("khkjdhsf", edit)
        const saleOrderRecord = this.props.record.model.root;
        let ptavIds = this.props.record.data.product_template_attribute_value_ids.records.map(
            record => record.resId
        );
        let customAttributeValues = [];

        if (edit) {
            /**
             * no_variant and custom attribute don't need to be given to the configurator for new
             * products.
             */
            ptavIds = ptavIds.concat(this.props.record.data.product_no_variant_attribute_value_ids.records.map(
                record => record.resId
            ));
            /**
             *  `product_custom_attribute_value_ids` records are not loaded in the view bc sub templates
             *  are not loaded in list views. Therefore, we fetch them from the server if the record is
             *  saved. Else we use the value stored on the line.
             */
            customAttributeValues =
                this.props.record.data.product_custom_attribute_value_ids.records[0]?.isNew ?
                this.props.record.data.product_custom_attribute_value_ids.records.map(
                    record => record.data
                ) :
                await this.orm.read(
                    'product.attribute.custom.value',
                    this.props.record.data.product_custom_attribute_value_ids.currentIds,
                    ["custom_product_template_attribute_value_id", "custom_value"]
                )
        }

        console.log("this.props.record ttttttttttt", this.props.record, this, CRMProductConfiguratorDialog)
        var new_cust_product = await this.props.record.model.rpc('/hak_product_configurator/check_product_customised', {
                product_tmpl_id: this.props.record.data.product_template_id[0],


            })

        console.log("returnreturnreturn", new_cust_product)

        if (new_cust_product){
            var main_product = new_cust_product[0]
            var line_prd = new_cust_product[1]
            var selected_vals = new_cust_product[2]
            var personalised_product_template = this.props.record.data.product_template_id[0]
            var personalised_product_product = this.props.record.data.product_id[0]
        }else{
            var main_product = this.props.record.data.product_template_id[0]
            var line_prd = {}
            var selected_vals = []
            var personalised_product_template = 0
            var personalised_product_product = 0
        }


        var quantity_j = this.props.record.data.product_uom_qty || 1
        console.log("saldjsada hhakkkkkkk tyttyyype", line_prd)

        this.dialog.add(CRMProductConfiguratorDialog, {
            productTemplateId: main_product,
            personalised_product_product: personalised_product_product,
            personalised_product_template: personalised_product_template,
            hak_type: this.props.record.data.hak_type,
            line_prd: line_prd,
            selected_vals: selected_vals,
//            productTemplateId: 47,
            partner: this.props.record.model.root.data.partner_id[0],
            partner_logo: this.props.record.model.root.data.partner_logo[0],
            ptavIds: ptavIds,
            customAttributeValues: customAttributeValues.map(
                data => {
                    return {
                        ptavId: data.custom_product_template_attribute_value_id[0],
                        value: data.custom_value,
                    }
                }
            ),
            quantity: this.props.record.data.product_uom_qty || 1,
            productUOMId: this.props.record.data.product_uom[0],
            companyId: saleOrderRecord.data.company_id[0],
            pricelistId: saleOrderRecord.data.pricelist_id[0],
            currencyId: this.props.record.data.currency_id[0],
//            personalisation: false,
            soDate: serializeDateTime(saleOrderRecord.data.date_order),
            edit: edit,
            save: async (mainProduct, optionalProducts, personalisation, products_print_vals) => {

            this.mainProduct = mainProduct
            this.personalisation = personalisation
            this.products_print_vals = products_print_vals

             console.log("tgiss.proppp",this, mainProduct, optionalProducts)
                          console.log("tgiss.propp55555555p", mainProduct, optionalProducts)



                if (personalisation){

                    await applyProductPersonalised(this.props.record, mainProduct);

                    console.log("jhjhxjczhjxjchzxjhcxzc", this, products_print_vals)





                    this._onProductUpdate();
//                    saleOrderRecord.data.product_line_ids.leaveEditMode();




                }else{


                    await applyProduct(this.props.record, mainProduct);

                   console.log("tgiss.proppp", CRMProductConfiguratorDialog.props,this,mainProduct, optionalProducts)


                    this._onProductUpdate();
                    saleOrderRecord.data.product_line_ids.leaveEditMode();
                    for (const optionalProduct of optionalProducts) {
                        const line = await saleOrderRecord.data.product_line_ids.addNewRecord({
                            position: 'bottom',
                            mode: "readonly",
                        });
                        await applyProduct(line, optionalProduct);
                    }

                }
            },

            update_logo: async (products_print_vals, product_tmpl_id) => {

                console.log("sakjdaksdsdkahskjdhsakjhdkjsa yyyyyyyrrrrrr", products_print_vals, this)





           for (var i = 0; i < products_print_vals.length; i++) {


                if(products_print_vals[i].spcl_logo){


                var url_logo = await this.toBase64(products_print_vals[i].spcl_logo)

                products_print_vals[i].spcl_logo = url_logo

                }


           }
           this.products_print_vals = products_print_vals

           console.log("sdkjhkjhkjdshfkjds", this.products_print_vals, products_print_vals)

           this.props.record.model.rpc("/hak_product_configurator/map_personal_logo",
                                                {
                                                    logos_detail: products_print_vals,
                                                    product_id: this.mainProduct.product_tmpl_id,
                                                    partner: this.props.record.model.root.data.partner_id[0],
                                                    crm : this.props.record.data.crm_id[0],
                                                    header_logo: this.props.record.model.root.data.partner_logo[0],

                                                },
                                            )





            },
            discard: () => {
                saleOrderRecord.data.product_line_ids.delete(this.props.record);
            },
        });



        console.log("jdfkjsdkfjkdsjf dhhhhhhhhhhhhhh", this)







    }


    async _convertConfiguratorDataToUpdateData(mainProduct) {
        const nameGet = await this.orm.nameGet(
            'product.product',
            [mainProduct.product_id],
            { context: this.context }
        );
        let result = {
            product_id: nameGet[0],
            product_uom_qty: mainProduct.quantity,
        };
        var customAttributeValues = mainProduct.product_custom_attribute_values;
        var customValuesCommands = [{ operation: "DELETE_ALL" }];
        if (customAttributeValues && customAttributeValues.length !== 0) {
            _.each(customAttributeValues, function (customValue) {
                customValuesCommands.push({
                    operation: "CREATE",
                    context: [
                        {
                            default_custom_product_template_attribute_value_id:
                                customValue.custom_product_template_attribute_value_id,
                            default_custom_value: customValue.custom_value,
                        },
                    ],
                });
            });
        }

        result.product_custom_attribute_value_ids = {
            operation: "MULTI",
            commands: customValuesCommands,
        };

        var noVariantAttributeValues = mainProduct.no_variant_attribute_values;
        var noVariantCommands = [{ operation: "DELETE_ALL" }];
        if (noVariantAttributeValues && noVariantAttributeValues.length !== 0) {
            var resIds = _.map(noVariantAttributeValues, function (noVariantValue) {
                return { id: parseInt(noVariantValue.value) };
            });

            noVariantCommands.push({
                operation: "ADD_M2M",
                ids: resIds,
            });
        }

        result.product_no_variant_attribute_value_ids = {
            operation: "MULTI",
            commands: noVariantCommands,
        };


        return result;
    }



    async _onProductUpdate() { } // event_booth_sale, event_sale, sale_renting

    onEditConfiguration() {
        if (this.isConfigurableLine) {
            this._editLineConfiguration();
        } else {
            this._editProductConfiguration();
        }
    }

    _editLineConfiguration() { } // event_booth_sale, event_sale, sale_renting

    _editProductConfiguration() {

         if (this.props.record.data.is_configurable_product) {
            this._openProductConfigurator(true);
        }


     } // sale_product_configurator, sale_product_matrix

    _convertConfiguratorDataToLinesCreationContext (optionalProductsData) {
        return optionalProductsData.map(productData => {
            return {
                default_product_id: productData.product_id,
                default_product_template_id: productData.product_template_id,
                default_product_uom_qty: productData.quantity,
                default_product_no_variant_attribute_value_ids: productData.no_variant_attribute_values.map(
                    noVariantAttributeData => {
                        return [4, parseInt(noVariantAttributeData.value)];
                    }
                ),
                default_product_custom_attribute_value_ids: productData.product_custom_attribute_values.map(
                    customAttributeData => {
                        return [
                            0,
                            0,
                            {
                                custom_product_template_attribute_value_id:
                                    customAttributeData.custom_product_template_attribute_value_id,
                                custom_value: customAttributeData.custom_value,
                            },
                        ];
                    }
                )
            };
        });
    }


}

CRMLineProductField.template = "sale.SaleProductField";

export const cRMLineProductField = {
    ...many2OneField,
    component: CRMLineProductField,
    extractProps(fieldInfo, dynamicInfo) {
        const props = many2OneField.extractProps(...arguments);
        props.readonlyField = dynamicInfo.readonly;
        return props;
    },
};

registry.category("fields").add("crm_product_many2one", cRMLineProductField);
