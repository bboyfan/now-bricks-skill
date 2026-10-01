# Popups

Popups are templates (`type: "popup"`) whose settings live in the template's settings (`_bricks_template_settings` → `popup*` keys, or `pageSettings` in exports). Verified against `includes/popups.php` (2.3.6).

## Creating a popup (export JSON)

```json
{
  "name": "newsletter-popup",
  "title": "Newsletter Popup",
  "type": "popup",
  "content": [ /* element nodes — the popup body */ ],
  "pageSettings": {
    "popupContentWidth": "560px",
    "popupJustifyConent": "center",
    "popupAlignItems": "center",
    "popupContentBackground": { "color": { "hex": "#ffffff" } },
    "popupContentPadding": { "top": "40px", "right": "40px", "bottom": "40px", "left": "40px" },
    "popupContentBorder": { "radius": { "top": "16px", "right": "16px", "bottom": "16px", "left": "16px" } },
    "popupBackground": { "color": { "rgb": "rgba(15, 23, 42, 0.7)" } },
    "popupCloseOn": "backdrop",
    "popupZindex": "10000"
  },
  "templateSettings": {},
  "global_classes": []
}
```

Note the key is `popupJustifyConent` — Bricks' own (misspelled) key. The wrapper classes are `.brx-popup` > `.brx-popup-content` + `.brx-popup-backdrop`.

## Popup settings keys

### Layout & style
| Key | Type |
|-----|------|
| `popupContentWidth` / `popupContentMinWidth` / `popupContentMaxWidth` | unit string |
| `popupContentHeight` / `popupContentMinHeight` / `popupContentMaxHeight` | unit string |
| `popupContentPadding` | spacing object |
| `popupContentBackground` | background object |
| `popupContentBorder` / `popupContentBoxShadow` | border / shadow objects |
| `popupJustifyConent` / `popupAlignItems` | flex values — position popup on screen (`flex-end` + padding = corner toast) |
| `popupPadding` | spacing around viewport edge |
| `popupBackground` | backdrop background |
| `popupDisableBackdrop` | `true` → page stays interactive (toast/notification style) |
| `popupBackdropTransition` | transition string |
| `popupZindex` | number |

### Behavior
| Key | Effect |
|-----|--------|
| `popupCloseOn` | `backdrop` \| `esc` \| `none` — default both backdrop+esc |
| `popupBodyScroll` | `true` allows body scrolling while open |
| `popupDisableAutoFocus` | skip focusing first focusable |
| `popupScrollToTop` | scroll popup content to top on open |
| `popupShowAt` / `popupShowOn` + `popupBreakpointMode` | breakpoint-limited display |

### Frequency limits
| Key | Limit per |
|-----|-----------|
| `popupLimitWindow` | page load |
| `popupLimitSessionStorage` | browser session |
| `popupLimitLocalStorage` | visitor (persistent) |
| `popupLimitTimeStorage` | show again after N hours |

### AJAX content
`popupAjax: true` fetches content on open (fresh dynamic data); loader: `popupAjaxLoaderAnimation` (`spinner` `ring` `ellipsis` `ripple` …), `popupAjaxLoaderColor`, `popupAjaxLoaderScale`. WooCommerce quick view: `popupIsWoo: true`.

## Triggering popups

### From any element — interaction
```json
"_interactions": [ { "id": "opn001", "trigger": "click", "action": "show", "target": "popup", "templateId": 123 } ]
```

`templateId` = the popup template's post ID. Close: `action: "hide"` with `target: "popup"` (inside the popup, a close button uses this with its own `templateId`).

### Auto-open on load / delay / exit intent
Put the interaction on the popup template itself (template settings → interactions) or any always-present element:

```json
{ "trigger": "contentLoaded", "delay": "5s", "action": "show", "target": "popup", "templateId": 123 }
{ "trigger": "mouseleaveWindow", "action": "show", "target": "popup", "templateId": 123, "runOnce": true }
{ "trigger": "scroll", "scrollOffset": "60%", "action": "show", "target": "popup", "templateId": 123, "runOnce": true }
```

Pair with `popupLimitLocalStorage: 1` so returning visitors aren't nagged.

### Template conditions decide where the popup is *available*
A popup only renders (hidden) on pages matching its template conditions — set `templateConditions` (see templates.md). `{ "main": "any" }` = site-wide.

## Popups in query loops

A popup opened from inside a loop item can show that item's data:

```json
{ "trigger": "click", "action": "show", "target": "popup", "templateId": 456,
  "popupContextType": "post", "popupContextId": "{post_id}" }
```

With `popupAjax: true` on the popup, content renders with the clicked post's context — the "card click → detail modal" pattern.

## Close button inside the popup

```json
{ "id": "cls001", "name": "icon", "parent": "...", "children": [],
  "settings": {
    "icon": { "library": "themify", "icon": "ti-close" },
    "_position": "absolute", "_top": "16px", "_right": "16px", "_cursor": "pointer",
    "_interactions": [ { "id": "cls0in", "trigger": "click", "action": "hide", "target": "popup", "templateId": 123 } ]
  } }
```

(Backdrop/ESC close work by default unless `popupCloseOn: "none"`.)

## Notes

- Popup content is a normal element tree — forms, loops, videos all work inside.
- Scroll-locking is on by default; toast-style popups want `popupDisableBackdrop: true` + `popupBodyScroll: true` + corner alignment.
- For accessibility Bricks traps focus and restores it on close; keep a visible close control.
