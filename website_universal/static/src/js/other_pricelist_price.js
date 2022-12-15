odoo.define('website_universal.otherpricelist_price', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

publicWidget.registry.otherPricelistPrice = publicWidget.Widget.extend({
	selector: '.js_product',
	events: {
		'change .js_add_cart_variants' : '_compute_price',
	},
	_compute_price: function(ev){
		var current_url = window.location.href;
		var myArray = current_url.split("#");
		var mtAttrs = myArray[1].replace('attr=','');
		if (mtAttrs){
			this._rpc({
				route: '/product/price',
				params:{
					'mtAttrs': mtAttrs,	
					'product_id' : parseInt(this.el.getElementsByClassName('product_template_id').product_template_id.value),
					'add_qty':parseInt(this.el.getElementsByClassName('quantity').add_qty.value),
				}
			}).then(function(result){
				if (result.price){
					$('.other_oe_price')[0].getElementsByClassName('oe_currency_value')[0].innerText = parseFloat(result.price).toFixed(2)
				}
			});
		}
	}
});

});
