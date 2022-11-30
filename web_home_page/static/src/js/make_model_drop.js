odoo.define('web_home_page.make_model_drop', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
	publicWidget.registry.MakeModelDrop = publicWidget.Widget.extend({
		selector: '.megamenu_my_vehicale',
        events: {
            "change select[name='car_make']": 'select_options',
            "click button": 'select_make_or_model'
        },
	    init: function () {
	    	this._super.apply(this, arguments);
	    },
	    start: function(ev){
	    	this._super.apply(this, arguments);
	    },
        select_options: async function(ev){
        	var self = this;
        	var make_id = parseInt(ev.target.value, 10);
        	this._rpc({
        		route: '/fetch/make/models',
        		params: {'make_id': make_id}
        	}).then(function(data){
        		self.$el.find("select[name='car_model']").html(data.datas);
        	});
        },
        select_make_or_model: function(){
        	var self = this;
        	var make_id = parseInt(this.$el.find("select[name='car_make']").val(), 10);
        	var model_id = parseInt(this.$el.find("select[name='car_model']").val(), 10);
        	if(model_id){
        		window.location.href = '/shop/category/' + String(model_id);
        	}else if(make_id){
        		window.location.href = '/shop/category/' + String(make_id);
        	}
        }
	});

});