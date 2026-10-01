# ACF & Custom Field Providers

Deep reference for ACF dynamic data plus Meta Box, JetEngine, Pods, Toolset, CMB2. Verified against `includes/integrations/dynamic-data/providers/` (2.3.6).

## Provider tag prefixes

| Provider | Prefix / pattern | Activates when |
|----------|------------------|----------------|
| ACF | `{acf_{field_name}}` | ACF or ACF Pro active |
| Meta Box | `{mb_{field_id}}` | Meta Box active |
| JetEngine | `{je_{field}}` | JetEngine active |
| Pods | `{pods_{field}}` | Pods active |
| Toolset | `{types_{field}}` | Toolset active |
| CMB2 | `{cmb2_{field}}` | CMB2 active |
| Native meta | `{cf_{meta_key}}` | always |
| WooCommerce | `{woo_*}` | Woo active (see woocommerce.md) |

## ACF field-type behavior

Tag is `{acf_` + field **name** (not label, not key).

| Field type | Usage | Notes |
|------------|-------|-------|
| text, textarea, number, range, email, url | `{acf_field}` | textarea: `:format` keeps line breaks → HTML |
| wysiwyg | `{acf_field}` | renders HTML; put in `text` (rich) element |
| select, radio, button_group | `{acf_field}` / `{acf_field:value}` | default returns label; `:value` returns stored value |
| checkbox | `{acf_field}` | comma-joined labels; `:value` for raw |
| true_false | `{acf_field:value}` | returns `1`/`0` — **always use `:value` in conditions** |
| image | `"image": { "useDynamicData": "{acf_field}", "size": "large" }` | works regardless of ACF return format (array/URL/ID) |
| gallery | image-gallery element: `"items": { "useDynamicData": "{acf_field}" }` | also loopable |
| file | `{acf_field}` (name/URL) · link control `{ "type": "meta", "useDynamicData": "{acf_field}" }` | `:link` wraps in anchor |
| link | `{acf_field}` → title · `{acf_field:array_value\|url}` · link control: `useDynamicData: "{acf_field}"` | return format Array recommended |
| oembed | `{acf_field}` in `html`/`text` element | outputs the embed iframe |
| post_object / relationship | as link: `{acf_field}` (title), `{acf_field:link}`; as **query loop source** | loop over related posts (below) |
| page_link | `{acf_field}` (URL) | |
| taxonomy | `{acf_field}` (term names), `:link` for linked | |
| user | `{acf_field}` (display name) | |
| date_picker / date_time_picker / time_picker | `{acf_field:M j, Y}` | pass a PHP date format filter |
| color_picker | `{ "raw": "{acf_field}" }` in any color object | |
| google_map | `{acf_field}` formatted address; map element accepts the field | |
| group | `{acf_{group}_{subfield}}` | underscore-chained; nested groups chain further |
| repeater | **loop source** + `{acf_{repeater}_{subfield}}` inside | see below |
| flexible content | loop source; `{acf_get_row_layout}` gives layout name | combine with conditions per layout |
| clone | behaves as the cloned field | |

**Options page fields** resolve automatically when the field group is assigned to an options page — same `{acf_field}` tag anywhere on the site.

## ACF repeater loops

Repeater = loop source on a block/div. Inside the loop, subfield tags resolve per row:

```json
{ "id": "loop01", "name": "block", "parent": "grid01", "children": ["nam001", "rol001", "pho001"],
  "settings": {
    "hasLoop": true,
    "query": { "objectType": "acf_team_members" }
  } }
```

The `objectType` for provider fields is the provider key the builder emits — for ACF repeaters it is the field reference shown in the builder's query type dropdown ("ACF: team_members"). When hand-authoring without builder access, the reliable pattern is:

1. Set `"objectType"` to `"acf_{repeater_field_name}"` — Bricks resolves provider loop types registered as `{provider}_{field}`.
2. Inside, use `{acf_team_members_name}`, `{acf_team_members_role}`, image control `{ "useDynamicData": "{acf_team_members_photo}" }`.
3. `{query_loop_index}` works for numbering.

Nested repeaters: inner loop element inside the outer loop, `objectType` = inner repeater tag; subfield tags chain (`{acf_outer_inner_field}`).

Relationship/post_object as loop: `"objectType": "acf_related_projects"` — inside, **standard post tags** (`{post_title}`, `{featured_image}`…) refer to each related post.

Flexible content as loop: each row is a layout; show per-layout blocks with a condition on `{acf_get_row_layout}`:

```json
"_conditions": [[ { "key": "dynamic_data", "dynamic_data": "{acf_get_row_layout}", "compare": "==", "value": "hero_block" } ]]
```

## Meta Box specifics

- Tag: `{mb_{field_id}}`; cloneable/group fields become loop sources like ACF repeaters (`"objectType": "mb_{group_id}"`), subfields `{mb_{group}_{subfield}}`.
- Image fields: `"useDynamicData": "{mb_field}"` in image controls; `:large` size filters work.
- Settings pages supported like ACF options.

## JetEngine / Pods / Toolset / CMB2

- Same pattern: provider prefix + field name; repeater-ish structures (JetEngine repeaters, Pods loops) register as loop sources.
- JetEngine listings/relations: prefer querying via post relationships or `je_` tags; complex JetEngine queries are better built with JetEngine's own components.

## Choosing fields when designing for a client site

When generating layouts that depend on custom fields:

1. Ask for (or read) the exact field names + types — tags are name-based and silently fail when wrong.
2. Default to ACF naming (`{acf_*}`) unless told otherwise.
3. For images always use the `useDynamicData` object form, never `{acf_image}` in a text setting.
4. Add `@fallback` for optional fields that have layout impact.
5. For true/false conditions append `:value`.

## PHP: registering a custom provider

```php
add_filter( 'bricks/dynamic_data/register_providers', function( $providers ) {
    $providers[] = 'my-crm'; // loads Provider_My_Crm
    return $providers;
} );
```

Class `Bricks\Integrations\Dynamic_Data\Providers\Provider_My_Crm extends Base` implementing `load_me()`, `register_tags()`, `get_tag_value( $tag, $post, $args, $context )`. For one-off tags prefer the `bricks/dynamic_tags_list` + `bricks/dynamic_data/render_tag` filters (see dynamic-data.md).
