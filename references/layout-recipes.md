# Layout Recipes

Composition patterns for one-shotting real designs. Pair with patterns/ for complete paste-ready files. All settings use verified shapes from style-settings.md.

## Page anatomy

```
section (tag: section)          ← one per band of the page
└── container                   ← centers content, theme-style max-width
    └── block / div trees       ← columns, grids, cards
```

- One `section` per visual band (hero, logos, features, testimonials, pricing, FAQ, CTA). Don't stack multiple bands in one section.
- Section spacing: `_padding` top/bottom on the section (e.g. `clamp(4rem, 8vw, 7rem)` via a global variable or raw string).
- Never set widths on `container` children with margins — use flex/grid gaps.

## Design quality defaults

- **Spacing scale**: 4-based (`4 8 12 16 24 32 48 64 96 128px`) or the site's `--space-*` variables. Same scale everywhere.
- **Type scale**: set `font-size` only when diverging from theme styles; use `clamp()` for display sizes: `"font-size": "clamp(2.25rem, 5vw, 3.5rem)"`.
- **Line length**: cap text columns: `"_widthMax": "65ch"` on text-bearing blocks.
- **Hierarchy per section**: eyebrow (small, uppercase, letter-spaced) → heading → supporting text → action. Build it once as a reusable header block in every section.
- **Hover states**: every interactive element gets `_cssTransition` + a `:hover` key.
- **Responsive pass**: every grid gets `tablet_portrait` and `mobile_portrait` overrides; reverse column order on mobile with `_direction:mobile_portrait` or `_order`.

## Columns (flex)

Two-column split (content + media):

```json
{ "id": "row001", "name": "block", "settings": {
    "_direction": "row", "_alignItems": "center", "_columnGap": "64px",
    "_direction:tablet_portrait": "column", "_rowGap:tablet_portrait": "40px" } }
```

Children: two `div`s with `"_flexGrow": "1"`, `"_flexBasis": "0"` (equal) or `_width: "45%"` / `"55%"` (asymmetric). Image-right alternating rows: even rows get `"_direction": "row-reverse"` (reset to `column` on mobile).

## Grids

```json
{ "_display": "grid", "_gridTemplateColumns": "repeat(3, minmax(0,1fr))", "_gridGap": "32px",
  "_gridTemplateColumns:tablet_portrait": "repeat(2, minmax(0,1fr))",
  "_gridTemplateColumns:mobile_portrait": "1fr" }
```

- Auto-fit (no breakpoints needed): `"repeat(auto-fit, minmax(280px, 1fr))"`
- Feature card spanning: child with `"_gridItemColumnSpan": "span 2"` or `"_gridItemRowSpan": "span 2"` (bento grids)
- Full-bleed row inside grid: `"_gridItemColumnSpan": "1 / -1"`
- Masonry: `_useMasonry: true` + `_masonryColumn` + `_masonryGutter` on the wrapper

## Cards

```json
{ "id": "crd001", "name": "block", "label": "Card", "settings": {
    "_background": { "color": { "hex": "#ffffff" } },
    "_border": { "radius": { "top": "16px", "right": "16px", "bottom": "16px", "left": "16px" },
                 "width": { "top": "1px", "right": "1px", "bottom": "1px", "left": "1px" },
                 "style": "solid", "color": { "rgb": "rgba(15,23,42,0.08)" } },
    "_padding": { "top": "32px", "right": "32px", "bottom": "32px", "left": "32px" },
    "_rowGap": "16px",
    "_cssTransition": "transform 0.25s ease, box-shadow 0.25s ease",
    "_transform:hover": { "translateY": "-4" },
    "_boxShadow:hover": { "values": { "offsetX": "0", "offsetY": "12", "blur": "32", "spread": "-8" }, "color": { "rgb": "rgba(15,23,42,0.18)" } }
} }
```

Make the whole card clickable: `link` on the card block; keep inner links out, or use a stretched pseudo-link via `_cssCustom`.
Image flush to card edges: negative margins on the image equal to card padding, or put the image before a padded inner block.

## Hero patterns

**Centered hero:** section (`_padding` ~ 8rem, `_alignItems: center`, `_textAlign` via typography) → container (`_rowGap: 24px`, `_alignItems: center`) → eyebrow `text-basic` + `h1` + sub `text-basic` (`_widthMax: 60ch`) + button row (`block`, `_direction: row`, `_columnGap: 16px`).

**Image-background hero:**
```json
"_background": { "image": { "url": "…" }, "size": "cover", "position": "center center" },
"_gradient": { "applyTo": "overlay", "gradientType": "linear", "angle": "180",
  "colors": [ { "color": { "rgb": "rgba(2,6,23,0.75)" }, "stop": "0" },
              { "color": { "rgb": "rgba(2,6,23,0.35)" }, "stop": "100" } ] }
```
White text via `_typography` on the content wrapper.

**Split hero:** two-column recipe + `_heightMin: "80vh"` on section, media column with `_objectFit` image or video element.

**Video hero:** section `_background` with `videoUrl` (+ poster image as background image fallback).

## Overlap & layering

- Pull-up card over hero: next section's container `"_margin": { "top": "-80px" }`, `_zIndex: "10"`, `_position: "relative"`.
- Absolute decorations: child with `_position: "absolute"` + offsets inside a `_position: "relative"` parent (`div` blobs, badge stickers). Add `"_pointerEvents": "none"` to decorations.
- Section transitions: `_shapeDividers` (wave/tilt) or `clip-path` via `_cssCustom`.

## Sticky patterns

- Sticky sidebar/TOC: column child `"_position": "sticky"`, `"_top": "96px"`, `"_alignSelf": "flex-start"`.
- Sticky section stacking (scrollytelling): each section `_position: sticky; _top: 0` + `_zIndex` increasing — verify overflow isn't hidden on ancestors.
- Sticky header: header template settings (templates.md), not element settings.

## Horizontal scroll / carousels

- Native scroll-snap row: wrapper `"_display": "flex"`, `"_overflow": "auto hidden"` via `_overflow: "auto"`, `_scrollSnapType: "x mandatory"`; children `_scrollSnapAlign: "start"`, fixed `_flexBasis`.
- JS slider: `slider-nested` (splide) — see elements.md.

## Section header block (reuse everywhere)

```json
{ "id": "shd001", "name": "block", "label": "Section Header", "settings": { "_rowGap": "12px", "_alignItems": "center", "_widthMax": "640px", "_margin": { "left": "auto", "right": "auto", "bottom": "56px" } } }
├── { "name": "text-basic", "settings": { "text": "PRICING", "tag": "span",
      "_typography": { "font-size": "0.8125rem", "font-weight": "600", "letter-spacing": "0.1em", "text-transform": "uppercase", "color": { "hex": "#1d4ed8" }, "text-align": "center" } } }
├── { "name": "heading", "settings": { "text": "Simple, honest pricing", "tag": "h2", "_typography": { "text-align": "center" } } }
└── { "name": "text-basic", "settings": { "text": "Supporting copy…", "_typography": { "text-align": "center", "color": { "hex": "#64748b" } } } }
```

## Dark sections

Set `_background` dark + override text colors on the section's `_typography` (inherited) — headings may need explicit `_typography.color` since theme styles target h1–h6. Alternative: one `dark-section` global class with `_cssCustom` setting heading/text colors.

## Logos / social proof strip

Grid `repeat(auto-fit, minmax(120px, 1fr))`, `_alignItemsGrid: center`, images with `_cssFilters: { "grayscale": "100", "opacity": "70" }` and hover reset.

## Footer (multi-column)

section (tag `footer`) → container → grid `"2fr 1fr 1fr 1fr"` (brand col + link cols, `1fr` stack on mobile) → link columns are `div`s with heading (`tag: "custom"`, `customTag: "span"`, styled) + `text-link` items in a `_rowGap` column → bottom bar block with `_borderTop`, `_direction: row`, `_justifyContent: space-between`.

## Full-page composition order

For "build me a landing page" requests, default to:
1. Header template (logo + nav-nested + CTA)
2. Hero
3. Logo strip
4. Features (3-col grid or alternating rows)
5. Product/screenshot section
6. Testimonials
7. Pricing
8. FAQ (accordion-nested, `faqSchema: true`)
9. Final CTA
10. Footer template

Deliver page content as one clipboard JSON; header/footer as separate template JSONs.
