# Bricks Reference: 04 Dynamic Data And Queries



---

## Module: bricks-dynamic-data

# Bricks: dynamic data

Dynamic data tags are Bricks' `{token}` syntax for binding content to live values. They resolve at render time, bind to the current post/term/user/loop context, and support modifier chains. Getting the syntax, scope, and modifier order wrong is how most "why doesn't this show?" tickets start.

## The 8 built-in providers

Files at `includes/integrations/dynamic-data/providers/provider-*.php`.

| Provider | File | Activation | Tag prefix / pattern |
|---|---|---|---|
| WordPress core | `provider-wp.php:12` | Always | `{post_*}`, `{wp_user_*}`, `{author_*}`, `{site_*}`, `{archive_*}`, `{term_*}`, `{featured_image}`, `{cf_meta_key}`, `{echo:...}` |
| ACF | `provider-acf.php:6` | ACF installed | `{acf_fieldname}` or the field group's returned tag (ACF field name, typically) |
| WooCommerce | `provider-woo.php:8` | Woo installed | `{woo_product_type}`, `{woo_product_price}`, `{woo_product_sale_price}`, `{woo_product_stock}`, etc. |
| CMB2 | `provider-cmb2.php:6` | CMB2 installed | `{cmb2_fieldname}` |
| JetEngine | `provider-jetengine.php:6` | JetEngine installed | `{je_fieldname}` |
| Pods | `provider-pods.php:6` | Pods installed | `{pods_fieldname}` |
| Toolset | `provider-toolset.php:6` | Toolset installed | `{ts_fieldname}` |
| MetaBox | `provider-metabox.php:6` | MetaBox installed | `{mb_fieldname}` |

**Don't trust a tag prefix blindly: and don't guess.** ACF field names are whatever the field was named in WP Admin; there is no reliable naming convention. `{acf_event_date}` and `{acf_start_date}` look equally plausible and only one will resolve. The only way to know is to look.

**Required lookup before writing any provider-specific tag:**
1. Call `bricks/list-dynamic-data-tags` with a `postId` from the target post type (for example, a product, event, project, or other custom post type). The response is scoped: ACF groups only appear for posts the group is assigned to.
2. Find your field's tag in the returned list. Copy the exact `tag` string.
3. Call `bricks/preview-dynamic-tag` with that tag and the same `postId`. If `unknownTags` is non-empty, the tag doesn't exist: go back to step 2.
4. Only then write it into an element.

Skipping this and guessing produces silently-broken templates: the tag renders as literal `{acf_start_date}` text in production with no error.

## Tag syntax

```
{tag_name}
{tag_name:modifier}
{tag_name:modifier:arg}
{tag_name:modifier1:arg:modifier2:arg}
```

The **colon (`:`)** separates tag name from modifier, modifier from argument, and chained modifiers. Confirmed at `includes/integrations/dynamic-data/providers/base.php:155-220`.

**Older `|` pipe syntax:** exists for one specific case: subkey access inside `array_value`:

```
{custom_field:array_value|first_name}
```

The pipe is **not a general-purpose modifier separator**: it's an `array_value` subkey accessor. Everything else is colon. `{post_title|format}` will not work.

## Common modifiers (from `base.php`)

| Modifier | Purpose | Example |
|---|---|---|
| date format string | Format a date/time value | `{post_date:M j, Y}` |
| `:format` | Keep HTML formatting for text values | `{post_excerpt:format}` |
| `:plain` | Strip HTML | `{post_excerpt:plain}` |
| `:raw` | No processing | `{cf_featured_image:raw}` |
| `:url` | Value interpreted as URL | `{cf_link_field:url}` |
| `:value` | Raw stored value (for fields with display/value pair) | `{acf_select:value}` |
| `:array_value\|key` (ACF/Meta) | Pull one key from an array return value | `{acf_link_field:array_value\|title}` |

Modifiers are parsed into provider-specific filters; do not assume arbitrary left-to-right function composition. Verify the intended combination. Positional date formats are stored as the parser's default `meta_key`, while known flags such as `:plain`, `:raw`, and `:array_value|key` set named filter keys (`includes/integrations/dynamic-data/providers/base.php:112-224`).

## Scope binding: the loop rule

Dynamic tags bind to the **current context**, which rebinds inside loops:

- Outside a loop: current main query's post (on a singular page), or nothing (on archives without an explicit post: use archive tags).
- Inside a Posts loop: the iteration's post.
- Inside a Terms loop: the iteration's term.
- Inside a Users loop: the iteration's user.

**Writing `{post_title}` inside a Users loop gives you the outer page's post title, not the user's display name.** Use the provider-specific tag: `{wp_user_display_name}`.

Full loop-tag cheatsheet in the `bricks-query-loops` skill.

## Meta-key access: `{cf_meta_key}`

Generic WP custom-field access uses the `cf_` prefix:

```
{cf_my_custom_key}              -> the meta value
{cf_my_custom_key:raw}          -> unprocessed
{cf_date_field:format:M j, Y}   -> formatted
```

`provider-wp.php` registers known `cf_` tags in the builder picker from site meta keys, but render also treats any tag beginning with `cf_` as post meta. The meta key is the part after `cf_`.

`bricks/dynamic_data/allowed_keys` does **not** gate post meta. It controls parser keys such as `@fallback`, `@sanitize`, `@key`, `@date`, `@from`, and `@to`.

## Echo tag: the escape hatch with a capability gate

`{echo:function_name(arg1, arg2)}` calls a PHP function at render time. Full threat model in the `bricks-custom-code` skill. Short version:

- Requires global code execution to be enabled.
- Requires the function be in the `bricks/code/echo_function_names` allow-list.
- In builder calls, the current user also needs `bricks_execute_code`; on normal frontend renders, the saved tag runs for visitors if global execution is enabled and the function is allow-listed.
- Without the required gate, returns empty string silently.
- Single quotes only for string args; no nested function calls; commas separate args.

**Never `return true` from the allow-list in production**: pre-1.9.7 RCE surface.

## Provider-specific surfaces

### ACF
- Direct access: `{acf_fieldname}` (uses ACF's field name, not label).
- Field groups have to be assigned to the current post's type for the tag to resolve.
- Relationship/post-object fields need the `:array_value|` pattern or a loop:
  - In a template displaying an ACF Relationship field: drop a Posts loop inside, set query to "Include -> dynamic data -> `{acf_my_rel}`".
  - Loop iterates related posts, `{post_title}` inside binds to the current related post.
- Repeater/Flexible Content: discover the provider-backed query type through `list-query-types` and use the actual field-specific `objectType`. The outer display tag can return a row count; it is not automatically an Array-loop source. Use **bricks-query-loops** for row/subfield context. Reserve Array loops for a supported source that returns parseable array data.

### WooCommerce
Product tags resolve inside a product context: single product page, product-loop iteration, or an MCP preview call that passes a product `postId`. Cart tags such as `{woo_cart_items_count}` use the cart context instead; do not require a product loop for them. The dynamic-data parser itself does not support a `post_id` argument inside the tag.
- `{woo_product_price}` includes currency symbol.
- `{woo_product_price:value}` returns numeric only.
- Sale price `{woo_product_sale_price}`: empty if not on sale (use conditional display).

### JetEngine / Pods / Toolset / MetaBox / CMB2
Tags are registered lazily: they need the plugin's `init` hook to fire before they're available. In the builder: appear in the picker. On the frontend: depend on plugin load order. If a tag exists in builder picker but renders empty, check plugin-init priority.

## Parser keys

Dynamic data supports parser keys after the tag, such as `@fallback`, `@sanitize`, and `@key` for supported tags. It does **not** support arbitrary `@post_id`, `@term_id`, or `@user_id` context overrides in the current parser. To preview or render against a specific post through MCP, pass the `postId` parameter to `preview-dynamic-tag` or render inside the correct loop/context.

## Custom dynamic-data providers

For custom tags, use `bricks/dynamic_tags_list` to expose the tag in the picker and `bricks/dynamic_data/render_tag` to render it. The internal provider registry is filtered through `bricks/dynamic_data/register_providers`, while `bricks/dynamic_data/register_hook` only changes the WP hook Bricks uses for provider registration (`includes/init.php:158-169`, `includes/integrations/dynamic-data/providers.php:32-45`).

See the `bricks-custom-dynamic-data-providers` skill for the full pattern.

## The `[render_dynamic_data]` shortcode

Sometimes you need Bricks-style dynamic data outside Bricks templates: in a widget, or shortcode-placement area.

```
[render_dynamic_data content="Hello {user_display_name}, welcome to {site_title}."]
```

Use this helper to render Bricks dynamic data in custom PHP output.

## Verify-after-write: preview before committing

Before pasting a dynamic tag into a template setting via `update-element`, validate it with `preview-dynamic-tag`:

```
preview-dynamic-tag (tag: "{acf_my_field:plain}", postId: 42, context: "text")
-> { rendered, isEmpty, unknownTags: [] }
```

The response includes:
- `rendered`: actual rendered string (or array for `image`/`link` contexts).
- `isEmpty`: true when the rendered value is empty after trim.
- `unknownTags`: tag names that no provider recognized; **non-empty means the tag will render as literal text in production**. Treat any entry here as a hard failure: fix the tag name (use `list-dynamic-data-tags` to discover the right one) before writing.

Use this for unfamiliar expressions in a representative post context. It cannot simulate an arbitrary term/user/ACF loop row; verify those in the actual loop. Empty output can be valid missing data or a context mismatch. Reuse established evidence for unchanged expressions instead of repeating every preview.

## Silent-failure debug order

1. **Tag renders as literal `{post_title}` in output?**
   a. Provider not loaded yet (plugin init order). Check the tag in the builder picker: if absent there, provider not registered.
   b. Typo in tag name. Picker is authoritative: or call `list-dynamic-data-tags` and grep the result.
   c. Context doesn't support the tag (e.g., `{post_title}` on a term archive page without a loop).
   d. `preview-dynamic-tag` for the same tag/post returns the tag in `unknownTags`: confirms (a) or (b).

2. **Tag resolves empty on the frontend, fine in builder?**
   a. Builder preview uses a fallback post. Frontend may have no equivalent context.
   b. The field is not assigned to the current post/context, or the provider resolved an empty value.
   c. `{echo:...}` is not allow-listed, global code execution is off, or a builder preview user lacks `bricks_execute_code`.

3. **Date modifier doesn't format?**
   a. Use the date-format syntax supported by that tag; `{post_date:M j, Y}` is valid. `:format` preserves HTML for text and is not a required date-format prefix.
   b. The stored value isn't a date parseable by `strtotime`. Check raw value first.

4. **ACF Relationship field shows post id, not title?**
   a. You're using `{acf_rel}` directly: that's the raw post id array. Wrap in a Posts loop or use `:array_value|` patterns.

5. **Loop-scope tag wrong: shows outer page data?**
   a. You're using a Posts-loop tag inside a Users loop (or vice versa). Use provider-specific tags.

6. **Tag works on one page, not another?**
   a. Plugin provider not active on that page (rare: plugin scope usually global).
   b. Post type doesn't have the field assigned (ACF field group scope).

## Never do

- Mix `:` and `|` as if they're interchangeable. Colon is the separator; pipe is only for `array_value|key`.
- Expect `{post_title}` inside a Users loop to give you the user's name. Use `{wp_user_display_name}`.
- Use `{echo:...}` as a general-purpose function caller without seeing the `bricks-custom-code` skill first: echo is a security surface.
- Hard-code the tag name for a third-party field without confirming in the builder's dynamic-data picker. Prefixes change.
- Assume `bricks/dynamic_data/allowed_keys` protects post meta. It only controls parser keys; avoid exposing sensitive meta through `cf_` tags or custom providers.


---

## Module: bricks-query-loops

# Bricks: query loops

A query loop makes one element render N times: once per post, term, user, API item, array entry, provider-backed field row or relation, WooCommerce cart item, or custom source.

## Where loops can live

The layout elements Container, Section, Block, and Div expose `hasLoop` and
`query`. The classic Accordion and Slider have their own query controls. For
nestable sliders, accordions, and tabs, repeat the appropriate child layout element;
do not assume the parent widget exposes `hasLoop`. Check its runtime schema before
writing (`includes/elements/container.php`, `accordion.php`, `slider.php`, and
`includes/abilities/element-settings-schema.php`).

## Discover the live query types first

Do not hard-code the query type list. Bricks seeds `queryTypes` with five built-ins, then runs the `bricks/setup/control_options` filter. Dynamic-data providers and plugins can register more `objectType` values at runtime.

When MCP abilities are available, call `bricks/list-query-loop-types` before choosing a non-core loop type. If it is not exposed as a direct tool, call it through `mcp_adapter_execute_ability`:

```json
{
  "ability_name": "bricks/list-query-loop-types",
  "parameters": {}
}
```

Use the returned `items[].objectType` values as the source of truth. If the ability is unavailable on an older branch, use `bricks/list-cms-sources`, `bricks/list-dynamic-data-tags`, and the provider docs as supporting context, but do not invent exact provider object keys.

## Grid and flex layouts with query loops

The element with `hasLoop: true` **is the repeating item**. It renders once per loop item. To lay repeated cards out together, their shared grid/flex container belongs on a non-looping parent. A repeated card can also use grid/flex internally to arrange its own children.

**Correct: grid container is the PARENT of the loop element:**

```
div  (grid container: display grid, repeat(3,1fr), no loop)
  `-- div  (hasLoop: true, query)   <- repeats once per post as a grid cell
        `-- card content
```

**Wrong: grid CSS on the loop element itself:**

```
div  (hasLoop: true, query, display grid, repeat(3,1fr))   <- WRONG
  `-- card content
```

Result of the wrong pattern: N separate 3-column grids each containing 1 card, all stacking vertically: a single tall column instead of a grid.

For an intended multi-card grid, insert a non-looping parent element, move the grid/flex CSS to that parent, and keep the loop element as the cell template inside it. In the builder this means wrapping the loop element in a Div or Block before enabling "Use Query Loop." Via MCP it means the `set-page-elements` tree has a plain container parent before the element that carries `hasLoop: true`.

## Query types

Built-in seed types:

| `objectType` | Engine | When to use |
|--------------|--------|-------------|
| `post` | `WP_Query` | Posts, pages, CPTs, products, media attachments. Default. |
| `term` | `WP_Term_Query` | Taxonomy archives, category grids. |
| `user` | `WP_User_Query` | Team pages, author directories. |
| `api` | Bricks Query API | Remote JSON/data sources configured in the Query API controls. |
| `array` | Bricks array parser | A JSON/bracket array string from controls or dynamic data. |

Provider and filter-added types can also appear:

| Pattern | Source | Notes |
|---------|--------|-------|
| `acf_*` | ACF provider | Relationship, Post Object, Repeater, and Flexible Content fields. Exact keys come from the field name/path. |
| `mb_*` | Meta Box provider | Post fields, group fields, and relationships. |
| `je_*`, `je_relation_*` | JetEngine provider | Repeater/posts fields and relations. |
| `wooCart` | WooCommerce | Current cart contents. |
| any custom key | `bricks/setup/control_options` plus `bricks/query/run` | Plugins can register their own loop types. |

`includes/setup.php:1120-1126` is only the seed list. The final list is produced after `bricks/setup/control_options` runs. Media is not a separate `objectType`: it is a Posts loop where `post_type` is `attachment`. Custom Query is also not an `objectType`; it is the PHP editor mode available for `post`, `term`, and `user` queries.

### Posts: the common gotchas

- **Always add `ID` as the secondary order-by** when using any non-ID primary (date, title, random). Without it, paginated pages can duplicate posts across pages.
- **"Disable Query Merge"** must be ON for header/footer/sidebar loops. Bricks auto-merges the archive/search query into the "main" loop on those pages: leaving it off turns every loop on the page into the same results.
- **Only one archive main query per page.** Bricks scans elements in builder order and uses the first loop marked `is_archive_main_query` to prepare the archive main query (`includes/database.php:222-287`). Do not mark a second loop as the archive main query: pagination and Query Filters will target the main query id Bricks selected, not a competing loop.
- **Random ordering + pagination**: set `Random seed TTL` to a non-zero value. Otherwise the random seed resets between pages and the same post appears on page 1 and page 2. Set to `0` to disable.
- **Include / Exclude with dynamic data** (v1.12+): the post type on the loop must match the field's referenced post type. Gallery fields -> Media. Relationship fields -> matching CPT. Mismatch returns no results, silently.

### Media attachments: the `{featured_image}` trap

In an attachment loop, use `{post_id}` for the image source and `{post_title}` for alt/title. **`{featured_image}` does not work for attachment items**: attachments don't have featured images of their own. Use a Posts query with `post_type` set to `attachment`.

### Provider-backed field loops

ACF, Meta Box, and JetEngine loop types are not generic labels like "ACF Repeater." They are exact runtime `objectType` keys such as `acf_team_members`, `mb_project_gallery`, or `je_relation_12`.

- ACF registers loop-capable fields: Relationship, Post Object, Repeater, and Flexible Content. Flexible Content loops can expose `acfFlexiblePreviewMode`.
- Meta Box registers loop-capable Post fields, Group fields, and relationships.
- JetEngine registers loop-capable Repeater/Posts fields and relations.
- Provider-backed loops use `bricks/query/run` and bind loop context through `bricks/query/loop_object`, `bricks/query/loop_object_id`, and `bricks/query/loop_object_type`.

### Array data

Array loops use `objectType: "array"` plus `arrayEditor` content. Use this for a literal JSON/bracket array string or dynamic data that resolves to array-like data. Provider loops such as ACF repeaters usually have their own `acf_*` object type; only use `array` for them when you intentionally feed their data into the array parser.

```
{query_array}                     -> current array entry (root)
{query_array @key:'cars'}         -> specific key's value
```

To loop through a nested array inside the parent loop: nest another Array Loop element, set `arrayEditor` to `{query_array @key:'cars'}`. Array-result filters (`array_conditions`) apply to `array` and to provider object types reported by Bricks as array-condition capable.

### Custom Query (PHP)

- Builder authoring requires the Bricks code-execution capability. Creating or changing Query editor PHP through abilities additionally requires the PHP opt-in and Application Password authorization in [bricks-custom-code](../bricks-custom-code/SKILL.md#code-authoring-through-abilities).
- For post, term, and user object types, the editor expects a PHP array of query args. Non-array output is ignored after validation and Bricks continues with the remaining query vars, which may produce an empty loop depending on context.
- Don't use this for things the normal Posts loop or query hooks can do. It is harder to audit and debug.

## The loop-marker trap (critical)

Bricks marks query-loop output so frontend AJAX pagination, Load More, Infinite Scroll, and Query Filters can swap the right DOM region.

Current source flow:

- Server render adds a `data-brx-loop-start` marker to the loop wrapper (`includes/query.php`).
- Frontend JS converts that marker to a comment shaped like `<!--brx-loop-start-{queryId}-->` (`src/assets/js/frontend.js`).

If cached or optimized HTML removes Bricks loop markers, AJAX swaps silently fail. Check both page source for `data-brx-loop-start` and the live DOM for `<!--brx-loop-start-...-->`. Configure optimization plugins to preserve Bricks loop markers.

## Loop-context dynamic tags

Inside a loop, the current post/term/user context rebinds so these tags resolve against the loop iteration, not the outer page:

**Posts loop:** `{post_id}`, `{post_title}`, `{post_excerpt}`, `{post_content}`, `{post_date}`, `{post_modified}`, `{featured_image}`, taxonomy-specific `{post_terms_{taxonomy}}`, and custom fields as `{cf_meta_key}` after lookup.

**Terms loop:** `{term_id}`, `{term_name}`, `{term_url}`, `{term_description}`, `{term_meta:key}`.

**Users loop:** `{wp_user_display_name}`, `{wp_user_email}`, `{wp_user_id}`, `{wp_user_meta:key}`

**API loop (v2.1+):** `{query_api @key:'title|rendered'}` for nested API data.

**Array loop (v2.2+):** `{query_array}`, `{query_array @key:'name'}`

**Provider-backed loops:** use provider dynamic tags for fields, and post tags when the provider maps the loop object to a `WP_Post` (for example ACF Relationship/Post Object or WooCommerce cart products). Preview dynamic tags against a real context before writing them into a reusable template.

Outside a loop these tags fall back to the current main query: which on an archive is the archive query, on a single post is that post, on a homepage is usually nothing. Always verify the context you expect.

**Tip: hide an outer section when a loop has no results.** Add an element condition to the non-looping wrapper using dynamic data `{query_results_count:LOOP_ELEMENT_ID}` with `compare: ">"` and `value: "0"`. `LOOP_ELEMENT_ID` is the raw Bricks id of the target loop element, not `brxe-...` and not a global query id. This controls server-rendered visibility; AJAX query filters do not rerun element conditions client-side.

## Custom queries via PHP hooks

If the UI can't express what you need, hook into the query pipeline. Don't reach for "Custom Query (PHP)" first: hooks are safer and don't require the code-execution capability on the user.

| Hook | Type | What it does |
|------|------|--------------|
| `bricks/posts/query_vars` | filter | Mutate `WP_Query` args for any Posts loop |
| `bricks/terms/query_vars` | filter | Same for `WP_Term_Query` |
| `bricks/users/query_vars` | filter | Same for `WP_User_Query` |
| `bricks/query/run` | filter | Short-circuit the query: return a custom array of items |
| `bricks/query/result` | filter | Mutate the result array post-fetch, pre-render |
| `bricks/query/result_count` | filter | Override the count (pagination uses this) |
| `bricks/query/result_max_num_pages` | filter | Override max pages for pagination |
| `bricks/query/loop_object` | filter | Swap the object the current iteration binds to |
| `bricks/query/loop_object_id` | filter | Swap just the id |
| `bricks/query/loop_object_type` | filter | Swap the type (post / term / user) |
| `bricks/query/no_results_content` | filter | Custom "no results" output |
| `bricks/query/before_loop` | action | Fires once before the loop renders |
| `bricks/query/after_loop` | action | Fires once after |
| `bricks/query/init_loop_index` | filter | Override starting index |
| `bricks/posts/merge_query` | filter | Control auto-merge behavior for Posts loops |

Most query lifecycle hooks pass the loop's `$query` object. `$query->element_id` scopes those callbacks to one loop. The `posts/terms/users/query_vars` filters pass query vars plus settings, element id, and element name, so check the signature before writing the callback.

## Debugging: "my loop shows nothing"

Check in this order:

1. **Did you click Save on the page?** Loop configs live in the element settings of the page, not in global state.
2. **Does the query return results outside Bricks?** Run the equivalent `WP_Query` in a plain template or via `wp shell`. If zero, the query is wrong, not Bricks.
3. **Is "Disable Query Merge" needed?** (Header/footer/sidebar loops almost always.)
4. **Does the loop element itself have visible content?** A Block with no children, set to "Use Query Loop", renders N invisible blocks.
5. **Are the loop's inner dynamic tags actually loop-aware?** `{post_title}` inside a Users loop resolves to the outer post, not the current user. You want `{wp_user_display_name}`.
6. **Is there a performance plugin or cache layer stripping loop markers?** See the loop-marker trap above.
7. **Is the include/exclude field post-type aligned?** (See Posts gotchas.)
8. **For provider-backed loops, is the exact `objectType` present in `bricks/list-query-loop-types`?** If not, the provider, field location, or runtime context is missing.
9. **Is there a `bricks/query/run` filter hooked somewhere returning `null` or `[]`?** Check theme code and any custom plugins.

If every Array loop item displays the same value, verify that the tag matches the loop that owns the value. Use `{query_array}` or `{query_array @key:'name'}` for the current Array loop item; use a parent loop tag such as `{post_title}` only for values owned by the parent.

## Never do

- Put the layout that distributes repeated cards on their non-looping parent. Grid/flex on an individual looping card is valid for its internal layout.
- **Don't loop a Template element inside another loop**: templates can't inherit loop context without explicit passing. Use a Block wrapping the content instead.
- **Don't guess provider `objectType` values from field labels.** Read the runtime list and use the exact key.
- **Prefer a scoped query hook** for reusable PHP query logic.
- Nested related-post loops can be appropriate, but run an additional query per outer item. Bound result counts, preserve the correct outer/inner context, and measure repeated-query cost before introducing caching or a different query structure.


---

## Module: bricks-query-filters

# Bricks: query filters

Connect each filter to its target query and verify indexing for sources that require it.

## The 8 filter elements

Defined at `includes/query-filters.php:705-716` and `includes/elements/filter-*.php`.

| Element | `$name` | Use when | Filter type |
|---|---|---|---|
| Filter - Checkbox | `filter-checkbox` | Multi-select values, taxonomies | `checkbox` |
| Filter - Radio | `filter-radio` | Single-select value | `radio` |
| Filter - Select | `filter-select` | Single-select dropdown | `select` |
| Filter - Range | `filter-range` | Numeric range (price, rating) | `range` |
| Filter - Search | `filter-search` | Text search across fields | `search` |
| Filter - Datepicker | `filter-datepicker` | Date range filter | `datepicker` |
| Filter - Submit / Reset | `filter-submit` | Explicit submit/reset button (non-live forms) | `apply` or `reset` (via `filterButtonType`) |
| Filter - Active Filters | `filter-active-filters` | Shows currently-active filters as chips | `active-filters` |

Every filter element extends `Filter_Element_Base` in `includes/elements/filter-base.php`.

## Target-query binding

Every filter element has a **`filterQueryId`** setting pointing at the query-element `_id` it filters. Without it, the filter does nothing: no error, no warning. The dropdown in the builder is labelled **"Target query"** and lists all query-producing elements on the page.

Where it lives: `filter-base.php:1100-1108`, control type `query-list`.

**Rules:**
- The target element must exist on the same page (header/footer queries can be targeted from the page if they're visible in the tree).
- The target must be a query-producing element: Posts, Users, Terms, Container/Block/Section/Div with query-loop enabled.
- Setting the target on one filter doesn't set it on sibling filters: each filter needs its own `filterQueryId`.
- MCP: `set-filter-target-query` updates this on one filter; `update-filter-element` can update it alongside other config.

## The filter index: required for custom fields

Filters that populate options from the database need indexed values. Bricks maintains table `{prefix}bricks_filters_index` (defined at `query-filters.php:7`).

**Indexable filter types** (`query-filters.php:740-748`): `checkbox`, `radio`, `select`, `range`, `datepicker`. Not indexable: `search`, `submit`, `active-filters`.

**Index triggers:** Bricks hooks post, term, user, and meta changes while Query Filters are enabled: `save_post`, `delete_post`, `set_object_terms`, `updated_post_meta`, `deleted_post_meta`, `edit_attachment`, `edited_term`, `delete_term`, `profile_update`, `user_register`, and `delete_user`. It also watches Bricks-content meta writes through `update_post_metadata` / `added_post_meta` so filter elements stay registered.

**Manual reindex:** `WP Admin > Bricks > Settings > Query filters > Regenerate filter index` (fires `wp_ajax_bricks_reindex_query_filters`). The request recreates the index table and queues index jobs, so large sites may keep indexing after the request returns. Needed after:
- Bulk-importing posts / users / terms (the triggers fire per-item but may be slow or skipped in bulk imports).
- Enabling a new filter on an existing field.
- Changing the indexed field's structure.

**Serialized meta values:** if the meta field stores serialized data (PHP-serialized array / JSON blob), filters can't index it as separate selectable values unless something expands it into rows. `bricks/query_filters/custom_field_index_rows` can do that for non-native providers such as ACF or Meta Box. Current source only applies that filter when `$provider !== 'none'`; plain native post meta is stored as one raw value by `generate_custom_field_index_rows()` (`includes/query-filters.php:1975-2024`).

```php
add_filter( 'bricks/query_filters/custom_field_index_rows', function( $rows, $object_id, $meta_key, $provider, $object_type ) {
    if ( $meta_key !== 'my_array_field' || $object_type !== 'post' ) return $rows;

    $raw = get_post_meta( $object_id, $meta_key, true );
    $decoded = maybe_unserialize( $raw );

    if ( ! is_array( $decoded ) ) return $rows;

    return array_map( fn( $v ) => [
        'filter_value' => $v,
        'filter_value_display' => $v,
    ], $decoded );
}, 10, 5 );
```

## Data sources

Filters that populate selectable values use **`filterSource`** (`filter-base.php`). Core Bricks registers three sources:

| Source | Setting keys | Use for |
|---|---|---|
| `taxonomy` | `filterTaxonomy`, `filterTermInclude`, `filterTermExclude`, `filterTaxonomyOrder`, `filterTaxonomyOrderBy` | WP taxonomies (category, post_tag, product_cat, custom taxonomies) |
| `wpField` | `sourceFieldType` (post/user/term), `wpPostField` / `wpUserField` / `wpTermField` | Native WP fields: post_author, post_date, user_role, etc. |
| `customField` | `sourceFieldType`, `customFieldKey`, label mapping | ACF / Meta Box / Pods / native meta keys |

WooCommerce adds `wcField` when its query-filter integration is active (`includes/integrations/query-filters/woocommerce.php:22-85`).

Custom providers can be registered via `bricks/filter_element/data_source_{source_key}`: see the `bricks-hooks-reference` skill.

## Frontend handshake: what actually happens on click

1. User clicks a filter option.
2. Bricks frontend JS reads filter instances from `window.bricksData.filterInstances` and the selected filter state.
3. It POSTs JSON to the Bricks REST endpoint `query_result` with `queryElementId`, `postId`, selected filters, original query vars, language, and template context (`src/assets/js/frontend.js:13313-13370`).
4. `Api::render_query_result()` runs the target query with the filter's meta_query / tax_query injected (`includes/api.php:1490-1530`).
5. Returns HTML for the target query's loop. Frontend swaps it in, updates URL via pushState.

**The 3 conditions the target query must meet for AJAX swap to work:**
1. The query loop emits Bricks loop markers. Current source adds `data-brx-loop-start` on server render and frontend JS converts it to `<!--brx-loop-start-{queryId}-->`.
2. No optimizer or cache layer removes those markers. Preserve Bricks `brx-loop` markers in HTML optimization settings.
3. The target query's `_id` actually matches what the filter sent. This can break after duplicating a component or section that contains the query.

## Components and filter targets

Current Bricks has component-aware query-loop handling: query trails can carry `data-query-component-id`, and frontend AJAX uses that component id when locating the loop DOM (`includes/elements/base.php:4163-4168`, `src/assets/js/frontend.js:2157-2210`).

Still, a filter only works when its `filterQueryId` points to a query instance present on the rendered page. If a component instance contains a filter but not the matching query, the filter has no usable target. Prefer keeping the filter and its target query together at the page/template level, or ship them together inside the same component.

## Scope rule: "Use query filter" on the source loop

Some loops need explicit opt-in for filter compatibility: primarily **nested loops and loops populated via `bricks/query/run`**. The flag `useQueryFilter` lives on the query-producing element. For standard Posts/Users/Terms loops at the page level, the flag is typically on by default.

If your filter UI renders but the target loop doesn't swap: check the target loop's settings panel for a "Use query filters" / "Filterable" toggle and enable it.

## Hooks: when the UI isn't enough

| Hook | Kind | Purpose |
|---|---|---|
| `bricks/filter_element/controls` | filter | Mutate the builder controls for all filters |
| `bricks/filter_element/populated_options` | filter | Mutate the option list after population |
| `bricks/filter_element/data_source_{source}` | filter | Register/mutate a custom data source |
| `bricks/filter_element/count_source_{source}` | filter | Custom per-source count for result-count display |
| `bricks/filter_element/filtered_source` | filter | Final filtered source |
| `bricks/query_filters/custom_field_meta_query` | filter | Customize meta_query for custom-field filters |
| `bricks/query_filters/range_custom_field_meta_query` | filter | Same for range filters |
| `bricks/query_filters/datepicker_custom_field_meta_query` | filter | Same for datepicker filters |
| `bricks/query_filters/custom_field_index_rows` | filter | Expand serialized/array meta into index rows |
| `bricks/query_filters/get_filter_object_ids` | filter | Object IDs a filter restricts to |
| `bricks/filter/taxonomy_args` | filter | Args for taxonomy term query |
| `bricks/filter_element/datepicker_db_date_format` | filter | DB date format for datepicker |

See the `bricks-hooks-reference` skill for the full index.

## Silent-failure debug order

1. **Filter renders but nothing happens on click?**
   a. Open DevTools Network tab, click a filter option. Do you see a POST to the Bricks REST `query_result` endpoint? No -> frontend JS broken (check for JS errors, conflicting scripts).
   b. Request fires but returns empty HTML -> `filterQueryId` doesn't match any query on the page, or target query has no results with the filter applied.
   c. Request succeeds, HTML comes back, but DOM doesn't update -> loop-marker stripping or target mismatch. Check source for `data-brx-loop-start` and the live DOM for `brx-loop-start`.

2. **Custom-field filter shows no options?**
   a. Run reindex: `WP Admin > Bricks > Settings > Query filters > Regenerate filter index`.
   b. If the field is serialized/array: hook `bricks/query_filters/custom_field_index_rows` to unpack.
   c. If the field was just added: save any post of that type once: that triggers per-post indexing.

3. **Filter options show but selecting them doesn't narrow results?**
   a. Wrong meta comparison: numeric field using string compare. Hook `bricks/query_filters/custom_field_meta_query` to fix.
   b. Values include whitespace / case mismatch: index holds one form, frontend sends another.

4. **"Active filters" element shows nothing even after filtering?**
   a. It needs its own `filterQueryId` set to the same target. It's not auto-bound.

5. **Works on one page, breaks on another?**
   a. Component duplication changed the target ID. Check `filterQueryId` against the rendered query instance.
   b. Header/footer loop targeted from a page, but header/footer render order doesn't include it on the archive. Move the target.

6. **Datepicker filter compares against the wrong format?**
   a. Hook `bricks/filter_element/datepicker_db_date_format` to match the stored format.

## MCP abilities for query filters

- `list-query-filters`: enumerate every filter element on a page, with target binding status.
- `get-filter-element`: full settings of one filter.
- `update-filter-element`: update any filter's config (source, options, target).
- `set-filter-target-query`: quick-path for the most common mistake (missing target binding).

The `bricks-query-loops` skill covers the source-loop side of filter/loop integration.

## Never do

- Expect a filter with no `filterQueryId` to work. It won't, and there's no error.
- Put filters inside components that might render on pages without their target query.
- Trust that a custom-field filter has options immediately after bulk-importing the field's data. Always reindex.
- Remove Bricks loop markers during HTML optimization.
- Use `search` filters on large datasets without a proper search index (ElasticPress, Algolia). Bricks' default search is a `LIKE '%term%'` against post_title/post_content: slow on 10k+ rows.


---

## Module: bricks-global-queries

# Bricks: global queries (via MCP)

A **global query** is a named, reusable query definition stored at the site level. Multiple loop/filter elements can reference the same global query by ID instead of duplicating args. Useful when the query is complex (ACF meta filters, taxonomy unions, custom SQL) and reused across templates.

Storage: `bricks_global_queries` (query rows with `id`, `name`, `category`, and `settings`) + `bricks_global_queries_categories` (category rows with `id` and `name` for the builder UI grouping).

## Abilities

- **`bricks/list-global-queries`**: summary rows plus category list.
- **`bricks/get-global-query`**: `{ queryId }`. Full query object.
- **`bricks/create-global-query`**: `{ label, category?, query }`. Returns `{ query }`. The API accepts `label` and `query`, then stores them in Bricks as `name` and `settings`. The optional `category` is a category ID, not a label.
- **`bricks/update-global-query`**: `{ queryId, label?, category?, query? }`. If `query` is provided, it replaces the whole query settings object.
- **`bricks/delete-global-query`**: `{ queryId }`. **Does not** unlink referencing elements: those keep the dangling id and fall back to their local query or render empty.
- **`bricks/create-global-query-category`**: `{ name }`. Returns `{ category }`.
- **`bricks/delete-global-query-category`**: `{ categoryId }`. Queries in that category are kept and become uncategorized.

## Query shape

Same shape as an inline query on a loop element:

```
{
  objectType: "post",      // "post" | "term" | "user"
  postType: ["post"],
  posts_per_page: 6,
  orderby: "date",
  order: "DESC",
  meta_query: [ ... ],
  tax_query: [ ... ]
}
```

`objectType` lives inside the `query` object. Common values are `post`, `term`, `user`, and `array`; Query API flows can also use `api`. For `post`, `term`, and `user`, it decides which Bricks query runner handles the args and which hooks fire (`bricks/posts/query_vars` vs `bricks/terms/query_vars` vs `bricks/users/query_vars`). The ability stores the query object as provided and does not narrow `objectType` itself (`includes/abilities/queries.php:123-142`).

For Query editor PHP, ability creates and changes use the same PHP opt-in,
authentication, and signing rules as page queries. See
[bricks-custom-code](../bricks-custom-code/SKILL.md#code-authoring-through-abilities).
Preserve protected existing query settings when changing only its label or category.

## Binding to a loop

An element consuming a global query stores its id in `settings.query.id`:

```
query:
  id: "abc123"    // presence of this makes Bricks load the global query settings
  # inline args are ignored when id points to a valid global query
```

Write this through `bricks/update-element` on the target element; the query runner resolves the id at render time.

## Categories

Categories are pure UI: they group queries in the builder's dropdown. Write shape:

```
bricks/update-global-query
  queryId: abc123
  category: "cat_abc"
```

If you need a new category, call `bricks/create-global-query-category` first and pass the returned category ID into `create-global-query` or `update-global-query`. Passing a new label as `category` is wrong; the current schema expects a category ID.

## Tool availability

> **If a `bricks/*` ability is not available as a direct tool**: first check whether it is outside the fast path and call it through `mcp-adapter-execute-ability` with `ability_name: "bricks/<name>"`. If the dispatcher also rejects it, call `bricks-list-ability-status` to check whether a site admin disabled it under Bricks > AI.

## Typical flow: reusable "Recent Products" query

```
bricks/create-global-query-category { name: "Shop" }
  -> { category: { id: "cat_abc", name: "Shop" } }

bricks/create-global-query
  label: "Recent Products"
  category: "cat_abc"
  query:
    objectType: "post"
    postType: ["product"]
    posts_per_page: 8
    orderby: "date"
    order: "DESC"
  -> { query: { id: "fp_8h2", name: "Recent Products", category: "cat_abc", settings: {...} } }

# Now bind it to an existing Products Loop element:
bricks/update-element
  postId: 42
  elementId: "loopx1"
  settings:
    query:
      id: "fp_8h2"
```

All future edits to "Recent Products" propagate to every element whose `settings.query.id` references that global query.

## Cross-context notes

- Global queries respect element-specific context. If the element lives in a single-post template, `get_the_ID()` inside query filters still resolves to the current post: the global query is the args, not the context.
- `bricks/posts/query_vars` filter fires for global queries exactly as it does for inline ones. Match on the calling element id, not the query id, if you need to branch per-consumer.

## Don't

- Don't delete a global query without first replacing or clearing references. Query-list controls on elements silently fall back when the id is missing, and that's hard to spot in a big site.
- Don't embed element-specific context in a global query (e.g., a hard-coded post id). Use dynamic tags (`{post_id}`) or the `bricks/posts/query_vars` hook so the query stays reusable.
- Use category IDs to organize queries in the UI; categories do not control permissions or routing.


---

## Module: bricks-custom-dynamic-data-providers

# Bricks: custom dynamic-data tags

Use public hooks for ordinary custom tags. The internal `Providers::register()` API
takes provider slugs, not instances, and constructs Bricks-namespaced provider
classes. It is not a general third-party registration API.

## Public text-tag recipe

Read [the executable example](assets/custom-text-tag.php) when implementing a simple
post-backed text tag. Adapt its namespace, tag, explicitly public data lookup and
text domain to the project; load the adapted file once from the child theme/plugin.
It deliberately supports one exact text tag, without modifiers or image/link values.

The three rendering paths matter:

- `bricks/dynamic_tags_list` makes a tag discoverable in the picker.
- `bricks/dynamic_data/render_tag` resolves an individual tag; preserve non-string
  results and unrecognized tags from other providers.
- `bricks/dynamic_data/render_content` and `bricks/frontend/render_data` handle tags
  embedded in content. Registering the picker/individual-tag callback alone does
  not implement these paths. Preserve surrounding HTML and unrelated expressions.

The example returns scalar data from individual resolution and escapes its text
replacement at the HTML-content boundary. Consumers of a raw individual value must
escape for their own output context. For image/link/array tags, implement the
specific Bricks value shape and escaping instead of reusing the text substitution.
See [the public custom-tag contract](https://academy.bricksbuilder.io/developer/dynamic-data/create-your-own-dynamic-data-tag/).

## Context and modifiers

Use the post supplied by the renderer. A preview post, page post and loop item are
not interchangeable. For term/user/provider loops, inspect `Bricks\Query`'s actual
loop object/type and define the intended behavior when no applicable context exists.
Do not substitute a guessed post ID or rely on unsupported parser context overrides.

If adding modifiers, parse only the syntax your tag advertises and test malformed,
empty and nested input. Do not rewrite all braces in arbitrary page content. For a
core-style provider integration that really needs `Base`, read
[the internal provider reference](references/internal-provider.md); its lifecycle
and formatting contract are different from public hook callbacks.

Cache expensive lookups using every input that can change the result, including
post/user/locale/arguments as applicable, and invalidate on the corresponding data
updates. Never expose secrets or user-private data through a public rendering tag.

## Verify

Test picker presence, direct tag rendering and a tag inside surrounding text/HTML;
include unrelated tags, non-string values and missing data. Verify the intended
frontend and Builder contexts, plus the actual loop when applicable. A post-only
`preview-dynamic-tag` call cannot certify arbitrary term/user/repeater row context.
The bundled example's isolated PHP test protects its callback behavior; it does not
replace a WordPress/Builder integration check for the adapted provider.


---

## Module: bricks-element-conditions

# Bricks: element conditions

Element conditions control whether Bricks renders an element's markup. Use CSS visibility controls when the markup should remain in the DOM.

Use this skill for `element.settings._conditions`. Use **bricks-templates-conditions** for template display rules such as where a header, popup, archive, or content template applies.

## The schema

Storage key: **`_conditions`** on `element.settings`.

The shape is an outer array of OR groups. Each group is an inner array of AND items:

```json
[
  [
    { "id": "abc123", "key": "user_logged_in", "compare": "==", "value": true },
    { "id": "def456", "key": "post_status", "compare": "==", "value": "publish" }
  ],
  [
    { "id": "ghi789", "key": "dynamic_data", "dynamic_data": "{post_title}", "compare": "contains", "value": "Sale" }
  ]
]
```

Meaning:

- The element renders when any outer group matches.
- Every item inside a matching group must match.
- `conditions: []` clears all conditions.
- Do not save an empty group such as `[[]]`. An empty group behaves like an always-true group in runtime logic.

## Condition item fields

| Field | Required | Notes |
|---|---:|---|
| `id` | No | Unique row ID. The MCP writer generates it when omitted. |
| `key` | Yes | Condition type, such as `user_logged_in`, `post_id`, `dynamic_data`, or `woo_product_stock_status`. |
| `compare` | No | Defaults to `==`. Use `empty` or `empty_not` when no `value` is needed. |
| `value` | Usually | Required unless `compare` is `empty` or `empty_not`. |
| `dynamic_data` | Only for `key: "dynamic_data"` | Dynamic tag to evaluate, such as `{post_title}`. Still provide `value` unless using `empty` or `empty_not`. |

## Compare operators

Core operators:

```txt
==, !=, >=, <=, >, <, contains, contains_not, empty, empty_not
```

Use value types that match the condition. For booleans, send real booleans (`true`, `false`), not strings. For IDs, send integers when possible. For dates and times, use the same format the builder control expects.

## Core condition keys

General:

```txt
browser, current_url, date, datetime, dynamic_data, featured_image,
operating_system, referer, time, weekday
```

Post:

```txt
post_author, post_date, post_id, post_parent, post_status, post_title
```

User:

```txt
user_id, user_logged_in, user_registered, user_role
```

WooCommerce:

```txt
woo_product_category, woo_product_featured, woo_product_new,
woo_product_purchased_by_user, woo_product_rating, woo_product_sale,
woo_product_sold_individually, woo_product_stock_management,
woo_product_stock_quantity, woo_product_stock_status, woo_product_tag,
woo_product_type
```

Custom integrations can add condition keys through Bricks filters. The dedicated MCP writer accepts core keys plus keys registered through `bricks/abilities/element_conditions/allowed_keys`.

## MCP abilities for element conditions

- `get-element-conditions`: read the element's `_conditions` array.
- `update-element-conditions`: replace the element's `_conditions` array. Full replacement only. Generates missing row IDs. Takes a pre-save revision.

Prefer the dedicated writer over generic `update-element` when changing `_conditions`. It validates the OR/AND shape and catches empty groups, missing keys, invalid compare operators, and incomplete dynamic-data conditions before saving.

## Safe workflow

1. Read the element with `get-page-elements` or `get-element-conditions`.
2. Preserve any existing groups you are not intentionally replacing.
3. Write the full `conditions` array with `update-element-conditions`.
4. Confirm the returned `revisionId` exists with `list-revisions`.
5. Read back with `get-element-conditions`.
6. Verify the page in a browser when the condition depends on runtime state such as login, URL, date/time, WooCommerce product context, or dynamic data.

## Examples

Logged-in users only:

```json
{
  "postId": 123,
  "elementId": "abc123",
  "conditions": [
    [
      { "key": "user_logged_in", "compare": "==", "value": true }
    ]
  ]
}
```

Specific post IDs:

```json
{
  "conditions": [
    [
      { "key": "post_id", "compare": "==", "value": 42 }
    ],
    [
      { "key": "post_id", "compare": "==", "value": 89 }
    ]
  ]
}
```

Dynamic data contains text:

```json
{
  "conditions": [
    [
      {
        "key": "dynamic_data",
        "dynamic_data": "{post_title}",
        "compare": "contains",
        "value": "Sale"
      }
    ]
  ]
}
```

Clear all element conditions:

```json
{
  "conditions": []
}
```

## Debug order

1. **Element does not render.** Read `_conditions`; if any group is intended to match, check each item in that group. One false item makes the whole group false.
2. **Element renders everywhere.** Look for an empty group or a condition using `empty` against a value that is always empty in the current context.
3. **Dynamic-data condition fails.** Confirm `dynamic_data` is present, the tag renders in the current post context, and the `value` comparison matches the rendered string.
4. **WooCommerce condition fails.** Confirm the page is in a product context and WooCommerce is active.
5. **Template and element conditions disagree.** Template conditions decide whether the template renders at all. Element conditions only run after the template/page element tree is already chosen.

## Never do

- Do not use template condition shapes (`{ "main": "any" }`) inside element `_conditions`.
- Do not save `[[]]` or groups with only generated IDs and no `key`.
- Do not use element conditions as a styling system. Use CSS or responsive/hide controls when markup should stay in the DOM.
- Do not guess custom condition keys. Read the live schema or integration docs first.


---

## Module: bricks-forms

# Bricks: forms

Use native form abilities for focused changes. Resolve the post and form element,
then `get-form-config` before editing an existing form. Read the runtime Form schema
for controls and action availability; optional features/plugins affect them.

## Choose the operation

| Change | Contract |
|---|---|
| Add, remove or reorder fields | `update-form-fields` replaces the entire ordered field array; merge the requested change into the full current array and preserve existing IDs |
| Change actions | `update-form-actions` replaces the supplied actions list and partially merges supported action settings; preserve unrelated actions and their order |
| New form | Native Form element with runtime-shaped fields/actions; no custom HTML form substitute |
| Diagnose submissions | `list-form-submissions` is paginated; missing storage does not prove the form never submitted |

Read [fields and actions](references/fields-and-actions.md) for supported field
shapes, action details, placeholder syntax, anti-spam or delivery troubleshooting.
Checkbox/select options are newline-separated. Email/webhook placeholders bind to
field IDs; keep them stable when changing labels or input names.

## Diagnose the actual failing stage

Separate rendering, client validation, server validation, action execution and
external delivery. A successful mail handoff does not prove delivery. Inspect the
configured transport/provider logs for the specific failure. Bricks credential UI
masking does not establish encrypted-at-rest storage; use supported configuration
and avoid copying secrets into page content or revisions.

## Verify within scope

A configuration review is read-only. A submission can send email/webhooks, create
users/posts or cause payment-related effects. For requested functional testing, use
an authorized test destination/fixture and check the intended action result. Do not
submit a production form merely to inspect its layout.

Inspect mutation readback for the exact fields/actions, omissions and preserved
configuration; use `get-form-config` when that evidence is missing. Verify relevant
validation/error/success states and deferred CAPTCHA initialization in a browser
when available. Report absent browser or delivery evidence explicitly.


---

## Module: bricks-media-assets

# Bricks: media assets

Use WordPress media library attachments for assets that should live with the site. Do not hotlink production images from third-party URLs unless the user explicitly asks for remote assets.

## Lookup first

Before uploading, search existing media:

```json
{
  "query": "hero",
  "mimeType": "image/"
}
```

For broad searches, choose the compact response mode. Fetch full detail only when you need the exact generated size URLs for a chosen attachment. Use `bricks-find-media`. If the direct tool is missing, call `mcp-adapter-execute-ability` with `ability_name: "bricks/find-media"`.

## Upload

Prefer base64 uploads when the file is already local or generated:

```json
{
  "filename": "hero.jpg",
  "base64": "<base64 file data>",
  "title": "Homepage hero",
  "alt": "Person using the product dashboard"
}
```

Base64 uploads must use a filename with a WordPress-allowed media extension and stay within the site's configured upload-size limit. Use the dedicated custom-font abilities for font files.

URL sideloading is only for normal public `http`/`https` URLs. Do not use internal, localhost, private-network, link-local, metadata-service, unsafe-port, credentialed, or file URLs. Remote downloads are also checked against the site's configured upload-size limit.

Uploads are persistent WordPress attachments. If an upload was only for temporary testing, a discarded design direction, or a replacement that should not stay in the library, delete it only after verifying it was created for this task, is still unused and cleanup is within scope. Use `bricks/delete-media` with the returned `id` as `attachmentId`; retain pre-existing/shared attachments.

## Image element settings

After upload, wire the returned attachment into an Image element:

```json
{
  "name": "image",
  "settings": {
    "image": {
      "id": 123,
      "url": "https://example.com/wp-content/uploads/hero.jpg",
      "filename": "hero.jpg",
      "size": "large",
      "full": "https://example.com/wp-content/uploads/hero.jpg"
    },
    "altText": "Person using the product dashboard",
    "loading": "eager"
  }
}
```

Use the `sizes` object returned by `upload-media` to choose an appropriate `size` and URL. Choose the image size from its rendered dimensions and available variants. Do not lazy-load an above-the-fold LCP/hero image; use lazy loading for appropriate below-fold images.

## Documents and downloads

Use the native `file` element for a document link or download. Fetch its runtime
schema: `source` selects `file`, `external`, or `dynamic`, with different settings
for each. Put an uploaded attachment in its `file` control (`id` and `url`). Preserve the requested link/download behavior and verify it in
the frontend (`includes/elements/file.php`).

## Galleries

For a native gallery, fetch the `image-gallery` schema before writing. Gallery controls differ from a single Image element and should not be guessed.

If the page needs a carousel with arbitrary content, use `slider-nested` and add Image elements inside slides instead of forcing an Image Gallery.

## Accessibility

- Always set useful alt text for informative images.
- Use empty alt text only for decorative images.
- Keep captions as content only when they are visible and useful to the visitor.

## Site reproduction

When reproducing a page:

1. Download source images.
2. Upload each to the WordPress media library.
3. Replace external image URLs in Bricks Image elements with the returned attachment `id`, `url`, `filename`, and chosen `size`.
4. Verify rendered images use local WordPress URLs and include `srcset` where expected.

## Never do

- Do not leave scraped source-site image URLs in final Bricks elements.
- Do not use URL sideloading for private or local network addresses.
- Do not upload fonts with `upload-media`; use the custom-font abilities.
- Do not guess gallery schema. Fetch it first with `bricks-element-schemas`.

## Custom icons

For a custom SVG icon library, use `list-icon-sets` and `list-custom-icons` before
creating a set or uploading an icon. Inspect the live schemas for
`create-custom-icon-set` and `upload-custom-icon`, then wire the returned icon shape
through the target element's icon control. Server sanitization may change SVG data;
verify the resulting icon. Set deletion removes its icon rows but does not imply
attachment cleanup. Preserve other set entries and shared attachments.

Keep page-specific alternative text on the element when appropriate; changing
attachment metadata can affect its other uses.


---

## Module: bricks-interactions

# Bricks: interactions

Interactions are the no-code behavior system: `{ trigger, action }` pairs that wire clicks, hovers, scrolls, and form events to DOM mutations, popup opens, offcanvas toggles, and JS callbacks. Element-level interactions are stored on `element.settings._interactions` as an array. Global classes can also store `_interactions`, and every element using that class inherits those rows at render time.

## The schema

Storage key: **`_interactions`** on `element.settings` or on a global class setting object. Array of objects. Each object has fields from `includes/interactions.php:94-491`: 30+ possible keys, most conditional on the trigger/action combination.

The `update-element-interactions` ability writes only element-level rows. It generates missing row IDs and validates trigger, action, target, JavaScript callback references, and action/trigger-specific required fields before saving.

Minimum shape:

```json
{
  "id": "abc123",
  "trigger": "click",
  "action": "show",
  "target": "custom",
  "targetSelector": "#my-modal"
}
```

## Element triggers

Authoritative list at `includes/abilities/interactions.php` (`Interactions::TRIGGERS`), sourced from `includes/interactions.php` controls. Popup template interactions add two template-only triggers, `showPopup` and `hidePopup`, under `template_interactions`.

| Trigger | Fires when |
|---|---|
| `click` | Element clicked |
| `mouseover` | Pointer over |
| `mouseenter` | Pointer enters bounding box |
| `mouseleave` | Pointer leaves bounding box |
| `focus` | Element focused (keyboard/tab) |
| `blur` | Focus lost |
| `scroll` | Page scrolled (configurable %/px) |
| `contentLoaded` | DOM ready |
| `mouseleaveWindow` | Exit-intent: pointer exits top of window |
| `enterView` | Element enters viewport |
| `leaveView` | Element leaves viewport |
| `animationEnd` | CSS animation completes |
| `formSubmit` | Form submitted (any form) |
| `formSuccess` | Form submitted + server returned success |
| `formError` | Form returned error |
| `ajaxStart` | Query AJAX loader started |
| `ajaxEnd` | Query AJAX loader completed |
| `filterSubmitStart` | Query filter submit started |
| `filterSubmitEnd` | Query filter submit completed |

Feature-scoped triggers (same const, also accepted by MCP):
- Query filters: `filterSubmitStart`, `filterSubmitEnd`, `filterOptionEmpty`, `filterOptionNotEmpty`
- WooCommerce: `wooAddedToCart`, `wooAddingToCart`, `wooRemovedFromCart`, `wooUpdateCart`, `wooCartContentsChanged`, `wooCouponApplied`, `wooCouponRemoved`

`wooCartContentsChanged` listens for `bricks/woocommerce/cart-contents-changed`,
so use it for behavior that must respond to Bricks cart-content updates. The frontend
also handles `wooDynamicFragmentsRefreshed` and `wooCheckoutStepChanged`, but the
2.4 interaction ability's allow-list does not admit those two values. Do not infer
ability support merely from frontend JavaScript; check the target site's schema.

## Actions

Authoritative list at `includes/abilities/interactions.php:68-87` (`Interactions::ACTIONS`).

| Action | What it does | Extra keys |
|---|---|---|
| `show` | Unhide target, or open a popup when `target: "popup"` | None, or `templateId` when `target: "popup"` |
| `hide` | Hide target, or close a popup when `target: "popup"` | None, or `templateId` when `target: "popup"` |
| `click` | Programmatic click on target | None |
| `startAnimation` | Trigger a CSS animation | `animationType`, `animationDuration`, `animationDelay` |
| `scrollTo` | Scroll to target | `scrollToOffset`, `scrollToDelay` |
| `setAttribute` | Add/set attribute on target | `actionAttributeKey`, `actionAttributeValue` |
| `removeAttribute` | Remove attribute | `actionAttributeKey` |
| `toggleAttribute` | Toggle attribute presence or value | `actionAttributeKey`, `actionAttributeValue` |
| `toggleOffCanvas` | Open/close an offcanvas element | `offCanvasSelector` |
| `loadMore` | Load next page on a query loop | `loadMoreQuery` |
| `loadMoreGallery` | Same, for image galleries | `loadMoreTargetSelector` |
| `openAddress` | Open a map info box | `infoBoxId` plus map element context |
| `closeAddress` | Close a map info box | `infoBoxId` plus map element context |
| `clearForm` | Reset form fields | `targetFormSelector` unless the trigger is a form event |
| `storageAdd` | Write to browser storage | `storageType`, `actionAttributeKey`, `actionAttributeValue` |
| `storageRemove` | Remove from browser storage | `storageType`, `actionAttributeKey` |
| `storageCount` | Increment a counter in browser storage | `storageType`, `actionAttributeKey` |
| `javascript` | Call a named JavaScript function on `window` | `jsFunction`, optional `jsFunctionArgs` |

There is no `openPopup`, `customJs`, or inline `javascript` source field. The `javascript` action calls an existing frontend function by name through `jsFunction` (for example `MyApp.trackCardClick`) and optional `jsFunctionArgs`; it does not evaluate arbitrary JavaScript text. To open a popup with native interaction data, use `action: "show"`, `target: "popup"`, and `templateId`. JavaScript can still call `bricksOpenPopup(id)`, but use the native shape when authoring Bricks data.

For `jsFunctionArgs`, each argument row needs `jsFunctionArg` and an `id`. The MCP writer generates missing IDs. Without IDs, the frontend skips the argument row.

## Targets: three modes

Defined at `includes/abilities/interactions.php` (`Interactions::TARGETS`). MCP accepts exactly these three explicit values: `self`, `custom`, `popup`. If `target` is omitted, Bricks treats the interaction as `self` at runtime. Offcanvas open/close is saved as `action: "toggleOffCanvas"`; during render Bricks rewrites it internally to an offcanvas target for frontend handling.

| Mode | Setting | Resolves to |
|---|---|---|
| `self` | `target: "self"` | The element that owns the interaction |
| `custom` | `target: "custom"`, `targetSelector: "#foo"` or `.bar` | CSS selector (querySelector semantics) |
| `popup` | `target: "popup"`, `templateId: 123` | A popup template id |

Use CSS selectors for custom targets. To target a specific Bricks element by id, use `#brxe-{element_id}` only when the target element has no custom CSS ID. If the target has `_cssId`, Bricks renders that custom ID on the frontend instead, so target the custom selector (for example `#hero-panel`). If you rely on the auto id, the selector also breaks if the element is duplicated (new id).

Safer: add a CSS class to the target via the Element ID/Class panel (e.g. `.js-main-nav`), then target `.js-main-nav` from the interaction. Survives element duplication.

## Global-class inheritance: interactions on classes

Interactions can live on a global class (same place as the class's other settings). Every element using that class inherits the interactions (`interactions.php:531-539`).

Merge rule: interactions on an element **stack with** (do not override) interactions on the element's applied classes. So if a button has `click -> show #foo` and the button also has a class with `click -> scrollTo #top`, both fire on click.

Edit the global class to change inherited interactions.

MCP readback exposes this explicitly:

- `interactions`: element-level rows only.
- `inheritedInteractions`: grouped global-class rows.
- `effectiveInteractions`: flattened frontend order, with `source`, `sourceId`, and `sourceName` on each row.

## Infinite-loop traps

1. **`enterView -> startAnimation` on a scroll-repeating element.** If the animation moves the element out of then back into view, it re-fires. Add `Run once` on the interaction.

2. **`click -> click` on another element that clicks back.** Infinite click loop. Happens often with "link both of these" logic. Add a guard or use a different mechanism.

## Run-once / frequency

Every interaction has a **Run once** boolean (`runOnce`) and optional **interaction conditions** (`interactionConditions`, defined in `includes/interactions.php`) based on browser storage:

- `windowStorage`: page-load counter
- `sessionStorage`: tab-lifetime counter
- `localStorage`: cross-session counter

With compare operators: `exists`, `notExists`, `==`, `!=`, `>=`, `<=`, `>`, `<`.

Example: "fire at most 3 times across sessions": add a condition against a local-storage key, then pair it with `storageCount` using `storageType: "localStorage"` and the same key in `actionAttributeKey`.

## Performance cost

Every interaction adds:
- Event listener(s) at DOM-ready.
- JSON payload in `data-interactions` attribute (shipped inline per element).
- Per-fire work: target lookup, condition check, action execution.

Profile pages with repeated interactive elements before changing their behavior.

- Use CSS pseudo-classes for simple hover and focus styling.
- Use global-class interactions for shared authoring. Each element still inherits the rendered interaction rows and listeners.
- Use an enqueued JavaScript handler when delegated event handling would reduce measured overhead.
- Store JavaScript callbacks in an enqueued file and reference them through `jsFunction`.

## Hooks

Few dedicated interaction hooks exist. For render-attribute level tweaks, use the element-render hooks (`bricks/element/render_attributes`). For popup-related interaction behavior, use `bricks/popup/attributes`.

Interactions are largely frontend-only. WPML-aware behavior for popup interactions is handled at `interactions.php:585-600, 688-705` (popup template id translation).

## Silent-failure debug order

1. **Interaction doesn't fire?**
   a. DevTools Elements -> find the element -> check `data-interactions` attribute. Is your interaction in the JSON? No -> saved state doesn't match builder. Resave.
   b. Check browser console for errors. For JavaScript actions, verify that the named function exists on `window` and inspect callback errors.
   c. Trigger mismatch: `click` on a disabled button, `scroll` on a non-scrolling container.

2. **Interaction fires but target isn't affected?**
   a. Target selector is wrong. Test `document.querySelectorAll("your-selector")` in the console.
   b. Target doesn't exist yet at trigger time (e.g., targeting an element inside a popup before the popup renders).

3. **Fires too many times?**
   a. Class-level interaction duplicating element-level. Check the applied classes.
   b. Missing `runOnce`. Enable it.
   c. One of the infinite-loop traps above.

4. **Fires on wrong elements?**
   a. Selector too broad. `.btn` matches every button on the page.
   b. Global class interaction applies to more elements than you expected.

5. **Works in builder, fails on frontend (or vice versa)?**
   a. Interaction references a popup template id that doesn't render in the builder context.
   b. Trigger is a frontend-only event (`formSubmit`): builder doesn't submit real forms.

## MCP abilities for interactions

- `get-element-interactions`: read element-level rows, inherited global-class rows, and flattened effective rows.
- `update-element-interactions`: replace element-level rows on an element. It validates element-level triggers only, generates missing row IDs, and never mutates inherited global-class rows. Popup template-level `showPopup` and `hidePopup` live in popup template settings as `template_interactions`.

Use `formSuccess` for actions that require a successful submission. Enable `runOnce` when the action should stop after its first matching event.


---

## Module: bricks-woocommerce

# Bricks: WooCommerce

Bricks exposes additional WooCommerce/product elements when the experimental advanced modular elements setting is enabled. Classic/default Woo surfaces remain available, and advanced modular cart/checkout/account elements are opt-in through the Bricks global setting `woocommerceUseAdvancedModularElements`.

## Setup-first workflow

For store setup, use the Woo setup abilities before writing raw element JSON:

1. Call `bricks/get-woo-setup-status`.
2. Call `bricks/plan-woo-setup` with the intended `areas`, `scope`, and `mode`.
3. Review the plan for setting changes, page creation/reuse, and destructive actions.
4. Call `bricks/run-woo-setup`, passing the returned `planId` when available.
5. Fetch exact schemas before custom element edits, then style with existing global classes/theme styles.

Use WooCommerce-owned abilities for product and order operations when they are available. Bricks Woo setup abilities configure Bricks pages, templates, presets, modular Woo elements, and setup-related Woo options.

Default to `mode: "classic"` unless the user explicitly wants the experimental modular v2 flow. Use `mode: "advanced"` only after explaining that it enables an experimental Bricks Woo setting that changes which Woo elements are registered and may affect existing classic Woo setups.

Important setup behavior:

- Missing Woo pages can be created and assigned.
- If a matching unassigned page already exists, reuse it only when it has no Bricks data and is empty or shortcode-only.
- Do not silently overwrite non-empty, block-based, or Bricks-built pages. Destructive page writes require explicit confirmation and `overwriteExistingPageContent`.
- For cart/checkout/account presets, setup can enable required Bricks Woo element gates such as notices, checkout coupon, and checkout login.
- Woo setup options can be read and changed through `bricks/get-woo-setup-options`, `bricks/set-woo-setup-options`, and the global settings abilities.
- When changing Woo page assignments directly, use existing page IDs or `0` to intentionally clear an assignment.

## Classic setup (default)

Classic setup uses:

- `shop`: use the Woo shop/archive template flow and classic shop/archive elements.
- `single_product`: use Woo single product template flow and product elements.
- `cart`: use the assigned Woo cart page plus classic cart elements.
- `checkout`: use the assigned Woo checkout page plus classic checkout elements.
- `my_account`: use the assigned Woo account page plus classic account elements.

After setup, customize by fetching exact schemas for the elements already inserted. Prefer preserving the generated Woo structure and changing spacing, typography, layout wrappers, and global classes over replacing the entire tree.

## Advanced modular setup (experimental)

Advanced modular setup is for users who need finer control over cart, checkout, and account states. Enable it only with user confirmation:

- Parent elements: `woocommerce-cart-v2`, `woocommerce-checkout-v2`, `woocommerce-account-page-v2`.
- Cart state children: `woocommerce-cart-v2-state-cart`, `woocommerce-cart-v2-state-empty`.
- Checkout state children: `woocommerce-checkout-v2-state-checkout`, `woocommerce-checkout-v2-state-login`, `woocommerce-checkout-v2-state-pay`, `woocommerce-checkout-v2-state-receipt`, `woocommerce-checkout-v2-state-thankyou`.
- Account state children include dashboard, orders, view order, downloads, addresses, edit address, edit account, payment methods, add payment method, login, lost password, lost password confirmation, and reset password states.
- Support elements include `woocommerce-dynamic-fragment`, `woocommerce-form-field`, `woocommerce-form-submit`, cart quantity/form, checkout billing/shipping/order/payment pieces, and account form pieces.

Treat v2 state elements as generated/managed structural children. Preserve their required structure. If the user asks to deeply customize v2 flows, fetch the parent and child schemas first and preserve required state wrappers.

For an existing Account v2 missing a newly available state, read
`bricks/get-element-schema` for `woocommerce-account-page-v2` and inspect its
`stateChildren`. Append only missing direct state children with fresh IDs; preserve
existing customized children. The returned list respects current feature gates
(`includes/abilities/reference.php`).

## Migrating classic to advanced

For an existing classic Woo setup:

1. Read setup status and Woo setup options first.
2. Plan advanced setup for only the requested areas.
3. Explain that advanced modular elements are experimental and ask before enabling `woocommerceUseAdvancedModularElements`.
4. Preserve existing page content unless the user explicitly confirms replacement.
5. Run setup, then restyle using the site's existing design system.

Old classic templates may remain after migration. Do not delete old templates or pages unless the user asks.

## Product and shop elements

Product-singular elements include title, price, gallery, reviews, rating, meta, content, short description, stock, tabs, related products, upsells, additional information, and add to cart. Build a custom single-product template by composing these in a WooCommerce single-product template (`wc_product`) when you want the Woo template flow.

Shop/archive elements include `woocommerce-products`, products pagination, orderby, filter, total results, archive description, breadcrumbs, and notices. The Woo products-filter wraps native Woo filtering and is separate from generic Bricks query filters.

`woocommerce-template-hook` may exist in the schema set, but only use it when the runtime registers it on the target site.

## Products via standard Posts loop

Products are a custom post type (`product`). You can use a **regular Bricks Posts loop** with `post_type: product`: no Woo element required. This gives you full control over the card layout.

Tradeoff:
- Posts-loop: full Bricks control, no Woo-specific dynamic tags without effort. Use `{woo_product_price}`, `{woo_product_stock}` etc. inside the loop: they'll resolve.
- `woocommerce-products` element: inherits Woo shop queries (sort, filters, pagination) automatically. Less customizable but matches Woo conventions.

**Rule of thumb:** if the user wants "our shop, styled our way" -> Posts loop of products with custom card design. If they want "Woo's standard shop with our header/footer" -> `woocommerce-products` element.

## Woo-specific dynamic data tags

From `provider-woo.php`. Available when current post is a product:

```
{woo_product_type}           -> simple / variable / grouped / external
{woo_product_price}          -> "$29.99" (with currency)
{woo_product_price:value}    -> "29.99" (numeric value)
{woo_product_regular_price}  -> regular price
{woo_product_sale_price}     -> sale price (empty if not on sale)
{woo_product_excerpt}        -> product short description
{woo_product_stock}          -> stock status / quantity
{woo_product_sku}
{woo_product_gtin}
{woo_product_rating}
{woo_product_on_sale}
{woo_product_badge_new}
{woo_add_to_cart}
```

**Outside product context:** these resolve empty. To render a specific product, place the tag inside a product loop or preview it through MCP with the target product `postId`.

## Cart & checkout: two flows

Two separate pages (`/cart/` and `/checkout/`), each with its own Bricks template option. Approach:

### Option 1: Bricks elements compose the Woo page
- Use the WooCommerce cart or checkout template type when available in Bricks; Woo template types are routed to their Woo page automatically.
- Compose cart elements: `cart-items` + `cart-collaterals`.
- If you are using a normal `content` template instead, scope it with `ids` to the configured Woo cart or checkout page. There is no `pageType: cart` condition in the Bricks template condition schema.

### Option 2: Standard Woo page with Bricks header/footer only
- Don't create a content template for cart/checkout.
- Woo's default templates render; Bricks only owns header/footer.
- Simpler but less flexible.

## WooCommerce template overrides

Woo's templating allows overriding individual template parts. Bricks doesn't interfere: if you place overrides in your child theme's `woocommerce/` directory, Woo uses them normally.

**Theme hierarchy for Woo templates:**
1. Your-theme/woocommerce/{template}.php
2. Parent-theme (bricks)/woocommerce/{template}.php
3. Woo-plugin-default/{template}.php

Bricks does include WooCommerce template files under its theme `woocommerce/` directory. A child theme override still wins because Woo checks the child theme before the parent theme.

**When to override vs. use Bricks elements:**
- Override Woo templates: you need to change the logic of a Woo surface (add a meta field to the order email, restructure the cart-item row HTML with custom attributes the element can't emit).
- Use Bricks elements: you need to restyle/relayout. Styling is Bricks' job.

## Key Woo hooks

| Hook | Kind | Purpose |
|---|---|---|
| `bricks/woocommerce/products_filters/options` | filter | Options for the Woo products-filter element |
| `woocommerce_loop_add_to_cart_link` | filter | Add-to-cart button HTML |
| `woocommerce_loop_product_title` | filter | Product card title HTML |
| `woocommerce_before_shop_loop` / `after_shop_loop` | action | Around shop loop |
| `woocommerce_single_product_summary` | action | Single product summary content |
| `woocommerce_cart_calculate_fees` | action | Add fees at checkout |

(Most hooks above are Woo's, not Bricks'. Check Woo's docs for the exhaustive list.)

From Bricks side, `includes/woocommerce.php` registers the integration at plugin load.

## Theme style for Woo

Bricks registers WooCommerce theme style controls for Woo buttons and Woo notices. Use existing global classes, variables, palettes, and theme styles first. If the site has a design system, match it. If the site is still stock, create only a clean functional setup unless the user also asks for styling or a new design system.

## Variations, attributes, and the variable-product gotcha

Variable products have sub-configurations (size, color). The single-product add-to-cart element handles the `<select>` UI by default.

**Gotcha:** if you build a custom product card on archive pages and link straight to `?add-to-cart=PRODUCT_ID`, you bypass the variation selector. User lands on cart with "which variant?" failure. Always let the user choose variants before adding to cart.

## Mini-cart, cart drawer, offcanvas cart

`woocommerce-mini-cart.php` is a Bricks Woo element. Use it when you want the built-in mini cart output. For a custom drawer, build with Bricks Offcanvas plus Woo cart elements, toggled by an interaction on a cart button in the header.

For a cart-count badge, use the registered `{woo_cart_items_count}` tag (`provider-woo.php`). It reads cart quantity without custom PHP. Confirm the runtime tag and cart context. For cart-dependent content that must refresh, inspect `woocommerce-dynamic-fragment` and the `wooCartContentsChanged` interaction trigger.

## My Account: composed pages

Account pages are Woo's multi-tab interface. Elements for each tab are separate:
- `woocommerce-account-dashboard.php` (not available as a separate Bricks element; default Woo)
- `woocommerce-account-orders.php`, `-addresses.php`, `-downloads.php`, `-payment-methods.php`, `-view-order.php`, `-edit-account.php`, `-edit-address.php`
- Login/registration: `-form-login.php`, `-form-register.php`
- Password: `-form-lost-password.php`, `-form-reset-password.php`

To customize account surfaces, use the dedicated Woo account elements or a Bricks Woo account template flow. The normal template condition schema does not include URL-pattern or `isEndpoint` condition kinds.

## Performance on Woo sites

Profile product archives, cart updates, and checkout separately; see [bricks-performance](../bricks-performance/SKILL.md).

- **CSS loading mode** = `file`: on Woo, inline CSS can balloon (product-specific styles per variant). File mode caches.
- **Product archives:** measure query and rendering time, then adjust pagination or query caching where it improves the measured bottleneck.
- **Mini-cart updates:** inspect fragment requests and their timings before changing refresh behavior.

## Silent-failure debug order

1. **Woo element renders placeholder text in builder, empty on frontend?**
   a. Current page isn't a product/archive/cart context. Element only works in its intended context.
   b. Test on an actual product single page, not the builder preview root.

2. **Add-to-cart button does nothing?**
   a. Product is out of stock but "Continue selling when out of stock" is off.
   b. Variable product without selected variation.
   c. JS error elsewhere preventing Woo scripts from initializing.
   d. CAPTCHA / Cloudflare interceptor blocking the AJAX call.

3. **Cart shows empty after adding?**
   a. Session cookie blocked (cookies-disabled on the browser, or test-mode without proper session handling).
   b. Cart fragments AJAX failing. Check Network tab for `wc-ajax=get_refreshed_fragments`.

4. **Checkout validation fires but form doesn't submit?**
   a. Custom JS on the page hijacking the submit event.
   b. Payment gateway misconfiguration: check Woo > Settings > Payments.

5. **Woo dynamic tag `{woo_product_price}` renders empty?**
   a. Not in a product context. Move inside a product loop or preview with the target product `postId`.
   b. Product has no price set (free product without explicit "0.00").

6. **Custom Woo template override ignored?**
   a. File path typo: Woo is strict: `child-theme/woocommerce/single-product/title.php` (mirrors plugin structure exactly).
   b. File-exists check not firing; try with a `cart/cart.php` override first as a sanity test.

## Never do

- Enable advanced modular Woo elements by default on an existing/production store.
- Overwrite assigned Woo pages without status, plan review, and explicit user confirmation.
- Treat v2 state elements as normal standalone elements; they are structural children of their v2 parent.
- Build a shop with a regular Posts loop **and** the `woocommerce-products` element on the same template: you'll double-render products.
- Put Woo elements outside their expected context (cart element on a product page): they'll render errors or empty.
- Bypass Woo's variation selector by building a direct-add-to-cart link on variable products.
- Skip the Woo theme style: it's there specifically for consistent button/badge/card styling across your Woo surfaces.
- Override a Woo template when a Bricks element would reshape it. Template overrides are harder to audit than Bricks-native.
- Cache product pages aggressively without excluding cart and checkout: you'll serve stale cart state.
