# Bricks JSON Formats & Storage

Three ways to get JSON into Bricks. Pick by destination. All shapes below verified against Bricks 2.3.6 source.

## Decision Table

| Goal | Format | Delivery |
|------|--------|----------|
| Section / part of a page | Clipboard format | User pastes into builder (Cmd/Ctrl+V in structure panel) |
| Whole reusable template (header, footer, archive, popup…) | Template export format | Bricks > Templates > Import |
| Create/update pages in bulk, migrations, CI | Postmeta insert | PHP / WP-CLI writes meta keys directly |

## 1. Clipboard Format (`bricksCopiedElements`)

What the builder itself writes to the clipboard (`writeToClipboard` in `assets/js/main.min.js`). Paste-target validation checks `source`.

```json
{
  "content": [ /* flat array of element nodes */ ],
  "source": "bricksCopiedElements",
  "sourceUrl": "https://yoursite.com",
  "version": "2.3.6",
  "globalClasses": [ /* full class objects for every id used in _cssGlobalClasses */ ],
  "globalElements": [],
  "components": [ /* only when content references components via cid */ ]
}
```

- `content` — flat list; hierarchy via `parent`/`children` ids.
- `globalClasses` — Bricks collects every class referenced by any element's `_cssGlobalClasses` and embeds the **full object** (see below). On paste, classes are merged: same `id` → skipped (local wins), same `name` → remapped to the local class id, otherwise added.
- `components` — full component definitions for any element node carrying a `cid`.
- `version` — set to the target site's Bricks version or current (`2.3.6`); paste does not hard-fail on version but include it.

### Element node

```json
{
  "id": "hxbbms",
  "name": "container",
  "parent": "sec001",
  "children": ["hdg001", "txt001"],
  "settings": { },
  "label": "Hero Content"
}
```

| Key | Required | Notes |
|-----|----------|-------|
| `id` | yes | 6-char alphanumeric, unique within the file. Semantic (`sec001`) or random (`jdhuyf`) both fine. |
| `name` | yes | Element type from the registry (see elements.md) |
| `parent` | yes | Parent id, or `0` for root (Sections). Never nest a section under a div. |
| `children` | yes | Ordered child ids (empty array for leaves). Must mirror parent IDs exactly. |
| `settings` | yes | Must be a dictionary `{}` — **NEVER an empty list `[]`**. |
| `settings._cssCustom` | no | In Bricks 2.4+, write `#brxe-{id}` for page elements, `.brxe-{id}` inside components. Do not leave raw `%root%` in output. |
| `label` | no | Structure-panel label; documents layout visually. |
| `themeStyles` | no | Per-element theme-style overrides (rare) |
| `cid` | no | Component reference ID. Note: Component instance nodes should omit `children`. |
| `properties` | no | Key-value mapping for component input properties (e.g. `{"prop_title": "Hello"}`). |

### Global class object

```json
{
  "id": "qwe123",
  "name": "card",
  "settings": {
    "_background": { "color": { "hex": "#ffffff" } },
    "_border": { "radius": { "top": "12px", "right": "12px", "bottom": "12px", "left": "12px" } },
    "_padding": { "top": "32px", "right": "32px", "bottom": "32px", "left": "32px" }
  }
}
```

Class `settings` use the exact same keys/shapes as element settings, including breakpoint/pseudo suffixes. Elements reference classes by **id** (not name): `"_cssGlobalClasses": ["qwe123"]`.

## 2. Template Export Format

What Bricks > Templates > Export produces and Import consumes (`Templates::export_template()` / `import_template()`).

```json
{
  "id": 1195,
  "name": "header-main",
  "title": "Header Main",
  "type": "header",
  "header": [ /* element nodes — for type=header */ ],
  "content": [ /* element nodes — for content-ish types */ ],
  "footer": [ /* element nodes — for type=footer */ ],
  "pageSettings": { },
  "templateSettings": {
    "templateConditions": [
      { "main": "any" }
    ]
  },
  "global_classes": [ /* same class objects as clipboard globalClasses */ ],
  "globalVariables": [ { "id": "v1", "name": "space-lg", "value": "2rem" } ],
  "globalVariablesCategories": []
}
```

- Put elements in the array matching the type: `header` types → `header` key, `footer` → `footer`, everything else (`content`, `section`, `popup`, `archive`, `search`, `error`, `single`, `wc_*`) → `content`.
- Optional metadata keys (`date`, `author`, `permalink`, `thumbnail`, `bundles`, `tags`) can be omitted when hand-authoring.
- Import regenerates all element ids, merges global classes (same rules as paste), downloads any remote image URLs into the media library, and regenerates CSS files if CSS loading = file.
- Template types and `templateConditions` shapes: see templates.md.

## 3. Programmatic Insert (postmeta)

Bricks stores element trees as **PHP-serialized arrays** in postmeta (WordPress serializes automatically via `update_post_meta`).

| Meta key | Holds |
|----------|-------|
| `_bricks_page_content_2` | Element array for page/template content |
| `_bricks_page_header_2` | Element array (header templates) |
| `_bricks_page_footer_2` | Element array (footer templates) |
| `_bricks_editor_mode` | `"bricks"` — required or the page renders with WP editor |
| `_bricks_template_type` | Template type slug (on `bricks_template` posts) |
| `_bricks_template_settings` | Template settings incl. `templateConditions` |
| `_bricks_page_settings` | Page settings: `customCss`, `customScriptsHeader`, `customScriptsBodyHeader`, `customScriptsBodyFooter`, … |

```php
$elements = json_decode( file_get_contents( 'section.json' ), true )['content'];

$post_id = wp_insert_post( [
    'post_type'   => 'page',            // or 'bricks_template'
    'post_status' => 'publish',
    'post_title'  => 'Landing Page',
] );

update_post_meta( $post_id, '_bricks_page_content_2', $elements ); // array, NOT json string
update_post_meta( $post_id, '_bricks_editor_mode', 'bricks' );
```

For a template post additionally:

```php
update_post_meta( $post_id, '_bricks_template_type', 'header' );
update_post_meta( $post_id, '_bricks_template_settings', [
    'templateConditions' => [ [ 'main' => 'any' ] ],
] );
```

After bulk inserts, regenerate CSS (only needed when CSS loading method is "External files"):

```bash
wp bricks regenerate_assets
```

Global classes used by inserted elements must exist in the `bricks_global_classes` **option** (array of class objects) — postmeta insert does not merge them for you:

```php
$classes = get_option( 'bricks_global_classes', [] );
// append any missing class objects, then:
update_option( 'bricks_global_classes', $classes );
```

## Key Option Names (site-wide stores)

| Option | Contents |
|--------|----------|
| `bricks_global_settings` | Global settings (CSS loading method, custom CSS/JS, feature toggles) |
| `bricks_global_classes` | Global class objects |
| `bricks_global_classes_categories` | Class categories |
| `bricks_global_variables` | `[{id, name, value, category}]` → emitted as `:root { --name: value }` |
| `bricks_color_palette` | Palettes: `[{id, name, colors: [{id, name, hex, rgb, raw}]}]` |
| `bricks_components` | Component definitions |
| `bricks_theme_styles` | Theme styles |
| `bricks_breakpoints` | Custom breakpoints |
| `bricks_global_pseudo_classes` | Enabled pseudo-classes (default `[':hover', ':active', ':focus']`) |

## Validation Commands

```bash
python3 -m json.tool layout.json > /dev/null && echo OK
# tree integrity (quick python check)
python3 - <<'EOF'
import json,sys
d=json.load(open('layout.json'))
els=d.get('content', d.get('header', d.get('footer', [])))
ids={e['id'] for e in els}
assert len(ids)==len(els), 'duplicate ids'
for e in els:
    assert e['parent']==0 or e['parent'] in ids, f"orphan parent: {e['id']}"
    for c in e.get('children',[]): assert c in ids, f"missing child {c} of {e['id']}"
used={c for e in els for c in (e['settings'].get('_cssGlobalClasses') or [])}
have={g['id'] for g in d.get('globalClasses', d.get('global_classes', []))}
assert used<=have, f"classes missing: {used-have}"
print('tree OK')
EOF
```
