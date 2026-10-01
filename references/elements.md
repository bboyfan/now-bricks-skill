# Element Catalog

Every element name registered in Bricks 2.3.6 (`includes/elements.php`), with the settings that matter for JSON authoring. Style every element with the universal `_` keys from style-settings.md; this file covers element-specific keys.

## Registry

**Layout (nestable):** `section` `container` `block` `div`
**Basic:** `heading` `text-basic` `text` (rich) `text-link` `button` `icon` `image` `video` `svg` `logo` `divider` `list` `alert` `html` `code` `shortcode` `template`
**Nestable interactive:** `accordion-nested` `tabs-nested` `slider-nested` `nav-nested` `dropdown` `offcanvas` `toggle` `toggle-mode` `slot`
**Media:** `image-gallery` `audio` `carousel` `instagram-feed`
**Marketing:** `icon-box` `social-icons` `pricing-tables` `counter` `countdown` `progress-bar` `pie-chart` `team-members` `testimonials` `animated-typing` `rating` `back-to-top`
**Forms & search:** `form` `search`
**WordPress:** `wordpress` `posts` `nav-menu` `sidebar` `breadcrumbs`
**Single post:** `post-title` `post-excerpt` `post-content` `post-meta` `post-author` `post-comments` `post-taxonomy` `post-navigation` `post-sharing` `post-toc` `post-reading-time` `post-reading-progress-bar` `related-posts`
**Query:** `pagination` `query-results-summary`
**Query filters (require the Query Filters feature):** `filter-search` `filter-select` `filter-checkbox` `filter-radio` `filter-range` `filter-datepicker` `filter-submit` `filter-active-filters`
**Maps:** `map` `map-leaflet` `map-connector`
**Legacy (avoid in new builds — use the `-nested` versions):** `accordion` `tabs` `slider`
**WooCommerce:** see woocommerce.md

## Layout Elements

`section` → root-level wrapper (renders `<section>`, inner width constrained by theme style). `container` → max-width inner wrapper. `block` → full-width flex div. `div` → unstyled div (no default width/display).

| Setting | Values | Notes |
|---------|--------|-------|
| `tag` | `section` `div` `header` `footer` `nav` `main` `article` `aside` `figure` `custom` | semantic HTML — use it |
| `customTag` | any tag | when `tag: "custom"` |
| `link` | link object | makes the whole element a link (`<a>`). Never use `customTag: "a"` or fake `href` attrs |
| `hasLoop` + `query` | see query-loops.md | turns the element into a query loop |
| `_shapeDividers` | see style-settings.md | section decorations |


Standard page skeleton:

```json
{ "id": "sec001", "name": "section", "parent": 0, "children": ["con001"], "settings": { "tag": "section" } }
{ "id": "con001", "name": "container", "parent": "sec001", "children": ["..."], "settings": {} }
```

Sections stack vertically at root. Inside a container, use `block`/`div` with `_display` flex or grid for columns/grids — there is no "column" element.

## Content Elements

### heading
```json
{ "text": "Build faster", "tag": "h2" }
```
`tag`: `h1`–`h6` | `custom`. Optional separator: `separator` (`right` `left` `both`), `separatorWidth/Height/Spacing/Style/Color/AlignItems`. `link` object makes it a link. Style size via `_typography`.

### text-basic — single paragraph/span (preferred for plain text)
```json
{ "text": "One paragraph of plain text.", "tag": "p" }
```
`tag`: `p` (default) | `span` | `div` | `custom`/`customTag`. `wordsLimit` + `readMore` for trimming.

### text — rich text (multiple paragraphs, HTML)
```json
{ "text": "<p>First.</p><p>Second with <strong>bold</strong>.</p><ul><li>Item</li></ul>" }
```
HTML allowed. Use for multi-paragraph content; use `text-basic` otherwise.

### button
```json
{
  "text": "Get started",
  "tag": "a",
  "link": { "type": "external", "url": "#pricing" },
  "style": "primary",
  "size": "lg",
  "icon": { "library": "themify", "icon": "ti-arrow-right" },
  "iconPosition": "right",
  "iconGap": "8px"
}
```
- `style`: `primary` `secondary` `light` `dark` `muted` `info` `success` `warning` `danger` (theme-style colors). **Omit `style` entirely for fully custom-styled buttons** and use `_background`/`_typography`/`_border` instead.
- `size`: `sm` `md` `lg` `xl`; `outline: true`; `circle: true`
- `tag`: `a` (default when link set) | `button` — use `button` + interactions for non-navigation actions.

### image
```json
{
  "image": { "id": 123, "url": "https://site.com/photo.jpg", "size": "large" },
  "altText": "Team at work",
  "loading": "lazy",
  "link": { "type": "lightbox" }
}
```
Dynamic: `"image": { "useDynamicData": "{featured_image}", "size": "large" }`. Caption: `caption`: `none` | `attachment` | `custom` (+ `captionCustom`). Lightbox settings under `lightbox*`. Object-fit cropping: set `_height`/`_aspectRatio` + `_objectFit: "cover"` (`_objectPosition` to focus).

### icon
```json
{ "icon": { "library": "ionicons", "icon": "ion-ios-checkmark-circle" }, "iconSize": "32px", "iconColor": { "hex": "#16a34a" } }
```
Libraries: `themify`, `ionicons`, `fontawesomeRegular/Solid/Brands`, `svg` (`{ "library": "svg", "svg": { "id": 1, "url": "..." } }`).

### icon-box
`icon` (icon object), `iconSize`, `iconColor`, `direction` (`row` = icon left, `column` = icon top; `iconPosition` is deprecated), `content` (HTML), `gap`, plus `icon*`/`content*` style sub-keys. For full control, build your own with `div` + `icon` + `heading` + `text-basic` instead.

### social-icons
Repeater key is `icons`: `[{ "id": "...", "label": "X", "icon": {...icon object}, "link": {...link object}, "iconColor"?, "iconSize"? }]`. Top-level: `iconColor`, `iconSize`, `gap`, `direction`.

### divider
`style` (`solid` `dashed` `dotted` `double`), `direction` (`horizontal`/`vertical`), `width`, `height` (thickness), `color`, optional centered `icon`.

### list
Repeater `items`: `[{ "title": "...", "description": "...", "link": {...} }]` plus `icon`, `iconColor`. For custom layouts prefer a `ul`-tagged `div` with children.

### video
File: `{ "media": "file", "fileUrl": "https://.../video.mp4", "fileControls": true, "fileLoop": true, "fileMute": true }`. YouTube: `{ "media": "youtube", "youTubeId": "dQw4w9WgXcQ" }`; Vimeo: `vimeoId`. `overlay`/`previewImage` for facade, `aspectRatio` (`"16:9"`).

### svg
`file` (media object to .svg), or `source: "code"` + `code` (raw SVG markup), `height`, `width`, `strokeColor`/`fill` via CSS.

### logo / nav-menu / sidebar / search
- `logo`: `logo` (image), `logoInverse` (sticky-header swap), `logoText` fallback, `logoWidth/Height`, `logoUrl`
- `nav-menu`: `menu` (WP menu ID), styling sub-keys, `mobileMenu` settings — prefer `nav-nested` for new builds
- `search`: `searchType` (`input` | `icon` overlay), `placeholder`, `ariaLabel`

### counter / countdown / progress-bar / rating
- `counter`: `countFrom`, `countTo`, `duration` (ms), `prefix`, `suffix`, `thousandSeparator`
- `countdown`: `date` (`"2026-12-31 23:59"`), repeater `fields` with `format` (`%d`/`%H`/`%M`/`%S`) + `label`
- `progress-bar`: repeater `bars`: `[{ "title": "...", "percentage": "80" }]`, `height`, `barBackgroundColor`
- `rating`: `rating` value, `ratingMax`, icon settings

### alert / html / code / shortcode / template
- `alert`: `content`, `type` (`info` `success` `warning` `danger`), `dismissable`
- `html`: `html` (raw markup, no PHP)
- `code`: `code` + `language` for display; `executeCode: true` runs HTML/CSS/JS (requires code execution permission — avoid generating it)
- `shortcode`: `shortcode` (`"[contact-form-7 id=\"5\"]"`)
- `template`: `template` (template post ID) — embeds a section template

## Nestable Patterns (exact structure required)

Nestables ship structural CSS classes via the **`_hidden` settings key** — keep these intact or styling/scripts break:

```json
"settings": { "_hidden": { "_cssClasses": "accordion-title-wrapper" } }
```

### accordion-nested
Element settings: `expandFirstItem`, `independentToggle`, `faqSchema` (bool — outputs FAQ JSON-LD), `transition`, title/content style keys.
Each item child is:

```
block (Item)
├── block  settings._hidden._cssClasses = "accordion-title-wrapper"   (_direction row, _justifyContent space-between, _alignItems center)
│   ├── heading  { "text": "Question?", "tag": "h3" }
│   └── icon     { "icon": {...}, "isAccordionIcon": true }
└── block  settings._hidden._cssClasses = "accordion-content-wrapper"
    └── text     { "text": "<p>Answer.</p>" }
```

### tabs-nested
Element settings: `openTab` (1-based), `openTabOn` (`click`/`hover`/`focus`), `direction` (row = horizontal tabs), title/content style keys. Structure:

```
tabs-nested
├── block (Tab menu)      _hidden._cssClasses = "tab-menu"      (_direction row)
│   ├── div (Title)       _hidden._cssClasses = "tab-title"     → children: text-basic "Tab 1"
│   └── div (Title)       _hidden._cssClasses = "tab-title"     → children: text-basic "Tab 2"
└── block (Content)       _hidden._cssClasses = "tab-content"
    ├── block (Pane)      _hidden._cssClasses = "tab-pane"      → children: any
    └── block (Pane)      _hidden._cssClasses = "tab-pane"      → children: any
```

Title count must equal pane count, in order.

### slider-nested (splide.js)
Element settings: `type` (`slide` `loop` `fade`), `perPage`, `perMove`, `gap`, `speed`, `autoplay`, `interval`, `pauseOnHover`, `height`, `arrows` + `arrow*` styling (`arrowColor`, `arrowBackground`…), `pagination` (dots, checkbox) + `paginationColor`/`paginationColorActive`/`paginationSpacing`. Breakpoint-responsive: `perPage:tablet_portrait` etc.
Children: each slide is a plain `block` (any content inside). Optional `splideJson` for raw splide config.

### nav-nested (accessible nav with mobile menu)
Children are free-form: `text-link` items, `dropdown` elements (each dropdown: `text` + children = its menu), `toggle` (hamburger). Key settings: `menuAlignment`, `mobileMenu` (breakpoint key at which nav collapses, e.g. `tablet_portrait`), `ariaLabel`, dropdown styling keys (`dropdownBackgroundColor`, `dropdownPadding`, …).

### dropdown
`text` (label), children render inside the dropdown content. `caret` settings included.

### offcanvas
Settings: `direction` (`left` `right` `top` `bottom`), `width`, `backdrop`, `disableScroll`, `transition`. Children: free content. Open via a `toggle` element (`selector` targeting the offcanvas) or interactions.

### toggle
`selector` (CSS selector of target offcanvas/element), `iconTypeOpen/Close`, accessible hamburger out of the box.

## Posts element vs query loop

The `posts` element is a legacy all-in-one grid (settings: `columns`, `gutter`, `content` repeater, `filter` tabs). **Prefer a `block`/`div` with `hasLoop` + `query`** (see query-loops.md) — it gives full layout control and works with query filters.

## Element defaults to remember

- Headings inherit theme-style typography — only set `_typography` when diverging.
- `button` `style` keys map to theme-style button colors; omit for custom.
- Every text-bearing setting accepts dynamic data tags: `"text": "{post_title}"`.
- `label` on the node (not in settings) names it in the structure panel — label everything in generated layouts.
