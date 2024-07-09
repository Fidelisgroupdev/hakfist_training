/** @odoo-module **/

    // require('web.dom_ready');
    import publicWidget from "@web/legacy/js/public/public_widget";

    publicWidget.registry.authsignup = publicWidget.Widget.extend({
        selector: ".field-user-type,.field-country_id",
        events: {
            'click .user_btn': 'usersignup',
            'click .company_btn': 'companysignup',
            'change #country_id': '_onChangeCountry',
        },
        start: function () {
            var defult_selected = this.$el.find('.person').is(":checked")
            if (defult_selected == true) {
                this.usersignup()
                this._onChangeCountry()
            }
        },

        usersignup: function () {
            $("div[class^='company_vat_group'] > label").remove()
            $("div[class^='company_vat_group'] > input").remove()
        },

        companysignup: function (){
            if ($('.label_vat').hasClass('label_vat') && $('.input_vat').hasClass('input_vat')) {
            }else{
                var label = '<label class="label_vat" for="vat">VAT</label>'
                var input = '<input type="text" name="vat" t-att-value="vat" id="vat" class="form-control form-control-sm input_vat" required="required"/>'
                $('div .company_vat_group').append(label)
                $('div .company_vat_group').append(input)
            }
        },

        _onChangeCountry: function(){
            var country_id = $("#country_id :selected").val();
            var temp = 0
            var country_list = []
            $("#state_id > option").each(function() {
                if ($(this).attr('country_id') == country_id){
                    $(this).removeClass('d-none')
                    country_list.push(this.value)
                    temp = temp + 1
                } else {
                    $(this).addClass('d-none')
                }
            });
            if (temp==0){
                $('#state_id').val("0")
                $(".field-state_id").addClass('d-none')
            }
            else{
                $(".field-state_id").removeClass('d-none')
                $("#state_id").val(country_list[0])
            }
        },
    });