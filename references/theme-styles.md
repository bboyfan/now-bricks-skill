# Theme Styles, Breakpoints & CSS Pipeline

Site-wide styling defaults and how settings become CSS. Verified against `includes/theme-styles.php`, `includes/breakpoints.php`, `includes/assets.php` (2.3.6).

## Breakpoints

Defaults (option `bricks_breakpoints` when customized):

| Key | Width | Media query |
|-----|-------|-------------|
| `desktop` | base (1279 builder width) | none — base styles |
| `tablet_portrait` | 991 | `max-width: 991px` |
| `mobile_landscape` | 767 | `max-width: 767px` |
| `mobile_portrait` | 478 | `max-width: 478px` |

- Desktop-first by default: bare key = desktop, suffixed keys cascade down.
- Custom breakpoints get their own keys; a site can switch to **mobile-first** (base = smallest, `min-width` queries) — check before authoring responsive JSON for an unfamiliar site.
- Settings-key grammar: `key:breakpoint:pseudo` (see style-settings.md).

## Theme styles

Option `bricks_theme_styles`.

### Verified Control Groups & Schema (Bricks 2.0+)

Bricks strictly organizes theme style settings by **control groups**. Putting settings at the root of `settings` will be ignored by `Assets::generate_inline_css_theme_style`.

```json
{
  "mystyle1": {
    "label": "Main",
    "settings": {
      "conditions": {
        "conditions": [
          { "main": "any" }
        ]
      },
      "typography": {
        "typographyBody": {
          "font-family": "var(--body-font)",
          "font-size": "16px",
          "line-height": "1.8",
          "color": { "raw": "var(--ink)" }
        },
        "typographyHeadings": {
          "font-family": "GenYoMin TC",
          "font-weight": "300",
          "letter-spacing": "0.04em",
          "color": { "raw": "inherit" }
        },
        "typographyHeadingH1": {
          "font-size": "48px",
          "line-height": "1.2"
        }
      },
      "links": {
        "typographyLinks": {
          "color": { "raw": "inherit" },
          "text-decoration": "none"
        }
      },
      "css": {
        "stylesheet": "/* Global centralized layout/component CSS rules */\n.section-wrap { width: min(100% - 48px, 1200px); margin-inline: auto; }"
      }
    }
  }
}
```

### Key Schema Facts:
1. **Typography Control Keys**:
   - `typographyBody`: Body text typography.
   - `typographyHeadings`: Applies to all H1–H6 headings simultaneously.
   - `typographyHeadingH1` ~ `typographyHeadingH6`: Individual heading overrides.
   - `typographyLinks`: Global link typography under the `links` group.
2. **Centralized CSS (`css.stylesheet`)**:
   - Bricks 2.0+ provides `css.stylesheet` inside Theme Styles.
   - **Architecture Rule**: Put shared layout classes and reusable styles here instead of duplicating identical `<style>` blocks across multiple inner pages.
   - Regenerate CSS files when saved: `\Bricks\Assets_Theme_Styles::generate_css_file( get_option('bricks_theme_styles') );`.
3. **Conditions Structure**:
   - Nested as `conditions: { conditions: [ { main: 'any' } ] }`.


## CSS generation order (inline or file)

1. `:root` global variables
2. Theme styles (matching conditions)
3. Global classes
4. Color palette variables
5. Page settings CSS
6. Header / content / footer element CSS
7. Popup CSS
8. Global custom CSS (Settings → Custom code)

Later wins at equal specificity — element settings beat global classes, which beat theme styles. `_cssCustom` outputs verbatim where the element's CSS lands.

## CSS loading methods

Bricks Settings → Performance:
- **Inline** (default): per-page `<style>`.
- **External files**: generated under `wp-content/uploads/bricks/css/` (`post-{id}.min.css`, theme styles, global classes…). After programmatic content changes, run `wp bricks regenerate_assets`.

## Page-level CSS/JS

Postmeta `_bricks_page_settings`:

```json
{
  "customCss": ".hero { background-blend-mode: multiply; }",
  "customScriptsHeader": "<script>…</script>",
  "customScriptsBodyHeader": "",
  "customScriptsBodyFooter": "<script>…</script>"
}
```

## Custom fonts

- Google fonts: set `font-family` by name — Bricks enqueues automatically (mind GDPR setting that disables remote Google fonts).
- Custom fonts post type (`bricks_fonts`): upload woff2; then `font-family` is the custom font's name.
- Adobe fonts via project ID in settings.
- Variable axes: typography supports `font-variation-settings` as a property key.

## Performance defaults worth setting in generated sites

- Disable unused icon fonts (Settings → Performance) — prefer SVG icons.
- `loading: "lazy"` on below-fold images (default), `eager` + `fetchpriority` for LCP hero images (via `_attributes`).
- Element CSS files method for heavily cached sites; inline for small ones.
