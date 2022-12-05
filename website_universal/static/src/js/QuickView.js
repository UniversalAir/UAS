odoo.define('website_universal.product_quick_view', function (require) {
'use strict';

const ajax = require('web.ajax');
const Dialog = require('web.Dialog');
const publicWidget = require('web.public.widget');
const { ProductCarouselMixins } = require('website_universal.mixins');
const OwlDialog = require('web.OwlDialog');
var wSaleUtils = require('website_sale.utils');
	
	const QuickViewDialog = Dialog.extend(ProductCarouselMixins, {
		events: _.extend({}, Dialog.prototype.events, {
			'dr_close_dialog': 'close',
			'click .js_add_cart_json': 'change_qty',
		}),
		/**
		* @constructor
		*/
		init: function (parent, options) {
			this.productID = options.productID;
			this.variantID = options.variantID || false;
			this.mini = options.mini || false;
			this._super(parent, _.extend({ renderHeader: false, renderFooter: false, technical: false, size: 'extra-large', backdrop: true }, options || {}));
		},
		willStart: function () {
			var quickView = ajax.jsonRpc('/website_universal/get_quick_view_html', 'call', {
				options: {productID: this.productID, variantID: this.variantID, mini: this.mini}
			});
			return Promise.all([quickView, this._super(...arguments)]).then((result) => {
				if (result[0]) {
					this.$content = $(result[0]);
					this.autoAddProduct = this.mini && this.$content.hasClass('auto-add-product'); // We will not open the dialog for the single varint in mini view
					if (this.autoAddProduct) {
						this.trigger('tp_auto_add_product');
					}

				}
			});
		},
		
		change_qty:function(ev){
			ev.preventDefault();
	        var self = this;
	        var $target = $(ev.currentTarget);
	        var $modal = $target.parents('.oe_advanced_configurator_modal');
	        var $parent = $target.parents('.js_product:first');
	        $parent.find("a.js_add, span.js_remove").toggleClass('d-none');
	        $parent.find(".js_remove");

	        var productTemplateId = $parent.find(".product_template_id").val();
	        var previous_qty = $parent.find('input[name="add_qty"]').val();
	        if ($target[0].ariaLabel === 'Add one'){
	        	var currunt_qty = (previous_qty - 1)+2
	        	$parent.find('input[name="add_qty"]').val(currunt_qty)
	        }else if ($target[0].ariaLabel === 'Remove one' && previous_qty > 1){
	        	var currunt_qty = previous_qty - 1
	            $parent.find('input[name="add_qty"]').val(currunt_qty)
	        }
		},
		
		
	});
	publicWidget.registry.productQuickView = publicWidget.Widget.extend({
		selector: '.product-action-icon-link',
		read_events: {
			'click .quick_views_open': '_onClick',
			'click .add_to_cart_ajax_js' : 'ajax_cart_add_to_cart',
		},
		/**
		* @private
		* @param  {Event} ev
		*/
		_onClick: function (ev) {
			this.QuickViewDialog = new QuickViewDialog(this, {
				productID: parseInt($(ev.currentTarget).attr('data-product-id'))
			}).open();
		},
		ajax_cart_add_to_cart:function (ev) {
			var $form = $(ev.target).closest('form');
			var product_id = parseInt($form.find("input[name='product_id']").val(), 10);
			var qty = parseInt($form.find("input[name='add_qty']").val(), 10);
			var $navButton = $('header .header-cart .cart-toggle:visible').first();
			this._rpc({
				route: "/shop/cart/update_json",
				params: {
					product_id: product_id,
					add_qty: qty
				},
			}).then(function (data) {
				if(data.cart_quantity){
					wSaleUtils.updateCartNavBar(data);
					wSaleUtils.animateClone($navButton, $form, -95, 20);   
				}
			});
		},
	});

	return QuickViewDialog;
});

// odoo.define('website_universal.product_quick_view_attributes', function (require) {
// 'use strict';

// const publicWidget = require('web.public.widget');
// var core = require('web.core');
// var _t = core._t;

// publicWidget.registry.swSubCategoryNavWidget = publicWidget.Widget.extend({
// 		selector: '#my_quick_view, .auto-add-product',
// 		events: {
// 			"change input[name='name']": '_change_qty'
// 		},

// 		start:function(ev){
// 			debugger;
// 		},
// 		_change_qty:function (ev){
// 			debugger;
// 		},
// 	});

// });
