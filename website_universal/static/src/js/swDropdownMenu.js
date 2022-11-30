odoo.define('website_universal.swDropdownMenu', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var datas = require('website_universal.comman');
var core = require('web.core');
var _t = core._t;

publicWidget.registry.swDropdownMenurWidget = publicWidget.Widget.extend({
		selector: '*[data-drop-down-menu="true"]',
		init: function () {
			this.opts = {
				activeCls: 'active',
				preventDefault: true,
				closeOnBody: true,
				blockedElements: '.blocked--link'
			};
			this._super.apply(this, arguments);
		},
		start:function(){
			var me = this;
			$.extend(me, datas);
			me.registerEventListeners();
			me.$el.data('plugin_data_swDropdownMenu', me);
			this._super.apply(this, arguments);  
		},
		onClickMenu: function(event) {
			var me = this;
			me.applyDataAttributes();
			if ($(event.target).is(me.opts.blockedElements)) {
				return;
			}
			if (me.opts.preventDefault) {
				event.preventDefault();
			}
			me.$el.toggleClass(me.opts.activeCls);
			if (me.opts.closeOnBody) {
				event.stopPropagation();
				$('body').bind( "touchstart click", function(event) {
					me.onClickBody(event);
				});
			}
		},
		registerEventListeners: function(ev){
			var me = this;
			me.$el.bind('click', $.proxy(me.onClickMenu, me));
		},
		onClickBody: function(event) {
			var me = this;
			if ($(event.target).is(me.opts.blockedElements)) {
				return;
			}
			// event.preventDefault();
			me.$el.removeClass(me.opts.activeCls);
		},
	});
});