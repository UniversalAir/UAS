odoo.define('website_universal.mobile_sidebar', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var core = require('web.core');
var _t = core._t;
	publicWidget.registry.mobile_sidebar = publicWidget.Widget.extend({
		selector: '.layout-sidebar',
		events:{

		},
        init: function () {
        	this._super.apply(this, arguments);
        	this.opts = {};
        },
        start:function(){
        	var self = this;
        	$(window).on('resize', function(){
        		self.responsiveSidebar();
        	})
        	this._super.apply(this, arguments);  
        	$(window).trigger('resize');
        },
        responsiveSidebar: function(){

			$('.layout-sidebar').each(function(){
				var $this = $(this);
				var mobile = window.matchMedia("(max-width: 1023px)");
				if (mobile.matches) {

					if (!$this.parent().find('.sidebar-toggle').length) {

						if ($this.hasClass('product-sidebar')) {
							$this.parent().prepend($('<div class="sidebar-toggle"><i class="fa fa-sliders"></i></div>'));
							// $this.parent().next().find('.top_shop_filter_bar').prepend($('<div class="sidebar-toggle"><i class="fa fa-sliders"></i></div>'));
						} else {
							$this.parent().prepend($('<div class="sidebar-toggle"><i class="fa fa-bars"></i></div>'));
						}

						$('<div class="sidebar-overlay"></div>').insertBefore($this);

						$this.prepend($('<div class="sidebar-toggle inside"><i class="fa fa-close"></i></div><div class="et-clearfix"></div>'));

						$this.parent().find('.sidebar-overlay').on('click',function(){
							$(this).removeClass('active');
							$this.removeClass('active');
							$('#et-content').removeClass('zindex');
						});

						$this.parent().find('.sidebar-toggle').on('click',function(){
							$this.toggleClass('active');
							$this.parent().find('.sidebar-overlay').toggleClass('active');
							$('#et-content').toggleClass('zindex');
						});

						$this.find('.sidebar-toggle').on('click',function(){
							$this.removeClass('active');
							$this.parent().find('.sidebar-overlay').removeClass('active');
							$('#et-content').removeClass('zindex');
						});

					}

				} else {
					$this.removeClass('active');
					$this.find('.sidebar-toggle').remove();
					$this.parent().find('.sidebar-overlay').remove();
					$this.parent().find('.sidebar-toggle').remove();
				}

			});
        }
    });
});

// $(document).ready(function(){


// var mobile = window.matchMedia("(max-width: 1023px)");
// function responsiveSidebar(){

// 	$('.layout-sidebar').each(function(){
// 		var $this = $(this);

// 		if (mobile.matches) {

// 			if (!$this.parent().find('.sidebar-toggle').length) {

// 				if ($this.hasClass('product-sidebar')) {
// 					$this.parent().prepend($('<div class="sidebar-toggle"><i class="fas fa-sliders-h"></i></div>'));
// 				} else {
// 					$this.parent().prepend($('<div class="sidebar-toggle"><i class="fas fa-bars"></i></div>'));
// 				}

// 				$('<div class="sidebar-overlay"></div>').insertBefore($this);

// 				$this.prepend($('<div class="sidebar-toggle inside"><i class="ien-eclose-3"></i></div><div class="et-clearfix"></div>'));

// 				$this.parent().find('.sidebar-overlay').on('click',function(){
// 					$(this).removeClass('active');
// 					$this.removeClass('active');
// 					$('#et-content').removeClass('zindex');
// 				});

// 				$this.parent().find('.sidebar-toggle').on('click',function(){
// 					$this.toggleClass('active');
// 					$this.parent().find('.sidebar-overlay').toggleClass('active');
// 					$('#et-content').toggleClass('zindex');
// 				});

// 				$this.find('.sidebar-toggle').on('click',function(){
// 					$this.removeClass('active');
// 					$this.parent().find('.sidebar-overlay').removeClass('active');
// 					$('#et-content').removeClass('zindex');
// 				});

// 			}

// 		} else {
// 			$this.removeClass('active');
// 			$this.find('.sidebar-toggle').remove();
// 			$this.parent().find('.sidebar-overlay').remove();
// 			$this.parent().find('.sidebar-toggle').remove();
// 		}

// 	});
// }
// responsiveSidebar();
// $(window).resize(responsiveSidebar);
// });