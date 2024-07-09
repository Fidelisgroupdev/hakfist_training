/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { useEffect } from '@odoo/owl';
import { registry } from "@web/core/registry";
import { Many2OneField, many2OneField } from "@web/views/fields/many2one/many2one_field";

import { SelectionField } from "@web/views/fields/selection/selection_field";
//import { SaleOrderLineProductField } from '@sale/js/sale_product_field';
import { serializeDateTime, serializeDate } from "@web/core/l10n/dates";
import { x2ManyCommands } from "@web/core/orm_service";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
//import { ProductConfiguratorDialog } from "@sale_product_configurator/js/product_configurator_dialog/product_configurator_dialog";

//import { CRMProductConfiguratorDialog } from "@hak_product_configurator/js_new/product_configurator_dialog/product_configurator_dialog";




patch(SelectionField.prototype, {

    onChange(ev) {
        const value = JSON.parse(ev.target.value);
        switch (this.type) {
            case "many2one":
                if (value === false) {
                    this.props.record.update({ [this.props.name]: false }, { save: this.props.autosave });
                } else {
                    this.props.record.update({
                        [this.props.name]: this.options.find((option) => option[0] === value),
                    }, { save: this.props.autosave });
                }
                break;
            case "selection":
                this.props.record.update({ [this.props.name]: value }, { save: this.props.autosave });
//                if (value == 'psc'){
//                    console.log("sjdhskjhdjsfkjd uuuuuuuudddddddddeeeeeeeddd", this)
//                    var context =  {
//                            default_crm_id: this.props.record.data.crm_id[0],
//                            default_crm_product_line_id: this.props.record.data.id,
//                            default_customer: this.props.record.evalContext.uid,
//                        }
//
//
//                        console.log("context", context)
//
//                    this.env.model.action.doAction({
//                            type: "ir.actions.act_window",
//                            res_model: "type.hak.psc",
//                            target: 'new',
//                            views: [[false, "form"]],
//                            context: context,
//                        });
//
//                }
                break;
        }
    }


});



