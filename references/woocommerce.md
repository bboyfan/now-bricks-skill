# WooCommerce

Woo templates, elements (real registered names), and dynamic data. Verified against `includes/woocommerce/` + `provider-woo.php` (2.3.6). Elements load only when WooCommerce is active.

## Template types

| Type | Replaces |
|------|----------|
| `wc_archive` | shop / category / tag archives |
| `wc_product` | single product |
| `wc_cart` / `wc_cart_empty` | cart / empty cart |
| `wc_form_checkout` / `wc_form_pay` | checkout / pay page |
| `wc_thankyou` / `wc_order_receipt` | order received / receipt |
| `wc_account_dashboard` `wc_account_orders` `wc_account_view_order` `wc_account_downloads` `wc_account_addresses` `wc_account_form_edit_address` `wc_account_form_edit_account` `wc_account_form_login` `wc_account_form_lost_password` `wc_account_form_lost_password_confirmation` `wc_account_reset_password` | My Account views |

## Element names (exact)

**Single product:** `product-title` `product-price` `product-rating` `product-short-description` `product-content` `product-add-to-cart` `product-gallery` `product-meta` `product-stock` `product-tabs` `product-additional-information` `product-reviews` `product-related` `product-upsells`

**Shop/archive:** `woocommerce-products` (grid with query) `woocommerce-products-filter` `woocommerce-products-orderby` `woocommerce-products-pagination` `woocommerce-products-total-results` `woocommerce-products-archive-description` `woocommerce-breadcrumbs`

**Cart:** `woocommerce-cart-items` `woocommerce-cart-collaterals` (totals) `woocommerce-cart-coupon` `woocommerce-mini-cart`

**Checkout:** `woocommerce-checkout-customer-details` `woocommerce-checkout-order-review` `woocommerce-checkout-order-payment` `woocommerce-checkout-order-table` `woocommerce-checkout-coupon` `woocommerce-checkout-login` `woocommerce-checkout-thankyou`

**Account:** `woocommerce-account-page` `woocommerce-account-orders` `woocommerce-account-view-order` `woocommerce-account-downloads` `woocommerce-account-addresses` `woocommerce-account-payment-methods` `woocommerce-account-add-payment-method` `woocommerce-account-form-login` `woocommerce-account-form-register` `woocommerce-account-form-edit-account` `woocommerce-account-form-edit-address` `woocommerce-account-form-lost-password` `woocommerce-account-form-reset-password`

**Misc:** `woocommerce-notice` `woocommerce-template-hook` (render any Woo hook output)

## Dynamic data tags (exact)

`{woo_product_price}` `{woo_product_regular_price}` `{woo_product_sale_price}` `{woo_product_sku}` `{woo_product_stock}` `{woo_product_stock_status}` `{woo_product_rating}` `{woo_product_excerpt}` `{woo_product_on_sale}` `{woo_product_type}` `{woo_product_images}` `{woo_product_gallery_images}` `{woo_product_cat_image}` `{woo_product_badge_new}` `{woo_add_to_cart}` (URL)
Cart: `{woo_cart_product_name}` `{woo_cart_quantity}` `{woo_cart_subtotal}` `{woo_cart_remove_link}` `{woo_cart_update}`
Order (thank-you/receipt context): `{woo_order_id}` `{woo_order_number}` `{woo_order_date}` `{woo_order_total}` `{woo_order_email}` `{woo_order_payment_title}`
Account: `{woo_my_account_endpoint}`

Image-type tags work in image controls: `"image": { "useDynamicData": "{woo_product_images}", "size": "woocommerce_thumbnail" }`.

## Custom product grid (preferred over `woocommerce-products`)

Query loop on a block (full layout control + query filters work):

```json
{
  "settings": {
    "hasLoop": true,
    "query": { "objectType": "post", "post_type": ["product"], "posts_per_page": "12",
               "orderby": "menu_order", "order": "ASC" }
  }
}
```

Card children: image (`{woo_product_images}`), `product-title`-style heading (`{post_title}`), `text-basic` price (`{woo_product_price}`), `product-add-to-cart` or button with `{woo_add_to_cart}` link.

- Sale badge: `text-basic` "Sale" with `_conditions` on `woo_product_sale == "1"` (or `{woo_product_on_sale}`), absolutely positioned.
- On-sale-only loop (PHP): `'post__in' => wc_get_product_ids_on_sale()` via `bricks/posts/query_vars`.
- Featured: tax_query_advanced on `product_visibility` field `name`, terms `["featured"]`.
- Price filters: `filter-range` on `customField` key `_price` (see query-filters.md).

## Single product template (`wc_product`)

Standard composition: section → container → two-col (`product-gallery` | details column: `product-title`, `product-rating`, `product-price`, `product-short-description`, `product-add-to-cart`, `product-meta`) → full-width `product-tabs` → `product-related`. Set builder preview: `templatePreviewType: "single"` + a product `templatePreviewPostId`.

## Quick view popup

Popup template settings: `"popupAjax": true, "popupIsWoo": true` with single-product elements inside. Trigger from the product card:

```json
"_interactions": [
  { "id": "qkv001", "trigger": "click", "action": "show", "target": "popup",
    "templateId": 123, "popupContextType": "post", "popupContextId": "{post_id}" }
]
```

## Conditions & interactions (Woo-specific)

- Conditions: `woo_product_sale`, `woo_product_stock_status`, `woo_product_type`, `woo_product_featured`, `woo_product_category`… (see conditions.md)
- Interaction triggers: `wooAddedToCart` `wooAddingToCart` `wooRemovedFromCart` `wooUpdateCart` `wooCouponApplied` `wooCouponRemoved` — e.g. open the mini-cart offcanvas on `wooAddedToCart`.

## PHP hooks

```php
// Product queries
add_filter( 'bricks/posts/query_vars', function( $vars, $settings, $element_id ) {
    if ( ( $vars['post_type'][0] ?? '' ) === 'product' ) {
        $vars['meta_query'][] = [ 'key' => '_stock_status', 'value' => 'instock' ];
    }
    return $vars;
}, 10, 3 );

// Checkout fields (standard Woo)
add_filter( 'woocommerce_checkout_fields', fn( $fields ) => $fields );
```

Mini-cart fragments refresh on `added_to_cart` / `wc_fragment_refresh` jQuery events as usual.
