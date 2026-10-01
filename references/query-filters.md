# Query Filters (Faceted Filtering)

AJAX filtering, sorting, live search, and pagination for query loops. Requires **Bricks Settings → General → Query Filters** enabled (this also creates the index table `wp_bricks_query_filters_index` and enables AJAX pagination). Verified against `includes/query-filters.php` + `includes/elements/filter-*.php` (2.3.6).

## Mental model

1. A query loop element (id, e.g. `loop01`) renders results.
2. Filter elements each point at it: `"filterQueryId": "loop01"`.
3. Bricks indexes filterable values (taxonomies, meta, post fields) in its own table; filtering happens over AJAX with URL params.

Filters only work on **post** query loops on the same page.

## Shared filter settings (all filter-* elements)

```json
{
  "filterQueryId": "loop01",
  "filterApplyOn": "change",
  "filterNiceName": "topic",
  "filterHideEmpty": true,
  "filterHideCount": false
}
```

| Key | Values | Meaning |
|-----|--------|---------|
| `filterQueryId` | loop element id | **required** |
| `filterApplyOn` | `change` (instant AJAX) / `click` (wait for filter-submit) | |
| `filterNiceName` | string | URL parameter name (clean URLs) |
| `filterHideEmpty` | bool | hide options with 0 results |
| `filterHideCount` | bool | hide result counts |
| `filterMultiLogic` | `OR` / `AND` | multi-select logic (checkbox) |

## Filter sources

Choice filters (`filter-select`, `filter-checkbox`, `filter-radio`) need a source:

**Taxonomy:**
```json
{ "filterSource": "taxonomy", "filterTaxonomy": "category", "filterTermInclude": [], "filterTermExclude": [], "filterHierarchical": true, "filterTermTopLevel": false }
```

**Custom field (ACF/Meta Box/native meta):**
```json
{ "filterSource": "customField", "sourceFieldType": "post", "customFieldKey": "difficulty",
  "labelMapping": "custom",
  "customLabelMapping": [ { "optionMetaValue": "beginner", "optionLabel": "Beginner friendly" } ] }
```

**WP field:**
```json
{ "filterSource": "wpField", "wpPostField": "post_author" }
```

## The elements

### filter-search (live search)
```json
{ "name": "filter-search", "settings": {
  "filterQueryId": "loop01", "placeholder": "Search articles…",
  "filterApplyOn": "change", "filterInputDebounce": 400, "filterMinChars": 2 } }
```

### filter-select
```json
{ "name": "filter-select", "settings": {
  "filterQueryId": "loop01", "filterSource": "taxonomy", "filterTaxonomy": "category",
  "filterLabelAll": "All categories", "filterNiceName": "cat" } }
```

Sorting variant (`filterAction: "sort"`):
```json
{ "name": "filter-select", "settings": {
  "filterQueryId": "loop01", "filterAction": "sort", "filterLabelAll": "Sort by",
  "sortOptions": [
    { "id": "so1abc", "optionLabel": "Newest", "optionSource": "date", "optionOrder": "DESC" },
    { "id": "so2def", "optionLabel": "Title A–Z", "optionSource": "title", "optionOrder": "ASC" },
    { "id": "so3ghi", "optionLabel": "Price low–high", "optionSource": "_price", "optionSourceFieldType": "customField", "optionOrder": "ASC", "optionOrderBy": "meta_value_num" }
  ] } }
```

### filter-checkbox / filter-radio
Same source settings; `displayMode: "button"` renders as toggle buttons. `filterMultiLogic` for checkbox AND/OR.

### filter-range (numeric meta, e.g. price)
```json
{ "name": "filter-range", "settings": {
  "filterQueryId": "loop01", "filterSource": "customField", "sourceFieldType": "post",
  "customFieldKey": "price", "min": "0", "max": "1000", "step": "10", "mode": "range" } }
```

### filter-datepicker
```json
{ "name": "filter-datepicker", "settings": {
  "filterQueryId": "loop01", "filterSource": "customField", "customFieldKey": "event_date",
  "enableTime": false, "isDateRange": true } }
```

### filter-submit
Button that applies all `filterApplyOn: "click"` filters in the same form/section. Settings: `text`, plus button styling.

### filter-active-filters
Chips showing active filters with remove buttons: `{ "filterQueryId": "loop01" }`.

### pagination (AJAX)
```json
{ "name": "pagination", "settings": { "queryId": "loop01", "ajax": true } }
```

## Counts, summaries, empty states

- `{query_results_count_filter:loop01}` — live-updating count text.
- `query-results-summary` element — "Showing X–Y of Z".
- `{active_filters_count}` — number of active filters.
- Interactions triggers `filterOptionEmpty` / `filterOptionNotEmpty` (+ `filterElementId`) and `ajaxStart`/`ajaxEnd` (+ `ajaxQueryId`) let you show loaders or empty-state blocks.

## Indexing gotchas

- After adding filters on meta keys or importing content programmatically, regenerate the index: Bricks → Settings → Query Filters → Reindex (or `wp bricks` CLI in newer builds; otherwise the settings button).
- Indexable sources: taxonomies, custom fields (post/term/user), WP post fields. ACF fields index by their meta key (e.g. repeater subfields as `parent_0_subfield` — filter on simple top-level fields).
- Filters + `is_archive_main_query` loops work; filters + multiple loops need distinct `filterQueryId` per loop.

## Complete wired example

```json
{
  "content": [
    { "id": "sec001", "name": "section", "parent": 0, "children": ["con001"], "settings": {} },
    { "id": "con001", "name": "container", "parent": "sec001", "children": ["bar001", "grid01", "pag001"], "settings": {} },
    { "id": "bar001", "name": "block", "parent": "con001", "children": ["src001", "cat001", "srt001"], "label": "Filter Bar",
      "settings": { "_direction": "row", "_columnGap": "16px", "_flexWrap": "wrap" } },
    { "id": "src001", "name": "filter-search", "parent": "bar001", "children": [],
      "settings": { "filterQueryId": "loop01", "placeholder": "Search…" } },
    { "id": "cat001", "name": "filter-select", "parent": "bar001", "children": [],
      "settings": { "filterQueryId": "loop01", "filterSource": "taxonomy", "filterTaxonomy": "category", "filterLabelAll": "All topics" } },
    { "id": "srt001", "name": "filter-select", "parent": "bar001", "children": [],
      "settings": { "filterQueryId": "loop01", "filterAction": "sort", "filterLabelAll": "Sort",
        "sortOptions": [ { "id": "so1aaa", "optionLabel": "Newest", "optionSource": "date", "optionOrder": "DESC" } ] } },
    { "id": "grid01", "name": "div", "parent": "con001", "children": ["loop01"], "label": "Results Grid",
      "settings": { "_display": "grid", "_gridTemplateColumns": "repeat(3, minmax(0,1fr))", "_gridGap": "24px",
        "_gridTemplateColumns:tablet_portrait": "repeat(2, minmax(0,1fr))",
        "_gridTemplateColumns:mobile_portrait": "1fr" } },
    { "id": "loop01", "name": "block", "parent": "grid01", "children": ["img001", "ttl001"], "label": "Card",
      "settings": { "hasLoop": true,
        "query": { "objectType": "post", "post_type": ["post"], "posts_per_page": "9" } } },
    { "id": "img001", "name": "image", "parent": "loop01", "children": [],
      "settings": { "image": { "useDynamicData": "{featured_image}", "size": "medium_large" }, "_aspectRatio": "3/2", "_objectFit": "cover" } },
    { "id": "ttl001", "name": "heading", "parent": "loop01", "children": [],
      "settings": { "text": "{post_title}", "tag": "h3", "link": { "type": "meta", "useDynamicData": "{post_url}" } } },
    { "id": "pag001", "name": "pagination", "parent": "con001", "children": [],
      "settings": { "queryId": "loop01", "ajax": true } }
  ],
  "source": "bricksCopiedElements",
  "sourceUrl": "https://example.com",
  "version": "2.3.6",
  "globalClasses": [],
  "globalElements": []
}
```
