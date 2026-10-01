---
name: bricks
description: "Master operating manual for Bricks Builder 2.4+ (WordPress). Unified edition combining CodeerHQ official MCP/Abilities API architecture with WPGaurav rapid JSON authoring and 16 pattern libraries."
---

# Bricks Builder Master Skill (2.4+ Unified Edition)

Single operational manual for **authoring paste-ready JSON** and **executing remote MCP operations** in Bricks Builder 2.4+.
Designed for minimal steps to execution with complete coverage of all 25 Bricks subsystem manuals.

---

## 1. Minimal-Step Action Guide

Identify the task objective and execute via the corresponding minimal path:

### Path A: Generate Bricks JSON for User

```text
Step 1: Pick Delivery Format (3-second decision)
  ├── Canvas Direct Paste (User presses Cmd+V) ➔ Clipboard format (`bricksCopiedElements`)
  ├── WP Admin Template Import (User imports .json) ➔ Template format (`content`, `global_classes`)
  └── Direct DB / WP-CLI / REST ➔ Pure element array (`_bricks_page_content_2`)
  → Full specs: references/json-formats.md

Step 2: Compose Elements & Style (Lookup cheat sheets or copy patterns)
  ├── Structure: Check patterns/INDEX.md for 16 ready-to-use sections (Hero, Cards, FAQ, Pricing, Forms)
  ├── Elements: Look up controls & tags in references/elements.md
  ├── Styles: Look up exact keys in references/style-settings.md (`_typography`, `_background`, `_padding:tablet_portrait`)
  └── Rem Base: Default 1rem = 16px (or 10px if 62.5% html reset). Convert clamp/rem accordingly.

Step 3: Validate & Deliver
  └── Run validator locally: `python3 ~/.gemini/skills/bricks/scripts/validate_bricks_json.py <file.json>`
```

### Path B: Operate Live Site via MCP Adapter / Abilities

```text
Step 1: Read Context (Avoid duplicate creations)
  └── Call `bricks-get-design-context` to fetch active palette color IDs, global classes, and component digests.

Step 2: Execute Action
  ├── Global Foundation (Colors, Classes, Styles) ➔ `bricks-commit-site-foundation`
  ├── Create/Update Page Elements ➔ `bricks-commit-site-edit-plan` or direct postmeta
  │   (Note: If optimistic digest conflict occurs, re-read digest and commit)
  └── Build Reusable Component ➔ `create-component` with `properties` & `connections`

Step 3: Flush & Frontend Verification
  └── Flush server Varnish & WP cache (`varnishadm 'ban req.url ~ .'` && `wp cache flush`), take browser screenshot.
```

---

## 2. Comprehensive Task Routing Table

Find the exact reference manual for any specific Bricks task:

| Subsystem / Task | Purpose & Content | Direct Manual |
|---|---|---|
| **JSON Delivery Formats** | Clipboard (`bricksCopiedElements`), Template Export, Postmeta keys | [`references/json-formats.md`](references/json-formats.md) |
| **CSS Style Settings Keys** | Exhaustive `_` keys: colors, typography, borders, shadows, responsive colons (`:tablet_portrait`) | [`references/style-settings.md`](references/style-settings.md) |
| **Element Catalog** | Element options, nestables, tag semantic overrides (`header`, `article`, etc.) | [`references/elements.md`](references/elements.md) |
| **Layout Recipes** | CSS Grid, Flexbox, Hero splits, Overlay cards, Sticky elements | [`references/layout-recipes.md`](references/layout-recipes.md) |
| **Pre-built UI Patterns** | 16 complete JSON layouts (Hero, Pricing, Cards, FAQ, Forms, Modals) | [`patterns/INDEX.md`](patterns/INDEX.md) |
| **Components & BEM Classes** | Component definitions, global class BEM organization, instance calls | [`references/components-classes.md`](references/components-classes.md) |
| **Dynamic Data Tags** | Built-in tags `{post_title}`, `{featured_image}`, custom functions `{echo:func}` | [`references/dynamic-data.md`](references/dynamic-data.md) |
| **Query Loops** | Post, Term, User, and repeater queries (`hasLoop`, `query` object structure) | [`references/query-loops.md`](references/query-loops.md) |
| **Query Filters & Search** | Faceted filtering, live search, AJAX pagination, infinite scroll | [`references/query-filters.md`](references/query-filters.md) |
| **Render Conditions** | Show/hide logic (`_conditions`), user roles, post types, custom field values | [`references/conditions.md`](references/conditions.md) |
| **Interactions & Animations** | Click triggers, scroll reveals, CSS class toggles, animation timelines | [`references/interactions.md`](references/interactions.md) |
| **Forms & Actions** | Native Form element, field mapping, email actions, custom webhooks | [`references/forms.md`](references/forms.md) |
| **Popups & Modals** | Popup templates, exit-intent triggers, scroll depth, session limits | [`references/popups.md`](references/popups.md) |
| **Templates & Conditions** | Template types (`header`, `footer`, `archive`, `404`), conditions (`main: any`) | [`references/templates.md`](references/templates.md) |
| **Theme Styles & Breakpoints** | Root font size, color palette hierarchy, custom breakpoint widths | [`references/theme-styles.md`](references/theme-styles.md) |
| **WooCommerce Integration** | Single product templates, cart, checkout, custom product loops | [`references/woocommerce.md`](references/woocommerce.md) |
| **ACF & Custom Fields** | Advanced Custom Fields, Meta Box, JetEngine, Pods repeaters & flexible content | [`references/acf-providers.md`](references/acf-providers.md) |
| **Custom Elements (PHP)** | Creating custom Bricks elements via child theme with control registration | [`references/custom-elements.md`](references/custom-elements.md) |
| **PHP Actions & Filters** | All official Bricks hooks, rendering overrides, custom code execution | [`references/hooks.md`](references/hooks.md) |
| **External Assets & Media** | Absolute media URLs, remote SVG inlining, re-hosting external assets | [`references/external-assets.md`](references/external-assets.md) |
| **Asset Loading & Security** | Inline vs File CSS loading, builder execution capabilities, code signing | [`references/assets-permissions.md`](references/assets-permissions.md) |
| **Official MCP Tool Mapping** | 11 dedicated Bricks Abilities, write tiers, brief evaluation & audit gates | [`references/mcp-adapter/01-workflow-and-routing.md`](references/mcp-adapter/01-workflow-and-routing.md) |
| **Official Design System API** | Palette IDs, category management, rem scale generators via MCP | [`references/mcp-adapter/02-design-systems-and-styles.md`](references/mcp-adapter/02-design-systems-and-styles.md) |
| **2.4+ Component Properties** | Component `properties` definitions & `connections: { "el_id": ["text"] }` binding | [`references/mcp-adapter/03-templates-layouts-and-elements.md`](references/mcp-adapter/03-templates-layouts-and-elements.md) |
| **Official Query Structure** | Deep schema for WP_Query objects & nested repeater loop bindings | [`references/mcp-adapter/04-dynamic-data-and-queries.md`](references/mcp-adapter/04-dynamic-data-and-queries.md) |
| **Official Code Execution Guard** | Code element signing, authorized user caps, server-side execution sandboxes | [`references/mcp-adapter/05-custom-code-and-extensions.md`](references/mcp-adapter/05-custom-code-and-extensions.md) |

---

## 3. Non-Negotiable Engineering Rules

1. **Flat Tree Integrity**:
   - The elements array is strictly flat. Tree hierarchy is formed exclusively via `parent` and `children`.
   - Every `children` ID must exist as a node whose `parent` points back.
   - Root elements must have `parent: 0` (Sections). Never place a `section` under a `div`.
2. **Settings Must Be a Dictionary**:
   - `settings` must always be an object `{}`. **Never emit an empty list `settings: []`**.
3. **Bricks 2.4+ Custom CSS Selectors**:
   - For page elements, custom CSS rules in `_cssCustom` must use `#brxe-{id}`.
   - For elements inside reusable components, custom CSS rules must use `.brxe-{id}`.
   - Do **not** leave unparsed `%root%` or `root` in programmatic output.
4. **Component Instances**:
   - Instance nodes (`cid: "..."`) must **omit `children`** so the component definition controls internal layout.
   - Dynamic parameters are passed via `"properties": { "prop_name": "value" }`.
5. **Verified Value Shapes**:
   - Colors: `{"hex": "#23221e"}` or `{"raw": "var(--brand-primary)"}`.
   - Typography: use explicit CSS property keys (`"font-size"`, `"line-height"`, `"letter-spacing"`).
   - Box-shadow: nested under `values` (`{"values": {"x": "0", "y": "4px", "blur": "12px", "spread": "0"}, "color": {...}}`).
6. **Responsive Grammar**:
   - Use colon suffixes for breakpoints and pseudo-states: `_padding:tablet_portrait`, `_background:hover`, `_margin:mobile_portrait:hover`.
   - Default breakpoints: `tablet_portrait` (991px), `mobile_landscape` (767px), `mobile_portrait` (478px). Desktop is the bare key.
7. **External Assets**:
   - Reference images and SVGs by absolute URLs or uploaded WordPress attachment IDs. Never invent non-existent IDs.
8. **Native Links (Zero Tolerance for Fake Attributes)**:
   - **Never simulate links** with `tag: "custom"`, `customTag: "a"`, or manual `_attributes: [{"name": "href", ...}]`.
   - Always use Bricks native `settings.link`:
     ```json
     "link": {
       "type": "external",
       "url": "/about/",
       "target": "_blank",
       "rel": "noopener noreferrer"
     }
     ```
     For internal anchor targets: `{"type": "external", "url": "#section-id"}`.
9. **Centralized CSS vs Panel Settings**:
   - Do **NOT** duplicate identical CSS across multiple pages. Put reusable layout and typography rules in `Theme Styles > css.stylesheet`.
   - Keep user-editable content (links, images, texts, button labels) in native element controls.
10. **WP-CLI / Programmatic Ops Guard**:
   - When calling Abilities (`wp_get_ability('bricks/set-page-elements')`) in CLI scripts, always call `wp_set_current_user(1);` first to bypass capability checks.
   - For standard posts/pages, omit `area` in `get-page-elements` / `set-page-elements` (only templates use `area: "header"` or `area: "footer"`).


---

## 4. Local Validation Command

Before delivering any JSON or committing to the database:

```bash
python3 ~/.gemini/skills/bricks/scripts/validate_bricks_json.py <path-to-json-file>
```
