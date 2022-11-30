odoo.define('website_universal.reimo_wishlist', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var wSaleUtils = require('website_sale.utils');
var ProductWishlist = require('website_sale_wishlist.wishlist');

var core = require('web.core');
var _t = core._t;

wSaleUtils.animateClone = function($cart, $elem, offsetTop, offsetLeft) {
	$cart.find('.o_animate_blink').addClass('o_red_highlight o_shadow_animation').delay(500).queue(function () {
		$(this).removeClass("o_shadow_animation").dequeue();
	}).delay(2000).queue(function () {
		$(this).removeClass("o_red_highlight").dequeue();
	});
	if($cart.length && $cart.hasClass('o_wsale_my_wish')){
		offsetTop = -95;
		offsetLeft = 20;
	}
	return new Promise(function (resolve, reject) {
		var $imgtodrag = $elem.find('img').eq(0);
		if ($imgtodrag.length) {
			var $imgclone = $imgtodrag.clone()
				.offset({
					top: $imgtodrag.offset().top,
					left: $imgtodrag.offset().left
				})
				.addClass('o_website_sale_animate')
				.appendTo(document.body)
				.animate({
					top: $cart.offset().top + offsetTop,
					left: $cart.offset().left + offsetLeft,
					width: 75,
					height: 75,
				}, 1000, 'easeInOutExpo');

			$imgclone.animate({
				width: 0,
				height: 0,
			}, function () {
				resolve();
				$(this).detach();
			});
		} else {
			resolve();
		}
	});
};

});