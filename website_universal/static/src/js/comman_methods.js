odoo.define('website_universal.comman', function (require) {
'use strict';

var menucontaint = require('website.content.menu');
var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;

publicWidget.registry.StandardAffixedHeader.include({
	init: function () {
		this._super(...arguments);
		this.scrolledPoint = 500;
	}
});
var datas = {
		applyDataAttributes: function(shouldDeserialize, ignoreList) {
			debugger;
			var me = this,
				attr;
			ignoreList = ignoreList || [];
			$.each(me.opts, function(key) {
				if (ignoreList.indexOf(key) !== -1) {
					return;
				}
				attr = me.$el.attr('data-' + key);
				if (typeof attr === 'undefined') {
					return true;
				}
				me.opts[key] = shouldDeserialize !== false ? me.deserializeValue(attr) : attr;
				return true;
			});
			return me.opts;
		},
		deserializeValue: function(value) {
				try {
					return !value ? value : value === 'true' || (value === 'false' ? false : value === 'null' ? null : numberRegex.test(value) ? +value : objectRegex.test(value) ? JSON.parse(value) : value);
				} catch (e) {
					return value;
				}
		},
	};

return datas;
});