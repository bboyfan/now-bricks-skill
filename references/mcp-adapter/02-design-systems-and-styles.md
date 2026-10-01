# Bricks Reference: 02 Design Systems And Styles



---

## Module: bricks-design-systems

# Bricks: design system authoring

> **If a `bricks/*` ability is not available as a direct tool**: first check whether it is outside the fast path and call it through `mcp-adapter-execute-ability` with `ability_name: "bricks/<name>"`. If the dispatcher also rejects it, call `bricks-list-ability-status` to check whether a site admin disabled it under Bricks > AI.

## Before you write anything

Call `bricks/get-design-context`. You are looking for three answers:

1. Does a matching resource already exist? Reuse it.
2. Is there a convention to follow? (kebab-case classes, `--space-{size}` variable naming, t-shirt or numeric scale: match it.)
3. Are there empty slots? (Palette exists but one color is missing, scale exists but one step is missing.) Fill the slot instead of creating a new parallel resource.

Also inspect `variableCategories`. If a category already has a `scale` config, use that category ID and prefix. Do not create `fs-*` variables when the typography category prefix is `text-`, and use the generator for changes to that scale. Exact local values can still be appropriate when the brief requires a value outside the scale; do not redefine the shared scale for one exception.

**A fresh Bricks install can have no saved design-system resources**: no custom theme style, classes, components, or saved variables. Bricks still exposes a built-in default color palette fallback in the builder and in `list-color-palettes`; do not tell users Bricks has no default palette. If it returns empty, create only the resources the task needs. Use **bricks-seed-design-system** when a full foundation is requested, not for every isolated edit.

## Current write preconditions

Global design writes no longer share one coarse version precondition. Immediately
before a focused write, call the matching focused read and pass its complete returned
ownership data unchanged:

- Global classes: single `create-global-class` has no resource ownership parameter;
  pass `expectedCategoryOwnership` only when assigning a category.
  `batch-create-global-classes` requires resource `expectedOwnership` and category
  ownership when categorized. Updates/deletes require the target row's
  `itemOwnership` as `expectedOwnership` plus `lockOwnership`.
- Variables/categories: both `variableOwnership` and `categoryOwnership`; category
  writes replace the complete category list and must preserve opaque fields.
- Palettes/colors: resource `ownership` for creates and target `itemOwnership` for
  updates/deletes. Chain each successful response's new `ownership` into sequential
  palette mutations.
- Theme styles: use the target `itemOwnership` for update/delete. Fetch the specific
  style when editing settings; a summary digest still covers the complete hidden row.
- Components: update/delete still require `expectedDesignSystemVersion` and now also
  the complete current `expectedComponentDigest`.

Deletion acknowledgement flags (`allowOrphans`) are mandatory where documented and
do not replace ownership. On any stale precondition, re-read and rebase; do not
manufacture ownership data from `get-design-context.version`.

## Global classes

- Names must be **unique across all classes**. The write aborts with `bricks_conflict_duplicate_global_class_name` if the name is taken. Read the existing one before retrying.
- Follow existing names and user-specified naming. On a new system without a convention, lowercase kebab-case such as `.button` or `.hero-text` is a useful default.
- Don't create modifier classes like `.button-red`: create a base class and a modifier class that sets only the color. Bricks supports class combinations natively.
- Class settings follow the same shape as element settings: call `bricks/render-elements` on a minimal element using the class to verify CSS output before committing settings programmatically.

## Global variables

- **Use the scale generator** (`bricks/generate-scale-variables`) for typography and spacing. Do not hand-author static spacing or type variables that match a configured scale prefix. The generator handles both typography and spacing using the category's scale configuration.
- When `get-design-context.variableCategories` includes spacing or typography categories with `scale`, pass the existing `categoryId` to `generate-scale-variables`. The generated names inherit the configured prefix, such as `space-` or `text-`.
- The scale generator resolves the html base font-size from three sources in order: **style manager value -> theme styles -> `10px` default**. If your scale outputs unexpected pixel values, that order is why.
- Variable names must be unique **at save time**, but **the builder UI does not validate this on create**: call `list-global-variables` first and guard against duplicates before writing. Conflict returns `bricks_conflict_duplicate_global_variable_name` on save.
- Variables are referenced in CSS as `var(--{name})`. Use the bare name (`space-m`, not `--space-m`) when creating: Bricks adds the `--` prefix when emitting CSS.
- When building a fluid scale, use the Bricks scale shape. `category.scale` has **four keys the builder cannot work without**, plus the math knobs:
  - `scaleScope`: **`"typography"` or `"spacing"`, nothing else.** Style Manager has one fixed tab per scope and lists a category only when `scale.scaleScope` matches the open tab. Omit it and the scale still shows a "scale" badge in the Variable Manager, still blocks hand-authored values for its prefix, and still gets cascade-deleted with the category — but **Style Manager > Typography/Spacing will be empty and the user can never edit or regenerate it**.
  - `scaleNames`: the ordered step names, e.g. `["2xs","xs","s","m","l","xl","2xl"]`. **This list is the scale's extent.** `regenerateVariables()` (fires when the html font size or min/max screen width changes, and on import) derives each variable's step from its *index in this list*. Omit it and the baseline index collapses to `0`, silently rewriting every variable at the wrong step.
  - `baseline`: must be one of the `scaleNames` entries. Default t-shirt baseline is `m`.
  - `prefix`: e.g. `text-`, `space-`.
  - Math knobs: `scaleType` (`tshirt` | `numeric` | `custom`), `minFontSize`, `maxFontSize`, `minScaleRatio` / `minScaleRatioSelect`, `maxScaleRatio` / `maxScaleRatioSelect`. Note: `*ScaleRatioSelect` wins unless it is the literal string `"custom"`, in which case `*ScaleRatio` is used.
- **Keep `scaleRange` and `scaleNames` in agreement.** The builder generates exactly one variable per `scaleNames` entry. `generate-scale-variables` instead takes a `scaleRange: { from, to }`, so it is possible to generate 11 variables against a 7-entry `scaleNames` — after which the Style Manager preview and `regenerateVariables()` both map variables onto the wrong steps. `scaleRange: { from: -2, to: 4 }` matches a 7-name list with baseline at index 2.
- `generate-scale-variables` with `save: false` returns candidate variables. Review names, values, and scope before saving; existing authorization to create the scale covers the matching persistence step.
- `generate-scale-variables` does not support saving with `save: true`. Persist the
  previewed rows with `set-global-variables`, using one fresh
  `list-global-variables` response's `variableOwnership` and `categoryOwnership`.
  If the category itself must change, first send the complete preserved category
  list to `set-global-variable-categories` with both current ownership values,
  then re-read before saving variables.
- Global variables are stored in a global option, not post revisions. Use `delete-global-variable` for cleanup of individual variables; it returns a `beforeDelete` snapshot.
- `set-global-variables` is an upsert, not a full replacement. Pass both current
  variable/category ownership values. `set-global-variable-categories` is a full
  category replacement and also requires both current values. `delete-global-variable`
  requires the row's `itemOwnership` plus literal `allowOrphans: true` after review.

## Color palettes

- Palettes are ordered arrays of colors. Each color has an id, `light` and optional
  `dark` value, plus a `raw` CSS-variable reference; individual colors do not have a
  separate display-name field.
- **Formats usually round-trip.** Light and dark shades preserve the parsed base format. Transparent shades are emitted as HSL/HSLA because the builder's transparent-shade path changes alpha directly.
- Before creating a new palette, check whether the existing primary palette has the color. Fragmented palettes are the most common design-system mess.
- **Generating shades.** Use `bricks/generate-color-shades` to produce light, dark, or transparent ramps from a base color. The ability uses Bricks' PHP color helper, ported from the builder Color Shades popup, so previews should match the builder math. Shade `raw` names become `var(--{base-variable}-{l|d|t}-{index})` only when the base color has a `raw` value such as `var(--brand-primary)` or when `baseVariable` is passed. Without that variable reference, each generated shade keeps the base raw value. Preview with `save: false`, then pass that exact preview's `saveOwnership` as `expectedOwnership` when saving; the save replaces existing shades of the same type, parent, and mode.
- A color ramp is two-step: create the base color with a `var(--name)` reference, then call `generate-color-shades` for `light` and `dark` (typically 4-5 steps each). `transparent` is optional for tint overlays.
- Palette/color deletes require target item ownership. Deleting named CSS-variable
  colors or palettes also requires `allowOrphans: true`; run the reference audit but
  treat its bounded evidence as non-exhaustive.

## Theme styles

- **Theme styles do not apply without conditions.** A style with an empty conditions array is ignored by the normal theme-style matcher. Always set `conditions` when creating: use `[{ main: "any" }]` for a site-wide base, or a more specific condition such as `postType`, `ids`, `terms`, or `archiveType`.
- By default, Bricks applies the highest-scoring matching theme style. More specific conditions beat broad ones: `postType` beats `any`, and exact `ids` beats `postType`.
- If the Theme styles loading method setting is enabled, Bricks loads every matching theme style in score order. In that mode, broad styles load earlier and more specific styles load later.
- The first theme style on a fresh site should almost always be `conditions: [{ main: "any" }]` so defaults actually render.
- Theme styles are stored in a global option, not post revisions. Use `delete-theme-style` for cleanup; it returns the removed style in `beforeDelete`.
- Updates and deletes require the target style's current `itemOwnership`. Fetch the
  exact style with `get-theme-styles({ style: id })` before changing settings.
- Deleting a style that has settings or conditions additionally requires
  `acknowledgeStyleRemoval: true` after reviewing the returned bounded impact
  evidence. This acknowledgement belongs to delete, not update.

## Components

- **Labels are unique across all components.** `bricks_conflict_duplicate_component_name` on collision.
- Components carry their own element tree. External references to global classes and CSS variables inside that tree are preserved: if a component uses `.button` and `var(--space-m)`, those references follow it wherever it's instanced.
- **Deleting a component with non-zero `usageCount` leaves orphan pointers.** The builder renders missing components as a placeholder. Either replace the usages first or explicitly accept the orphans with the user.
- Prefer `extract-component-from-elements` over copying element trees. The extraction rewrites ids cleanly and swaps the source subtree to a component instance in one write, with a revision snapshot.

See the **bricks-components** skill for slots, nested components, and property binding specifics.

## Workflows

### Add a color ramp to an existing palette
1. `list-color-palettes`, then `create-color` with its resource ownership and the intended `raw` variable reference.
2. Preview `generate-color-shades` with `save: false`; re-run with `save: true` and the preview's `saveOwnership` as `expectedOwnership`.
3. Repeat for `dark` (and optional `transparent` for tints).
4. `list-color-palettes` to verify.

### Add or replace a scale
1. Pick the naming first (t-shirt or numeric) and stick to it across typography + spacing.
2. `generate-scale-variables` with `save: false`: review output with user.
3. Once approved, pass the returned rows to ownership-guarded `set-global-variables`.
4. `list-global-variables` to verify.

For building a full design system from an empty site, use the **bricks-seed-design-system** skill. For cleanup of an existing one, use **bricks-audit-design-system**.

## Style Manager and state configuration

Use the live `get-style-manager` / `set-style-manager` contract for root font size,
fluid viewport bounds and default mode. The setter replaces the complete option:
read and preserve unrelated keys. Changing the rem basis or scale bounds is a
site-wide decision, not a local spacing fix.

For custom pseudo-class choices, use `list-pseudo-classes` / `set-pseudo-classes`
with current ownership. Preserve existing selectors; removal acknowledgement does
not prove existing styles are unused. Verify hover, focus and responsive states
where the changed resource is consumed. Existing framework naming/scales take
precedence over introducing a parallel scheme.


---

## Module: bricks-seed-design-system

# Bricks: seed a design system from scratch

Use this skill when `bricks/get-design-context` returns an empty or near-empty editable system and the user wants a real foundation before any page authoring. Fresh Bricks installs can have no saved theme style, custom scale, classes, or components. Bricks provides a default palette fallback. Create editable tokens before authoring pages.

When `bricks-commit-site-foundation` is available and the brief also includes a homepage and global header/footer, use that compound greenfield route instead of executing this manual sequence. This skill remains the fallback for a greenfield design-system-only task or older ability surfaces. For an existing or partial system, use **bricks-design-systems** to fill the requested gaps without reseeding.

> **If a `bricks/*` ability is not available as a direct tool**: first check whether it is outside the fast path and call it through `mcp-adapter-execute-ability` with `ability_name: "bricks/<name>"`. If the dispatcher also rejects it, call `bricks-list-ability-status` to check whether a site admin disabled it under Bricks > AI.

## Order of operations

For the requested foundation, create only needed resources in dependency order.
The names, palette size and scales below are defaults to adapt to the brief:

1. **Naming agreement** for colors and scales.
2. **Color palette**: `create-color-palette` (named container).
3. **Base hues into the palette**: `create-color` for each brand/neutral base.
4. **Color shades for each base**: `generate-color-shades` light + dark (+ transparent if needed).
5. **Root font-size basis**: create the minimal root theme style before generating either scale.
6. **Spacing scale** as fluid variables: `generate-scale-variables`.
7. **Typography scale** as fluid variables: `generate-scale-variables` again (same ability, different category).
8. **Complete the root theme style** so it references the persisted tokens.
9. **Base global classes**: `button`, `card`, `container`, `stack`: referencing the new variables.
10. **Site templates**: create header/footer templates when the brief includes a homepage or whole-site identity. Their roots must not repeat the automatic semantic landmarks.
11. **Components**: extract genuinely repeated authored structures such as cards or hero patterns after their real content exists; do not pre-build speculative components.

## Step 1: agree on naming with the user

Choose deliberately:

- **Scale naming:** t-shirt (`2xs`, `xs`, `s`, `m`, `l`, `xl`, `2xl`) or numeric. Pick one and use it for both spacing and typography: do not mix.
- **Color base names:** `brand-primary`, `brand-secondary`, `neutral`, `success`, `warning`, `danger` is a common set. Confirm the brand has a second accent color or if one primary is enough.
- **Shade count and direction:** default to 4 steps light + 4 steps dark per base color. Ask if the brand needs more nuance (5-6) or less (2-3).

When the user delegated the design direction or asked for autonomous implementation, choose coherent defaults and continue without a confirmation round trip. Ask only when the naming or scale choice would conflict with supplied brand requirements or materially change an existing system.

## Step 2: create the palette container

```
list-color-palettes -> capture ownership
create-color-palette (name: "Brand", expectedOwnership: ownership)
-> returns palette.id and new ownership
```

Capture the returned `palette.id` and `ownership`. Every subsequent palette/color write
uses this `paletteId` and the latest returned resource ownership.

## Step 3: seed the base colors

The `create-color` ability accepts: `paletteId`, `light` (required), `dark` (optional), `raw` (optional CSS variable reference like `var(--brand-primary)`), `parent`, `type`. There is **no** `name` field on individual colors: colors are identified by their CSS variable name (`raw`) and shown in the picker by value.

```
create-color (paletteId, light: "#2B6CB0", raw: "var(--brand-primary)", expectedOwnership: latestOwnership)
create-color (paletteId, light: "#ED64A6", raw: "var(--brand-secondary)", expectedOwnership: latestOwnership)
create-color (paletteId, light: "#1A202C", raw: "var(--neutral-900)", expectedOwnership: latestOwnership)
create-color (paletteId, light: "#F7FAFC", raw: "var(--neutral-100)", expectedOwnership: latestOwnership)
# ... etc for each base
```

After every call, replace `latestOwnership` with that response's `ownership`.
Do not fan these writes out in parallel: each append changes the palette graph.

The `raw` value matters: the shade generator emits `var(--{baseName}-{l|d|t}-{n})` derived from the variable name in `raw`. If you skip `raw` or `baseVariable`, generated shades keep the same raw base value instead of creating predictable CSS variable references.

## Step 4: generate shades for each base

For each base color (skip pure neutrals if you're using explicit `neutral-100` through `neutral-900`):

```
lightPreview = generate-color-shades (paletteId, colorId, shadeType: "light", steps: 4, save: false)
generate-color-shades (paletteId, colorId, shadeType: "light", steps: 4, save: true, expectedOwnership: lightPreview.saveOwnership)
darkPreview = generate-color-shades (paletteId, colorId, shadeType: "dark", steps: 4, save: false)
generate-color-shades (paletteId, colorId, shadeType: "dark", steps: 4, save: true, expectedOwnership: darkPreview.saveOwnership)
```

Pass both `shadeType` and `steps`.

Result: a ramp like `brand-primary-l-1..l-4` (lighter than base) and `brand-primary-d-1..d-4` (darker).

Transparent shades are opt-in: use them when you need translucent overlays (e.g. backdrop scrims). Format is `brand-primary-t-1..t-N` with decreasing alpha.

## Step 5: establish the root font-size basis

Both spacing and typography scale generation resolve rem values against the current
HTML font size. Determine the intended root size from the brief or existing site and
default to `100%` when neither specifies one. Create a minimal root theme style before
either scale and capture its ID. Set `<root-font-size>` below to that value and use
the same basis for both scales.

```
create-theme-style (
  label: "Root",
  conditions: [{ main: "any" }],
  settings: { typography: { typographyHtml: "<root-font-size>" } }
)
```

Re-read the theme style and design context before continuing.

## Step 6: generate the spacing scale

```
generate-scale-variables({
  category: {
    id: "preview-space",
    name: "Spacing",
    scale: {
      scaleScope: "spacing",
      scaleType: "tshirt",
      scaleNames: ["2xs", "xs", "s", "m", "l", "xl", "2xl", "3xl"],
      prefix: "space-",
      minFontSize: 16,
      minScaleRatio: 1.25,
      minScaleRatioSelect: 1.25,
      maxFontSize: 20,
      maxScaleRatio: 1.333,
      maxScaleRatioSelect: 1.333,
      baseline: "m"
    }
  },
  scaleRange: { from: -3, to: 4 },
  save: false
})
```

Output names use Bricks t-shirt steps: `--space-2xs`, `--space-xs`, `--space-s`, `--space-m` (baseline), `--space-l`, `--space-xl`, `--space-2xl`, `--space-3xl`.

**`scaleNames` must list exactly the steps `scaleRange` produces, in order** — eight names here for `from: -3, to: 4`. The builder generates one variable per `scaleNames` entry, and `regenerateVariables()` reads a variable's step from its index in that list. A short or misaligned list silently rewrites every value at the wrong step the next time the html font size or screen widths change.

Review with the user and adjust the ratios. `generate-scale-variables` rejects
`save: true`; preview with `save: false`, then persist the returned rows as described
below. First create or update the complete category list with
`set-global-variable-categories`, passing the
latest `categoryOwnership` as `expectedOwnership` and the same read's
`variableOwnership` as `expectedVariableOwnership`. Then preview by saved
`categoryId` and persist the returned generated rows through `set-global-variables`
with fresh `expectedVariableOwnership` and `expectedCategoryOwnership`. Preserve all
existing categories in the category replacement. Do not hand-author static
`space-*` variables.

## Step 7: generate the typography scale

Use `generate-scale-variables` with a typography category.

```
generate-scale-variables({
  category: {
    id: "preview-text",
    name: "Typography",
    scale: {
      scaleScope: "typography",
      scaleType: "tshirt",
      scaleNames: ["xs", "s", "m", "l", "xl", "2xl", "3xl", "4xl"],
      prefix: "text-",
      minFontSize: 16,
      minScaleRatio: 1.2,
      minScaleRatioSelect: 1.2,
      maxFontSize: 20,
      maxScaleRatio: 1.333,
      maxScaleRatioSelect: 1.333,
      baseline: "m"
    }
  },
  scaleRange: { from: -2, to: 5 },
  save: false
})
```

Output names use the same t-shirt naming model: `--text-xs`, `--text-s`, `--text-m`, `--text-l`, `--text-xl`, `--text-2xl`, `--text-3xl`, `--text-4xl`.

The generator uses the same root basis established in Step 5. If that basis changed,
stop and regenerate both spacing and typography scales from a fresh read.

Do not create static `text-*`, `fs-*`, or matching typography-prefix variables by hand when the category has a scale config.

As with spacing, `generate-scale-variables` is preview-only. Persist its exact rows
through ownership-guarded `set-global-variables`; do not retry `save: true`.

## Step 8: complete the root theme style

```
update-theme-style (
  id: <root-theme-style-id>,
  expectedOwnership: <fresh root theme-style itemOwnership>,
  conditions: [{ main: "any" }],
  settings: {
    typography: {
      typographyHtml: "<root-font-size>",
      typographyBody: {
        "font-family": "...",
        "color": "var(--neutral-900)",
        "font-size": "var(--text-m)"
      },
      typographyHeadings: {
        "font-family": "...",
        "color": "var(--neutral-900)"
      },
      typographyHeadingH1: { "font-size": "var(--text-4xl)" },
      typographyHeadingH2: { "font-size": "var(--text-3xl)" }
    }
  }
)
```

**Critical:** `conditions: [{ main: "any" }]`. Use `any`, not `entireWebsite`. A theme style with no conditions is silently ignored.

If the user wants per-CPT overrides later, create a second theme style with `conditions: [{ main: "postType", postType: ["product"] }]`. By default, Bricks uses the highest-scoring matching theme style, so this post-type style beats the broader `any` style on product pages.

## Step 9: seed base classes

After tokens are in place, create the minimum viable class library:

- `.container`: max-width + horizontal padding using `--space-*`.
- `.stack`: vertical rhythm using `--space-*` gap.
- `.cluster`: horizontal wrap using `--space-*` gap.
- `.button`: padding, background `var(--brand-primary)`, hover `var(--brand-primary-d-1)`.
- `.card`: padding, background, border-radius, subtle shadow.

Don't pre-create modifier classes (`.button-lg`, `.button-danger`). Add them when a page needs them.

## Verification

Use authoritative mutation readback when it contains the complete affected resource.
Otherwise run the matching read below. Render only the representative token behavior
needed to verify the system:

1. After palette/colors/shades: `list-color-palettes` (filter to the new paletteId).
2. After scales: `list-global-variables`: confirm category present and step count matches.
3. After theme style: `get-theme-styles` with the returned id: confirm `conditions` and `settings` round-trip.
4. Apply a generated spacing variable to a representative element using its supported padding control. Verify the generated `clamp()` rule and computed spacing at narrow and wide viewports.
5. For the palette, render an element with `background: var(--brand-primary)`: confirm the emitted CSS references the variable, not a hardcoded hex.

If the read doesn't match what you wrote, **stop** and surface the discrepancy to the user: don't keep building on a broken foundation.

## When the user already has a partial system

Use this only for **fully fresh** installs. If `get-design-context` returns partial state (e.g. two colors and a half-built scale), do not wipe and re-seed. Instead:

- Find the missing slots (see **bricks-design-systems** skill's "empty slots" rule).
- Fill them with names matching the existing convention.
- If the existing system is genuinely broken (inconsistent naming, fragmented palettes), propose a cleanup plan to the user first: never silently restructure.

## Related abilities

- `create-color-palette`, `update-color-palette` (rename), `delete-color-palette`: palette CRUD.
- `create-color`, `update-color`, `delete-color`: single color CRUD.
- `generate-color-shades`: auto-derive light/dark/transparent ramps.
- `set-global-variables` (ownership-guarded upsert) and
  `delete-global-variable`: variable CRUD; category replacement is separate.
- `generate-scale-variables`: fluid scale generator.
- `list-theme-styles`, `get-theme-styles`, `create-theme-style`, `update-theme-style`: theme style CRUD.
- `list-global-classes`, `create-global-class`, `update-global-class`: class CRUD.


---

## Module: bricks-audit-design-system

# Bricks: audit & clean the design system

Use this skill when the user says things like "review my design system", "clean up unused classes", "why are my colors inconsistent", or "audit my design tokens". For a generic whole-site audit, use **bricks-site-audit** instead. The entry point here is `bricks/audit-design-system`: read-only, safe to run without approval.

> **If a `bricks/*` ability is not available as a direct tool**: first check whether it is outside the fast path and call it through `mcp-adapter-execute-ability` with `ability_name: "bricks/<name>"`. If the dispatcher also rejects it, call `bricks-list-ability-status` to check whether a site admin disabled it under Bricks > AI.

## Run the audit

```
bricks/audit-design-system (scope: "all")
```

Scope options:
- `all`: everything (default; may take a few seconds on large sites)
- `orphans`: **errors** only: elements referencing classes/variables/components that no longer exist
- `unused`: resources with no references found in the scan; check coverage before calling them unused
- `theme-styles`: theme styles with no conditions (silently ignored)
- `palettes`: duplicate `raw` values + palette entries whose `raw` value does not contain a CSS variable reference

For a fast check without scanning posts: `skipPostScan: true` (skips unused + orphans, keeps theme-styles + palettes).

## How to read the output

Every issue has:
- `severity`: `error`, `warning`, or `info`
- `category`: `orphans`, `unused`, `theme-styles`, or `palettes`
- `resourceType` + `resourceId`: what to fix
- `message`: what's wrong
- `suggestion`: recommended action (not auto-applied)

**Present issues grouped by severity.** Explain rendering errors first, then configuration warnings and cleanup suggestions.

## How to decide what to fix

When any fix requires creating or renaming a design resource, apply the rules from the **bricks-design-systems** skill (naming conventions, uniqueness constraints, shade generation).

### Errors (report; repair when within the requested scope)
- **Orphan class reference**: an element is pointing at a class id that doesn't exist. Either the class was deleted without cleaning up references, or the data was imported broken. Fix path: either recreate the class, or locate and strip the stale id from `_cssGlobalClasses` on affected elements.
- **Orphan variable reference**: CSS text says `var(--foo)` but `--foo` isn't defined anywhere. The rule will fall back to nothing (transparent, inherit, etc.) and render wrong. Fix path: create the variable, or rewrite the reference.
- **Orphan component reference**: `"cid":"..."` points at a component that no longer exists. The builder shows a missing-component placeholder. Fix path: recreate the component with the original id (rare, usually requires a backup) or use `update-element` / `set-page-elements` to remove the stale instance.

### Warnings (determine whether configuration is intentional)
- **Theme style with no conditions**: the style is inert in the normal theme-style matcher. Either the user meant to apply it site-wide (`conditions: [{ main: "any" }]`) or they abandoned it mid-config. Ask which.

### Infos (summarize, fix only when user asks)
- **Unused global class**: may be intentional (staging a class for upcoming work). Do not delete solely from this finding. Review reference coverage and the requested cleanup scope.
- **Unused global variable**: same.
- **Unused component**: same.
- **Palette color without a variable reference in `raw`**: the color can still work, but it is only referenced by its stored value. If the site uses tokenized colors, set `raw` to a CSS variable reference such as `var(--brand-primary)`. Leave literal values alone when that is intentional.
- **Duplicate color across palettes**: the same hex appears N times. Offer to consolidate.

## Fix workflow

For a review request, report findings and proposed repairs without mutating. For
an authorized cleanup/fix request, apply a coherent batch within that scope; do not
ask for approval again for every item. Clarify only unresolved intent, affected
resources or destructive choices not covered by the request.

1. Read the affected records and inspect scan bounds, pagination and permissions.
   Zero discovered uses is not proof of no external CSS, plugin or inaccessible-page
   references. A single-use component or duplicate color can be intentional.
2. Choose the smallest repair; preserve opaque fields, existing IDs and unrelated
   references. Use fresh resource-specific ownership/digests and required deletion
   acknowledgements. Back up supported global resources before destructive cleanup.
3. Apply sequentially where ownership changes; on conflicts re-read/rebase the
   still-authorized edit. Do not delete edited or unowned resources by name alone.
4. Re-run relevant checks and report the actual changes, remaining findings and
   coverage limits. Use **bricks-quality-gate** for broad/shared-resource effects.

## Things the audit misses (and you should mention)

- **Naming inconsistency**: mix of `camelCase` / `kebab-case` / `snake_case` across classes or variables. The audit does not check naming conventions. Scan `list-global-classes` / `list-global-variables` manually if the user asks.
- **Semantic overlap**: `.btn` and `.button` are both used, defining similar styles. The audit can't infer intent. Suggest merging if you see it.
- **Scale gaps**: spacing or typography scale missing middle steps. Read `list-global-variables` and check for numeric/t-shirt continuity.
- **Unused palette entries**: palette colors not referenced by any class, variable, or element setting. The audit doesn't scan for this; add it to the manual pass if the palette is large.

## When not to run this

- Right after a fresh install (`get-design-context` is empty): there's nothing to audit. Use the **bricks-seed-design-system** skill instead.
- Mid-edit, when the user is actively working on design tokens: the audit will flag in-progress work as "unused." Wait until a stable point.


---

## Module: bricks-naming-conventions

# Bricks: naming conventions

Follow user-specified names and the site’s existing naming convention.

> **If a `bricks/*` ability is not available as a direct tool**: first check whether it is outside the fast path and call it through `mcp-adapter-execute-ability` with `ability_name: "bricks/<name>"`. If the dispatcher also rejects it, call `bricks-list-ability-status` to check whether a site admin disabled it under Bricks > AI.

## Detection

Call `bricks/get-design-context`. Scan the returned names for:

**Global classes**
- Case: `lowercase` / `kebab-case` / `PascalCase` / `camelCase`. Most Bricks sites use kebab-case.
- Prefix convention: `is-*`, `has-*`, `u-*` (utilities), `c-*` (components), no prefix at all.
- Modifier separator: `.button--primary` (BEM) / `.button-primary` (flat) / `.button.primary` (class combos: Bricks supports these natively).

**Global variables**
- Hyphen convention: `--space-md` vs `--spacing-md` vs `--spacer-4`.
- Scale naming: t-shirt (`xs sm md lg xl`), numeric (`1 2 3 4 5 6`), custom.
- Baseline: `md` (t-shirt), `4` (numeric), something else.
- Color naming: `--color-primary-500`, `--brand-primary`, `--c-primary`. All valid; pick the one already on the site.

**Components**
- Title case (`Hero Section`) vs kebab-case (`hero-section`) vs space-separated lowercase (`hero section`).
- Property naming: `label` vs `title` vs `heading`. Inside the component, property ids usually match the builder's auto-generated pattern.

**Templates**
- `Header`, `Footer`, `Single Post`, `Archive: Products`. Em-dash or hyphen? Capitalization? Match what exists.

## Rules

1. **Follow the existing convention by default.** If the user explicitly specifies an exact name such as `BrandHero`, preserve it. Flag consequential naming conflicts.

2. **Preserve existing names.** When conventions are mixed, follow the relevant resource group. Ask when the choice affects shared resources.

3. **One pattern, one scale.** If a t-shirt spacing scale already exists, don't add a numeric one alongside. Extend the t-shirt scale (`2xs`, `3xl`) if needed.

4. **Use readable component labels**, such as `Hero: Dark Variant`, unless the user supplied an exact name.

5. **Read nearby resource names** when the convention is unclear.

## Red flags

- Resolve conflicting case or prefix conventions before extending shared resources.
- Adding `--color-*` variables to a site that already uses `--brand-*`: use the existing prefix.
- Creating a `.btn` class on a site that already has `.button`: that's the same resource spelled differently; reuse, don't add.


---

## Module: bricks-breakpoints

# Bricks: breakpoints (via MCP)

Bricks ships default breakpoints (`desktop`, `tablet_portrait`, `mobile_landscape`, `mobile_portrait`) and lets you add custom ones. The full set lives in the `bricks_breakpoints` option and drives both the builder device-switcher and the generated responsive CSS.

Two tools:

1. **`bricks/list-breakpoints`**: returns `{ customEnabled, isMobileFirst, baseKey, baseWidth, breakpoints, defaults, breakpointOwnership, globalSettingsOwnership }`. `baseKey` / `baseWidth` identify the base row; `isMobileFirst` is derived by core Bricks from the stored breakpoint list before it sorts the list for output.
2. **`bricks/set-breakpoints`**: write the full list. Always pass the latest `breakpointOwnership` as `expectedOwnership`. If `customEnabled` is present, also pass the same read's `globalSettingsOwnership` as `expectedGlobalSettingsOwnership`. A replacement that removes or renames a key additionally requires `allowRemovedBreakpoints: true` after reviewing the returned bounded usage evidence.

## Shape

Each breakpoint is an object:

```
{
  key: "tablet_portrait",   // machine key, unique: /^[a-z0-9_-]+$/i
  label: "Tablet portrait", // shown in builder, required non-empty
  width: 991,               // integer >= 0: see paradigm below
  icon: "bricks-icon-device-tablet", // optional
  base: true                // omit or false on all other rows
}
```

Exactly one row must have `base: true`. The base is the fallback: every other breakpoint is a media query relative to it. `base` is a boolean on the row itself, not a `type` enum.

## Mobile-first vs desktop-first

Bricks derives the paradigm from **which row is the base**, not from a separate setting:

- **Desktop-first (Bricks default):** the base row is not the last row in the saved breakpoint list. Base styles apply everywhere; narrower breakpoints layer on as `@media (max-width: Npx)`.
- **Mobile-first:** the base row is the last row in the saved breakpoint list. Base styles apply from `0` upward; wider breakpoints layer on as `@media (min-width: Npx)`.

`list-breakpoints` exposes the derived result as `isMobileFirst: boolean`. There is no `cssBreakpointType` global setting. If you change the base row, call `list-breakpoints` after saving and verify `isMobileFirst` before continuing.

**Caution:** use `bricks/set-breakpoints` for reading, restoring, adding, removing, or width changes when you can verify the result immediately. For a desktop-first to mobile-first paradigm switch, stop unless `list-breakpoints` confirms `isMobileFirst: true` after the write. Core Bricks derives the paradigm from stored base-row position, and the ability writer also sorts the replacement list before saving (`includes/abilities/breakpoints.php:242-249`), so the readback is the contract.

**A master "use custom breakpoints" toggle (`customBreakpoints`) in `bricks_global_settings` controls whether your custom set is applied at all: Bricks falls back to the built-in defaults when it's off.** That key is not in the `bricks/set-global-settings` registry. Use `bricks/set-breakpoints` with `customEnabled: true` or `customEnabled: false`, then verify with `list-breakpoints.customEnabled`.

The breakpoint and global-settings envelopes are separate authorities. Never derive
either from `designSystemVersion`, and never reuse one in place of the other. Re-read
after any stale-ownership response instead of retrying the same write.

**Switching paradigm rewrites every rendered stylesheet.** Regenerate CSS files (`bricks/regenerate-css-files`) after the write when `cssLoading=file`: otherwise cached files lag the new media-query semantics. `set-breakpoints` returns a `note` field prompting the regen when the flag is set.

## Ordering

`set-breakpoints` sorts rows by width before saving. Submit a clear complete list, then read back with `list-breakpoints` and use the returned order and `isMobileFirst` value as truth for generated CSS.

## Removing a breakpoint

- Any element with settings keyed to that breakpoint keeps the data (Bricks never deletes element settings on breakpoint removal: it becomes orphaned).
- Regenerate CSS after removal to drop the now-unused media queries from emitted files.

## Tool availability

> **If a `bricks/*` ability is not available as a direct tool**: first check whether it is outside the fast path and call it through `mcp-adapter-execute-ability` with `ability_name: "bricks/<name>"`. If the dispatcher also rejects it, call `bricks-list-ability-status` to check whether a site admin disabled it under Bricks > AI.

## Typical flow: add a custom "large-desktop" breakpoint without changing paradigm

```
bricks/list-breakpoints
  -> current: [desktop (base, 1279), tablet_portrait (991), mobile_landscape (767), mobile_portrait (478)]

bricks/set-breakpoints
  customEnabled: true
  expectedOwnership: <list-breakpoints.breakpointOwnership>
  expectedGlobalSettingsOwnership: <list-breakpoints.globalSettingsOwnership>
  breakpoints:
    - { key: "mobile_portrait",   label: "Mobile portrait",   width: 478 }
    - { key: "mobile_landscape",  label: "Mobile landscape",  width: 767 }
    - { key: "tablet_portrait",   label: "Tablet portrait",   width: 991 }
    - { key: "desktop",           label: "Desktop",           width: 1279, base: true }
    - { key: "large_desktop",     label: "Large desktop",     width: 1600 }

bricks/regenerate-css-files
```

The explicit `base: true` stays on `desktop`, so this remains desktop-first. Verify
the returned `isMobileFirst: false`; moving the base to the smallest row would be a
separate site-wide paradigm change.

## Don't

- Don't submit an array without exactly one `base: true`: the write is rejected with `bricks_invalid_param` (param `breakpoints`).
- Don't reuse an existing `key` for a new breakpoint: Bricks stores per-breakpoint settings under that key and you'll silently merge with the old data.
- Don't skip the CSS regen after reordering or removing a breakpoint.
- Don't remove or rename a key without reviewing the conflict's usage evidence and
  explicitly passing `allowRemovedBreakpoints: true` when the change is intended.


---

## Module: bricks-custom-fonts

# Bricks: custom fonts (via MCP)

Custom fonts in Bricks are three things bound together:

1. A `bricks_fonts` custom post type: one post per **font family**.
2. A `fontFaces` postmeta map on that family. Keys are weight/style strings such as `400`, `700`, or `400italic`.
3. Uploaded WP media attachments that store the actual font files.

The MCP abilities mirror that model (`includes/abilities/fonts.php`).

## Abilities

- **`bricks/list-custom-fonts`**: returns `{ fonts, total, page, perPage }`. Each row includes `id`, `family`, and `faceCount`.
- **`bricks/get-custom-font`**: body `{ fontId }`. Returns `{ font: { id, family, fontFaces } }`.
- **`bricks/create-custom-font`**: body `{ family }`. Creates the `bricks_fonts` post and returns `{ font }`. There is no `displayName` parameter.
- **`bricks/upload-custom-font-file`**: body `{ filename, content }`, where `content` is base64. Returns `{ attachmentId, url, format, bytes }`.
- **`bricks/update-custom-font`**: body `{ fontId, family?, fontFaces? }`. If `fontFaces` is provided, it replaces the whole font-face map.
- **`bricks/delete-custom-font`**: body `{ fontId }`. Deletes the font family post. It does not delete uploaded media attachments.

## Upload flow

Do not use `bricks/upload-media` for font files. The current font flow is:

```
bricks/upload-custom-font-file
  filename: "inter-regular.woff2"
  content: "<base64 bytes>"
  -> { attachmentId: 500, url: ".../inter-regular.woff2", format: "woff2", bytes: 42112 }

bricks/create-custom-font { family: "Inter" }
  -> { font: { id: 42, family: "Inter", fontFaces: {} } }

bricks/update-custom-font
  fontId: 42
  fontFaces:
    "400":
      - { woff2: 500 }
```

The upload ability stores the font file as a WP attachment. `update-custom-font` references those attachment IDs inside `fontFaces`.

**Enforced at upload time:**

- Extension allow-list: `woff2`, `woff`, `ttf`, `otf`, `eot`.
- MIME sniff via `wp_check_filetype_and_ext()`: extension alone is not trusted.
- Size limit: 8 MB decoded by default, filterable through `bricks/abilities/fonts/max_bytes`.

## `fontFaces` shape

```json
{
  "400": { "woff2": 500, "woff": 501 },
  "400italic": [
    { "woff2": 502, "unicode-range": "U+0000-00FF" },
    { "woff2": 503, "unicode-range": "U+0100-017F" }
  ],
  "700": { "woff2": 504 }
}
```

Rules:

- Keys are non-empty weight/style strings. Use `400`, `700`, `400italic`, etc.
- Each value may be one subset object or an array of subset objects. `validate_font_faces()` accepts both and normalizes a single subset back to an object (`includes/abilities/fonts.php:528`, `includes/abilities/fonts.php:571`).
- Format keys must be one of `woff2`, `woff`, `ttf`, `otf`, `eot`.
- Values are positive WP attachment IDs created by `bricks/upload-custom-font-file`.
- `unicode-range` is optional and lets multiple subsets share one weight/style variant.

## CSS output

Bricks generates `@font-face` rules from the `fontFaces` map and attachment URLs:

```css
@font-face {
  font-family: "Inter";
  font-weight: 400;
  font-style: normal;
  font-display: swap;
  src: url("/wp-content/uploads/.../inter-regular.woff2") format("woff2");
}
```

The family is then selectable in Bricks typography controls.

Frontend output currently emits `font-display: swap` in `includes/custom-fonts.php:304`. Bricks settings abilities do not expose a verified `customFontsDisplay` key, so do not claim font-display can be changed through MCP unless `bricks/list-settings-schema` shows that key on the target site.

## Tool availability

> **If a `bricks/*` ability is not available as a direct tool**: first check whether it is outside the fast path and call it through `mcp-adapter-execute-ability` with `ability_name: "bricks/<name>"`. If the dispatcher also rejects it, call `bricks-list-ability-status` to check whether a site admin disabled it under Bricks > AI.

## Adobe / Google fonts

Adobe Fonts uses the admin setting `adobeFontsProjectId`; Google Fonts can be disabled in the admin UI through `disableGoogleFonts`. Do not assume either is writable through MCP. Inspect `bricks/list-settings-schema` on the target site before changing provider settings.

## Don't

- Don't pass a URL or filesystem path as a face file. Upload base64 bytes with `bricks/upload-custom-font-file`.
- Don't send `displayName`, `id`, or `faces`; current schemas use `family`, `fontId`, and `fontFaces`.
- Don't update one face by sending a partial `fontFaces` object unless you intend to replace the whole map.
- Don't delete a family that's referenced by live typography controls without replacing the reference.


---

## Module: bricks-settings

# Bricks: global settings (via MCP)

Bricks global settings (the `bricks_global_settings` option: hundreds of keys backing the admin Settings pages) are exposed to MCP through an **allow-list registry**. Discover writable keys, read their current values, then send a partial update.

Three tools. Use them in order:

1. **`bricks/list-settings-schema`**: read-only discovery. Returns every key the MCP will accept, with type, category, description, and validation hints. Call this first if you don't already know which key to write.
2. **`bricks/get-global-settings`**: read current values for keys in the registry. Never returns excluded credential values or code-execution toggles.
3. **`bricks/set-global-settings`**: partial-merge write. Takes `{ settings: { key: value, ... } }`. Other keys untouched.

## Partial-merge semantics

`set-global-settings` updates the keys you send and leaves everything else alone. Batch requested top-level changes in one call.

```
bricks/set-global-settings
  settings:
    postTypes: ["page","post","product","bricks_template"]
    cssLoading: "file"
```

Result: `postTypes` and `cssLoading` updated; every other setting (maintenance mode, disable emojis, etc.) retained exactly as it was.

## What the registry contains

Dozens of keys across categories. Current examples from `includes/abilities/settings.php`:

- **general**: `postTypes`, `wp_to_bricks`, `bricks_to_wp`, `disableClassManager`, `disableVariablesManager`, `disableOpenGraph`, `disableSeo`, `elementAttsAsNeeded`, `customImageSizes`, `disableSkipLinks`, `smoothScroll`, `deleteBricksData`, `searchResultsQueryBricksData`, `themeStylesLoadingMethod`, `duplicateContent`, `enableQueryFilters`
- **templates/forms**: `publicTemplates`, `myTemplatesAccess`, `myTemplatesWhitelist`, `remoteTemplates`, `saveFormSubmissions`
- **builder/MCP**: `builderAutosaveInterval`, `builderQueryMaxResults`, `builderLocale`, `abilitiesApi`
- **performance toggles**: `cssLoading`, `disableBricksCascadeLayer`, `disableEmojis`, `disableJqueryMigrate`
- **bricks-maintenance**: `maintenanceMode`, `maintenanceTemplate`, `bypassMaintenanceUserRoles`, `maintenanceExcludedPosts`
- **password protection**: `passwordProtectionEnabled`

Call `list-settings-schema` to see the current full list: it's auto-generated from the registry and stays in sync with Bricks updates.

## Excluded settings

These are blocked at the registry level (see `Settings::EXCLUDED_SETTING_KEYS`). Attempting `set-global-settings` with any of these returns `bricks_setting_excluded`. The literal list:

- `licenseKey`: plus any key starting with `license`, `apiKey`, or `apiSecretKey`
- `instagramAccessToken`
- `myTemplatesPassword`
- `remoteTemplatesPassword`
- `remoteTemplates[].password`
- `executeCodeEnabled`: master toggle for the custom-PHP execution path
- `executeCodeCapabilities`: role matrix controlling who can execute code
- `codeSignaturesLocked`: prevents tampering with the signature-verification defense
- `codeExecutionMode`
- `htmlExecutionMode`

Use an authorized admin/configuration workflow for excluded settings. Signature regeneration also has no MCP ability; see [bricks-maintenance](../bricks-maintenance/SKILL.md).

`remoteTemplates` can manage saved source URLs and optional names only. Passwords are preserved if already configured, but never returned or written. New MCP-written remote template URLs must be public `http`/`https` URLs: private, loopback, link-local, unsafe-port, credentialed, or non-resolving hosts are rejected because those URLs are later used for outbound template-library fetches.

## Credential status

Use `bricks-list-credential-status` when you only need to know whether a credential exists. It returns rows with `configured`, `readable: false`, and `writable: false`; it never returns the stored value or a masked fragment.

Good uses:

- Map work: check `apiKeyGoogleMaps.configured` before building a Google Maps experience.
- Form spam protection: check the matching site key and secret key before enabling reCAPTCHA, hCaptcha, or Turnstile.
- Integrations: check Mailchimp, SendGrid, Instagram, and template-library credentials before assuming the integration can run.

Do not ask for the raw value. If a required credential is missing, tell the user which setting to add in the Bricks admin UI.

## Unknown-key handling

`set-global-settings { settings: { fooBarBaz: 1 } }` where `fooBarBaz` isn't in the registry returns `bricks_setting_unknown`.

For these settings, use the dedicated abilities:

- Breakpoints -> `bricks/list-breakpoints`, then `bricks/set-breakpoints` with its
  `breakpointOwnership`; changing `customEnabled` also requires the returned
  `globalSettingsOwnership`
- Style manager -> `bricks/set-style-manager`
- Pseudo-classes -> `bricks/list-pseudo-classes`, then `bricks/set-pseudo-classes`
  with its `ownership` as `expectedOwnership`; removals require
  `allowRemovedPseudoClasses: true` after reviewing usage evidence
- Element enable/disable -> element-manager abilities
- Icon libraries -> icons abilities
- Builder role access -> `bricks/list-builder-permissions`, `bricks/upsert-builder-capability`, `bricks/set-builder-role-access`

The registry is for keys that don't fit into one of those domains.

## Tool availability

> **If a `bricks/*` ability is not available as a direct tool**: first check whether it is outside the fast path and call it through `mcp-adapter-execute-ability` with `ability_name: "bricks/<name>"`. If the dispatcher also rejects it, call `bricks-list-ability-status` to check whether a site admin disabled it under Bricks > AI.

## Typical flow

```
bricks/list-settings-schema
  -> scan output for "maintenance" category
  -> find maintenanceMode, maintenanceTemplate, bypassMaintenanceUserRoles, maintenanceExcludedPosts

bricks/get-global-settings (optional: check current values)

bricks/set-global-settings
  settings:
    maintenanceMode: "maintenance"
    maintenanceTemplate: 123
    bypassMaintenanceUserRoles: "custom"
    maintenanceExcludedPosts: ["45","88"]
```

## Don't

- Don't write settings by calling `bricks/get-global-settings` -> mutating -> `bricks/set-global-settings` with the whole blob. It works, but it defeats partial-merge and races with admin UI saves.
- Don't retry on `bricks_setting_excluded`: the exclusion is permanent and deliberate.
- Don't treat `list-settings-schema` output as cacheable across Bricks versions: new keys show up with updates.
