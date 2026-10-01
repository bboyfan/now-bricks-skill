# Bricks Reference: 01 Workflow And Routing



---

## Module: bricks-start-here

# Bricks orientation

Use Bricks abilities as the authoritative interface to the connected WordPress site. Runtime reads override bundled examples and schemas.

## Fast routing

- **Explicit host workspace:** when the task environment itself announces the
  `bricks.workspace/v1` capability, edit only the authorized projected files with
  ordinary file tools. The host owns validation, persistence, and authoritative
  readback after the agent finishes. Do not add MCP discovery or commit calls to
  that route.
- **Known single existing target:** call the narrow read/write abilities directly. If `bricks-resolve-agent-file` and `bricks-commit-agent-file` are available, their schemas provide a self-contained two-call path; do not load another skill merely to repeat that contract.
- **New visual section, page, or static template shell:** load **bricks-html-css-to-bricks** and convert semantic HTML/CSS before persistence.
- **New homepage plus site identity, brand system, or whole-site direction on a fresh install:** call `bricks-commit-site-foundation` with one compact manifest. It owns the palette, fluid scales, root theme style, globally conditioned header/footer templates, page-body import, and front-page setting. Do not preflight it with low-level design reads: the ability refuses non-greenfield state and same-key retries resume safely. Load the three low-level skills only when this compound ability is unavailable.
- **Small exact existing-site edit:** no skill is required. Prefer the self-described one-call `commit-exact-site-edits` route for supported page text/structure, component definition fields, global-variable values, and class/theme-style leaves. It accepts exact IDs or exact unique human names and exact current text/labels where its live schema advertises them. Supply `expectedValue`, or literal `allowBlindWrite: true` only when the user intentionally supplied that exact target and requested replacement regardless of its current value.
- **Typed target discovery, an oversized/complex page, dependency analysis, recovery, or 2-25 coordinated resources outside the exact route:** load **bricks-agent-repository**. Prefer `checkout-site-edit-map` → `commit-site-edit-plan` only when the live schema/response advertises the requested operation; otherwise use canonical files.
- **Create or substantially redesign a design system:** load **bricks-design-systems** or **bricks-seed-design-system**.
- **Component schema/slot/property work:** load **bricks-components**.
- **Dynamic data, queries, filters, forms, interactions, conditions, media, or templates:** load only the matching task skill.

Do not call version, start-here, the full ability catalog, design context, or a site manifest when the exact target and narrow ability are already known.
Never infer `bricks.workspace/v1` from filenames, a skill installation, or a local
`.bricks` directory. Without an explicit host capability announcement, WordPress
abilities remain the write path.

## Invariants

1. Before directly **creating** a class, variable, palette color, theme style, or component, call `bricks-get-design-context` with `responseFormat: "summary"`; reuse compatible existing resources and breakpoints. The exceptions are `bricks-commit-site-foundation` for a full greenfield site and `bricks/commit-html-css-page-import` when the task is only one known empty page body. Both read the state they need; do not add redundant discovery calls. The page importer does not create palettes, scales, theme styles, components, or templates, so never use it alone for a whole-site brief. Do not force same-named duplicates.
2. For an unfamiliar element or complex setting, inspect `bricks/get-element-schema` through the dispatcher and consult **bricks-element-schemas** for nested control values. Never guess a query, media, form, interaction, or condition shape.
3. Element IDs are six characters. Preserve IDs and parent/children references in existing flat trees; nested create input may omit IDs when the ability permits generation.
4. Preserve opaque fields, component slots/properties/variants, and unrelated resources. Respect every expected version, digest, ownership value, and usage count returned by the matching current read.
5. Treat returned authoritative readback, revision, version, and digest as the result. On ambiguity, stale state, partial commit, or manual recovery, stop and follow the returned recovery route instead of guessing or retrying under a new key.
6. Destructive writes require explicit user approval. Global data has no post-revision undo; export supported affected items before destructive global changes.
7. Use rendered frontend HTML for verification, never as editable source.

## Access and verification

Direct tools use hyphenated names for slash-named abilities. If an enabled ability is not direct, call `mcp-adapter-execute-ability` with its `bricks/...` name. If execution says it is disabled, inspect dispatcher ability `bricks/list-ability-status`; do not route around an administrator decision.

After broad page/template/component changes, verify persisted state and the frontend. Use **bricks-browser-verify** when browser access exists. For one focused write, do not add redundant reads when the mutation already returns authoritative readback.

For dynamic tags, enumerate `bricks/list-dynamic-data-tags` for a relevant post and preview every tag before persistence. Never invent provider tag names.


---

## Module: bricks-agent-repository

# Bricks agent repository

Treat Bricks as a typed repository while WordPress remains authoritative.

## Explicit host-owned file workspace

Use this route only when the task environment explicitly announces
`bricks.workspace/v1`. Treat the projected files as a temporary authorized checkout:

1. Inspect and edit only the supplied resource files with ordinary file tools.
2. Preserve opaque fields, IDs, baselines, and files outside the requested scope.
3. Do not edit host metadata, credentials, session files, or baseline digests.
4. Do not call write abilities in parallel. The host validates and saves the changed
   files after the agent finishes.
5. Report the edited files, then wait for the host result before claiming the changes
   were saved to WordPress.

Never infer `bricks.workspace/v1` from filenames, a `.bricks` directory, an
installed skill, or prior tasks. If the host does not announce it, use the ability
routes below.

## Choose the smallest route

- **Exact supported edit:** use `commit-exact-site-edits`.
- **Exact edit that needs target discovery:** use `checkout-site-edit-map`, then
  `commit-site-edit-plan` when the returned `editableOps` supports the change.
- **Known target needing structural editing:** use `resolve-agent-file`, then
  `commit-agent-file`.
- **Two to 25 coordinated resources:** use one site changeset.
- **Unknown or ambiguous targets, dependency analysis, or recovery:** use
  `checkout-site-repository` with narrow filters.

Never fetch every full document merely to locate one target.

## Exact edits

Use `commit-exact-site-edits` when the live schema supports the requested operation
and the target is an exact ID, unique full name, current text, or label. Supply
`expectedValue`. Use `allowBlindWrite: true` only when the user intentionally supplied
the exact target and requested replacement regardless of its current value.

Use only operations advertised by the live schema. Component attribute edits on this
route are limited to `role` and `aria-*`; use the canonical file route for broader
custom attributes. Never change a component instance boundary or overwrite content
controlled by a component property.

## Edits that need discovery

Call `checkout-site-edit-map` with the smallest target list that can locate the edit:

```json
{
  "targets": [
    { "scope": "page", "postId": 13 },
    { "scope": "design", "resource": "globalVariable", "id": "accent" }
  ],
  "elementIds": ["bbbbbb"]
}
```

Omit `elementIds` when they are unknown. Do not substitute unsupported ID arrays or
parameters. Copy each returned `selectionRef` into one advertised operation and call
`commit-site-edit-plan` once with a stable idempotency key. Repeat that exact call to
resume safely. Request `responseFormat: "summary"` unless another edit needs the full
document.

Use `preview-site-edit-plan` with `resourcePath` and `selectionDigest` only when the
user asks for a dry run. Fall back to canonical files when the map is truncated or
does not support the required element, property, link, attribute, or structural edit.

## Repository discovery

When the target is not exact, call `checkout-site-repository` with the narrowest
useful `query`, `postTypes`, `designKinds`, `includeDocuments`, `includeDesign`,
`includeDependencies`, and `perPage`. Follow cursors only while later results may
matter. After selecting a target, continue with the smallest edit route above.

## Two-call known-target path

Call `bricks/resolve-agent-file` with an exact `scope`, `query`, and optional
`resourceKinds`. Proceed only when it returns one target and a canonical document.
Follow its `editingContract` for canonical keys, native style shapes, responsive
suffixes, flat-tree ordering, and preservation rules. Commit the target and requested
edit through `bricks/commit-agent-file` with one stable idempotency key. Prefer compact
readback; request the full document only when another edit needs it.

For custom attributes, preserve ordered `_attributes` records shaped as `{ "id"?: string, "name": string, "value": string }`. The returned editing contract is authoritative.

## Changesets

There is no atomic whole-site transaction across WordPress hooks, assets, caches, and plugins. Keep each step safe if later work fails:

- Keep every intermediate pages-first state valid.
- Preview the complete bounded changeset once.
- Apply/resume with the same token and outer idempotency key until terminal.
- Continue only from `in_progress`; success is `committed` with authoritative readback for every changed step.
- Stop on `failed_before_commit`, `partial_commit`, or `manual_recovery`. Re-read and re-plan; never assume rollback.
- Clear a recovery record through the destructive resolution ability only after explicit human approval; clearing it does not undo saved changes.

Split work above 25 resources into independently valid batches. For renames or reference migrations, use dependency hints to narrow authoritative consumer reads; hints are not proof that a resource is unused.

## Boundaries

- Rendered HTML is verification evidence, not editable source.
- Page files may reference but cannot mutate shared design resources.
- Workspaces update existing resources. Use focused create/delete abilities and their required preconditions for lifecycle changes.
- Never replace focused ownership/version/digest requirements with a repository baseline.
- Do not reconstruct redacted component or code-sensitive data from frontend markup.
- Prefer a fresh targeted checkout over retaining a large snapshot across unrelated tasks.


---

## Module: bricks-plan-from-brief

# Bricks: plan from a brief

When the user describes broad or ambiguous work such as "build a pricing page" or
"add a hero to the homepage", do not immediately write. Establish the minimum site
state needed for a concrete plan. For a known scalar or exact target edit, skip this
skill and use the focused fast path.

> **If a `bricks/*` ability is not available as a direct tool**: first check whether it is outside the fast path and call it through `mcp-adapter-execute-ability` with `ability_name: "bricks/<name>"`. If the dispatcher also rejects it, call `bricks-list-ability-status` to check whether a site admin disabled it under Bricks > AI.

## Step 1: Read the site

Read only the surfaces needed by the brief; parallelize independent reads:

- `bricks/get-mcp-version` only when compatibility or availability is uncertain.
- `bricks/get-design-context` when the brief creates or reuses design resources.
- `bricks/list-cms-sources` when dynamic content or an unknown post type is involved.
- `bricks/list-templates` when template routing or reuse is involved.
- If the brief references a specific page: `bricks/find-post` + `bricks/get-page-elements`.

## Step 2: Translate the brief into resources

For each sentence in the brief, identify which Bricks primitives it maps to:

- "Pricing table" -> element tree on a post, likely reusing an existing `.card` component if one exists.
- "Primary button" -> existing `.button` class or `.button-primary`? Don't create a new class; reuse.
- "New service landing page" -> `bricks/create-post` + `bricks/set-page-elements`. Consider attaching a header/footer template via `bricks/set-template-conditions`.
- "Make it responsive" -> read active breakpoints with `bricks/list-breakpoints`. Base settings have no breakpoint suffix; other settings use the returned keys. An existing page tree may not contain every active breakpoint.
- "Match our brand" -> use existing palette + theme styles. Never invent new brand colors.

## Step 3: Identify gaps

For each resource the brief needs, mark it as **exists / missing / ambiguous**:

- **Exists:** reuse. List the id/name in the plan.
- **Missing:** add a create/write step to the plan. Name it to match site conventions (see **bricks-naming-conventions** skill).
- **Ambiguous:** the brief says "CTA button" but there are two candidate classes. List both options in the plan and ask the user which to reuse.

## Step 4: Order the plan

1. Design-system writes first (classes, variables, components). They're referenced by downstream writes.
2. Content writes second (pages, templates).
3. Wire-up writes last (template conditions, menu entries).

Within each tier, destructive writes last. Prefer small reversible writes while planning. Batch independent same-post element setting edits only when one revision is acceptable.

## Step 5: Present the plan

Before executing, show the user:

- The intended changes and their execution order.
- The list of existing resources you'll reuse.
- The list of new resources you'll create, with names.
- The list of ambiguities that need their input.

Proceed within the user’s existing authorization once material ambiguities are resolved. Ask before expanding scope or making a destructive change that was not authorized.

## Step 6: Execute

Call abilities in order. After each mutation, capture the response (especially `revisionId` / resource id). After each meaningful milestone, verify with a read before moving on. Report what you did and what the user needs to check in the builder.

## Red flags that mean stop and ask

- Brief mentions a feature/plugin that isn't installed (check `list-cms-sources`, `list-dynamic-data-tags`).
- The brief conflicts with the existing design system or requires replacing shared resources beyond the requested scope.
- Brief names a specific file / template / component that doesn't exist: confirm the spelling, don't silently create a new one.


---

## Module: bricks-site-reproduction

# Bricks: live-site reproduction

Sequence a fetch step (browser tool, web fetch, or scraper), page import or conversion, design-system abilities (`create-color-palette`, `create-color`, `set-global-variables`, `create-component`), and the `bricks-browser-verify` skill. For one new page that needs no component injection or other tree surgery, `commit-html-css-page-import` owns conversion and persistence; never call `convert-html-css-to-bricks-data` before it.

This skill is the primary route. Do not load every related skill up front. Load one
companion only when the exact source requires it—for example media upload, a form, a
popup, or an interaction. Treat the related-skills section as a reference map.

Match the source layout, typography, content, and behavior to the fidelity requested by the user.

## Target scope

First distinguish a new empty target, an authorized full rebuild and a section
added to an existing page. For additions, inspect the target and reuse its design
resources; convert only the requested fragment, then insert with `add-element`
using the actual parent and sibling position. Preserve unrelated content and site
settings. `set-page-elements` requires the complete intended tree, never just the
new fragment. Create a root theme style or parallel token system only when the
brief includes that site-wide design change.

## The five-phase loop

```
1. Fetch    -> grab the target URL's HTML + CSS (and optionally screenshots)
2. Analyze  -> extract tokens (colors, spacing, typography) and identify components
3. Reuse    -> map existing tokens; create missing resources when needed
              -> bind body, heading, and page defaults through an active root theme style
4. Rebuild  -> convert reviewed HTML/CSS per page, wire components, handle converter limits
5. Verify   -> side-by-side via bricks-browser-verify, iterate
```

## Phase 1: Fetch

Three patterns, ranked by fidelity:

### Pattern A: Browser navigation (best for JS-rendered sites)

```
browser.navigate({ url: "https://target-site.com" })
browser.evaluate({ code: "document.documentElement.outerHTML" })
```

Grab:
- Full rendered HTML (`document.documentElement.outerHTML`)
- All stylesheets (inline + linked, concatenated)
- Viewport screenshot at multiple widths
- Asset URLs (images, fonts) for download

### Pattern B: WebFetch (best for static-HTML sites)

```
WebFetch({ url: "https://target-site.com", prompt: "return raw HTML" })
```

Lighter than a browser, no JS execution. If the site is React/Vue SPA with CSR, this returns an empty shell: fall back to Pattern A.

### Pattern C: Scraper / user-provided export

If neither browser navigation nor fetch works (anti-scraping, auth, etc.), ask the user to:
1. Open the page in their browser.
2. Save As -> Webpage, Complete.
3. Share the HTML file + assets folder.

## Phase 2: Analyze

### Token extraction

Scan the CSS for recurring values. Manual or with a small script:

```
Colors mentioned 3+ times:
  #0F172A   -> 14 occurrences  (likely Neutral/900)
  #4F46E5   -> 9 occurrences   (likely Primary)
  #F8FAFC   -> 22 occurrences  (likely Background)
  #64748B   -> 7 occurrences   (likely Muted)

Spacing (rem/px):
  4px, 8px, 16px, 24px, 32px, 48px, 64px, 96px
  (power-of-two-ish ladder)

Typography:
  font-family: 'Inter', sans-serif  (15 rules)
  Sizes: 14px, 16px, 18px, 24px, 32px, 48px, 72px
```

The unique values become your token set. Name them semantically, not chromatically:
- `primary` / `accent` / `bg-subtle` / `text-muted`: not `blue-500` / `gray-100`.
- `space-xs` / `space-sm` / `space-md` / `space-lg`: not `8px` / `16px` / `24px` / `48px`.

### Component identification

Scan the HTML for repeated structures:
- `<header>` or `<nav class="site-header">`: one instance, sitewide.
- Cards: grep for `class="*card*"` occurrences.
- CTAs: recurring button-wrapped-in-section patterns.
- Footers: `<footer>`, once.
- Testimonial blocks, pricing tables, feature lists: project-dependent.

Create components for structures that need reuse.

### Page inventory

If the target is a multi-page site: list pages you need to reproduce. Usually:
- Home
- Pricing / Plans
- About
- Contact
- Blog index + a sample post

Inventory every page in the requested scope and work through them in batches.

## Phase 3: Seed

### Create tokens on the Bricks site

Colors: call `list-color-palettes` first, pass its `ownership` as
`expectedOwnership`, and chain each successful mutation's returned `ownership`
into the next palette/color mutation.
```
create-color-palette({
  name: "Brand",
  colors: [
    { light: "#4F46E5", raw: "var(--brand-primary)" },
    { light: "#0F172A", raw: "var(--neutral-900)" },
    { light: "#64748B", raw: "var(--neutral-600)" },
    { light: "#F8FAFC", raw: "var(--neutral-50)" }
  ],
  expectedOwnership: palettes.ownership
})
```

Other tokens (spacing, radius, typography, shadow):
```
// `globals` is one fresh list-global-variables response.
set-global-variables({
  variables: [
    { name: "space-xs",  value: "4px",    category: "<spacing-category-id>" },
    { name: "space-sm",  value: "8px",    category: "<spacing-category-id>" },
    { name: "space-md",  value: "16px",   category: "<spacing-category-id>" },
    ...
    { name: "text-body", value: "16px",   category: "<typography-category-id>" },
    { name: "text-h1",   value: "72px",   category: "<typography-category-id>" },
    { name: "font-family-sans", value: "'Inter', system-ui, sans-serif", category: "<typography-category-id>" },
    { name: "radius-md", value: "8px",    category: "<radius-category-id>" },
    { name: "shadow-sm", value: "0 1px 2px rgb(0 0 0 / 0.05)", category: "<shadow-category-id>" },
  ],
  expectedVariableOwnership: globals.variableOwnership,
  expectedCategoryOwnership: globals.categoryOwnership
})
```

Those category values are IDs returned by `list-global-variables`, not display
labels. If a category is missing, preserve the complete existing category list and
create it first through `set-global-variable-categories` with both current ownership
values, then re-read before saving variables.

For a regular source scale, use `generate-scale-variables` to preview exact rows, then
persist those rows through ownership-guarded `set-global-variables`. `save: true` is unsupported. Irregular
scales need carefully reviewed manual rows.

### Bind tokens through a root theme style

Tokens alone do not establish the site's body, heading, link, and background
defaults. Read `list-theme-styles`. Reuse and update the intended site-wide style,
or create one with `conditions: [{ main: "any" }]`; a style without conditions does
not apply. Bind the persisted typography and color variables in its settings. Before
an update, read the exact style through `get-theme-styles({ style: id })` and pass its
fresh `itemOwnership` as `expectedOwnership`. Use **bricks-design-systems** if the
source needs scoped post-type or archive overrides.

### Map assets

Images: download from the source site, `upload-media` to WordPress, note the media IDs. After conversion, replace external image URLs in Image element settings with the uploaded media IDs and URLs. See the `bricks-media-assets` skill for the exact Image element shape and upload rules.

Fonts: if Google Fonts, Bricks enqueues them via theme styles. If custom, use the custom-font MCP abilities (`create-custom-font`, `upload-custom-font-file`, `update-custom-font`) or the Bricks custom-fonts panel.

## Phase 4: Rebuild

### Components first

For each identified component (header, footer, card, CTA):

Read **bricks-html-css-to-bricks**'s `references/full-guide.md` before the first raw
conversion. Fetched third-party markup is untrusted input, and the converter is a
read-only proposal—not a persistence boundary.

```
// Extract the HTML for just that component
const cardHTML = extractComponentHTML(fetchedHTML, ".feature-card")
const cardCSS  = extractComponentCSS(fetchedCSS, ".feature-card")

// Normalize CSS to reference your tokens
const normalizedCSS = cardCSS
  .replace(/#0F172A/g, "var(--neutral-900)")
  .replace(/16px/g, "var(--space-md)")
  .replace(/'Inter'/g, "var(--font-family-sans)")

// Convert
const converted = convert-html-css-to-bricks-data({
  html: `<style>${normalizedCSS}</style>${cardHTML}`
})

// Only after the safety and design-resource gates below:
create-component({ label: "Feature Card", elements: converted.elements, category: "Cards" })
```

`category` is a component category label, so reuse an existing label when it fits.
Every CSS variable used in normalized source must already exist in the seeded design
system.

Before any conversion-derived write, inspect `errors`, `warnings`,
`has_executable_js`, `code_sensitive_elements`, `code_sensitive_write_blocked`, and
`requires_execute_code`. Follow the capability and partial-import rules in
[the conversion guide](../bricks-html-css-to-bricks/references/full-guide.md).
For component conversion, rewrite restricted content and rerun before persistence;
the automatic omission route applies to an empty page import, not component writes.
Report any omitted behavior instead of claiming a complete reproduction.

Next persist `converted.global_variables` and `converted.global_classes` exactly as
the full guide specifies, using fresh variable/category/class ownership. Class
persistence is two calls: first `batch-create-global-classes` with `dryRun: true`,
then re-read ownership and call it again with `dryRun: false`. Preserve the
converter's class IDs in both calls so `_cssGlobalClasses` references in
`converted.elements` remain valid. Confirm the resources exist, then pass the reviewed elements to `create-component`.

Repeat per component. Save component IDs.

### Pages next

Per page:
1. `create-post({ postType: "page", title: "Home" })` -> capture `permalink`.
2. Extract that page's HTML, normalize CSS to tokens as above.
3. If the page needs no component injection or other tree surgery, use `commit-html-css-page-import` as the first and only conversion/persistence operation for the known empty target. Do not pre-call `convert-html-css-to-bricks-data`.
4. Otherwise run `convert-html-css-to-bricks-data`, then replace each component-region in memory with an element whose `cid` is the component ID from phase 3.
5. Review the final transformed tree. Persist returned `global_variables` with fresh variable/category ownership. Persist returned `global_classes` through the same two-call, ownership-refreshed atomic batch workflow above, preserving every converter class ID so the tree's `_cssGlobalClasses` references remain valid. Then insert the new subtree, or call `set-page-elements` once with the complete intended tree when whole-page scope requires it. Never persist the duplicated raw-component tree as an intermediate page.

### Handle convert-html-css-to-bricks-data limits

See `bricks-html-css-to-bricks` skill. After conversion, manually:
- Wire Slider Nestable children if the source has a carousel.
- Configure Form element actions if the source has a contact form.
- Add Interactions (e.g., sticky header, scroll-to-anchor).
- Replace repeated card lists with Query Loops + dynamic data.

## Phase 5: Verify

Use `bricks-browser-verify`:

1. Open the target URL with the available browser tool. Screenshot.
2. Open rebuilt page permalink. Screenshot.
3. Side-by-side compare. Articulate deltas.
4. Fix via `update-element` or `set-global-variables` (prefer the latter for systemic issues).
5. Re-verify.

**Compare:**
- Compare colors against the source and requested brand palette.
- Match font families, weights, sizes, and line height.
- Animation timings: source may have 300ms fade; yours may be 200ms Bricks default. Adjust via interactions.
- Image aspect ratios: target might have forced 16:9; your converted element has `auto`. Fix per-element.

**Investigate:**
- Entire sections missing: `convert-html-css-to-bricks-data` failed or source had conditionally-rendered content.
- Catastrophic layout break: token mismatch (you used `var(--space-md)` but didn't create it).
- Text wrapping differently: font-family or line-height not seeded.

## Silent-failure debug order

1. **Fetched HTML is empty shell (React/Vue CSR)?**
   a. Need a browser tool with JavaScript execution, not a plain HTML fetch.

2. **Tokens don't propagate after seeding?**
   a. Theme style not using them: bind variable to theme style manually, or seed with explicit theme-style settings.

3. **Converted page missing components?**
   a. `convert-html-css-to-bricks-data` doesn't know to use components. You replace raw element subtrees with component-instance references after conversion.

4. **Verify screenshot doesn't match target at all?**
   a. Cache serving stale Bricks CSS. Flush / regenerate.
   b. Tokens not created before conversion: CSS references undefined vars.
   c. Fonts different: check theme style typography settings.

5. **JS / forms / popups don't work?**
   a. `convert-html-css-to-bricks-data` is static. Wire behavior manually per `bricks-forms` / `bricks-popups` / `bricks-interactions` skills.

## Related skills

- `bricks-browser-verify`: the verification half of the loop.
- `bricks-html-css-to-bricks`: the conversion step details.
- `bricks-figma-to-bricks`: sibling workflow when source is Figma instead of live URL.
- `bricks-design-systems` / `bricks-seed-design-system`: token seeding mechanics.
- `bricks-components`: component extraction + reuse.


---

## Module: bricks-quality-gate

# Bricks: quality gate (verify-after-write)

Some Bricks writes can succeed at the storage layer and still leave the page broken: wrong routing, a lost reference, a silently rejected setting, or a mistyped dynamic tag. Verify in proportion to the write and use authoritative mutation readback instead of repeating it.

> **If a `bricks/*` ability is not available as a direct tool**: first check whether it is outside the fast path and call it through `mcp-adapter-execute-ability` with `ability_name: "bricks/<name>"`. If the dispatcher also rejects it, call `bricks-list-ability-status` to check whether a site admin disabled it under Bricks > AI.

## Verification approach

Inspect every mutation response for target identity, persisted changed values (or
an equivalent authoritative result), normalization/omissions and completion state.
When it establishes those facts for a focused change, do not repeat the same read.
A revision ID alone proves neither the requested values nor the final tree; versions
and digests are guards, not semantic readback. Read the affected resource when those
facts are absent, a write is broad/destructive, or the response reports uncertainty.
Use render/browser evidence for the behavior the change affects. Stop dependent
writes when checks disagree and investigate the actual persisted state.

| Wrote | Explicit verification when mutation readback is insufficient |
|---|---|
| `update-element`, `batch-update-elements`, `add-element`, `remove-element` | `get-page-elements` (post id): confirm the changed element ids in the returned tree |
| `update-element-conditions` | `get-element-conditions`: confirm `_conditions` round-tripped and group/item counts match intent |
| `update-element-interactions` | `get-element-interactions`: confirm `interactions` round-tripped and check `effectiveInteractions` for inherited class rows |
| `set-page-elements` | `get-page-elements`: diff vs what you sent |
| `set-template-conditions` | `get-template` (id): confirm `templateConditions` round-tripped |
| `create-template`, `set-template-settings` | `get-template` / `get-template-settings`: confirm `type`, `title`, settings |
| `set-global-variables` | `list-global-variables`: confirm count and shape |
| `create-color`, `update-color`, `delete-color` | `list-color-palettes (paletteId)`: diff colors array |
| `create-color-palette`, `update-color-palette`, `delete-color-palette` | `list-color-palettes`: confirm presence/absence |
| `create-theme-style`, `update-theme-style` | `get-theme-styles (id)`: confirm settings + conditions |
| `create-global-class`, `update-global-class` | `list-global-classes`: confirm class settings |
| `create-component`, `update-component`, `extract-component-from-elements` | `get-component (id)`: confirm tree, properties, variants, `_version`, `propertyGroups`, slot elements, `slotChildren`, nested component `properties`, and returned `designSystemVersion` |
| `delete-component` | `get-design-context (includeUsage: true)`: confirm the component is absent and no unexpected references remain |
| `regenerate-css-files` | spot-check a frontend page in the bricks-browser-verify skill |
| `reindex-filters` | `list-query-filters`: confirm filters still resolve their target queries |

## Pre-write checks

Global design writes use resource-specific ownership and digest preconditions.
Copy the complete ownership values from one latest matching read; never reconstruct
them from `designSystemVersion` or mix values from different reads:

- Classes: single create uses no resource ownership and only needs
  `expectedCategoryOwnership` when categorized. Batch create uses
  `list-global-classes.ownership`; update/delete use the target `itemOwnership` as
  `expectedOwnership` plus `lockOwnership`. Categorized batch/update writes also use
  `categoryOwnership`.
- Variables/categories: `variableOwnership` + `categoryOwnership`; item delete uses
  the exact variable `itemOwnership` and literal `allowOrphans: true`.
- Palettes/colors: resource `ownership` for creates, target `itemOwnership` for
  updates/deletes, and preview `saveOwnership` for saved shade generation.
- Theme-style updates/deletes: the target `itemOwnership` from a complete current
  theme-style read. Do not derive it from summarized visible settings. Deleting a
  non-empty style additionally requires reviewed `acknowledgeStyleRemoval: true`.
- Components: current `expectedDesignSystemVersion` plus full
  `expectedComponentDigest`; slot/deletion acknowledgements are additional, not
  substitutes for either precondition.
- Breakpoints/pseudo-classes: their latest resource ownership. Breakpoint writes
  that include `customEnabled` also require current global-settings ownership.

On an ownership/digest conflict, re-read and rebase the intended edit. Do not retry
the stale payload.

For unfamiliar dynamic tags, discover the current tag/controls and preview against
a representative post when that context can represent the intended use:

```
preview-dynamic-tag (tag: "{your_tag:modifier}", postId: <representative post>, context: "text")
```

Inspect `rendered`, `isEmpty` and `unknownTags`. Resolve unknown tags before using
them. Empty output can be valid missing data or the wrong preview context; it is not
by itself a broken field. This ability does not accept an arbitrary term/user/ACF
loop row. Verify those expressions in their actual loop context and report missing
runtime evidence instead of rejecting a valid tag from an unrelated post preview.

For broad same-post element setting edits, validate first when the write ability offers a dry run. If normalization changes settings you did not intend, stop before saving.

## Post-write check categories

### 1. Meta routing (header/footer)

When writing to a `bricks_template` post:

1. After the write, call `get-page-elements (postId)`: the response should include the new/updated element.
2. If the post is `_bricks_template_type = header`, the tree must come from `_bricks_page_header_2` automatically: `get-page-elements` handles routing; if the response is empty after a successful write, the area inference is wrong (file a bug, don't keep writing).

### 2. Validation rejections (caught at write time, but verify the message)

The Bricks MCP write layer rejects:
- `query: null` and queries missing `objectType` -> `set-page-elements`, `add-element`, `update-element`.
- Empty / malformed `link` settings (external without url, internal without postId) -> element link controls.
- Unbalanced `{` / `}` in non-code settings -> dynamic-data sanity check.
- Unknown keys in `set-global-variables` (use complete rows returned by the current
  contract; response-only `itemDigest` / `itemOwnership` are stripped safely).
- Unknown enum values in template `conditions[i].main` (must be one of `any`, `frontpage`, `postType`, `archiveType`, `search`, `error`, `terms`, `ids`, `hook`).
- Invalid element `_conditions` groups, missing `key`, invalid `compare`, or incomplete `dynamic_data` rows.
- Invalid element `_interactions` trigger/action/target values, missing required action fields, inline JavaScript payloads, or JavaScript callback args without valid row data.
- Term identifiers not in `taxonomy::id` form.

If you got back a `bricks_*` error code from one of these, **do not retry the same payload**. Read the message, fix the shape, then write.

### 3. Reference integrity

Some writes can orphan references that no validator catches:

- Renaming a CSS variable in `set-global-variables` doesn't update existing element settings that reference `var(--old-name)`. After the rename, **search the design system** for stale references:
  - `list-global-classes` -> grep settings for `var(--old-name)`.
  - Inventory editable pages/posts/templates with `checkout-site-repository`, following cursors, then inspect their complete element settings. Also inspect component definitions, including nested instances.
  - Record pagination, permission and scan limits; zero bounded matches do not prove a site-wide absence of use.
  - `get-theme-styles` -> grep for `var(--old-name)`.
- Deleting a color (`delete-color`) silently breaks every `var(--name)` reference. Same search before deleting.
- Deleting a global class silently breaks every element that named it in `_cssGlobalClasses`. Search elements before deleting.
- Deleting a component can orphan every element instance with the deleted `cid`, including nested instances inside other component definitions. Before deleting, read `get-component` for the full `componentDigest` and `get-design-context` with `includeUsage: true`; pass `expectedDesignSystemVersion`, `expectedComponentDigest`, the reviewed `expectedUsageCount`, and literal `allowOrphans: true`. Show affected posts/templates/components before the delete. The acknowledgement is mandatory even at zero discovered usages.
- Global-data writes are not revision-backed. Before a destructive change, use `bricks/list-transfer-items` and `bricks/export-transfer-package` to save the affected supported items. Restore only after `bricks/inspect-transfer-package`, passing its returned `zipHash` as `expectedZipHash` plus explicit item IDs. Any replacement requires clear user intent and `allowOverwrite: true`. Load **bricks-import-export** for the full flow.

### Component write integrity

For component writes, check these specifically:

- `update-component` used both the latest `designSystemVersion` and complete
  `componentDigest` from current reads. On either conflict, re-read and merge instead
  of retrying the stale payload.
- `get-component` returns `_version`. Missing `_version` makes the builder treat the component as an old beta component and highlight it in red.
- Every property `connections` key exists as an element id inside the component tree.
- Every nested component instance property key exists on the referenced component.
- Every parent-property reference uses `parent:cid_<componentId>:prop_<propertyId>` and points at the current outer component id after create/update remapping.
- Every `slotChildren` key is a real `slot` element id on the referenced component, and every slotted child id exists in the same tree.
- If `elements` were replaced on `update-component`, unchanged `properties` must still point at surviving element ids.
- If existing slots were removed, `allowSlotOrphans: true` was an explicit reviewed
  acknowledgement; bounded usage evidence is not proof that no instance content exists.

### 4. Render verification

For UI-affecting changes (layout, typography, color), the meta-write succeeded does not mean the rendered page is correct. Use the `bricks-browser-verify` skill to:

1. Open the affected frontend URL.
2. Visually confirm the change is present.
3. Check the browser console for runtime errors.
4. Resize to test responsive breakpoints if the change is layout-related.

Report any render checks that could not be completed.

### 5. Pagination and "did I read everything?"

`list-*` abilities are paginated. `hasMore: true` in the response means you only saw a subset. For verify-after-write, **scope the read to the resource you wrote** (filter by id, paletteId, type, etc.): never rely on page-1 results to confirm something you wrote that might be on page 5.

## When verify fails: the response

1. Stop dependent mutations and compare the requested change with actual readback.
2. Determine whether the operation failed before writing, committed partially, or
   completed with normalization. Preserve returned recovery/idempotency identifiers.
3. Re-read and rebase a still-authorized focused edit on an ownership conflict. Do
   not resend the stale payload or replay a whole partially committed operation.
4. Continue a safe correction/resume within existing authorization. Ask only when
   identity, intended scope or a destructive recovery choice remains ambiguous.
5. Use the matching recovery contract: page revisions where supported; inspected
   transfer backups or durable changeset recovery for applicable global operations.

## Common silent-failure smells

- Tool returned success but `get-*` shows the old state -> save was vetoed by a hook (look for `bricks/save_*` filters in the project's custom code).
- Element id in your write doesn't appear in the read-back tree -> wrong post id, wrong area, or the element was inside a component you didn't read.
- Theme style created but no visual change on the frontend -> empty `conditions` array (silently inert) or condition doesn't match the page you tested.
- `set-template-conditions` succeeded but template still doesn't render -> another template of the same type has a higher score (see `templates-conditions` scoring).
- `update-element-conditions` succeeded but the element still renders -> another OR group matches, or the page/template you tested is not the same context used by the condition.
- `update-element-interactions` succeeded but the old behavior still fires -> the interaction may be inherited from a global class. Check `effectiveInteractions`.
- Global variable rename done; `list-global-variables` shows the new name but elements still emit the old `var()` -> element settings reference the old name; do the reference-integrity sweep.

## Batch verification

For independent same-post element setting edits, prefer one batch write plus one readback over several update/read cycles. Keep destructive, uncertain, or user-sensitive changes isolated.

## Ability compatibility checklist

Use this when checking whether a site's Bricks abilities are installed, enabled, and returning safe results. Skip this for normal site-building work:

1. Start with `bricks-get-mcp-version`, `bricks-list-ability-status`, `mcp-adapter-discover-abilities`, and `mcp-adapter-get-ability-info` for every `bricks/*` ability.
2. Record enabled, disabled, default-enabled, direct-tool availability, dispatcher availability, annotations, and permission results. Builder-permission abilities are expected to be default-off unless the admin explicitly enables them.
3. Keep ordinary compatibility checks read-only. Invalid-input or mutation probes belong on an explicitly authorized disposable test site with known fixtures and recovery.
4. Assert credential redaction: license/API/code-execution/template-source secrets must never be returned as values. Credential status abilities may return configured/readable/writable booleans only.
5. In authorized mutation tests, track created fixture IDs and clean up only owned fixtures within the approved scope. Retain existing media and global resources.
6. Keep remote-template tests lightweight by using `list-remote-templates` default summary mode and a small `perPage` to choose a template. Use `bricks/insert-remote-template` for insertion. Use `mode: "full"` only when intentionally inspecting the complete remote payload for debugging.

## Related skills

- `bricks-browser-verify`: render-verification on the frontend.
- `bricks-dynamic-data`: `preview-dynamic-tag` pre-write check + `unknownTags` interpretation.
- `bricks-templates-conditions`: scoring rules for "which template won" investigations.
- `bricks-element-conditions`: OR/AND grouping and element render rules.
- `bricks-interactions`: inherited class rows, required action fields, and frontend interaction debugging.
- `bricks-headers-footers`: area-routing context for element-write verifies.


---

## Module: bricks-browser-verify

# Bricks: browser verification

Verify the requested page and state with the browser tools available in the client.
Builder preview and the public frontend can differ in authentication, template/query
context, CSS loading, caching and JavaScript initialization.

## Resolve the target and scope

- Use a supplied frontend URL or post ID. Otherwise use `bricks/find-post` with the
  user's title/slug and inspect status/access before choosing a result.
- `create-post` returns a permalink; `find-post` currently returns builder metadata
  without a public permalink. Resolve an existing page's URL from an available
  WordPress source or verified permalink structure. `builderUrl` is the edit route.
- No match does not prove nonexistence. Check lookup/status scope, then ask for the
  page ID or preview link if identity remains unresolved. Do not create a substitute.
- For a draft, use a valid authenticated preview. Do not publish or republish it to
  make verification easier.
- “Check and tell me what's wrong” authorizes inspection. “Fix these problems”
  authorizes repairs within that scope. Verification after a build can include
  corrections needed to finish that already-authorized build.

Without a browser, continue useful scoped reads of persisted elements, settings,
references and `render-elements` output. State that visual/interactive behavior is
unverified. Ask for screenshots only when they would resolve the remaining task.

## Inspect relevant states

| Request | Evidence |
|---|---|
| Match a design | Same viewport, content and font readiness; compare hierarchy, geometry, typography, images and intentional differences |
| Responsive review | Actual `list-breakpoints` keys, widths and direction; requested widths and relevant transition boundaries, including overflow |
| Regression check | Comparable before/after state; without a baseline report current defects rather than claiming no regressions |
| Menu, popup, tabs or accordion | Initial, opened/selected and closed states; keyboard activation, focus movement/return and relevant ARIA state |
| Query/filter/Load More | Expected records, empty state, changing selection and pagination; wait for the actual asynchronous result |
| Performance | Measure the symptom with available network/timing tools; use **bricks-performance** for diagnosis |

Use observed URLs/selectors and the actual browser API, not invented universal tool
names. Wait for meaningful readiness rather than a fixed delay. Do not submit forms,
place orders or activate external side effects merely to inspect layout; use an
authorized test flow when functional execution is part of the request.

Describe discrepancies with a target and location. A screenshot does not prove
native editability, working interactions or accessibility. Pixel tolerances depend
on the brief; no fixed five-pixel threshold proves completion.

## Repair within the requested scope

Read the affected element's settings, classes and responsive overrides; obtain the
specific runtime controls before changing it. Prefer a focused `update-element` or
same-post batch for local repairs. A mismatch in one card does not establish that its
shared class/global variable is wrong everywhere. Change a shared resource only
when the intended scope includes its other uses, retaining ownership/digest guards.

Inspect mutation readback for saved values, normalization and partial state; use a
focused read when those facts are missing. Revisit the affected states. Preserve
unrelated settings, elements and resources. Use **bricks-quality-gate** for broad or
uncertain writes.

## Diagnose missing or stale output

- Blank page: verify URL, draft access, response status and rendering errors.
- Builder UI: resolve the frontend/preview route.
- Old CSS: inspect loaded files/inline styles and persisted settings. Reload through
  supported browser controls. Regeneration/cache purging is a scoped repair, not an
  automatic read-only review step. Do not toggle global CSS loading as a shortcut.
- Different preview values: compare authentication, preview post, loop row,
  conditions and template selection.
- Repeated attempts without new evidence: stop the ineffective loop and pursue the
  relevant diagnostic. Do not blame a plugin/server merely because three tries failed.

Report checked URL/status, viewports/states, findings and verification limits. List
fixes separately from observations when fixes were authorized.


---

## Module: bricks-site-audit

# Bricks: site audit

A read-only data/configuration audit. Report actual coverage and access limits.
It does not by itself certify frontend rendering, accessibility, performance,
security or every third-party integration. Add those checks only when requested
or needed to investigate an observed finding; disclose unavailable evidence.

> **If a `bricks/*` ability is not available as a direct tool**: first check whether it is outside the fast path and call it through `mcp-adapter-execute-ability` with `ability_name: "bricks/<name>"`. If the dispatcher also rejects it, call `bricks-list-ability-status` to check whether a site admin disabled it under Bricks > AI.

## Checks

### 0. Complete Bricks document inventory

Call `bricks/checkout-site-repository` with `includeDesign: false`,
`includeDependencies: false`, and the maximum `perPage`. Follow every returned
`nextCursor` while `hasMore` is true. This is the authoritative bounded inventory of
editable Bricks pages, posts, custom-post-type documents, and templates for the
audit. Record every `postId`, `postType`, `file`, `status`, `documentDigest`, and
element count. If the
scan cannot complete, label the entire audit incomplete; do not silently report a
site-wide result.

Use this inventory for the revision and dynamic-data checks below. `list-templates`
still supplies template conditions and settings, but it is not a substitute for the
complete document inventory.

Process inventory pages incrementally. Extract findings from each full document and
discard its tree before reading the next one. If the complete scan exceeds available
tool or context limits, report the exact completed coverage and ask whether to
continue. Never label a partial scan complete.

### 1. Design-system rot

Call `bricks/audit-design-system` (scope: "all"). It returns severity-tagged issues covering orphan references, unused classes/variables/components, inactive theme styles, and palette fragmentation. Use the **bricks-audit-design-system** skill for how to triage and fix the output.

Manual follow-ups the ability doesn't cover:
- **Duplicate-intent classes.** `.button` + `.btn`, `.card` + `.cards`. Read `list-global-classes` and scan names.
- **Single-use components.** `usageCount === 1` from `get-design-context` with `includeUsage: true`: single use is not a defect; report only when it creates a concrete maintenance problem.

### 2. Template hygiene

Call `bricks/list-templates` and follow `page`/`perPage` while `hasMore` is true
before claiming the audit covers every template.

- **Potentially unused templates.** Check insertion, nesting, popup/menu and other references. No placement conditions alone does not mean unused.
- **Overlapping template conditions.** Compare priorities and representative matching URLs. Overlap can be intentional fallback/override behavior; identify actual shadowing before recommending removal.
- **Missing default templates.** No default single template means the theme's built-in template runs, which may not be what the user expects.

### 3. Revision bloat

For every post ID in the completed document inventory, count revisions via
`bricks/list-revisions`. Report counts and retention/storage context. A count alone does not establish bloat
or authorize cleanup; revisions may be intentional recovery history.

### 4. Dynamic data

Call `bricks/list-dynamic-data-tags` and follow `page`/`perPage` while `hasMore` is
true, then call `bricks/list-cms-sources`. Use relevant `postId` contexts when
provider tags vary by post type.

For every inventoried `postId`, call `bricks/get-page-elements` to read the complete
stored element tree, then scan every element setting for dynamic-tag
references. If any document cannot be read, disclose that target and mark this check
incomplete.

- **Missing providers referenced in content.** Posts using `{acf_foo}` on a site without ACF installed. Check by scanning element settings for `{*}` patterns that don't resolve against `list-dynamic-data-tags`.
- **Ambiguous modifiers.** Tags using `|upper` (JS pipe syntax) instead of `:upper` (Bricks syntax): broken.

### 5. Bricks abilities

Call `bricks/get-mcp-version`. Record `bricksVersion`, `bricksAbilitiesVersion`, `adapterVersion`, `wordpressVersion`, `abilitiesApiActive`, and `disabledAbilityCount`. If an expected `bricks/*` ability is missing as a direct tool, remember that many abilities are dispatcher-only; call `bricks/list-ability-status` before concluding the site is outdated or misconfigured.

## Report format

Return a structured audit:

```
## Design system
- Fragmentation: <count> issues
- Duplicate-intent classes: <list>
- Unused classes in the current authoritative scan: <list>
- ...

## Components
- Orphans: <list>
- Single-use (informational only): <list>

## Templates
- Overlapping conditions: <list>
- Unused: <list>

## Revisions
- Revision counts and retention concerns: <list>

## Dynamic data
- Missing providers: <list>
- Broken tag syntax: <list>

## Bricks abilities
- Abilities version: <bricksAbilitiesVersion>
- Missing expected abilities: <list or none>
```

## Never do

- A report-only audit does not authorize cleanup. When fixes are also requested, use the relevant scoped repair workflow and existing authorization; ask only about unresolved destructive choices.


---

## Module: bricks-maintenance

# Bricks: maintenance (via MCP)

Three admin-only housekeeping abilities mirror Bricks maintenance actions (`includes/abilities/maintenance.php`):

- **`bricks/regenerate-css-files`**: rebuild Bricks CSS files.
- **`bricks/list-orphaned-elements`**: scan for element rows whose `parent` id no longer exists in the same tree.
- **`bricks/cleanup-orphaned-elements`**: remove those orphan rows.

## `bricks/regenerate-css-files`

Input schema is empty:

```
bricks/regenerate-css-files
  -> { success: true, generatedFiles: [...], generatedFileCount: 42, cssLoading: "file" }
```

There is no `postIds` parameter. The ability runs the site-wide Bricks file-regeneration helper.

Use it after:

- Adding, removing, or reordering breakpoints.
- Bulk-editing theme styles, variables, or global classes outside normal builder saves.
- Migrating many element trees or template styles.
- Switching `cssLoading` to file mode and needing the generated files ready.

Normal builder saves regenerate the affected post CSS automatically. This ability is the bulk version.

## Orphaned elements

An orphan is an element whose `parent` id references another element that does not exist in the same meta tree.

The list operation is read-only:

```
bricks/list-orphaned-elements
  -> { totalOrphans: 47, totalPosts: 12, orphansByPostId: { "42": [...] } }
```

Cleanup supports a dry run and sweeps all detected orphans:

```
bricks/cleanup-orphaned-elements({ dryRun: true })
  -> { success: true, dryRun: true, totalCleaned: 47, postsCleaned: 12, message: "Would remove 47 orphaned elements across 12 posts." }

# After review and explicit approval:
bricks/cleanup-orphaned-elements({ dryRun: false })
  -> { success: true, totalCleaned: 47, postsCleaned: 12, message: "Removed 47 orphaned elements across 12 posts." }
```

**Destructive unless `dryRun: true`.** Always list first, run the dry run, review the affected posts, and obtain explicit approval before the committing call. There is no MCP parameter for limiting cleanup to a selected post list.

## What's excluded

Code-signature regeneration is available in the admin UI. It has no MCP ability. Regeneration can authorize previously quarantined code; require explicit authorization for that operation.

Academy reference: https://academy-preview.bricksbuilder.io/builder/features/code-signatures/

## Tool availability

> **If a `bricks/*` ability is not available as a direct tool**: first check whether it is outside the fast path and call it through `mcp-adapter-execute-ability` with `ability_name: "bricks/<name>"`. If the dispatcher also rejects it, call `bricks-list-ability-status` to check whether a site admin disabled it under Bricks > AI.


---

## Module: bricks-skills-update

# Bricks: update skills

Use this skill when the update check prints:

```txt
BRICKS_SKILLS_UPDATE_AVAILABLE <old> <new> <tag>
```

## Upgrade flow

1. Locate the installed Bricks skills root:

```bash
_BS_UPDATE_CHECK=""
for _CAND in "$HOME/.bricks/skills/bricks-skills/scripts/bricks-skills-update-check" "$PWD/scripts/bricks-skills-update-check" "$HOME/.claude/skills/bricks-skills/scripts/bricks-skills-update-check" "$HOME/.codex/skills/bricks-skills/scripts/bricks-skills-update-check"; do
  [ -f "$_CAND" ] && _BS_UPDATE_CHECK="$_CAND" && break
done
echo "$_BS_UPDATE_CHECK"
```

2. If no path is found, tell the user the update checker is not available in this install and point them to the README install section.

3. Force a fresh check:

```bash
sh "$_BS_UPDATE_CHECK" --force || true
```

If it reports `BRICKS_SKILLS_UPDATE_CHECK_FAILED`, the release service was unreachable. Keep the installed version and retry later; do not describe the result as up to date.

4. If it reports an available update, run the paired upgrade script. Pass the reported tag when available:

```bash
_BS_ROOT=$(cd "$(dirname "$_BS_UPDATE_CHECK")/.." && pwd)
sh "$_BS_ROOT/scripts/bricks-skills-upgrade" "<tag>"
```

If the update check did not include a tag, omit the argument. The script will discover the latest eligible published release. Stable installs exclude drafts and prereleases; an existing prerelease install can receive prereleases or stable releases. An explicitly requested prerelease tag remains supported.

5. If the upgrade script prints `BRICKS_SKILLS_NOT_GIT_INSTALL`, this install is managed by the host client rather than by a Bricks-owned git checkout. Tell the user to either:

- switch to the git install from the README, or
- update through their current client, for example `/plugin marketplace update bricks-skills` in Claude Code.

6. If the upgrade script prints `BRICKS_SKILLS_NO_RELEASE_FOUND`, no published GitHub Release is available yet. Tell the user to keep the current version.

If it prints `BRICKS_SKILLS_RELEASE_CHECK_FAILED`, the release service was unreachable or returned malformed data. No checkout was attempted; keep the current version and retry later.

If it prints `BRICKS_SKILLS_DOWNGRADE_REFUSED`, stop. The requested release is older than the installed version. Never add `--allow-downgrade` unless the user explicitly asks to install that older version after seeing the warning.

If it prints `BRICKS_SKILLS_PINNED`, the checkout already reported the release version but was still following another branch. The script successfully pinned it to the published release tag; treat this as a successful upgrade and reload the client if required.

7. If the upgrade succeeds and the user is using Claude Code plugin install from a local marketplace, tell them to run:

```txt
/plugin marketplace update bricks-skills
/reload-plugins
```

This refreshes Claude Code's installed plugin cache from the updated git checkout.

8. If the upgrade succeeds, read `CHANGELOG.md` and summarize the changes between the old and new versions in 3-5 bullets.

9. If the upgrade script prints `BRICKS_SKILLS_LOCAL_CHANGES_STASHED`, tell the user local changes were stashed in the skills repo and can be restored manually from that repo with `git stash pop`.

10. If the upgrade script prints `BRICKS_SKILLS_STASH_FAILED`, stop. Release metadata may already have been fetched and validated, but no checkout was attempted; inspect the reported git error before retrying.

11. If it prints `BRICKS_SKILLS_WORKTREE_NOT_CLEAN`, stop. The script refused to check out a release because changes remained after the stash attempt; release metadata/tags may already have been fetched. Inspect both `git status` and `git stash list` before retrying.
