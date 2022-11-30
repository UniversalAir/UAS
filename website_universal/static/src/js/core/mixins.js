odoo.define('website_universal.mixins', function (require) {
"use strict";

const ajax = require('web.ajax');
let wUtils = require('website.utils');
let { Markup} = require('web.utils');
let {qweb, _t} = require('web.core');
let {updateCartNavBar} = require('website_sale.utils');
// const { CartSidebar } = require('theme_prime.sidebar');


let ProductCarouselMixins = {
    _bindEvents: function ($target) {
        // Resolve conflict when multiple product carousel on same page
        const $carousel = $target.find('#o-carousel-product');
        $carousel.addClass('d_shop_product_details_carousel');
        $carousel.find('.carousel-indicators li').on('click', ev => {
            ev.stopPropagation();
            $carousel.carousel($(ev.currentTarget).index());
        });
        $carousel.find('.carousel-control-next').on('click', ev => {
            ev.preventDefault();
            ev.stopPropagation();
            $carousel.carousel('next');
        });
        $carousel.find('.carousel-control-prev').on('click', ev => {
            ev.preventDefault();
            ev.stopPropagation();
            $carousel.carousel('prev');
        });
    },
};


return {
    ProductCarouselMixins: ProductCarouselMixins,
};
});
