# Dynamic Data

Tag syntax, the full WordPress tag list, filters/arguments, and where tags work in settings JSON. Provider-specific tags (ACF, Meta Box, …): acf-providers.md. Verified against `includes/integrations/dynamic-data/` (2.3.6).

## Syntax

```
{tag}
{tag:filter1:filter2}
{tag @key:'value'}
{tag:filter @fallback:'default'}
```

Colon filters are positional; `@key:'value'` arguments are named. Tags work in any text setting, and in image/link/video controls via `useDynamicData` (see below). Tags compose inside strings: `"Call us: {acf_phone}"`, `"https://wa.me/{acf_whatsapp}"`.

## WordPress tags

### Post
`{post_title}` `{post_id}` `{post_url}` `{post_slug}` `{post_type}` `{post_excerpt}` `{post_content}` `{post_date}` `{post_modified}` `{post_time}` `{post_comments_count}` `{read_more}` `{featured_image}` `{featured_image_tag}`

### Author / current user
`{author_name}` `{author_id}` `{author_bio}` `{author_email}` `{author_website}` `{author_archive_url}` `{author_avatar}`
`{wp_user_id}` `{wp_user_login}` `{wp_user_email}` `{wp_user_display_name}` `{wp_user_first_name}` `{wp_user_last_name}` `{wp_user_description}` `{wp_user_role}` `{wp_user_picture}` `{wp_user_meta:meta_key}`

### Site / page / archive
`{site_title}` `{site_tagline}` `{site_url}` `{site_logo}` `{page_title}` `{page_url}` `{archive_title}` `{archive_description}`

### Terms
`{post_terms_category}` `{post_terms_post_tag}` `{post_terms_{taxonomy}}` — linked list of the post's terms
In term loops/archives: `{term_id}` `{term_title}` `{term_name}` `{term_description}` `{term_link}` `{term_count}` `{term_meta:key}`

### Dates
`{current_date:Y-m-d}` `{current_wp_date}` `{format_date @date:'{acf_event_date}' @from:'Ymd' @to:'M j, Y'}`

### Query / filters
`{query_loop_index}` `{query_results_count}` `{query_results_count_filter}` `{active_filters_count}` `{search_term}` `{query_api @key:'data|0|title'}`

### Custom fields & code
`{cf_meta_key}` — any native postmeta
`{echo:function_name}` / `{echo:my_func('arg1', '{post_id}')}` — whitelisted PHP (below)
`{do_action:hook_name}` — fires an action, captures output

## Filters & arguments

| Filter/arg | Applies to | Effect |
|------------|-----------|--------|
| `:value` / `:label` | choice fields | raw stored value vs display label |
| `:plain` | text/html | strip tags |
| `:format` | textarea/wysiwyg | keep HTML formatting |
| `:link` | most | wrap output in a relevant `<a>` |
| `:url` | post/term/file fields | return URL instead of title/markup |
| `:image` | image-capable | render as `<img>` |
| `:{image_size}` | image tags | `{featured_image:thumbnail}`, `{acf_photo:large}` |
| `:{number}` | excerpt/content/text | word limit: `{post_excerpt:24}` |
| `:{date format}` | date tags | PHP format: `{post_date:M j, Y}` (escape colons: `Y-m-d\TH\:i)` |
| `:{separator}` | term lists | `{post_terms_category: \| }` |
| `:array_value\|key` | array-returning fields | `{acf_link:array_value\|title}` |
| `:raw` | any | output the literal tag (escape hatch) |
| `@fallback:'text'` | any | value when empty |
| `@fallback-image:123` | image contexts | fallback attachment ID/URL |
| `@start-at:1` / `@pad:2` | `{query_loop_index}` | 1-based / zero-padded |
| `@key:'a\|b\|0'` | `{query_api}`/`{query_array}` | nested array path (pipe-separated) |
| `@sanitize:false` | text | skip sanitization (trusted content only) |
| `@exclude:'f1,f2'` | counts | exclude specific query filters |

## Dynamic data in non-text controls (exact shapes)

```json
"image":       { "useDynamicData": "{acf_portrait}", "size": "large" }
"items":       { "useDynamicData": "{acf_gallery}", "size": "medium" }
"link":        { "type": "meta", "useDynamicData": "{post_url}" }
"link":        { "type": "external", "url": "mailto:{author_email}" }
"videoPoster": { "useDynamicData": "{acf_poster}", "size": "large" }
"_background": { "image": { "useDynamicData": "{featured_image}", "size": "large" } }
"text":        "{post_title}"
"code":        "{acf_embed_html @sanitize:false}"
```

Color via dynamic data: `{ "raw": "{acf_brand_color}" }` inside any color object.

## `{echo:}` security

Functions must be whitelisted:

```php
add_filter( 'bricks/code/echo_function_names', function() {
    return [
        'wp_get_attachment_image',
        'my_reading_time',
        '@^get_field', // regex: allow get_field*
    ];
} );
```

Literal names or `@`-prefixed regex. Without whitelisting, `{echo:}` outputs nothing. Arguments: single-quoted strings, commas separate, nested dynamic tags allowed: `{echo:my_func('{post_id}', 'large')}`.

## Conditions + dynamic data

`_conditions` accept dynamic data comparisons — see conditions.md:

```json
[[ { "key": "dynamic_data", "dynamic_data": "{acf_is_featured:value}", "compare": "==", "value": "1" } ]]
```

ACF true/false fields: always append `:value` to get `1`/`0` instead of the localized "Yes"/"No".

## Custom tags (PHP)

```php
// 1. Register the tag for the builder picker
add_filter( 'bricks/dynamic_tags_list', function( $tags ) {
    $tags[] = [ 'name' => '{my_stat}', 'label' => 'My Stat', 'group' => 'Custom' ];
    return $tags;
} );

// 2. Resolve it
add_filter( 'bricks/dynamic_data/render_tag', function( $tag, $post, $context ) {
    if ( $tag === 'my_stat' || $tag === '{my_stat}' ) {
        return get_option( 'my_stat_value', '0' );
    }
    return $tag;
}, 10, 3 );

// 3. Also replace inside longer content strings
add_filter( 'bricks/dynamic_data/render_content', function( $content, $post, $context ) {
    return str_replace( '{my_stat}', get_option( 'my_stat_value', '0' ), $content );
}, 10, 3 );
add_filter( 'bricks/frontend/render_data', function( $content, $post ) {
    return str_replace( '{my_stat}', get_option( 'my_stat_value', '0' ), $content );
}, 10, 2 );
```

In PHP, render any string containing tags: `bricks_render_dynamic_data( $content, $post_id, $context )` with context `text` | `image` | `link` | `media`.

## Behavior notes

- Tags resolve against the **current loop object** inside query loops (post → term → user → repeater rows switch automatically).
- Nested tags resolve up to 10 levels.
- Empty values render as empty string — pair important UI with `@fallback` or `_conditions`.
- `{post_content}` inside a post-content element of the same post would recurse — Bricks blocks it; don't nest it.
