# Referencing External Assets (from a reference URL)

When the user gives a **reference URL** — "build this like `https://…`", "use the images/video from that page", or just pastes a link — Bricks designs can reference *any* remotely-hosted media by its absolute URL. No WordPress attachment is required: every media control accepts a plain `url` (or `external`) string. This makes the skill **host-independent** — it works with assets from the reference site, a CDN, an image API (Unsplash/Pexels), YouTube/Vimeo, or any public URL.

All value shapes below are the same ones verified in [style-settings.md](style-settings.md) and [elements.md](elements.md) — this file just maps *page asset → Bricks element/shape*.

## Workflow

1. **Fetch & inventory.** Pull the reference page (WebFetch or equivalent) and list every asset with its source:
   - `<img src>`, `srcset`, `<picture><source>`
   - CSS `background-image: url(…)` (inline `style=` and stylesheets)
   - `<video>` / `<source>`, and YouTube/Vimeo `<iframe>` embeds → extract the **video id**
   - `<svg>` inline markup, `.svg` files, icon sprites
   - `<audio>` / `<source>`
   - `<link rel="icon">`, logo images, Open Graph `og:image`
2. **Resolve to absolute URLs.** Convert relative paths (`/img/hero.jpg`, `./a.png`, protocol-relative `//cdn…`) against the reference origin so the URL works off-site. Pick the **largest** candidate from `srcset` for heroes.
3. **Map each asset** to the right element + shape (tables below).
4. **Decide hotlink vs. re-host** (see below) and note the choice in the final summary.
5. **Capture metadata** — `alt` text, captions, and the asset's purpose — so the rebuilt element stays accessible.

## Asset → Bricks mapping

| Page asset | Bricks target | External shape |
|------------|---------------|----------------|
| `<img>` content image | `image` element | `"image": { "url": "https://…/photo.jpg" }` (add `"size": "full"`) |
| Decorative / section background image | any container's `_background` | `"_background": { "image": { "url": "https://…" }, "size": "cover", "position": "center center", "repeat": "no-repeat" }` |
| Looping background video (mp4/webm) | `section`/`container`/`block`/`div` `_background` | `"_background": { "videoUrl": "https://…/bg.mp4", "videoLoop": "1", "videoPlayOnMobile": false }` |
| Self-hosted `<video>` | `video` element | `{ "media": "file", "fileUrl": "https://…/clip.mp4", "fileControls": true, "fileLoop": true, "fileMute": true }` |
| YouTube embed | `video` element | `{ "media": "youtube", "youTubeId": "dQw4w9WgXcQ" }` (+ `"previewImage"`/`"overlay"` for a facade) |
| Vimeo embed | `video` element | `{ "media": "vimeo", "vimeoId": "76979871" }` |
| Inline `<svg>` markup | `svg` element | `{ "source": "code", "code": "<svg …>…</svg>" }` |
| `.svg` file (decorative) | `svg` element | `{ "file": { "url": "https://…/shape.svg" } }` |
| `.svg` used as an icon | icon control | `{ "library": "svg", "svg": { "url": "https://…/icon.svg" } }` |
| `<audio>` | `audio` element | external `url` on its media control |
| Logo | `logo` element / `image` | `"logo": { "url": "https://…/logo.svg" }` |
| Click-to-zoom image | `image` + link | `"link": { "type": "lightbox", "lightboxImage": { "url": "https://…/full.jpg" } }` |
| Image gallery / slider | `image-gallery` / `carousel` | each item carries its own `url` (no `id`) |

Examples (drop straight into a node's `settings`):

```json
"image": { "url": "https://cdn.example.com/hero@2x.jpg", "size": "full" }
```
```json
"_background": { "image": { "url": "https://cdn.example.com/grid.png" }, "size": "cover", "position": "center center", "repeat": "no-repeat" }
```
```json
"_background": { "videoUrl": "https://cdn.example.com/loop.mp4", "videoLoop": "1", "videoScale": true }
```

For dynamic/CMS-driven media, swap the static `url` for `"external": "{acf_url}"` or `"useDynamicData": "{featured_image}"` (see [dynamic-data.md](dynamic-data.md) / [acf-providers.md](acf-providers.md)).

## Hotlink vs. re-host

`id` (WP attachment id) never resolves on another site — **always include a real absolute `url`**, and rely on `url`/`external`, not `id`.

| Format | Behavior | Use when |
|--------|----------|----------|
| **Clipboard paste** (`bricksCopiedElements`) | external `url`s **hotlink** — they stay remote and load from the source host | fast prototyping / wireframing |
| **Template import** (`.json` template) | Bricks **downloads** `image` controls that have a `url` into the Media Library on import | production builds you want self-hosted |

For production, re-host third-party media in the Media Library and reference it by its uploaded `url` (with `id`). Hotlinking risks broken images (hotlink protection, CORS), layout shift, and licensing problems.

## Robustness & licensing rules

- **Absolute URLs only** — resolve relatives; never emit `/wp-content/...` from another origin.
- **Don't hotlink copyrighted/brand assets into production.** For mimicking a competitor's layout, follow the **wireframe-first default** ([layout-recipes.md](layout-recipes.md)): reproduce structure/spacing/typography but substitute the actual photos/logos with the user's own assets, neutral placeholders (Unsplash/Pexels with attribution), or pure-CSS stand-ins. Flag any asset whose license you can't confirm.
- **Inline SVG over hotlinked SVG** — use the `svg` element's `code` source for icons/shapes; it avoids cross-origin fetch issues and is restyleable via CSS (`currentColor`, `fill`).
- **Prefer CSS to images for decoration** — gradients, shapes, and `_gradient`/`clip-path` beat hotlinking a decorative PNG.
- **Accessibility** — carry over `alt`/captions; mark purely-decorative images so they don't add noise to the tree.
- **Verify reachability** — if a URL 404s or blocks hotlinking, fall back to a placeholder and say so in the summary.

See also: [assets-permissions.md](assets-permissions.md) (how Bricks *loads* assets/CSS, not external referencing).
