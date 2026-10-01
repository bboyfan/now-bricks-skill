# Query Loops

Turn any `block`/`div`/`container` into a repeating loop. The element's children are the card template, rendered once per result. Verified against `includes/query.php` (2.3.6).

## Activation

```json
{
  "id": "loop01",
  "name": "block",
  "parent": "con001",
  "children": ["card01"],
  "label": "Posts Loop",
  "settings": {
    "hasLoop": true,
    "query": {
      "objectType": "post",
      "post_type": ["post"],
      "posts_per_page": "9",
      "orderby": "date",
      "order": "DESC"
    }
  }
}
```

The loop element itself repeats — put the grid (`_display: "grid"`) on its **parent**, or make the loop element the grid item. Common pattern: parent `div` with grid settings → child loop `block` with `hasLoop` (each iteration is one grid cell).

Inside the loop, all dynamic tags resolve per-item: `{post_title}`, `{featured_image}`, `{post_url}`, `{post_excerpt:20}`, `{acf_*}` etc.

## `query.objectType` values

| objectType | Loops over | Extra providers |
|------------|-----------|-----------------|
| `post` | WP_Query posts | — |
| `term` | WP_Term_Query terms | — |
| `user` | WP_User_Query users | — |
| `acf_relationship` / repeater tags | see acf-providers.md — select the ACF repeater/relationship as loop source | requires ACF |
| `metabox_group`, JetEngine, Woo cart… | provider-registered types | respective plugin |
| `api` (2.1+) | external REST API results — use `{query_api @key:'path|to|field'}` | — |
| `array` (2.2+) | static array data | — |

ACF repeater loops: `"objectType": "acfRepeater"` style keys are provider-generated — in practice set the query type in the builder once to inspect, or use the tag-based form: `"query": { "objectType": "{acf_team_members}" }` resolves the repeater. Safest cross-version form for repeaters is objectType set to the provider key emitted by the builder; for hand-authoring prefer post/term/user + relationship fields.

## Post query keys (inside `query`)

```json
{
  "objectType": "post",
  "post_type": ["post", "page", "product"],
  "posts_per_page": "12",
  "offset": "0",
  "orderby": "date",
  "order": "DESC",
  "meta_key": "event_date",
  "post_status": ["publish"],
  "post__in": [12, 34],
  "post__not_in": [56],
  "post_parent": "42",
  "ignore_sticky_posts": true,
  "exclude_current_post": true,
  "is_archive_main_query": false,
  "disable_query_merge": false,
  "infinite_scroll": false,
  "s": "search term"
}
```

- `orderby`: `date` `modified` `title` `menu_order` `rand` `comment_count` `meta_value` `meta_value_num` `post__in` (set `meta_key` when ordering by meta)
- `is_archive_main_query: true` on archive templates makes the loop adopt/merge the main query (pagination + filters work natively).
- `exclude_current_post: true` for related-posts loops.

### Taxonomy filtering — simple form

```json
"tax_query": ["category::12", "post_tag::7"]
```

Format `taxonomy::term_id`. Exclusion list: `"tax_query_not": ["category::3"]`. Relation: `"tax_query_relation": "AND"`.

### Taxonomy filtering — advanced form

```json
"tax_query_advanced": [
  { "taxonomy": "category", "field": "term_id", "terms": [5, 10], "operator": "IN", "include_children": true }
]
```

### Meta query

```json
"meta_query": [
  { "id": "mq1abc", "key": "price", "value": "100", "compare": ">=", "type": "NUMERIC" },
  { "id": "mq2def", "key": "featured", "value": "1", "compare": "=" }
],
"meta_query_relation": "AND"
```

`compare`: `=` `!=` `>` `>=` `<` `<=` `LIKE` `NOT LIKE` `IN` `NOT IN` `BETWEEN` `NOT BETWEEN` `EXISTS` `NOT EXISTS`. `type`: `CHAR` `NUMERIC` `DATE` `DATETIME` `DECIMAL` `SIGNED` `UNSIGNED` `TIME`. Values accept dynamic data (`"value": "{current_date:Y-m-d}"`).

## Term query keys

```json
{
  "objectType": "term",
  "taxonomy": ["category"],
  "number": "12",
  "orderby": "name",
  "order": "ASC",
  "hide_empty": true,
  "parent": "0",
  "include": [], "exclude": [],
  "current_post_term": true
}
```

`current_post_term: true` → only terms of the current post (tag-cloud pattern). Inside the loop use `{term_name}`/`{term_title}`, `{term_link}`, `{term_description}`, `{term_count}`.

## User query keys

```json
{
  "objectType": "user",
  "number": "8",
  "orderby": "display_name",
  "order": "ASC",
  "role__in": ["author", "editor"]
}
```

Loop tags: `{wp_user_display_name}`, `{wp_user_picture:thumbnail}`, `{wp_user_description}`, `{wp_user_meta:job_title}`, `{author_archive_url}`.

## Loop-context dynamic tags

| Tag | Output |
|-----|--------|
| `{query_loop_index}` | 0-based index — `{query_loop_index @start-at:1}` for 1-based, `@pad:2` to zero-pad |
| `{query_results_count}` | total results |
| `{query_results_count_filter}` | total results, auto-updates with AJAX filters |

Stagger animations by index: use `_attributes` with `data-index="{query_loop_index}"` + CSS, or interactions with delay.

## Pagination

`pagination` element targeting the loop:

```json
{
  "name": "pagination",
  "settings": { "queryId": "loop01", "ajax": true, "midSize": 2, "endSize": 1 }
}
```

`queryId` = the loop element's **id**. `ajax: true` re-renders in place (needs Query Filters enabled in Bricks settings).

## Infinite scroll / Load more

Infinite scroll — inside the loop's `query`:

```json
"query": { "...": "...", "infinite_scroll": true, "infinite_scroll_margin": "300px", "infinite_scroll_delay": "600" }
```

Load more — an interaction on a button:

```json
"_interactions": [
  { "id": "int001", "trigger": "click", "action": "loadMore", "loadMoreQuery": "loop01" }
]
```

Hide the button when done: trigger `filterOptionEmpty`/AJAX end interactions, or leave to Bricks (it disables automatically when the last page loads).

## Query results summary (1.12.2+)

```json
{ "name": "query-results-summary", "settings": { "queryId": "loop01", "statsFormat": "Showing %start%–%end% of %total%" } }
```

## No-results state

Give the loop's parent a sibling `block` with `_conditions` on `{query_results_count}` == 0, or use the loop element's built-in `empty_result` template setting if targeting the posts element. Simplest robust approach:

```json
{
  "name": "text-basic",
  "settings": {
    "text": "Nothing found. Try different filters.",
    "_conditions": [[ { "key": "dynamic_data", "dynamic_data": "{query_results_count:loop01}", "compare": "==", "value": "0" } ]]
  }
}
```

## PHP hooks (for reference docs see hooks.md)

```php
add_filter( 'bricks/posts/query_vars', fn( $vars, $settings, $element_id ) => $vars, 10, 3 );
add_filter( 'bricks/query/run', fn( $results, $query_obj ) => $results, 10, 2 );
add_filter( 'bricks/query/loop_object', fn( $object, $loop_key, $query_obj ) => $object, 10, 3 );
```
