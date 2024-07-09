/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { url } from "@web/core/utils/urls";


publicWidget.registry.carousel = publicWidget.Widget.extend({
    selector: '.dynamic_snippet_template',
    events: {

             "mouseenter .o_carousel_product_card": "_onHover",
             "mouseleave .o_carousel_product_card ": '_onMouseOut',
    },

    _onHover: async function (ev) {

        var element = ev.currentTarget;
         $('.product_prev_carousel').empty();

        console.log(element,"elementelementelementelementelement")
        var InputElement = element.querySelector('input');
        var odxPrevElement = $(element).find('#prev_carousel');
        var ad_modal =$(odxPrevElement).find('.ad_modal');
        var res_id = ad_modal.attr('data-product-id');


        var popHtmlElement = odxPrevElement.find('#pop_html_carousel');


        $('#pop_html').empty();
        $('.product_prev').empty();


        var content = url("/web/content", {
                model: 'product.product',
                field: 'branding_image',
                id: res_id,
            })

        var modalHtml ="<img src="+content+"  style='background-color:transparent ;height:auto;width:74%; object-fit: contain; margin-left: 75px;box-shadow: 0px 4px 8px rgba(0, 0, 0, 1.0);' />";


        odxPrevElement.addClass('prev_product_carousel');
        popHtmlElement.addClass('product_prev_carousel');
        $('.product_prev_carousel').append(modalHtml);
        $('.prev_product_carousel').modal('show');


        var carousel = $('#s_dynamic_snippet_1').carousel();
        carousel.carousel('pause');


    },

    _onMouseOut: function (){
        $('.product_prev_carousel').empty();
        $('.prev_product_carousel').modal('hide');
        $('#prev_carousel').modal('hide');
        $('.prev_product_carousel').removeClass('prev_product_carousel');
        $('.product_prev_carousel').removeClass('product_prev_carousel');

    },


  });
