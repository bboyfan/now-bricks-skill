# Element Conditions (`_conditions`)

Render an element only when conditions pass. Server-side — hidden elements produce no markup. Verified against `includes/conditions.php` (2.3.6).

## Structure: OR of ANDs

```json
"_conditions": [
  [
    { "key": "user_logged_in", "compare": "==", "value": 1 },
    { "key": "user_role", "compare": "==", "value": ["subscriber"] }
  ],
  [
    { "key": "post_id", "compare": "==", "value": "42" }
  ]
]
```

Outer array = OR groups. Inner array = AND conditions. Above: (logged-in AND subscriber) OR (post 42).

## Condition keys

### Post
| Key | Compare | Value |
|-----|---------|-------|
| `post_id` | `==` `!=` `>=` `<=` `>` `<` | post ID string |
| `post_title` | `==` `!=` `contains` `contains_not` | string |
| `post_parent` | numeric ops | parent ID |
| `post_status` | `==` `!=` | array of statuses |
| `post_author` | `==` `!=` | user ID |
| `post_date` | numeric ops | `"2026-06-11"` |
| `featured_image` | `==` `!=` | `"1"` (set) / `"0"` (not set) |

### User
| Key | Compare | Value |
|-----|---------|-------|
| `user_logged_in` | `==` `!=` | `1` (in) / `0` (out) |
| `user_id` | numeric ops | ID |
| `user_role` | `==` `!=` | array of role slugs |
| `user_registered` | `<` (after) `>` (before) | `"2026-01-01"` |

### Date & time (server timezone)
| Key | Value example |
|-----|---------------|
| `weekday` | `"1"`–`"7"` (Mon–Sun) |
| `date` | `"2026-06-11"` |
| `time` | `"2:30 PM"` |
| `datetime` | `"2026-06-11 14:30"` |

All with full numeric comparators — schedule content with a `>=` start and `<` end pair.

### Environment
| Key | Compare | Value |
|-----|---------|-------|
| `browser` | `==` `!=` | `chrome` `firefox` `safari` `edge` `opera` `msie` |
| `operating_system` | `==` `!=` | `windows` `mac` `linux` `iphone` `ipad` `android` … |
| `current_url` | `==` `!=` `contains` `contains_not` | string (query params included — use for UTM-based variants) |
| `referer` | same | string |

### Dynamic data — the universal escape hatch

```json
{ "key": "dynamic_data", "dynamic_data": "{acf_show_banner:value}", "compare": "==", "value": "1" }
{ "key": "dynamic_data", "dynamic_data": "{acf_subtitle}", "compare": "empty_not" }
{ "key": "dynamic_data", "dynamic_data": "{cf_stock_count}", "compare": ">", "value": "0" }
{ "key": "dynamic_data", "dynamic_data": "{post_terms_category:plain}", "compare": "contains", "value": "News" }
```

Comparators: `==` `!=` `>=` `<=` `>` `<` `contains` `contains_not` `empty` `empty_not` (`empty`/`empty_not` need no `value`).
ACF true/false: append `:value`. Anything you can express as a tag, you can condition on.

### WooCommerce (when active)
`woo_product_type`, `woo_product_sale` (`"1"`/`"0"`), `woo_product_stock_status` (`instock`/`outofstock`/`onbackorder`), `woo_product_stock_quantity`, `woo_product_featured`, `woo_product_rating`, `woo_product_category`, `woo_product_tag`, `woo_product_purchased_by_user`, `woo_product_sold_individually`, `woo_product_stock_management`, `woo_product_new`.

## Recipes

**Members-only block + logged-out CTA (pair):**
```json
{ "settings": { "_conditions": [[ { "key": "user_logged_in", "compare": "==", "value": 1 } ]] } }
{ "settings": { "_conditions": [[ { "key": "user_logged_in", "compare": "==", "value": 0 } ]] } }
```

**Limited-time promo:**
```json
"_conditions": [[
  { "key": "datetime", "compare": ">=", "value": "2026-06-15 00:00" },
  { "key": "datetime", "compare": "<",  "value": "2026-06-22 00:00" }
]]
```

**Show only when an optional ACF field has content:**
```json
"_conditions": [[ { "key": "dynamic_data", "dynamic_data": "{acf_video_url}", "compare": "empty_not" } ]]
```

**Empty query fallback message** (`loop01` = loop element id):
```json
"_conditions": [[ { "key": "dynamic_data", "dynamic_data": "{query_results_count:loop01}", "compare": "==", "value": "0" } ]]
```

## Notes

- Conditions hide elements **and their children**; on templates they combine with template conditions.
- Conditions run on render — cached pages won't re-evaluate per visitor unless the cache varies (mind `user_logged_in` + full-page caching).
- Builder canvas always shows conditioned elements; only the frontend hides them.

## Custom conditions (PHP)

```php
add_filter( 'bricks/conditions/groups', function( $groups ) {
    $groups[] = [ 'name' => 'membership', 'label' => 'Membership' ];
    return $groups;
} );

add_filter( 'bricks/conditions/options', function( $options ) {
    $options[] = [
        'key'     => 'mp_level',
        'group'   => 'membership',
        'label'   => 'Membership level',
        'compare' => [ 'type' => 'select', 'options' => [ '==' => '==', '!=' => '!=' ] ],
        'value'   => [ 'type' => 'select', 'options' => [ 'free' => 'Free', 'pro' => 'Pro' ] ],
    ];
    return $options;
} );

add_filter( 'bricks/conditions/result', function( $result, $key, $condition ) {
    if ( $key !== 'mp_level' ) return $result;
    $level = my_get_user_level();
    return $condition['compare'] === '!=' ? $level !== $condition['value'] : $level === $condition['value'];
}, 10, 3 );
```
