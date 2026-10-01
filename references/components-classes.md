# Components, Global Classes & Variables

Reusable styling and structure primitives. Verified against `includes/components.php`, `includes/database.php`, `includes/assets.php` (2.3.6).

## Global classes

Stored in option `bricks_global_classes`. Object shape:

```json
{
  "id": "crd001",
  "name": "card",
  "settings": {
    "_background": { "color": { "hex": "#ffffff" } },
    "_border": { "radius": { "top": "16px", "right": "16px", "bottom": "16px", "left": "16px" } },
    "_boxShadow": { "values": { "offsetX": "0", "offsetY": "4", "blur": "16" }, "color": { "rgb": "rgba(15,23,42,0.08)" } },
    "_padding": { "top": "32px", "right": "32px", "bottom": "32px", "left": "32px" },
    "_background:hover": { "color": { "hex": "#f8fafc" } },
    "_cssCustom": ".card:focus-within { outline: 2px solid currentColor; }"
  },
  "category": null
}
```

- Class settings = element settings (same keys, same shapes, breakpoints + pseudo suffixes included).
- Elements attach by **id**: `"_cssGlobalClasses": ["crd001"]`.
- In clipboard/template JSON, include each referenced class object in `globalClasses` / `global_classes`.
- On import/paste, classes merge by id (skip) or name (remap) — naming classes well prevents duplicates across pastes.
- `_cssCustom` inside a class uses the literal class selector (`.card`), not `%root%` — when copying styles between classes Bricks rewrites it.

**When to use global classes vs inline settings:** repeated patterns (cards, buttons, badges, section paddings) → class; one-off tweaks → element settings. For full designs, a small set of classes (`card`, `btn-primary`, `section-pad`, `eyebrow`) keeps the JSON light and the site maintainable.

## Global variables

Option `bricks_global_variables`:

```json
[
  { "id": "gv001", "name": "space-section", "value": "clamp(4rem, 8vw, 7rem)", "category": null },
  { "id": "gv002", "name": "radius-card", "value": "16px" }
]
```

Emitted as `:root { --space-section: clamp(4rem, 8vw, 7rem); }`. Use anywhere via `raw`/string values: `"_padding": { "top": "var(--space-section)" }`. Template exports carry them in `globalVariables`.

## Color palettes

Option `bricks_color_palette`: `[{ "id": "...", "name": "Brand", "colors": [{ "id": "c1a2b3", "name": "Primary", "hex": "#1d4ed8" }] }]`.
A palette color used in settings carries its `id` → CSS `var(--bricks-color-c1a2b3)`. Only reference palette ids that exist on the target site; otherwise ship plain `hex`/`raw` values.

## Components (1.12+)

Stored in option `bricks_components`. A component = element tree + typed properties; instances reference it.

```json
{
  "id": "cmp001",
  "label": "Feature Card",
  "elements": [
    { "id": "root01", "name": "block", "parent": 0, "children": ["ico001", "ttl001"], "settings": {} },
    { "id": "ico001", "name": "icon", "parent": "root01", "children": [], "settings": {} },
    { "id": "ttl001", "name": "heading", "parent": "root01", "children": [], "settings": { "text": "Title" } }
  ],
  "properties": [
    { "id": "prp001", "label": "Title", "type": "text", "default": "Feature" }
  ]
}
```

An **instance** in page content is a thin node:

```json
{ "id": "ins001", "cid": "cmp001", "name": "block", "parent": "con001", "children": [], "settings": { "properties": { "prp001": "Fast indexing" } } }
```

- `cid` points to the component; `instanceId` appears on nested instance contexts.
- Clipboard JSON must carry referenced components in the top-level `components` array (the builder does this automatically on copy).
- Variants (2.2+): component variants add `:variant-{id}` suffixed settings keys.

**Authoring guidance:** components are powerful but coupling is high — for generated layouts prefer plain element trees + global classes unless the user explicitly works with components.

## Global elements (legacy)

Option `bricks_global_elements` — single elements shared across pages (pre-components). Element node carries a `global` id. Prefer components on 1.12+.

## Pseudo-classes registry

Option `bricks_global_pseudo_classes`, default `[':hover', ':active', ':focus']`. Using other pseudo suffixes (`:before`, `:after`, `:focus-within`…) in settings requires them to exist there — template import auto-creates missing ones; clipboard paste of unknown pseudos may not. Safest: stick to the defaults in settings keys and use `_cssCustom` for `::before`/`::after` content styling.
