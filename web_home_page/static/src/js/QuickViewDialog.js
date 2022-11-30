odoo.define('web_home_page.QuickViewDialog', function (require) {
'use strict';
	const ajax = require('web.ajax');
	const Dialog = require('web.Dialog');
	const publicWidget = require('web.public.widget');
	var QuickViewDialog = Dialog.extend({
	    events: _.extend({}, Dialog.prototype.events, {
	        'dr_close_dialog': 'close'
	    }),
	    template: 'web_home_page.product_quick_view',
	    /**
	     * @constructor
	     */
	    init: function (parent, options) {
	        this.productID = options.productID;
	        this.mini = options.mini || false;
	        this.variantID = options.variantID || false;
	        this.add_if_single_variant = options.add_if_single_variant || false;
	        this._super(parent, _.extend({renderHeader: false, renderFooter: false, technical: false, size: 'extra-large', backdrop: true}, options || {}));
	    },
	    /**
	     * @override
	     */
	    start: function () {
	        var sup = this._super.apply(this, arguments);
	        var self = this;
	        // Append close button to dialog
	        $('<button/>', {class: 'close', 'data-dismiss': "modal", html: '×'}).prependTo(this.$modal.find('.modal-content'));
	        this.$modal.find('.modal-dialog').addClass('modal-dialog-centered d_product_quick_view_dialog dr_full_dialog');
	        if (this.mini) {
	            this.$modal.find('.modal-dialog').addClass('is_mini');
	        }
	        ajax.jsonRpc('/web_home_page/get_quick_view_html', 'call', {
	            options: {productID: this.productID, variantID: this.variantID}
	        }).then(data => {
	            this.$el.find('.d_product_quick_view_loader').replaceWith(data);
	            this.trigger_up('widgets_start_request', {
	                $target: this.$('.oe_website_sale'),
	            });
	        });
	        return sup;
	    },
	});
	return QuickViewDialog;
});