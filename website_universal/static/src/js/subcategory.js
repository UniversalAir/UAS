odoo.define('website_universal.swSubCategoryNav', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
	publicWidget.registry.swSubCategoryNavWidget = publicWidget.Widget.extend({
		selector: '*[data-subcategory-nav="true"]',
		events: {
			'click a.link--go-forward, a.is_back_button': 'select_categories'
		},
		init: function () {
			this._super.apply(this, arguments);
		},
		start: function(ev){
			this._super.apply(this, arguments);
		},
		select_categories: async function(ev){
			ev.preventDefault();
			ev.stopPropagation();
			var self = this;
			this._rpc({
				route: $(ev.currentTarget).data('fetchurl'),
			}).then(function(data){
				self.$el.parent().find('.shop_department_main').slideToggle( "hide", function() {
					self.$el.find('.categories_dropdwon_cl').replaceWith(data);
					self.$el.parent().find('.shop_department_main').slideToggle("show");
				});
			});
		}
	});
});