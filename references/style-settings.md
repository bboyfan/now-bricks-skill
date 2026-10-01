# Style Settings & Value Shapes

Universal `_`-prefixed settings available on every element, plus the exact JSON shape of each value type. All shapes verified against `includes/assets.php` and `includes/elements/base.php` (Bricks 2.3.6). **Do not improvise shapes** — a wrong shape silently produces no CSS.

## Settings-Key Grammar (responsive + states)

```
{key}[:{breakpoint}][:{pseudo}]
```

| Part | Values |
|------|--------|
| breakpoint | `tablet_portrait` (≤991), `mobile_landscape` (≤767), `mobile_portrait` (≤478). Desktop = bare key (default desktop-first). Custom breakpoints use their own keys. |
| pseudo | `:hover`, `:active`, `:focus` (defaults), plus any enabled in Settings (e.g. `:before`, `:after`, `:focus-within`) |

Examples:

```json
{
  "_padding": { "top": "6rem", "bottom": "6rem" },
  "_padding:mobile_portrait": { "top": "3rem", "bottom": "3rem" },
  "_background:hover": { "color": { "hex": "#1d4ed8" } },
  "_transform:tablet_portrait:hover": { "scaleX": "1.05", "scaleY": "1.05" }
}
```

Breakpoint comes before pseudo. Legacy underscore syntax (`_padding_tablet_portrait`) still parses but never write it.

## Root font size (rem base)

`rem` resolves against the site's **root font size** (`html { font-size }`), not against the element. Before emitting any `rem`/`clamp()` value, **confirm what `1rem` equals** with the user:

- **Default = 16px** — browser default; also Bricks' default unless theme styles or CSS change it. Use this if the user doesn't specify.
- **`html { font-size: 62.5% }` reset → 1rem = 10px** — common on many themes; halves the effective size of every rem you write. A `2.5rem` heading becomes 25px, not 40px.
- A custom root size (e.g. `18px`) shifts everything proportionally.

Implications:

- **Converting px from a reference** — px ÷ (rem base) = rem. At 16px, `40px → 2.5rem`; at 10px, `40px → 4rem`. Get the base wrong and the whole design scales off.
- **When in doubt, ask, or use px** for precise one-off values and reserve `rem` for type/spacing that should scale with the root.
- `em` is relative to the *element's* font-size — don't mix it up with `rem`.

The root size lives in theme styles (`bodyTypography.font-size`) → [theme-styles.md](theme-styles.md). Bare numbers always get `px` appended (rule 4) — write the unit explicitly for `rem`.

## Core Value Shapes

### Color — always an object

```json
{ "hex": "#1a1a2e" }
{ "rgb": "rgba(26, 26, 46, 0.8)" }
{ "raw": "var(--brand-primary)" }
{ "id": "fkmcdz", "name": "Primary", "hex": "#1a1a2e" }
```

Resolution priority: `raw` → `rgb` → `hex`. A palette color carries `id` (emitted as `var(--bricks-color-{id})`) — only reference palette ids that exist on the target site. `raw` accepts any CSS color value, CSS variables, even dynamic data tags.

### Spacing (`_margin`, `_padding`) — per-side object, string values with units

```json
{ "top": "6rem", "right": "1.5rem", "bottom": "6rem", "left": "1.5rem" }
```

Omit sides you don't set. Negative margins fine: `"top": "-4rem"`. Bare numbers get `px`.

### Typography (`_typography`) — **CSS property names as keys**

```json
{
  "font-size": "1.125rem",
  "font-weight": "600",
  "font-style": "italic",
  "line-height": "1.5",
  "letter-spacing": "0.02em",
  "text-align": "center",
  "text-transform": "uppercase",
  "text-decoration": "none",
  "white-space": "nowrap",
  "font-family": "Inter",
  "color": { "hex": "#0f172a" },
  "text-shadow": {
    "values": { "offsetX": 0, "offsetY": 2, "blur": 4 },
    "color": { "rgb": "rgba(0,0,0,0.25)" }
  }
}
```

NOT camelCase. Any `property: value` pair in this object is emitted as CSS, so all font/text properties work. `font-family` is the family name string (Google fonts load automatically by name; site custom fonts by their name).

### Background (`_background`)

```json
{
  "color": { "hex": "#0f172a" },
  "image": { "id": 123, "url": "https://site.com/img.jpg", "size": "large" },
  "position": "center center",
  "size": "cover",
  "repeat": "no-repeat",
  "attachment": "fixed",
  "blendMode": "multiply"
}
```

- Dynamic image: `"image": { "useDynamicData": "{featured_image}", "size": "large" }`
- External/static URL only: `"image": { "url": "https://..." }` or `"image": { "external": "https://... or {acf_url}" }`
- Custom position: `"position": "custom"` + top-level `"positionX": "20%"`, `"positionY": "80%"`
- Custom size: `"size": "custom"` + `"custom": "120% auto"`
- **Video background** (section/container/block/div only) — same object: `"videoUrl": "https://.../bg.mp4"`, plus optional `videoScale`, `videoAspectRatio`, `videoStartTime`, `videoEndTime`, `videoLoop` (`"1"`), `videoPlayOnMobile`

### Gradient (`_gradient`)

```json
{
  "applyTo": "background",
  "gradientType": "linear",
  "angle": "135",
  "colors": [
    { "color": { "hex": "#6d28d9" }, "stop": "0" },
    { "color": { "hex": "#2563eb" }, "stop": "100" }
  ]
}
```

- `applyTo`: `background` (background-image) | `overlay` (::before layer) | `text` (background-clip)
- `gradientType`: `linear` | `radial` | `conic`; `angle` in degrees (number or string, `deg` appended)
- Stops are numbers 0–100 (`%` appended) or any CSS length string. Add `"repeat": true` for repeating gradients.

### Border (`_border`)

```json
{
  "width": { "top": "1px", "right": "1px", "bottom": "1px", "left": "1px" },
  "style": "solid",
  "color": { "rgb": "rgba(15, 23, 42, 0.1)" },
  "radius": { "top": "16px", "right": "16px", "bottom": "16px", "left": "16px" }
}
```

`radius` order is top-left, top-right, bottom-right, bottom-left (mapped from top/right/bottom/left keys). Style only renders if `width` set; per-side styles derive from the one `style` value.

### Box shadow (`_boxShadow`) — offsets nest under `values`

```json
{
  "values": { "offsetX": "0", "offsetY": "8", "blur": "24", "spread": "-4" },
  "color": { "rgb": "rgba(15, 23, 42, 0.12)" },
  "inset": true
}
```

Omit `inset` for normal shadows. Numbers get `px`.

### Transform (`_transform`) — flat object

```json
{
  "translateX": "-50%",
  "translateY": "10",
  "rotate": "3",
  "scaleX": "1.05",
  "scaleY": "1.05",
  "skewX": "0",
  "skewY": "0"
}
```

Plus `rotateX/Y/Z`, `perspective`, `scale3dX/Y/Z`. Pair with `_transformOrigin: "center bottom"`. Number-only translate gets `px`, rotate gets `deg`.

### CSS filters (`_cssFilters`) — flat object

```json
{ "blur": "4", "brightness": "110", "contrast": "105", "grayscale": "0", "hue-rotate": "0", "invert": "0", "opacity": "100", "saturate": "120", "sepia": "0" }
```

Only include filters you set. `blur` gets `px`; percentage-type filters get `%`.

### Image control (element `image`, backgrounds, etc.)

```json
{ "id": 5231, "url": "https://site.com/wp-content/uploads/photo.jpg", "size": "large" }
{ "useDynamicData": "{acf_team_photo}", "size": "medium" }
{ "url": "https://external.example.com/photo.jpg" }
```

When pasting to another site, `id` won't exist — include a working `url` (template import downloads it; clipboard paste keeps the URL).

### Link control (`link` on button/heading/text-basic/container/div…)

```json
{ "type": "external", "url": "https://example.com", "target": "_blank", "rel": "noopener noreferrer", "ariaLabel": "Read the guide" }
{ "type": "internal", "postId": 42 }
{ "type": "meta", "useDynamicData": "{post_url}" }
{ "type": "external", "url": "#pricing" }
{ "type": "lightbox", "lightboxImage": { "id": 12, "url": "https://..." } }
```

> [!WARNING]
> **Anti-Pattern Prohibited**: Never simulate links by adding `_attributes: [{"name": "href", ...}]` or setting `customTag: "a"`. Always use the native `settings.link` object above. Both `target: "_blank"` and `newTab: true` are supported in Bricks internal normalization.


Dynamic URL composition works in `useDynamicData`: `"https://wa.me/{acf_phone}"`.

### Icon control

```json
{ "library": "themify", "icon": "ti-arrow-right" }
{ "library": "fontawesomeSolid", "icon": "fas fa-check" }
{ "library": "ionicons", "icon": "ion-md-star" }
{ "library": "svg", "svg": { "id": 311, "url": "https://site.com/icon.svg" } }
```

### Custom attributes (`_attributes`)

```json
[ { "id": "ax1b2c", "name": "data-section", "value": "hero" } ]
```

### Custom CSS (`_cssCustom`) — use `%root%` for the element

```css
%root% { clip-path: polygon(0 0, 100% 0, 100% 85%, 0 100%); }
%root%:hover .card-icon { transform: rotate(8deg); }
```

## Universal Settings Catalog

### Layout

| Key | Value |
|-----|-------|
| `_display` | `flex` `grid` `block` `inline-block` `inline` `none` |
| `_margin`, `_padding` | spacing object |
| `_width`, `_widthMin`, `_widthMax` | string with unit (`"640px"`, `"100%"`, `"60vw"`) |
| `_height`, `_heightMin`, `_heightMax` | string with unit |
| `_aspectRatio` | `"16/9"`, `"1"` |
| `_overflow` | `hidden` `auto` `scroll` `visible` (or `"hidden auto"`) |
| `_opacity` | `"0.85"` |
| `_visibility` | `visible` `hidden` |
| `_zIndex` | `"10"` |
| `_position` | `relative` `absolute` `fixed` `sticky` |
| `_top` `_right` `_bottom` `_left` | string with unit |
| `_order` | `"-1"`, `"2"` |
| `_cursor` | CSS cursor value |
| `_mixBlendMode`, `_isolation`, `_pointerEvents` | CSS values |

### Flex (on the element itself when display:flex; container/block/div/section)

| Key | Value |
|-----|-------|
| `_direction` | `row` `column` `row-reverse` `column-reverse` (layout elements) |
| `_flexDirection` | same — non-layout elements |
| `_flexWrap` | `wrap` `nowrap` `wrap-reverse` |
| `_justifyContent` | `flex-start` `center` `flex-end` `space-between` `space-around` `space-evenly` |
| `_alignItems`, `_alignSelf`, `_alignContent` | `flex-start` `center` `flex-end` `stretch` `baseline` |
| `_columnGap`, `_rowGap` | string with unit |
| `_gap` | string with unit (non-layout elements) |
| `_flexGrow`, `_flexShrink` | `"0"` / `"1"` |
| `_flexBasis` | `"33.333%"`, `"auto"` |

### Grid (set `_display: "grid"` first)

| Key | Value |
|-----|-------|
| `_gridTemplateColumns` | `"repeat(3, minmax(0, 1fr))"`, `"repeat(auto-fit, minmax(280px, 1fr))"` |
| `_gridTemplateRows` | `"auto 1fr"` |
| `_gridGap` | `"24px"` or `"24px 32px"` (row col) |
| `_gridAutoFlow` | `row` `column` `dense` `row dense` |
| `_gridAutoColumns`, `_gridAutoRows` | `"1fr"`, `"minmax(200px, auto)"` |
| `_justifyItemsGrid`, `_alignItemsGrid` | `start` `center` `end` `stretch` |
| `_justifyContentGrid`, `_alignContentGrid` | `start` `center` `end` `space-between` … |
| `_gridItemColumnSpan` | on children: `"span 2"`, `"1 / -1"` |
| `_gridItemRowSpan` | on children: `"span 2"` |
| `_gridItemJustifySelf` | on children |

### Masonry (layout elements, 1.11.1+)

`_useMasonry` (bool), `_masonryColumn` (number), `_masonryGutter` (unit string), `_masonryHorizontalOrder` (bool), `_masonryTransitionDuration`, `_masonryTransitionMode` (`scale` `fade` `slideLeft` `slideRight` `skew`)

### Style groups

| Key | Shape |
|-----|-------|
| `_typography` | typography object above |
| `_background` | background object above |
| `_gradient` | gradient object above |
| `_border` | border object above |
| `_boxShadow` | box-shadow object above |
| `_transform` / `_transformOrigin` | transform object / string |
| `_cssFilters` | filters object above |
| `_cssTransition` | `"all 0.3s ease"` — transition string (write the properties, not just `all`, when animating hover states) |

### Scroll snap (layout elements)

`_scrollSnapType` (`"x mandatory"`), `_scrollSnapAlign` (`start` `center` `end`), `_scrollSnapStop`, `_scrollMarginTop`

### Identity & code

| Key | Shape |
|-----|-------|
| `_cssId` | `"pricing"` (no `#`) |
| `_cssClasses` | `"u-text-center is-dark"` (plain classes, space-separated — no CSS generated, just attached) |
| `_cssGlobalClasses` | `["classId1", "classId2"]` — **ids** of global class objects |
| `_cssCustom` | CSS string with `%root%` |
| `_attributes` | attributes array above |
| `_conditions` | see conditions.md |
| `_interactions` | see interactions.md |

### Shape dividers (layout elements)

```json
"_shapeDividers": [
  {
    "id": "sd1a2b",
    "shape": "wave",
    "front": true,
    "horizontalAlign": "bottom",
    "height": "120px",
    "fill": { "hex": "#ffffff" },
    "flipHorizontal": false,
    "flipVertical": false
  }
]
```

### Hide per breakpoint

There is no `_hidden` flag — use `"_display:mobile_portrait": "none"`.

## Common Mistakes (these silently fail)

| Wrong | Right |
|-------|-------|
| `"_typography": { "fontSize": "18px" }` | `"_typography": { "font-size": "18px" }` |
| `"_boxShadow": { "offsetY": "8px", ... }` | `"_boxShadow": { "values": { "offsetY": "8" }, ... }` |
| `"_gradient": { "stops": [...] }` | `"_gradient": { "colors": [ { "color": {...}, "stop": "0" } ] }` |
| `"_background": "#fff"` | `"_background": { "color": { "hex": "#ffffff" } }` |
| `"_padding": "2rem"` | `"_padding": { "top": "2rem", "bottom": "2rem", ... }` |
| `"_typography:hover"` for link color | works, but prefer setting on the element with pseudo: `"_typography:hover": { "color": {...} }` |
| `"_padding:tablet"` | `"_padding:tablet_portrait"` (no breakpoint named `tablet` by default) |
| color string in border: `"color": "#eee"` | `"color": { "hex": "#eeeeee" }` |
