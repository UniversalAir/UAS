odoo.define('website_universal.slider', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;

	publicWidget.registry.SwOwlsliderWidget = publicWidget.Widget.extend({
		selector: '*[data-swowl_slider="true"]',
		events:{

		},
        init: function () {
        	this._super.apply(this, arguments);
        	this.opts = {};
        },
        start:function(){
        	this.opts = this.$el.data();
        	if(this.opts['ajaxurl'] == true){
        		if(this.opts['domain']){
        		 	this.opts['domain'] = JSON.stringify(this.opts['domain']);
        		}
        		this.fetch_products();
        	}
        	this._super.apply(this, arguments);  
        },
        fetch_products: function(e){
        	var self = this;
        	$.ajax({
                    url: '/fetch/products_items',
                    type: 'http',
                    method: 'POST',
                    dataType: 'html',
                    data: this.opts,
                    success: function(result) {
                    	if(result.trim().length){
                    		self.$el.closest('.oe_website_sale').removeClass('d-none');
                        	self.carosel_start_data(result);
                    	}
                    }
            });
        },
        carosel_start_data: function(result){
        	this.$el.html(result);
        	this.$el.owlCarousel({
			    loop:false,
			    margin:4,
			    nav:true,
			    dots: false,
			    responsive:{
			        0:{
			            items:1
			        },
			        600:{
			            items:2
			        },
			        1000:{
			            items:4
			        }
			    }
			});
        },
    });

	publicWidget.registry.widget_product_categories = publicWidget.Widget.extend({
		selector: '.widget_product_categories',
		events:{
			'click .cat-parent > a': "on_click_toggle",
			'click .cat-parent > a > span.toggle': "toggle_child_elm"
		},
        init: function () {
        	this._super.apply(this, arguments);
        	this.opts = {};
        },
        start:function(){
        	this.$el.find('.cat-parent > a').append('<span class="toggle"></span>');
			this.$el.find('.current-cat').parents('.cat-parent').addClass('animate').children('a').addClass('active');
			this.$el.find('.current-cat').parents('.cat-parent').children('a').addClass('animate').children('span.toggle').addClass('active');
			this.$el.find('.current-cat').parents('ul.children').stop().slideDown(300);
        	this._super.apply(this, arguments);  
        },
        on_click_toggle: function(ev){
        	$(ev.currentTarget).toggleClass('active');
			if ($(ev.currentTarget).parent().next('.children').length != 0) {
				$(ev.currentTarget).parent().toggleClass('animate');
				$(ev.currentTarget).parent().next('.children').stop().slideToggle(300, "easeOutExpo");
			};
			// ev.preventDefault();
        },
        toggle_child_elm: function(e){
        	e.stopImmediatePropagation();
			$(e.currentTarget).toggleClass('active');
			if ($(e.currentTarget).parent().next('.children').length != 0) {
				$(e.currentTarget).parent().toggleClass('animate');
				$(e.currentTarget).parent().next('.children').stop().slideToggle(300, "easeOutExpo");
			};
			e.preventDefault();
        }
	});

	publicWidget.registry.widget_tabs_info = publicWidget.Widget.extend({
		selector: '.description_info_tabs',
		events:{
			'click .tabs > li > a': "on_click_tabs_toggle",
			'click .card-header-tabs > li > a': "on_click_nav_toggle",
		},
        init: function () {
        	this._super.apply(this, arguments);
        },
        start:function(){
        	this._super.apply(this, arguments);  
        },
        on_click_tabs_toggle: function(ev){
        	this.$el.find('.tabs > li').removeClass('active');
        	this.$el.find('.woocommerce-Tabs-panel').css('display','none');
        	var tabid = $(event.target).parent().attr('aria-controls');
        	$(event.target).parent().addClass('active');
        	this.$el.find(".woocommerce-Tabs-panel[id='"+tabid+"']").css('display', 'block');
        },
        on_click_nav_toggle: function(ev){
        	this.$el.find('.card-header-tabs > li > a').removeClass('active');
        	this.$el.find('.tab-pane').css('display','none');
        	var tabid = $(event.target).attr('aria-controls');
        	$(event.target).addClass('active');
        	this.$el.find(".tab-pane[id='"+tabid+"']").css('display', 'contents');
        },
         
	});
});