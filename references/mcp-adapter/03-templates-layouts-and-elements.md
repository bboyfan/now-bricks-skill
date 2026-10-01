# Bricks Reference: 03 Templates Layouts And Elements



---

## Module: bricks-html-css-to-bricks

# Bricks: HTML/CSS to Bricks

For a known empty page body, write semantic HTML/CSS and call `commit-html-css-page-import` once with one page identifier, complete `html` and `css`, `documentPurpose: "page-content"`, `replaceExisting: false`, and a new stable `idempotencyKey`. Import sibling page sections only: omit `<main>` because Bricks owns that landmark, and never embed a site-wide `<header>` or `<footer>` in a normal page. For the interior of an empty Bricks header/footer template, use `documentPurpose: "template-content"` and omit the automatic landmark. Do not call version, context, status, discovery, repository, changeset, the generic dispatcher, raw converter, or explicit preview first.

The ability checks the current design system, previews the conversion, saves it safely, and returns the persisted result. Exact retries reuse the same key.

If the result has `autoApplied: true`, require `committed: true` and `transactionState: "committed"`; the compact default response is authoritative. Request `responseFormat: "detailed"` only when complete design snapshots and preview data are needed. If it has `nextAction: "review_warnings"`, inspect every warning and the frozen preview; responses that require warning acknowledgement remain detailed automatically. Call `apply-html-css-page-import` with the returned `previewToken`, the same `idempotencyKey`, and `acknowledgeWarnings: true` only after review. On errors or policy violations, revise the source and use a new idempotency key. Render-check desktop and mobile after persistence.

Check `partial` and `omittedElements` even on a successful commit. On an empty target, Bricks can omit elements the caller cannot author (and their descendants), retain the permitted content and its dependencies, and commit automatically when those omissions are the only warnings. Report the omissions and verify that the retained result still meets the brief; do not call it a complete import. Partial replacement of existing content is rejected. Other warnings still require the returned acknowledgement flow. Do not retry by increasing permissions or inventing a skip-policy parameter.

Use `documentPurpose: "migration"` only when faithfully migrating an external fragment whose semantic wrappers and browser defaults are part of the source contract. It is not an escape hatch for a rejected page shell.

## Native-only profile

When custom CSS and new globals are forbidden, preview with:

```json
{
  "options": {
    "preserve_html_defaults": false,
    "custom_css_policy": "forbid",
    "global_resource_policy": "forbid_creates"
  }
}
```

Do not weaken these policies to make a preview pass. Rewrite unsupported selectors or declarations into native-mappable HTML/CSS and preview the complete candidate again.

For one-off native styling, give elements stable HTML IDs and target those IDs in CSS. Ordinary class selectors propose global Bricks classes and can violate `forbid_creates`. Put responsive overrides in the supplied CSS with explicit media queries; do not omit the `css` field when the brief includes responsive behavior. With default Bricks breakpoints, mobile portrait is `@media (max-width: 478px)`. If the site uses custom breakpoints, read design context and use the site's actual width.

## Native element hints

- `<section>` creates a Section.
- `<div class="brxe-container">` creates a centered native Container.
- `<div class="brxe-block">` creates a native Block.
- `<a class="brxe-button" href="...">Label</a>` creates a linked native Button; a plain `<a>` remains a Text Link.
- Headings, paragraphs, images, video, audio, SVG, divs, and forms map conservatively to native elements.
- Code, iframe, canvas, tables, and unsupported structures can produce Code fallbacks. Rewrite them when native-only output is required.

Do not nest Containers inside Containers or Sections inside Sections. Use Blocks or Divs for inner layout. Make browser-default typography explicit in CSS. When the source uses `rem`, pass both `options.source_root_font_size_px` and `options.target_root_font_size_px`. Pass the same explicit value for both when no scaling is needed; this avoids a normalization warning and second acknowledgement call. Rem normalization does not rescale media-query widths, so author those widths for the target site.

## Other conversion work

Use `convert-html-css-to-bricks-data` only when the task needs converted data without immediately replacing one known empty page: snippets, component authoring, CSS-only reconciliation, reusable globals, or manual Bricks-specific wiring. Its output is read-only and must be reviewed before persistence.

For these advanced routes, read [full-guide.md](references/full-guide.md) before acting. It covers write preconditions, global classes and variables, CSS-only conversion, executable-content safety, source rendering fidelity, dynamic/nestable element limits, and post-conversion quality checks.


---

## Module: bricks-figma-to-bricks

# Bricks: Figma to native editable content

Use the selected frame/specification and available Figma access. A missing
integration blocks only source information unavailable by other means; a complete
supplied specification can be enough. Load companions only for an actual subproblem
such as slots, font upload or form actions.

## Choose the target workflow before writing

| Target | Preferred path |
|---|---|
| Known empty page/template body; static source needs no tree surgery | `commit-html-css-page-import` can be the first Bricks operation; submit page content without site header/footer or redundant `main`; inspect omissions/completion |
| Existing page; add a section | Read target tree and relevant design resources; build only the new subtree; `add-element` at the requested parent/sibling position |
| Existing page; change identified elements | Focused partial updates, preserving unrelated settings, children, interactions and references |
| Authorized whole-page rebuild or component/stateful tree assembly | Convert/assemble in memory; persist the complete intended tree with applicable stale-state safeguards |
| New site/design system | Establish the agreed foundation; **bricks-design-systems** or **bricks-seed-design-system** when that scope applies |

Resolve the supplied target or use `find-post`. Create a page only when the brief
calls for one; failed lookup does not authorize a substitute. `set-page-elements`
replaces every element. Keep a complete baseline whenever replacing an existing tree.

## Reuse and map design resources

For existing-site work read relevant design context and actual breakpoint keys,
widths and direction. Summaries help select resources; read exact records where
values, bindings or ownership matter. Reuse appropriate classes, palette colors,
variables, theme styles and components before creating equivalents.

- Preserve exact values, including fractional spacing such as 7.5px. Reuse a token
  only when its meaning and resolved value fit.
- Keep section-specific differences local unless a reusable resource is justified.
  Do not redefine a shared token to repair one section.
- Match the site's naming convention; translate incoming references rather than
  renaming the site's variables to fit an export.
- Establish typography, font availability, rem basis, image crop and responsive
  behavior. Figma text-style names do not determine HTML heading semantics.
- Evaluate the actual export. CSS alone does not establish structure/interactions;
  no exporter is universally the most faithful.

### Missing resources and theme defaults

Palette/color creates use the latest `list-color-palettes` resource `ownership`;
updates use target `itemOwnership`. `create-color` takes `paletteId` and values such
as `light`, not a `hex`/name pair. A palette color with `raw: "var(--name)"` emits
that variable: do not duplicate it as a global variable.

Variables/categories use paired ownership from one fresh `list-global-variables`
read. Category fields are IDs. `generate-scale-variables` previews; persist reviewed
rows through `set-global-variables`, not `save: true`. Use **bricks-design-systems**
for category changes and shared-resource details.

Create/update root defaults only for a foundation or requested site-wide change.
An active root theme style uses `conditions: [{ main: "any" }]`; empty conditions
are inactive. A section insertion does not require a new root theme style or scale.

## Convert and assemble

Use read-only `convert-html-css-to-bricks-data` when the empty-page importer does
not fit. Convert the relevant fragment; inspect warnings, fallback elements and
capability omissions before persistence. Read [the HTML/CSS guide](../bricks-html-css-to-bricks/references/full-guide.md)
for resource reconciliation and conversion mechanics.

Preserve IDs for new accepted converter resources. When reusing an equivalent or
resolving a collision, deliberately map every affected reference. Do not persist
duplicate names or indiscriminately regenerate IDs.

Reuse components when they fit. Create one when repetition or exposed properties
justify it, not automatically for every card/button. Persist its dependencies and
use returned component IDs/remapped bindings for instances. Assemble the final tree
in memory instead of saving a temporary duplicated version.

Static conversion does not establish native Tabs, Accordion, Slider, navigation,
popup triggers, interactions or form actions. Read their runtime schemas and the
relevant companion only when needed. Offcanvas is an element; a popup uses a
template. Do not substitute inert visual imitations for these behaviors.

### Existing-page insertion

Identify the anchor's actual ID, parent and sibling position. Resolve ambiguity
before the dependent write. `add-element` accepts a nested `element` subtree,
`parentId` (`"0"` for root) and zero-based `position` among siblings. Insert after
the observed anchor and preserve old siblings/order. Bricks can generate omitted
internal IDs for nested input.

Inspect returned IDs and perform a focused read when saved settings/structure are
not established by the response. If insertion cannot be expressed through available
operations, use a supported workspace path or merge into a complete fresh baseline
before replacement. Never send only the new section to `set-page-elements`.

## Completion evidence

Check the intended subtree/position, resource mappings and preserved old content.
Inspect import completion and omissions; incomplete content is not a faithful build.
When browser access exists compare the source viewport and relevant site breakpoints,
then test native interactions. Use **bricks-browser-verify** for this work. No fixed
pixel tolerance proves success. Repair within the brief and explain intentional
deviations. Without a browser, perform available data/render checks and report
visual/interactive verification as outstanding.


---

## Module: bricks-templates-conditions

# Bricks: templates & conditions

Bricks templates are WP posts of the `bricks_template` custom post type, tagged with a `_bricks_template_type` meta (`'header'`, `'footer'`, `'content'`, etc.) and gated by display **conditions**. For every page the site renders, Bricks picks **one template per part** (header, footer, content) by scoring conditions: the highest score wins. WooCommerce adds extra template types when its integration is active. Use this as the condition-selection reference for the normal Bricks template flow.

## The 8 normal template types plus password protection

Normal template types are registered in `includes/setup.php`. `password_protection` is a conditional template type used by password protection. Post_meta constant `BRICKS_DB_TEMPLATE_TYPE = '_bricks_template_type'` (`functions.php`).

| Value | Purpose | Eligible contexts |
|---|---|---|
| `header` | Site header | All pages (one winner per page) |
| `footer` | Site footer | All pages |
| `content` | Single-post body ("Single") | `is_singular()`: single posts, pages, CPTs |
| `section` | Reusable content block | Inserted via the Template element: doesn't self-render |
| `popup` | Popup template | Rendered when conditions match + an interaction opens it |
| `archive` | Archive layout | `is_archive()`, `is_post_type_archive()`, taxonomies, authors, dates |
| `search` | Search results | `is_search()` |
| `error` | 404 page | `is_404()` |
| `password_protection` (conditional) | Password gate | When WP password-protection is active on a post |

Each template post has one type value (via the meta). `section` is special: it doesn't self-render; it's used by the Template element inside other templates.

## The one-template-wins rule

For each render part (header, content, footer), Bricks iterates every template of that type, scores each template's conditions against the current request, and picks the **highest-scoring template**. Do not rely on same-score ties: the source stores matches by score, so a later template at the same score can replace an earlier one based on query iteration order.

Resolution logic: `includes/database.php:625-708` (`find_template_id()`).

Templates that lose selection are skipped. When a template does not appear, check matching conditions, competing templates, page-level disable settings, and the requested render context before concluding which template won.

## Condition scoring (0 -> 10, plus boosts)

From `includes/database.php::screen_conditions()`. Higher = more specific = wins.

| Score | Condition match | Example |
|---|---|---|
| 0 | No conditions | Ultimate fallback |
| 1 | Template type matches content type | Search template on a search page |
| 2 | `main: any` | Entire website |
| 3 | `main: archiveType` with `archiveType: any` | Any archive page |
| 4 | Any term archive with no `archiveTerms` list | All taxonomy archives |
| 7 | Singular post-type match, all CPT archives with `archivePostTypes` omitted, or runtime `taxonomy::all` term-archive match | All posts of type Product |
| 8 | Child pages of specific IDs, assigned terms, specific archive CPT, author, date, search/error, or specific term archive | Archive of `product_cat: deals` |
| 9 | Front page | `main: frontpage` |
| 10 | Specific post ID via `main: ids` | Exactly post id 42 |
| +100 | Password-protection templates | Password protection wins over normal templates |

**Implication:** a template with `main: any` (score 2) gets beaten by a template with a post-type match (score 7 or 8) on that post type. Use `any` as the base fallback, then create specific templates that win on their pages.

## Content-type resolution: what page is this?

From `database.php:489-525`. WP context -> Bricks content_type:

| WP function | content_type |
|---|---|
| `is_singular()` | `content` |
| `is_post_type_archive()`, `is_tax()`, `is_category()`, `is_tag()`, `is_author()`, `is_date()` | `archive` |
| `is_search()` | `search` |
| `is_404()` | `error` |

Filterable via `bricks/database/content_type` (`database.php:518`): useful for custom routing plugins.

Then `find_template_id()` picks a template of the matching type whose conditions score highest.

## The condition data structure (canonical)

Stored in `_bricks_template_settings` meta, under the `templateConditions` key.

The MCP `set-template-conditions` ability accepts the conditions array at the top level:

```json
{
  "templateId": 123,
  "conditions": [
    { "main": "any" },
    { "main": "frontpage" },
    { "main": "postType", "postType": ["post", "page"] },
    { "main": "archiveType", "archiveType": ["postType"], "archivePostTypes": ["product"] },
    { "main": "search" },
    { "main": "error" },
    { "main": "terms", "terms": ["category::5", "product_cat::12"] },
    { "main": "ids", "ids": [42, 89] },
    { "main": "any", "hookName": "woocommerce_after_main_content", "hookPriority": 10 }
  ]
}
```

Bricks stores that array as `_bricks_template_settings.templateConditions`.

The `main` enum is exactly: `any`, `frontpage`, `postType`, `archiveType`, `search`, `error`, `terms`, `ids`, `hook`. `hook` is accepted by the MCP validator for legacy/convenience input, but `set-template-conditions` stores it as `any` when `hookName` is present (`includes/abilities/templates.php:1006-1014`). **Do not invent kinds.** In particular:
- `any` (NOT `entireWebsite`)
- `terms` (NOT `archiveTerm`)
- `hookName` is for **section templates only**: it injects the section's content at the named WP action.

Term identifiers accepted by `set-template-conditions` depend on the condition key:

- `terms`: strings in `taxonomy::id` form, e.g. `"category::5"`, `"product_cat::12"`. Do not send raw term IDs or term objects.
- `archiveTerms`: strings in `taxonomy::id` or `taxonomy::all` form, e.g. `"category::5"`, `"product_cat::all"`. The `taxonomy::all` branch is archive-only (`includes/database.php:1049-1054`).

**Multiple conditions in the array = OR.** Any single condition match wins.

## Header and footer templates

Check header and footer template selection separately from the content template.

Best practice: a single header template with `{ "main": "any" }` (score 2) as the base, then variants for specific sections if needed.

See the `bricks-headers-footers` skill for the meta-routing rules MCP element-write tools follow when editing header/footer template trees.

## Archive template: the CPT trap

To create a CPT archive layout:
1. Template type = `archive`.
2. Condition: `{ "main": "archiveType", "archiveType": ["postType"], "archivePostTypes": ["product"] }`.
3. On the frontend, `/product/` (or whatever the CPT's archive slug is) will now use this template.

**Trap:** if the CPT has `has_archive = false` in its registration, there's no archive URL and the template has no context to render in. Fix the CPT registration or use a regular page + a Posts loop instead.

## Search + error templates

- `search`: triggered by `?s=query` or `/?s=query`. Use `{ "main": "search" }` for search-results templates. Do not use `{ "main": "any" }` unless you intentionally want a broad body-template fallback, because Bricks scores all body-type templates together.
- `error`: 404 template. Conditions typically `{ "main": "any" }` too.

If you don't create them, WP falls back to the default theme files (which Bricks sometimes renders minimally, sometimes not at all, depending on theme).

## Preview mode: testing template conditions

In the builder, the top-right has a **Preview as** dropdown. Use it to simulate different content types: Bricks evaluates conditions against the simulated context.

It does not simulate every frontend route, custom query, or plugin filter perfectly. For those, view the frontend.

## Related hooks

| Hook | Purpose |
|---|---|
| `bricks/database/content_type` | Override the WP context -> Bricks content_type mapping (`database.php:518`) |
| `bricks/active_templates` | Mutate the list of active templates after resolution (`database.php:606`) |
| `bricks/get_templates` | Filter the full template query result (`templates.php:954`) |
| `bricks/render_with_bricks` | Whether Bricks renders at all for this request (`helpers.php:1741`) |

See `hooks-reference` for the complete template hook list.

## "No condition" templates: inert fallbacks

A template with **no conditions** does not match through `screen_conditions()` itself. `find_template_id()` adds narrow fallbacks for some template types: header/footer can score 0 when default templates are enabled, and a template whose type matches the current content type can score 1. Do not use empty conditions as a normal site-wide rule; use `{ "main": "any" }` instead.

## Silent-failure debug order

1. **Template doesn't show where expected?**
   a. Open the builder -> the template -> Template settings -> Conditions. Does the current page match at all?
   b. Another template of the same type has a higher score. Check `WP Admin > Bricks > Templates`: compare conditions across all templates of the same type.
   c. Condition uses a CPT or taxonomy slug that changed. Slugs don't get live-migrated.

2. **Template shows where not expected?**
   a. `main: any` on a template that should be specific. Replace with a more specific condition.
   b. Condition list has an extra OR entry that's too broad.

3. **Multiple templates "should" render, only one does?**
   a. Working as designed. Only one template per part wins. Use the Template element (inserts a `section` type) to compose.

4. **Header is empty / page has no header?**
   a. No header template matches. Create one with `{ "main": "any" }` as fallback.
   b. Header template exists but its conditions do not match the current page.

5. **Archive template not rendering on the CPT archive?**
   a. CPT has `has_archive = false`: no archive URL exists.
   b. Check whether the intended scope is all archives, a post-type archive, or specific taxonomy terms; match the condition to that scope.

6. **Content template wins but you wanted the "single" default?**
   a. A `content` template with score 2+ beats WP's default single. Remove the unwanted condition or delete the template.

## Never do

- Set `main: any` on a `content` template unless you really want it to cover every singular page.
- Leave overlapping conditions unresolved. Check their scores against the intended page contexts.
- Mix `main: any` with other conditions expecting AND semantics. Conditions are OR. If you need AND, author a single `main: ids` with the specific list.
- Move a template's type from `archive` to `content` after it's been used: existing conditions assume the old type's rendering context.
- Forget that `section` templates don't self-render. They're building blocks for the Template element.
- Pass `entireWebsite` or `archiveTerm` as `main`: those names exist nowhere in the schema and will be rejected.

## MCP abilities relevant here

- `list-templates`: enumerate all templates with type + conditions.
- `get-template`: full template content + settings.
- `create-template`, `delete-template`: template CRUD. Use `set-template-settings` and `set-template-conditions` for settings and condition changes.
- `set-template-conditions`: replace the `templateConditions` array (uses the canonical shape above).
- `duplicate-post`: copies a template including conditions and regenerates element ids.

## Related skills

- `headers-footers`: header/footer template rules + meta routing for element writes.
- `popups`: covers popup-type templates specifically.
- `query-loops`: covers archive/content template queries.
- `components`: for `section`-type templates and reusable content.


---

## Module: bricks-headers-footers

# Bricks: header & footer templates

Header, footer, and content elements live on the **same** `bricks_template` (or normal page) post: but in **different postmeta keys**. Get the key wrong and your write silently lands in a meta no renderer reads. Most "I edited the header but nothing changed" tickets come from this.

## The three meta keys

Defined in root `functions.php`:

| Constant | Default value | Holds |
|---|---|---|
| `BRICKS_DB_PAGE_HEADER` | `_bricks_page_header_2` | Header element tree |
| `BRICKS_DB_PAGE_CONTENT` | `_bricks_page_content_2` | Content / page-body element tree |
| `BRICKS_DB_PAGE_FOOTER` | `_bricks_page_footer_2` | Footer element tree |

Each meta value is a serialized PHP array of element objects. Same shape across all three: only the meta key differs.

A `bricks_template` post with `_bricks_template_type = 'header'` stores its tree in `_bricks_page_header_2`, **not** in `_bricks_page_content_2`. Reading `_bricks_page_content_2` on that post returns `''` and your render is blank.

## Area lookup: `Database::get_data()` and `get_bricks_data_key()`

Bricks core has two helpers that you should mirror in any custom code:

```php
\Bricks\Database::get_bricks_data_key( $area );  // 'header' | 'footer' | 'content'
\Bricks\Database::get_data( $post_id, $area );   // returns the element tree
```

`$area` is `'header'`, `'footer'`, or `'content'`. Pass the wrong area and you'll silently read/write the wrong tree.

The Bricks Save_Pipeline also accepts area: `Save_Pipeline::execute( $post_id, $elements, $area )`.

## How MCP element-writes pick the area

The Bricks MCP element-write abilities (`add-element`, `update-element`, `remove-element`, `set-page-elements`) **infer the area from the post's template type**:

- Post type `bricks_template` + `_bricks_template_type = 'header'` -> area `'header'` -> reads/writes `_bricks_page_header_2`.
- Post type `bricks_template` + `_bricks_template_type = 'footer'` -> area `'footer'` -> `_bricks_page_footer_2`.
- Anything else (regular pages, posts, content templates, archive templates, popup templates) -> area `'content'` -> `_bricks_page_content_2`.

You don't have to specify the area in the call. Just pass `postId` and the element id: the routing is automatic.

## The `<header>` / `<footer>` wrapper is automatic: don't double up

When Bricks renders a header or footer template on the frontend, it **wraps the entire element tree in a semantic landmark for you**:

- Header template content -> emitted as `<header bricks-data>...your tree...</header>` (`includes/frontend.php:1062`).
- Footer template content -> emitted as `<footer bricks-data>...your tree...</footer>` (`includes/frontend.php:1150`).

So the root element of a header template should **not** carry `tag: "header"` (or `tag: "custom"` + `customTag: "header"`). Same for footer. Doing so produces nested `<header><header>...</header></header>`: invalid HTML5 landmarks, accessibility regression, and triggers the "duplicate `<header>`" rule in axe / WAVE.

**The right defaults inside a header/footer template:**

- Use a `section` element for the top-level layout (it renders as `<section>` by default, which is fine inside a `<header>` landmark).
- Or a `block` / `container` element with `tag: "div"` if you don't want a section landmark either.
- For the navigation row: `nav` is a valid tag on a container/section, AND it's correct inside a `<header>`: different landmarks, no nesting conflict.

**A common safe shape for a header template:**

```
section (tag: section, default)
`-- nav-nested or block (tag: nav)
    |-- logo image
    `-- menu items
```

Nothing here sets `tag: header`. The wrapping `<header>` comes from the renderer.

**Same rule for footers.** The footer template's root should be a `section` or `block` (not `tag: footer`). Bricks adds the `<footer>` wrapper when it renders.

Bricks supplies the landmark wrapper for header and footer templates. Use ordinary layout elements inside that wrapper.

Note: the `tag` control's built-in option set on container/section/block does not include `header` or `footer`: those are reachable only via `tag: "custom"` + `customTag: "..."`. If you find yourself reaching for the custom escape hatch to set `header`, that's the cue you're double-wrapping.

## Why naive postmeta writes break

These all silently no-op or corrupt the tree:

- Writing element JSON to `_bricks_page_content_2` on a header template (wrong key: no renderer reads it).
- Writing without `wp_slash()`: element values containing `\\` get unslashed by `update_post_meta` and the next read returns broken data.
- Writing without going through `Save_Pipeline::execute`: bypasses revision creation, queryId reindex, and filter-index rebuild. Visible until next save, then mangled.
- Bulk-replacing the array without preserving global elements / global classes references: turns connected classes into orphans.

## Header / footer template lookup

Bricks finds the active header/footer template via `find_template_id( 'header' | 'footer' )`: same scoring as content templates (see `bricks-templates-conditions` skill). The highest-scoring matching template wins.

If no header template matches, **no header is rendered**. The `<body>` opens straight into the page content. Check that a matching header template exists.

Best fallback: one header + one footer template, each with `conditions: [{ "main": "any" }]` (NOT `entireWebsite`). Then add specific overrides per section.

## Common authoring patterns

### "Add a logo to the existing header"

1. `list-templates` filtered by `type: header` -> find the active header template id.
2. `get-page-structure (postId: <header-id>)` -> see the existing tree (Bricks routes correctly).
3. `add-element (postId: <header-id>, parentId: <nav-container-id>, element: { name: "image", settings: { image: { url: "..." } } })` -> write goes to the header meta automatically.
4. Verify by reloading the frontend or calling `get-page-elements (postId: <header-id>)`: confirm the new element id appears in the tree.

### "Make the footer the same on all pages"

It already is, by default. Footer template with `{ "main": "any" }` is global; no per-page overrides needed unless you create them. If a specific page has its own footer, you (or the user) created a more-specific condition somewhere.

### "I edited an element but the change isn't visible"

Order of investigation:
1. Did the write hit the right post? `update-element` returns the postId: confirm it matches the visible header/footer.
2. Are there multiple header/footer templates with overlapping conditions? Check scoring (`bricks-templates-conditions` skill).
3. Is the page cached? Bricks caches CSS per-post; a settings change may need a CSS regen (`regenerate-css-files` ability or "Regenerate CSS files" in admin).
4. Is the element inside a component? Component changes need a re-render of every host post (`regenerate-css-files` again).

## "It changed in the builder but not on the frontend"

Builder runs an unsaved version in memory; frontend reads the persisted meta. If save failed (lock, save endpoint error, hook error), the builder shows the new state but the frontend serves the old one.

Verify by reading the meta directly:

```
get-page-elements (postId)
```

If the meta is the old version, the save didn't land. Look for: locked-by-other-user errors, save endpoint errors, or hook errors in the PHP error log.

## Page-vs-template: when you actually own the header

For pages (`page` post type), Bricks first looks for a matching header template. If none matches, the page renders without a header. **Pages don't have their own per-page header by default**: the header is always template-driven.

If you need a page-specific header: create a header template scoped to that page (`{ "main": "ids", "ids": [42] }`).

## Never do

- Write directly to `_bricks_page_content_2` on a header or footer template post: silently lost.
- Pass an `area` arg to MCP element abilities expecting it to override the auto-routing: the abilities derive area from template type.
- Edit header/footer trees through `wp_update_post` content fields: Bricks doesn't render from `post_content`.
- Forget to `wp_slash()` an array of elements before `update_post_meta` if you're writing in custom PHP. Bricks core's Save_Pipeline does this for you.
- Assume "no header on this page" means there's a bug. It usually means no header template matches the page's conditions.

## Related abilities

- `list-templates (type: header|footer)`: find existing templates of each type.
- `get-template`, `create-template`, `delete-template`: template CRUD; use `set-template-settings` or `set-template-conditions` for settings and conditions. The template `type` controls which Bricks data area the renderer reads.
- `set-template-conditions`: control which pages a header/footer applies to.
- `add-element` / `update-element` / `remove-element` / `set-page-elements`: area-aware element writes.
- `regenerate-css-files`: force a CSS rebuild when style changes don't propagate.

## Related skills

- `bricks-templates-conditions`: full scoring rules for which header/footer wins on a given page.
- `bricks-nestable-elements`: Nav Nested + Offcanvas live almost exclusively in headers.
- `bricks-mega-menus`: Bricks-native Nav Nested mega menus and WordPress menu-backed mega menu setup.
- `bricks-quality-gate`: the verify-after-write loop that catches silent header/footer regressions.


---

## Module: bricks-sidebars

# Bricks: sidebars (via MCP)

Bricks registers its own sidebars (widget areas) on top of theme-provided sidebars. They appear in `Appearance > Widgets` and in the Bricks Sidebar element picker.

Storage: `bricks_sidebars` option, as an ordered array of `{ id, name, description }` rows (`includes/abilities/sidebars.php`).

## Reuse before creating

For “show the existing sidebar,” resolve its ID with `list-sidebars`, then use the
Sidebar element's `settings.sidebar` control. The sidebar-management abilities use
`sidebarId` arguments; that is not the element setting key. Preserve its existing
widget placements. Registering a sidebar does not add widgets; an empty sidebar can
legitimately render empty. Inspect widget assignment through an available WordPress
surface when diagnosing it, and do not recreate the sidebar as a repair shortcut.

## Abilities

- **`bricks/list-sidebars`**: returns `{ sidebars, total }`.
- **`bricks/create-sidebar`**: body `{ name, description? }`. The ID is derived from the name.
- **`bricks/update-sidebar`**: body `{ sidebarId, name?, description? }`. ID is immutable.
- **`bricks/delete-sidebar`**: body `{ sidebarId }`. Deletes the Bricks sidebar row and removes the same key from WP core `sidebars_widgets`.

## ID generation

You do not send an ID on create. Bricks derives it:

1. Lowercase the name.
2. Replace spaces with underscores.
3. Strip every character except `a-z`, `0-9`, and `_`.

Example:

```
bricks/create-sidebar { name: "Shop Sidebar", description: "Product filters" }
  -> { sidebar: { id: "shop_sidebar", name: "Shop Sidebar", description: "Product filters" } }
```

Avoid names that collapse to the same ID, such as `Shop Sidebar` and `Shop Sidebar!`.

## What Bricks does automatically

- Calls `register_sidebar()` for every Bricks sidebar during `widgets_init`.
- Supplies default `before_widget`, `after_widget`, `before_title`, and `after_title` wrappers.
- Registers the sidebar for WordPress widgets. Picker availability and rendered output depend on widget assignment; registration alone does not populate it.

Check theme-registered sidebar IDs as well as Bricks sidebars before choosing a name; the duplicate check covers only Bricks IDs and names.

## Tool availability

> **If a `bricks/*` ability is not available as a direct tool**: first check whether it is outside the fast path and call it through `mcp-adapter-execute-ability` with `ability_name: "bricks/<name>"`. If the dispatcher also rejects it, call `bricks-list-ability-status` to check whether a site admin disabled it under Bricks > AI.

## Typical flow: add a Shop sidebar, assign widgets

```
bricks/create-sidebar { name: "Shop Sidebar", description: "Product filters" }
  -> { sidebar: { id: "shop_sidebar", name: "Shop Sidebar", description: "Product filters" } }

# Widgets are still WordPress core. Assign them via Appearance > Widgets or the widgets REST API.

bricks/add-element
  postId: 99
  parentId: "mainc1"
  element:
    name: "sidebar"
    settings:
      sidebar: "shop_sidebar"
```

## Don't

- Don't send `{ id, name }` to `create-sidebar`; current schema accepts `name` and optional `description`.
- Don't assume deleted sidebar widgets move to inactive widgets. The delete ability removes the sidebar key from `sidebars_widgets`.
- Don't rename a sidebar by deleting and recreating it. Use `update-sidebar` to keep the ID stable.


---

## Module: bricks-popups

# Bricks: popups

A popup in Bricks is a **template with `_bricks_template_type = popup`**. Create the popup template first, then wire triggers, display conditions, frequency limits, and any JS control around that template.

## The storage shape

- **Template type:** `popup`: stored as `_bricks_template_type` post_meta on a Bricks template post (`includes/templates.php:1053-1062`). Canonical string: `'popup'`.
- **Content:** the popup's inner element tree lives on the template post's `_bricks_page_content_2` meta (same as any Bricks template).
- **Settings:** popup settings live inside the template settings object stored in `_bricks_template_settings`, not as individual post meta rows. `Helpers::get_template_settings()` and `Helpers::set_template_settings()` read and write this object.

Key template setting keys:

| Setting key | Purpose |
|---|---|
| `popupCloseOn` | `backdrop`, `esc`, or `none`. If no value is saved, the frontend uses the default `backdrop-esc` behavior (`includes/popups.php`) |
| `popupBodyScroll` | Presence flag: `true` enables body scroll while open; unset/false removes the flag (`includes/popups.php:124-129`) |
| `popupAjax` | Presence flag: `true` AJAX-loads content per trigger instead of inline; unset/false removes the flag (`includes/popups.php:182-187`) |
| `popupLimitWindow` | Per-page-load limit count (`includes/popups.php:525-556`) |
| `popupLimitSessionStorage` | Per-session limit count |
| `popupLimitLocalStorage` | Cross-session limit count |
| `popupLimitTimeStorage` | Hours until popup can show again |
| `popupIsInfoBox` | Boolean: popup is used as a map info-box (`includes/popups.php:160-165`) |

These keys sit next to generic template settings in the same settings object. Through MCP, `popupCloseOn` must be a single scalar value: `backdrop`, `esc`, or `none`; pass `null`, `false`, or an empty string to unset optional popup settings.

## Triggers vs display conditions: two separate systems

**Triggers (when)**: what action on the page fires the popup.
- Stored on the **element that triggers the popup** (not on the popup itself), via the Interactions system.
- Example: a button has an interaction with `trigger: "click"`, `action: "show"`, `target: "popup"`, and `templateId` set to the popup template id.
- Defined at `includes/interactions.php:46-86`.

**Display conditions (where)**: whether the popup is eligible to show on the current page at all.
- Stored on the **popup template**, under Template settings -> Conditions. It uses the same condition schema as templates: `any`, `frontpage`, `postType`, `archiveType`, `search`, `error`, `terms`, `ids`, and `hook`.
- A popup with no matching conditions is not included in `Database::$active_templates['popup']`, so its DOM is not rendered on normal page loads.
- Defined in the template-conditions subsystem (see `bricks-templates-conditions` skill).

**The "no conditions = no fire" trap:**
A popup with *no display conditions set* will not fire automatically because it is not rendered into the page in the normal popup collection. `bricksOpenPopup(id)` only works after matching conditions or another rendering path places the popup DOM on the page. A popup with `trigger: contentLoaded` still needs matching display conditions.

**The correct flow for a page-load popup on the home page:**
1. Create a template, type = popup, with content.
2. Add an interaction with `trigger: "contentLoaded"`, `action: "show"`, `target: "popup"`, and `templateId` set to the popup template id.
3. Also set display conditions: where = home page. Use `{ main: "frontpage" }` for the front page or `{ main: "any" }` for site-wide eligibility.

## Trigger types (interaction-style)

From `includes/interactions.php` and `includes/settings/settings-template.php`. Popup openers use normal interactions with `action: "show"` and `target: "popup"`. Popup templates can also use template-level lifecycle triggers, `showPopup` and `hidePopup`, in `template_interactions`.

| Trigger | Fires when |
|---|---|
| `contentLoaded` | Page DOM-ready |
| `scroll` | Page scrolled (configurable % or px) |
| `click` | Element clicked |
| `mouseenter` / `mouseleave` / `mouseover` / `focus` / `blur` | Pointer / focus events |
| `mouseleaveWindow` | Exit-intent (pointer leaves top of window) |
| `enterView` / `leaveView` | Element enters/leaves viewport |
| `animationEnd` | A CSS animation finished on the element |
| `formSubmit` / `formSuccess` / `formError` | Form events |
| `ajaxStart` / `ajaxEnd` | Query AJAX loader lifecycle |
| `filterSubmitStart` / `filterSubmitEnd` | Query filter submit lifecycle |
| `showPopup` / `hidePopup` | Popup-template lifecycle triggers only. They are stored in popup template settings as `template_interactions`, not on normal element interactions. |
| `filterOptionEmpty` / `filterOptionNotEmpty` | Query-filter options (conditional) |
| `wooAddedToCart` / `wooAddingToCart` / `wooRemovedFromCart` / `wooUpdateCart` / `wooCouponApplied` / `wooCouponRemoved` | WooCommerce events (conditional) |

**Popup opening is an interaction action:**
- On any rendered element, use an interaction with `action: "show"`, `target: "popup"`, and `templateId` set to the popup template id.
- `toggleOffCanvas` is for off-canvas elements, not the normal popup template target.
- A JavaScript action that calls `bricksOpenPopup(POPUP_ID)` is still valid, but the native interaction shape is the first choice when authoring Bricks data.

## Frequency limits: the four layers

Bricks exposes 4 frequency counters per popup (stored in browser state by popup id):

| Layer | Key | Lifetime | Use for |
|---|---|---|---|
| Page-load | `window.brx_popup_{id}_total` | Single page navigation | "Show once per page" |
| Session | `sessionStorage.brx_popup_{id}_total` | Browser tab closed | "Show once per session" |
| Local | `localStorage.brx_popup_{id}_total` | Cleared only by user | "Show once forever" |
| Time | `localStorage.brx_popup_{id}_lastShown` | Hours configured | "Show once every N hours" |

Configured on the popup template's settings (`popupLimit*` keys). `popupLimitTimeStorage` is the hours-TTL for the time layer.

The limit check runs in `bricksPopupCheckLimit()` (`frontend.js:10711-10760`) before `bricksOpenPopup()` proceeds.

**Testing frequency limits:** clear only the tested popup’s `brx_popup_{id}_*` storage keys before retesting.

## JS API: programmatic control

Defined in `frontend.js:10334-10410` and `:10651-10699`.

```js
bricksOpenPopup( popupIdOrDomNode, timeout = 0, additionalParam = {} );
bricksClosePopup( popupIdOrDomNode );
```

- First arg: the template **post id** (integer) or the already-rendered DOM node.
- `timeout`: milliseconds before the open actually fires. Bricks adds animation-duration automatically; use this for deliberate extra delay.
- `additionalParam`: only used when `popupAjax` is on. Use `popupContextId` and `popupContextType` to set the render context explicitly, or let Bricks derive loop context from `loopId`.

Common patterns:

```js
// Open via id
bricksOpenPopup( 123 );

// Open with 2-second delay
bricksOpenPopup( 123, 2000 );

// Open AJAX popup with post context (e.g. product quick-view)
bricksOpenPopup( 123, 0, { popupContextId: currentProductId, popupContextType: 'post' } );

// Close
bricksClosePopup( 123 );
```

Use the native interaction or `bricksOpenPopup()` to open a popup.

## AJAX popups: the context gotcha

`popupAjax` mode renders popup content server-side per-trigger. That means dynamic tags inside the popup resolve against the AJAX request's context, not the page that triggered it.

- Without an explicit context, dynamic tags like `{post_title}` use the current page context or the loop context Bricks can derive from `loopId`.
- Pass the context you want as `additionalParam`: `bricksOpenPopup(id, 0, { popupContextId: 42, popupContextType: "post" })`. Supported context types are `post`, `term`, and `user` (`popupContextType`).
- AJAX popups are slower than inline popups: use for heavy content or per-item previews, not for a global newsletter popup.

## Display-condition cascades

A popup can have display conditions like any template. Rules for how they evaluate:

- Conditions are the same flat OR array used by Bricks templates. Any matching condition can make the popup eligible.
- Exclude conditions can remove the popup from a context that would otherwise match.
- If the popup has conditions but the current page doesn't match any, the popup is not rendered into the DOM. `bricksOpenPopup(id)` returns without opening because there is no popup node to target.

For "usable everywhere via JS": set conditions to `{ main: "any" }`.

## Silent-failure debug order

1. **Popup doesn't show on expected trigger?**
   a. Open DevTools -> Application -> Local Storage + Session Storage -> look for `brx_popup_{id}_*`. Clear them. Retry.
   b. Check the popup template's display conditions: does the current page match?
   c. Check the page DOM for `.brx-popup[data-popup-id="POPUP_ID"]`. If it is absent, conditions do not match or the popup was not rendered by another path.

2. **Popup opens but content is stale / wrong post?**
   a. AJAX mode + missing `additionalParam.popupContextId`. Pass the context with `popupContextType` when needed.

3. **Popup opens twice?**
   a. Two interactions both calling `bricksOpenPopup(id)`. Or a popup with `contentLoaded` trigger *and* a button `click -> open popup` on the same page: both fire.

4. **`bricksOpenPopup(id)` silently does nothing?**
   a. The popup template is not rendered on this page (no matching conditions). Grep `.brx-popup[data-popup-id="{id}"]` in the page source: if absent, conditions don't match.
   b. Frequency limit already hit. Clear the tested popup’s storage keys.
   c. Popup id doesn't exist (typo / deleted template).

5. **Exit-intent popup fires on mobile?**
   a. It shouldn't: `mouseleaveWindow` only fires on desktop. If it does, a different trigger is wired in too.

6. **Popup rendered but not visible?**
    a. CSS specificity issue: something else has a higher z-index. Bricks popups use `z-index: 10000` by default, unless `popupZindex` or CSS overrides it; check for other overlays.
   b. Animation never completes: element has `display: none` stuck. Check DevTools -> Elements for the popup's `.brx-popup` root.

## MCP abilities for popups

- `list-popups`: enumerate every popup template on the site with display-condition summary.
- `get-popup-config`: full config of one popup (content tree + settings).
- `update-popup-settings`: change popup-specific template settings, including frequency, AJAX loading, close behavior, and template-level `template_interactions`. Use `set-template-conditions` for display conditions and `update-element-interactions` for opener elements.

## Never do

- Build a popup by dragging elements onto a page and expecting to "make it a popup": it has to be a template with `_bricks_template_type = popup`.
- Skip display conditions and assume the popup will "just show." With no matching conditions, the popup is not rendered into the normal page DOM.
- Put a form inside a popup without a success-state or close behavior: users submit and may not see what happened.
- Assume `contentLoaded` = instant. It's DOM-ready, which on slow networks can be seconds after the user perceives the page as loaded.


---

## Module: bricks-mega-menus

# Bricks: mega menus

Preserve the site's navigation model. Ordinary menu edits do not require a mega
panel or a new header. Pick the existing-menu or native-element path before writing.

## Ordinary WordPress menu edits

Use `list-nav-menus` and `get-nav-menu` to resolve the current menu and item IDs.
Use `save-nav-menu` for the requested labels, links, hierarchy/order and locations,
preserving unrelated fields and Bricks item metadata. Omitted items are retained,
not deleted; removals need explicit item IDs through `delete-nav-menu-items`.
Do not create a section template or enable mega-menu settings for an ordinary link
change. Read back the affected tree and check the rendered header when possible.

## Default decision

For a new header without an established menu model, **Nav Nested + Dropdown** is a useful native option. It is fully Bricks-native: the menu, dropdown panel, layout, styles, and mobile behavior live in the header template element tree, so normal element abilities can create and edit everything.

Use **WordPress Nav Menu + Bricks section template** only when:

- The user explicitly asks for menus managed in Appearance > Menus.
- The site already has meaningful WordPress menus that should be preserved.
- Non-builder users need to edit menu labels/order/links from the WordPress dashboard.

## New Bricks-native mega menu

Author this inside the active header template. Load **bricks-headers-footers** first if you have not already identified the header template and area.

Safe shape:

```text
header template
`-- section
    `-- nav-nested
        |-- text-link
        |-- dropdown (settings.megaMenu = true)
        |   `-- div/block/container with _hidden._cssClasses = brx-dropdown-content
        |       `-- rich mega menu content: grids, columns, headings, images, buttons, nav links
        `-- toggle / close controls as needed for mobile
```

Important settings:

- On the `dropdown` element, set `megaMenu: true`.
- Use `megaMenuSelector` when the panel should match a specific wrapper width and horizontal position, such as a custom header inner wrapper. If omitted, Bricks uses the document body width.
- Use `megaMenuSelectorVertical` only when the vertical offset must be calculated from a specific header node.
- Keep `toggleOn` intentional: hover for classic desktop menus, click for touch-friendly or complex panels.
- Style the panel through Dropdown and Nav Nested controls where possible: dropdown background, border, box shadow, width, transform, transition, z-index, item typography, and mobile-menu controls.
- In mega menu mode, dropdown content children are not forced into `<li class="menu-item">` wrappers. Use layout elements freely for columns/cards; add text links where a real menu link is needed.

Mobile behavior:

- Nav Nested mobile controls live on the `nav-nested` parent.
- Mega menu dropdown content becomes static inside the open mobile menu and min-width is reset.
- Check that rich panels still scan well in a narrow drawer; desktop grids often need a simpler mobile column layout.

## Reusing an existing WordPress menu

Use this when the site already has a WordPress menu or the user asks for dashboard-managed menus.

Discovery:

1. `bricks/list-nav-menus` through the dispatcher to see existing menus, locations, and Bricks mega-menu metadata.
2. `bricks/get-nav-menu` for the exact menu tree before editing.
3. `bricks/list-templates` filtered to `section` if you need an existing mega menu template.

If a mega menu template is needed:

1. Create a Bricks template with `bricks/create-template`, `type: "section"`, and `status: "publish"`.
2. Build the panel content with normal element abilities on that section template.
3. Attach it to a top-level WordPress menu item with `bricks/save-nav-menu` using:

```json
{
  "menuId": 123,
  "items": [
    {
      "menuItemId": 456,
      "title": "Services",
      "url": "/services/",
      "bricksOptions": {
        "megaMenuTemplateId": 789
      }
    }
  ]
}
```

Then make sure the header has a `nav-menu` element with:

- `menu` set to the WordPress menu ID.
- `megaMenu: true`.
- `megaMenuSelector` if the panel should match a header wrapper instead of the body.
- `megaMenuToggleOn` set intentionally.

## Editing WordPress menus safely

`bricks/save-nav-menu` can create/rename a menu, assign registered theme locations, create/update/reorder items, and set Bricks item options. It preserves omitted items. WordPress menu edits have no Bricks revisions.

Use explicit destructive abilities for removals:

- `bricks/delete-nav-menu-items` for specific menu item IDs.
- `bricks/delete-nav-menu` for a whole menu.

Before destructive calls, inspect the current `bricks/get-nav-menu` snapshot and
ensure the exact removal is authorized. Ask only if scope or targets are unclear. The delete response returns `beforeDelete`; retain it for
recovery after the operation.

## Verification

Read back first:

- `bricks/get-page-elements` on the header template: confirm the `nav-nested`, `dropdown`, or `nav-menu` settings persisted.
- `bricks/get-nav-menu`: confirm item order, parent IDs, and Bricks `megaMenuTemplateId` / `multilevel` options.
- `bricks/list-revisions` for header/template element writes that returned `revisionId`.

Browser verification should cover:

- Desktop open state, width, and horizontal alignment.
- Hover/click behavior.
- Keyboard focus and escape/outside close.
- Mobile drawer open state and nested panel stacking.
- Links inside the mega panel setting the top-level active/current state.

## Common mistakes

- Building a new header with `nav-menu` only because the word "menu" appears in the request. Prefer `nav-nested` for new work.
- Attaching `megaMenuTemplateId` to a nested WordPress menu item. Bricks mega menus are for top-level menu items.
- Creating the mega panel as a header/footer template. Use a section template for WordPress-menu-backed mega panels.
- Forgetting to enable `megaMenu` on the header `nav-menu` element. The menu item meta alone is not enough.
- Deleting omitted WordPress menu items during a save. Never infer deletion from omission; use the explicit delete ability.


---

## Module: bricks-components

# Bricks: components

A component is a reusable element tree stored globally. Instances reference the main component through `"cid": "..."` on the host element; editing the main component updates every instance.

> **If a `bricks/*` ability is not available as a direct tool**: first check whether it is outside the fast path and call it through `mcp-adapter-execute-ability` with `ability_name: "bricks/<name>"`. If the dispatcher also rejects it, call `bricks-list-ability-status` to check whether a site admin disabled it under Bricks > AI.

## Choose the change level

An edit to a component definition affects its instances; an instance property edits
that instance. Infer the level from the user's request and inspect existing bindings.
Ask only if the intended scope is ambiguous. Preserve unaffected instance values,
slots and nested definitions. A single use does not make a component defective.

For a remote library, discover the installed remote-component surface and source
configuration before importing; do not assume remote-template abilities return
component definitions. If no supported remote import is available, explain that
boundary and use an available native import workflow rather than inventing an API.
For Gutenberg use, identify which properties should be exposed to content editors
and verify the installed components-as-blocks configuration and supported property
types. A Bricks frontend preview alone does not certify editing/saving the block.

## Stored component shape

A valid component record has:

- `id`: same id as the root element.
- `elements`: flat Bricks element rows. The root element has `parent: 0` and the component label on `label`.
- `properties`: array of property definitions. Empty array is valid.
- `variants`: array of `{ id, name }`. Variant ids start with `variant-`.
- `_created`, `_user_id`, `_version`: builder metadata. If `_version` is missing, the builder treats the component as an old beta component and shows: `Components highlighted in red were created in Bricks 1.12-beta and are no longer supported. Please delete all of them.`
- Optional top-level fields: `category`, `desc`, `propertyGroups`, `blockEditor`, `blockCategory`, `blockIcon`, `blockPreviewImage`.

Do not hand-write global option records unless you are repairing data. Use component abilities so ids, property connections, parent-property references, validation, and metadata are handled consistently.

## Ability workflow

For MCP work, use this order:

1. Read first: `bricks/list-components`, `bricks/get-component`, or `bricks/get-design-context`.
2. Preserve both `designSystemVersion` and the complete `componentDigest` from the
   same current component read. The digest covers hidden and opaque component fields;
   do not synthesize it from the visible tree.
3. For `bricks/update-component`, pass `expectedDesignSystemVersion` and
   `expectedComponentDigest`. If either precondition changed, re-read and merge your
   edit into the newest component.
4. For `bricks/delete-component`, pass `expectedDesignSystemVersion`,
   `expectedComponentDigest`, the freshly reviewed `expectedUsageCount`, and literal
   `allowOrphans: true`. Deletion always requires that acknowledgement, even at zero
   discovered usages, so do not delete unless the user explicitly accepted that
   usage discovery is bounded and missing instances could remain.
5. Read back with `bricks/get-component` after create/update/extract. Confirm `_version`, properties, property groups, slots, nested component props, and `slotChildren`.

Treat `elements` on `bricks/update-component` as a full replacement tree. To edit
one element, read the component, change only that element in the returned tree, then
send the whole modified tree back with both current preconditions. For a known
single existing component, prefer the self-described `bricks/resolve-agent-file` →
`bricks/commit-agent-file` path when available. It binds the same authoritative
digest and avoids both repository discovery and rebuilding a large component payload
by hand.

Slot IDs matter because instance slot content is keyed by slot element id. When replacing a component tree, preserve existing slot ids if you can. Any removed existing slot requires explicit `allowSlotOrphans: true`, even when the fresh bounded usage scan finds no content. Review the returned slot-removal evidence first; it is audit evidence, not proof that every instance was found.

## Reuse existing components

`bricks/list-components` returns component summaries with `label`, `desc`, properties, variants, slot count, and element count. `bricks-get-design-context` with `responseFormat: "summary"` also includes component summaries.

When building a page, section, card, CTA, listing item, testimonial, team member, or other repeated pattern, check the existing component labels/descriptions before creating a new component or raw element tree. If one clearly fits, inspect it with `bricks/get-component` and use a component instance (`{ "cid": "componentId" }`) with properties and `slotChildren` as needed.

Reuse components whose structure and properties fit the requested design.

## Create

The builder's source-of-truth UI is **Save as component** on an element except Template or Filter. It prompts for:

- **Name** (required): shown in the Components panel.
- **Category** (optional): groups the panel.
- **Description** (optional).

**Prefer `bricks/extract-component-from-elements` over manual copy-paste.** The extraction rewrites element ids cleanly, swaps the source subtree to an instance in one write, and snapshots a revision. Manual copy leaves duplicate ids and breaks future extraction.

When creating a component, or editing one with an empty `desc`, write a concise useful description. Describe what the component is for and the main customization surface, for example: "Reusable listing card with image, price, address, meta, and optional featured badge." Avoid marketing copy, implementation trivia, and long prose.

When creating from scratch with the ability, pass either nested element objects or flat Bricks rows. The ability regenerates ids, so property `connections` may reference the ids in your input and will be remapped in the saved component.

```json
{
  "ability_name": "bricks/create-component",
  "parameters": {
    "label": "Metric card",
    "category": "marketing",
    "desc": "Small stat card with eyebrow, value, and supporting copy.",
    "elements": [
      {
        "id": "metric",
        "name": "div",
        "parent": 0,
        "children": ["eyebrw", "valtxt", "bodytx"],
        "settings": { "_cssGlobalClasses": ["card-shell"] }
      },
      {
        "id": "eyebrw",
        "name": "text-basic",
        "parent": "metric",
        "settings": { "text": "Listings sold" }
      },
      {
        "id": "valtxt",
        "name": "heading",
        "parent": "metric",
        "settings": { "text": "128" }
      },
      {
        "id": "bodytx",
        "name": "text",
        "parent": "metric",
        "settings": { "text": "Across the last twelve months." }
      }
    ],
    "properties": [
      {
        "id": "eyebrow",
        "label": "Eyebrow",
        "type": "text",
        "connections": { "eyebrw": ["text"] },
        "default": "Listings sold"
      },
      {
        "id": "value",
        "label": "Value",
        "type": "text",
        "connections": { "valtxt": ["text"] },
        "default": "128"
      }
    ]
  }
}
```

## Label uniqueness

Component labels must be **unique across all components**. Attempting to create a duplicate returns `bricks_conflict_duplicate_component_name`. Read `list-components` before creating.

## Properties: the binding model

Properties are the only way to customize an instance without editing the main. Unconnected properties are dead weight.

### Common property types (Bricks 2.0+)

| Type | Binds to |
|------|----------|
| Text | Text / textarea controls |
| Rich text | Rich text control |
| Icon | Icon / Icon Box controls |
| Image | Image control |
| Image gallery | Gallery / Carousel controls |
| Link | Link controls (Button, Heading link, etc.) |
| Select | Text or Select controls |
| Toggle | Toggle controls (most commonly "Hide element") |
| Query loop (`query`) | Query loop control on layout elements |
| Global classes (`class`) | Global classes control (Bricks 2.0+) |

The stored `type` usually follows the connected control type. The builder also allows compatible matches such as `text` properties on textarea controls, `select` properties on text/textarea/editor controls, and `toggle` properties on checkbox controls (`ControlProperty.vue`).

### Defining a property

1. Open the main component's Properties panel (edit icon in the component's control panel, or the gear icon).
2. Add property: `name` (required), `description`, `group`, `default`.
3. Navigate to the target element inside the component.
4. Click the **purple `+` icon** next to the target control: pick the property.

A property that's defined but not connected to any control shows a broken-link icon and a warning. Fix by connecting or delete the property.

Ability shape:

```json
{
  "id": "title",
  "label": "Title",
  "type": "text",
  "desc": "Main visible heading.",
  "group": "content",
  "connections": {
    "abc123": ["text"]
  },
  "default": "Featured listing"
}
```

Supported property definition fields are `id`, `label`, `type`, `connections`, `default`, `desc`, `group`, `options`, `multiple`, and `replace`. Supported `type` values are `text`, `editor`, `icon`, `image`, `image-gallery`, `link`, `select`, `toggle`, `query`, and `class`.

`connections` is keyed by element id inside the component. Each value is an array of setting/control keys on that element. For a global-class property, connect to `_cssGlobalClasses`.

For `type: "class"` specifically:

- `multiple` is explicit. Omit it or set `false` for a single-select instance picker. Set `true` for multi-select.
- If `options` is omitted, the instance picker lists all current global classes.
- If `options` is present, each option is a named preset. The option `value` should be an array of global class IDs, and the instance stores the option `id`, not the raw class-id array. The component abilities auto-generate missing option ids on create/update so the stored data stays builder-compatible.
- `replace: true` replaces the element's existing global classes with the resolved property classes. Omit it to merge with the element's existing classes.

### Disconnecting

On the bound control, hover the property chip -> click the unlink icon. The control returns to its raw value.

### Global-class property (the underused one)

Instead of baking styling variants into the component, add a **Global classes** property and bind it to the Classes control on the styled element. Without custom `options`, each instance picks from all global classes. With custom `options`, each instance picks one preset by default, or multiple presets only when `multiple: true`.

For true component variants such as `<Button variant="primary" | "secondary">`, use named class presets and usually `replace: true`, otherwise the property classes merge with the element's existing classes and can stack conflicting variants.

Multiple global-class properties can bind to the same element: useful for orthogonal dimensions (size + color + emphasis).

### Toggle + "Hide element": DOM-level variation

A Toggle property connected to the "Hide element" control **removes the element from the DOM** at render time (not `display: none`). Use this for optional sub-sections that should be absent from the rendered page.

## Nested components

A component's element tree can contain instances of other components. That's how you compose (Card uses Button, PostGrid uses Card).

When creating an instance through an ability, `{ "cid": "componentId" }` is enough. The ability resolves the host element `name` from the referenced component root unless you intentionally pass a specific host name.

**Caveats the builder won't stop you from:**

- **Circular nesting**: Component A instances B, B instances A. The builder's component-children resolver has a circular-reference guard (`src/vue/store/actions/elements.js:1464-1475`), but that is not a save-time design validator and other recursive component paths still traverse nested instances. Always check: does this component's tree, directly or transitively, instance the component you're currently editing?
- **Property scoping**: a nested component's properties are separate from the outer component's. An outer property can't directly bind into an inner component's slot. You have to surface the binding by adding a matching property on the outer component and wiring it through: tedious but explicit.
- **Global resources follow the component**: classes (`.button`) and variables (`var(--space-m)`) referenced inside a component persist across instances. When sending a component to another site, those globals must exist there too or rendering breaks silently.

### Passing an outer property into a nested component

Use the nested component instance's `properties` map and a parent-property reference:

```json
{
  "id": "button",
  "name": "div",
  "parent": "card01",
  "cid": "cta123",
  "properties": {
    "label": "parent:cid_card01:prop_ctaText"
  }
}
```

The referenced component id is the current component root id, and the referenced property id is the outer component property. If the component is created through `bricks/create-component`, the ability remaps `parent:cid_<oldRoot>:prop_<property>` to the regenerated root id.

## Slots

Bricks components have a real **Slot** element (`includes/elements/slot.php`, registered since 2.2). Use it when an instance needs to provide arbitrary child elements inside the component.

How it works:

1. Add a Slot element inside the main component where instance content should render.
2. Instance-provided children are stored in `slotChildren`, keyed by the slot element id.
3. Frontend render resolves the slot from the parent component instance and renders those children in place.

Use slots for arbitrary child content. Use Text or Rich text properties for simple strings. `bricks/list-components` exposes `slotCount`; `bricks/get-component` returns the full component element tree, so count elements whose `name` is `slot` when you need the detailed shape.

Ability shape for an instance with slotted children:

```json
{
  "id": "card01",
  "name": "div",
  "parent": 0,
  "cid": "cardcmp",
  "slotChildren": {
    "slotid": ["head01", "body01"]
  }
}
```

The `slotChildren` key is the `id` of a `slot` element inside the referenced component `cardcmp`. The child ids must exist in the same post/component element tree and should use the component instance id as their `parent`.

For ability input, slot children may also be nested objects:

```json
{
  "name": "div",
  "cid": "cardcmp",
  "slotChildren": {
    "slotid": [
      { "name": "heading", "settings": { "text": "Custom headline" } },
      { "name": "text", "settings": { "text": "Custom body." } }
    ]
  }
}
```

## Instances: how changes propagate

- Editing the **main component** (purple-outlined) updates every instance immediately.
- Editing an **instance** only overrides that instance's property values. Structural changes to an instance's tree are not possible: you can't add a sibling to an element inside an instance.
- To diverge one instance structurally, use the context-menu **Unlink component** action in the builder. It expands the instance into normal elements, resolves property values, preserves nested component references, and removes the host element's `cid` (`src/vue/components/common/TheContextMenu.vue:575-752`).

## Deletion: orphans and the placeholder

Deleting a component while instances exist leaves orphans. In the builder, each orphan instance renders as a **"missing component" placeholder**. The `"cid"` on the host element is still there; it just points to nothing.

Before deleting:

1. Call `bricks/get-component` for the complete current `componentDigest`, then call
   `bricks/get-design-context` with `includeUsage: true` for the component's
   `usedOnPosts` list. The list can include posts/templates and component definitions
   that nest this component.
2. Capture `designSystemVersion`, `componentDigest`, and the current usage count
   (`count(usedOnPosts)` for the target component) from current reads.
3. If usage is non-empty, show the user the list and ask: replace usages first, or accept the orphans?
4. Never call `delete-component` without explicit confirmation. Pass
   `expectedDesignSystemVersion`, `expectedComponentDigest`,
   `expectedUsageCount`, and `allowOrphans: true`; if any current precondition or
   usage count changed, re-read before deleting.

To clean up orphans after the fact: scan element trees for `"cid": "..."` referencing deleted ids (`bricks/audit-design-system` covers this), then use `update-element` or `set-page-elements` to strip the stale cid.

## Workflows

### Extract an element subtree into a component

```
extract-component-from-elements (
  postId: 123,
  rootElementId: "abc123",
  label: "Card",
  category: "cards",
  desc: "Reusable card component."
)
```

Returns the new component id + the revision snapshot. The subtree on the source post is replaced with an instance. Component extraction creates the component with empty `properties` and `variants` arrays: convert literals to properties by editing the main component afterward.

### Retype a property (e.g. text -> rich text)

There is no "retype" operation. The workflow is:

1. Delete the property.
2. Add a new property with the target type.
3. Rebind the target control.
4. Update every instance to set the new property.

Before retyping a property, identify affected instances and include their updates in the change.

### Rename a component

Labels are editable on the main component. The `cid` doesn't change, so all instances still resolve correctly. Include the old and new names when reporting the change.

## Red flags

- **"Save as component" on a large subtree with many dynamic tags**: the extraction preserves tags but they now resolve against wherever the instance lands. A `{post_title}` deep inside a component behaves differently on a single post vs. a standalone page. Verify the component's dynamic-data assumptions before extracting.
- **Shared styling**: use global classes. Use components for shared structure and behavior.
- **Many unrelated properties**: consider splitting independent sections into nested components.
- **One-off layouts**: use instance properties for supported variations. Create a separate component when the structure needs to diverge.


---

## Module: bricks-nestable-elements

# Bricks: nestable elements

Nestable elements contain editable child elements. Runtime schemas describe controls and values; they do not necessarily include the complete native child structure.

## Common nestable elements

Source: `includes/elements/*.php` (`public $nestable = true`).

| Element | File | `$name` | Category | Notes |
|---|---|---|---|---|
| Container | `container.php` | `container` | layout | The base layout element; children unrestricted |
| Section | `section.php` | `section` | layout | Extends Container |
| Block | `block.php` | `block` | layout | Extends Container |
| Div | `div.php` | `div` | layout | Extends Container |
| Slider Nestable | `slider-nested.php` | `slider-nested` | media | 3 default slide-blocks with Heading + Button |
| Accordion Nestable | `accordion-nested.php` | `accordion-nested` | general | 2 default items with title/content wrappers |
| Tabs Nestable | `tabs-nested.php` | `tabs-nested` | general | Default tab-button + tab-content pairs |
| Dropdown | `dropdown.php` | `dropdown` | general | Toggle + content |
| Nav Nested | `nav-nested.php` | `nav-nested` | general | Menu builder replacing the non-nestable Nav |
| Offcanvas | `offcanvas.php` | `offcanvas` | general | Slide-in panel |
| Back to Top | `back-to-top.php` | `back-to-top` | general | Icon + text children default |
| Slot | `slot.php` | `slot` | general | Component slot: renders children passed by the parent component instance |

**The non-nestable counterparts still exist**: "Slider," "Accordion," and "Tabs" use repeater controls instead of child elements. Use the nestable versions when each item needs arbitrary Bricks children.

## The child contract

Inspect runtime controls and preserve the native child wrappers, including WooCommerce v2 state children. Obtain structure from a valid existing element, a concrete recipe below, or the installed source; do not infer it from `nestable: true`.

Child-generation methods:
- `get_nestable_item()`: returns the **default item template** (e.g., a Slider's default slide is a Block wrapping a Heading + Button). When you click "Add item" in the builder, this template is cloned.
- `get_nestable_children()`: returns the **full initial children tree** when the element is first added to the page.

Both methods can be overridden per-element. For Slider Nestable, that's `slider-nested.php:1112` and `:1135` respectively.

## Loop-context scope: the outer-level rule

A layout element with query-loop controls repeats **that layout element**, including its child tree. For a nestable widget, choose the child wrapper that represents one item; do not assume the widget parent itself accepts query controls.

For product carousels, keep one non-looping Slider Nestable parent and put the
Posts query on one child slide Block. Put `{post_title}`, `{post_excerpt}`, and other
product content inside that Block. Each query result repeats that slide; other saved
slides remain additional slides, so remove unwanted defaults only within the
requested design scope (`slider-nested.php::render` renders its child elements).

## The "one loop context per level" trap

You cannot nest a Posts loop inside a Posts loop and have the inner loop see the outer post automatically. The inner loop's query runs independently.

When an inner query needs the outer item, inspect the loop context through
`Query::get_loop_object()` using the outer query element ID, then build the intended
query args in a scoped hook. Do not assume the current global post is still the outer
item after the inner query starts. See [bricks-query-loops](../bricks-query-loops/SKILL.md)
for query hooks and context verification.

## Components with data-producing queries

Queries can live inside components in current Bricks. The runtime tracks component context for query loops, including `component_id` on the `Query` instance and `data-query-component-id` on the query trail (`includes/query.php:77`, `includes/elements/base.php:4163-4168`).

Even so, keep data-producing queries at the page or template level when another control needs to target them, such as pagination or Query Filters. Component-owned queries are harder to reason about because the rendered query id can include instance context.

## Slider Nestable specifics

- Each slide is a Block by default. You can change any slide to a Section / Container / Div or wrap in other elements.
- To repeat slides, put the query loop on a child Block.
- Splide powers Slider Nestable. The element enqueues `bricks-splide` and stores options in `data-splide` (`includes/elements/slider-nested.php:10-23`, `:1204-1355`). Not all Splide options are exposed; use the custom options control or a scoped render-attributes hook when you need an option Bricks does not surface.
- Performance: each Slider Nestable initializes its own Splide instance. Heavy pages with many sliders should keep slide markup and images lean, and should be tested after AJAX loop updates because Bricks rebuilds Splide when query results change.

## Accordion Nestable specifics

- Default 2 items, each with a title block + content block.
- State: open/closed is client-side only (no server-side persistence).
- Accessibility: Bricks handles `aria-expanded` and keyboard navigation. Don't add duplicate logic.
- Multiple-open vs single-open is a setting on the parent (`accordionOneAtATime`).

## Tabs Nestable specifics

For a new two-tab widget, read [the native nested fixture](assets/tabs-nested.json).
Use it as `add-element.element`, adapting labels and pane content before insertion.
It omits internal IDs so the nested-input normalizer can generate them. It is not
a persisted flat page array or an entire write request.

Required structure (Bricks 2.4 `tabs-nested.php::get_nestable_children`):

```text
tabs-nested (openTab: "0")
  block (_hidden._cssClasses: "tab-menu", _direction: "row")
    div (_hidden._cssClasses: "tab-title") -> title content
    div (_hidden._cssClasses: "tab-title") -> title content
  block (_hidden._cssClasses: "tab-content")
    block (_hidden._cssClasses: "tab-pane") -> first pane content
    block (_hidden._cssClasses: "tab-pane") -> second pane content
```

Keep these exact class tokens and wrapper relationships; they drive native styling,
ARIA generation and JavaScript pairing. `_hidden._cssClasses` is a runtime virtual
setting and may be absent from the bundled controls snapshot. Keep title/pane order
and counts aligned. Do not manually add active-state classes or duplicate native
ARIA logic. Put converted cards inside each pane, not directly under the Tabs root.


- Two subtrees: tab buttons (one per tab) and tab content (one per tab). Bricks auto-matches by order.
- Custom tab bodies are the primary reason Tabs Nestable exists: the non-nestable Tabs couldn't hold arbitrary content per tab.
- Set the initial active tab with `openTab` (0-indexed; `tabs-nested.php::set_controls`).

## Nav Nested specifics

- Builds navigation as native editable elements; retain an existing WordPress-menu workflow when that matches the site.
- Each menu item is a Link or a Dropdown (another nestable) containing sub-Links or rich content.
- Mobile behavior (hamburger, drawer) configured on the Nav Nested parent.
- Use **bricks-mega-menus** when a Dropdown should become a full-width/rich mega panel.
- If a site already has WordPress menus, place a `nav-menu` element inside Dropdown content or use the WordPress menu-backed path from **bricks-mega-menus**. Nav Nested itself is still an element-tree menu builder.

## Offcanvas specifics

- Separate from popup but similar conceptually. Differences:
  - Offcanvas is an element that can live inline on any page.
  - Popup is a template with its own conditions and frequency limits.
  - Use offcanvas for navigation drawers, cart drawers, filters sidebars.
  - Use popup for promotional modals, confirmations, dialogs.
- Toggle via interactions (`action: toggleOffCanvas`).

## Silent-failure debug order

1. **Nestable renders but no children?**
   a. Check the builder tree: do children exist? If not, insert them (they don't auto-populate after initial add-from-library).
   b. Custom class on the nestable wrapper hiding children (display: none / height: 0).

2. **Looped nestable shows default children instead of looped data?**
   a. The intended child layout element does not have Query Loop enabled.
   b. Query is targeting the wrong element. Check element-specific query settings.

3. **Accordion items not clickable?**
   a. Custom z-index / position elsewhere on the page blocking clicks.
   b. JS error elsewhere preventing Bricks' frontend.js from initializing.

4. **Tabs show all content at once?**
   a. `frontend.js` not loaded: check script enqueue.
   b. Custom CSS on `.brxe-tabs-nested *` overriding `display: none` on inactive panels.

5. **Slider sometimes misaligned on load?**
   a. Splide initialized before images or fonts settled. Set explicit image dimensions and test after AJAX loop updates.
   b. Fonts loading late causing re-flow. Preload fonts.

Verify nested-loop behavior on the frontend after saving.

## MCP write notes

- `add-element` / `update-element` / `remove-element` route writes to the correct meta key for the host post: page content vs header template vs footer template. Pass `postId` and the element ID.
- Element-write abilities reject `query: null` and queries missing `objectType`. If you're seeding a nestable with a query, pass at least `{ objectType: "post", postType: ["post"] }`.
- Link settings on Buttons / Headings / Images are validated at write time: `external` requires a `url`; `internal` requires `postId` or `useDynamicData`. Empty link objects are rejected.
- Dynamic-data tags inside settings are bracket-balance-checked at write time: `{post_title` (missing close) returns an error. Code/CSS/script settings are exempt (they legitimately contain `{`).


---

## Module: bricks-element-schemas

# Bricks: element schemas

Use this skill when a write needs exact element keys, control value shapes, CSS-mapped settings, inherited controls, globals, page settings, template settings, or schema validation.

The runtime Bricks MCP and the bundled resolved schemas answer different questions:

- **Runtime MCP:** what this connected site actually has installed and registered.
- **Bundled schemas:** how Bricks values are shaped, especially complex controls such as `image`, `link`, `typography`, `query`, `repeater`, `form`, `interactions`, and responsive/pseudo-class setting keys.

Use both for non-trivial writes. Runtime first, bundled value schema second. The bundled snapshot is generated from Bricks 2.4; conditional or dynamically assembled controls can be absent from a static export. A missing bundled key does not prove a runtime control is unsupported.

Runtime control schemas are not full default-child templates. For native widget
nesting, inspect a valid existing instance or a concrete recipe in
**bricks-nestable-elements**. Internal virtual settings such as `_hidden._cssClasses`
can be accepted at runtime even when absent from the bundled snapshot; confirm the
installed contract rather than discarding required native wrapper classes.

## Element IDs vs frontend IDs

Bricks element `id` is an internal builder identifier and is also used in the default frontend selector `#brxe-{id}`. When you set it yourself, it must be exactly 6 characters. In nested `{name, children}` input, you may omit ids and Bricks will generate them while preserving parent-child nesting. In flat arrays, provide or preserve valid 6-character ids for every `id`, `parent`, and `children` reference.

Do not use element `id` for human-readable anchors such as `hero` or `pricing-section`. Bricks renders `id="brxe-{id}"` by default. Only set `settings._cssId` when you intentionally need a custom HTML id instead of the default Bricks id.

## Lookup order

1. **Connected Bricks site:** prefer runtime MCP.
   - List element types through `mcp-adapter-execute-ability` with `ability_name: "bricks/list-element-types"` and optional pagination or category parameters.
   - Get one element through the same dispatcher with `ability_name: "bricks/get-element-schema"` and `parameters: { "elementName": "<name>" }`.
   - These two abilities are not named direct tools on the default Bricks MCP server. A custom server may expose them directly, but the dispatcher is the portable path.

2. **Bundled full resolved schemas:** use the scripts in this skill. The pack includes the resolved schema bundle for elements, controls, global data, page settings, template settings, and general content-area structure.

3. **Local Bricks repo or generated bundle:** if you are developing Bricks itself, use the scripts against `schema-docs-bundle/schema-resolved` or `includes/schema` to match the checkout exactly.

4. **Academy docs:** use deployed schema docs only when the local skill bundle is unavailable or you need to compare against published docs.

Do not load every schema into context. Fetch the one element/control/global schema you need.

## Responsive and pseudo-class keys

Use active site breakpoint keys and pseudo-class selectors from
`bricks/list-breakpoints` and `bricks/list-pseudo-classes`. Append them to a
CSS-generating control: `_typography:tablet_portrait`, `_background:hover`, or
`_background:tablet_portrait:hover`. Do not turn `:hover` into `::hover`, and do not
suffix content/behavior controls merely because the resulting key looks valid.
The runtime settings schema validates these combinations
(`includes/abilities/style-settings-schema.php`).

## When to fetch a schema

Fetch the schema before writing if:

- The element type is uncommon, complex, WooCommerce-specific, or nestable.
- You are editing an element already present on the site and you do not know its control keys.
- You are writing media, form, query, interaction, condition, selector, or responsive/pseudo-class settings.
- You are converting HTML and the converter output includes a fallback `code` element or a complex element such as `form`.

For simple repeated builds, default to the small core set in `references/common-elements.md`, then fetch exact schemas only for the elements and controls you actually use.

## Scripts

From this skill directory:

```bash
node scripts/list-schemas.mjs --schema-root /path/to/bricks/schema-docs-bundle/schema-resolved
node scripts/get-schema.mjs element image --schema-root /path/to/bricks/schema-docs-bundle/schema-resolved
node scripts/get-schema.mjs element form --schema-root /path/to/bricks/includes/schema
node scripts/get-schema.mjs element image --compact --settings image,altText,loading
node scripts/get-schema.mjs control image --compact
node scripts/get-schema.mjs general content-area --compact
node scripts/get-schema.mjs element image --list-settings
node scripts/list-schemas.mjs --schema-root references/schema-resolved
node scripts/list-schemas.mjs --common
node scripts/list-schemas.mjs --converter
```

If `--schema-root` is omitted, scripts search upward from the current directory for:

- `schema-docs-bundle/schema-resolved`
- `includes/schema`
- `references/schema-resolved` inside this skill

Use `--compact` when you need value shapes without loading a full element schema. Use `--settings key1,key2` to limit an element schema to the controls you plan to write.

## Static manifest

`references/schema-manifest.json` is a compact discovery manifest generated from the Bricks schema source. Use it to decide what exists and whether an element is common, nestable, WooCommerce-specific, or supported by the HTML-to-Bricks converter.

The manifest is not the schema. Treat it as a map, then fetch the exact schema on demand.

Read one bundled element, control, or settings schema at a time.

## Common build bias

Most maintainable Bricks sites use a small set of elements many times:

- Layout: `section`, `container`, `block`, `div`
- Content: `heading`, `text-basic`, `button`, `image`, `icon`
- Reuse/data: query-loop settings on layout elements, components, dynamic tags
- Navigation/forms when needed: `nav-nested`, `form`

Prefer these for new builds unless the user asks for a specific widget or the existing page already uses one. For less-used elements, fetch the schema before editing.

## HTML-to-Bricks converter coverage

The converter intentionally uses a limited element set. It currently maps to:

`section`, `container`, `block`, `div`, `heading`, `text-basic`, `text-link`, `icon`, `button`, `image`, `svg`, `video`, `audio`, `code`, `divider`, `form`.

Treat converted output as a starting point. If the source implies sliders, accordions, tabs, product widgets, maps, filters, or query-driven cards, convert the static structure first, then replace or refine with the proper Bricks element schema.

## Never do

- Do not guess setting keys for complex elements.
- Do not invent long or semantic element `id` values. Use an exact 6-character internal id, or omit ids only in nested children format. Only set `settings._cssId` when a custom HTML id is explicitly needed.
- Do not paste full schema bundles into a prompt.
- Do not use Academy/static schemas over runtime MCP when connected to the actual site.
- Do not write raw post meta directly. Use Bricks abilities so validation, revisions, and permissions run.
