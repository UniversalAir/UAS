odoo.define('website_universal.ajax_cart', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var wSaleUtils = require('website_sale.utils');
var  websiteSaleCartLinkSale = require('website_sale.cart');
// var  QuickViewDialog = require('website_universal.QuickViewDialog');
var core = require('web.core');
var _t = core._t;
	
	wSaleUtils.updateCartNavBar = function(data) {
		var amount_total = data.amount_total;
		var $universal_qtyNavBar = $(".header-cart .cart-contents .cart_qty");
		var cart_amount = $(".header-cart .cart-contents .cart_amount:visible");
		cart_amount.html(amount_total);
		_.each($universal_qtyNavBar, function (qty) {
	        var $qty = $(qty);
		        // $qty.parents('li:first').removeClass('d-none');
		        $qty.html(data.cart_quantity).hide().fadeIn(600);
	    });
	    var $qtyNavBar = $(".my_cart_quantity");
	    _.each($qtyNavBar, function (qty) {
	        var $qty = $(qty);
	        $qty.parents('li:first').removeClass('d-none');
	        $qty.html(data.cart_quantity).hide().fadeIn(600);
	    });
	    $(".js_cart_lines").first().before(data['website_sale.cart_lines']).end().remove();
	    $(".js_cart_summary").first().before(data['website_sale.short_cart_summary']).end().remove();
	}

	publicWidget.registry.websiteSaleCartLink.include({
		selector: 'header .header_show_cart_popover',
		start: function () {
	        this.$el.popover({
	            trigger: 'manual',
	            animation: true,
	            html: true,
	            title: function () {
	                return _t("My Cart");
	            },
	            container: 'body',
	            placement: 'top',
	            template: '<div class="popover mycart-popover" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>'
	        });
	        return this._super.apply(this, arguments);
	    },
	});
	// publicWidget.registry.WebsiteSale.include({
    //     events: _.extend(publicWidget.registry.WebsiteSale.prototype.events, {
    //         'click .add_to_cart_ajax_js': 'ajax_cart_add_to_cart',
    //         'click .quick_views_open': '_onClickQuickView'
    //     }),
    //     ajax_cart_add_to_cart: function(ev){
    //     	debugger;
    //         var $form = $(ev.target).closest('form');
    //         var product_id = parseInt($form.find("input[name='product_id']").val(), 10);
    //         var qty = parseInt($form.find("input[name='add_qty']").val(), 10);
    //         var $navButton = $('header .header-cart .cart-toggle:visible').first();
    //         this._rpc({
    //             route: "/shop/cart/update_json",
    //             params: {
    //                 product_id: product_id,
    //                 add_qty: qty
    //             },
    //         }).then(function (data) {
    //             if(data.cart_quantity){
    //                 wSaleUtils.updateCartNavBar(data);
    //                 wSaleUtils.animateClone($navButton, $form, -95, 20);   
    //             }
    //         });
    //     },
    //     _onClickQuickView: function(ev){
    //     	debugger;
    //     	this.QuickViewDialog = new QuickViewDialog(this, {
	//             productID: parseInt($(ev.currentTarget).attr('data-product-id'))
	//         }).open();
    //     }
    // });

});