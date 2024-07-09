/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { url } from "@web/core/utils/urls";


publicWidget.registry.PreviewProduct = publicWidget.Widget.extend({
    selector: '.oe_product',
    events: {

         "mouseenter .oe_product_image": "_onHover",
         "mouseleave .oe_product_image ": '_onMouseOut',
    },

    _onHover: async function (ev) {



        var element = ev.currentTarget;
        var spanElement = element.querySelector('span');
        var res_id = spanElement.getAttribute('data-oe-id');
        var odxPrevElement = $(element).find('#odx_prev');
        var popHtmlElement = odxPrevElement.find('#pop_html');

        $('#pop_html').empty();
        $('.product_prev').empty();


        var content = url("/web/content", {
                model: 'product.template',
                field: 'branding_image',
                id: res_id,
            })

        var modalHtml ="<img src="+content+"  style='height:100%;width:100%;border-radius: 10px;box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.6);'/>";


        odxPrevElement.addClass('prev_product');
        popHtmlElement.addClass('product_prev');
        $('.product_prev').append(modalHtml);
        $('.prev_product').modal('show');


    },

    _onMouseOut: function (){
        $('.product_prev').empty();
        $('.prev_product').modal('hide');
        $('#odx_prev').modal('hide');
        $('.prev_product').removeClass('prev_product');
        $('.product_prev').removeClass('product_prev');

    },


  });
