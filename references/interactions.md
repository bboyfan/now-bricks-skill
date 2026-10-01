# Interactions & Animations (`_interactions`)

Event → action bindings on any element: entrance animations, toggles, popups, load-more, custom JS. Verified against `includes/interactions.php` + `includes/setup.php` (2.3.6).

## Shape

```json
"_interactions": [
  {
    "id": "int1ab",
    "trigger": "enterView",
    "action": "startAnimation",
    "animationType": "fadeInUp",
    "animationDuration": "0.6s",
    "animationDelay": "0.1s",
    "target": "self",
    "runOnce": true
  }
]
```

Array of interaction objects. `id` = unique 6-char string. `target`: `self` (default) | `custom` (+ `targetSelector`) | `popup` (+ `templateId`).

## Triggers

| Trigger | Extra keys | Fires on |
|---------|-----------|----------|
| `click` | `disablePreventDefault` | click on the element |
| `mouseover` / `mouseenter` / `mouseleave` | | hover states |
| `focus` / `blur` | | form/keyboard focus |
| `enterView` | `rootMargin` (e.g. `"0px 0px -20% 0px"`) | element scrolls into viewport |
| `leaveView` | | leaves viewport |
| `scroll` | `scrollOffset` (px or %) | page scrolled past offset |
| `contentLoaded` | `delay` (`"2s"`) | page load (+delay) |
| `mouseleaveWindow` | | exit intent |
| `animationEnd` | `animationId` | chain after another interaction's animation |
| `ajaxStart` / `ajaxEnd` | `ajaxQueryId` | query filter AJAX lifecycle |
| `filterOptionEmpty` / `filterOptionNotEmpty` | `filterElementId` | filter results state |
| `formSubmit` / `formSuccess` / `formError` | `formId` (`"#brxe-abc123"`) | form lifecycle |
| `wooAddedToCart` `wooRemovedFromCart` `wooUpdateCart` `wooCouponApplied` … | | WooCommerce events |

## Actions

| Action | Extra keys |
|--------|-----------|
| `show` / `hide` | — (with `target: "popup"` + `templateId` opens/closes popups) |
| `startAnimation` | `animationType`, `animationDuration` (`"0.5s"`), `animationDelay` |
| `setAttribute` / `removeAttribute` / `toggleAttribute` | `actionAttributeKey`, `actionAttributeValue` — toggle classes via key `class` |
| `click` | simulate click on target |
| `scrollTo` | `scrollToOffset`, `scrollToDelay` |
| `toggleOffCanvas` | `offCanvasSelector` |
| `loadMore` | `loadMoreQuery` (query element id) |
| `javascript` | `jsFunction` (global fn name), `jsFunctionArgs` (strings; `%brx%` passes `{source, target}` elements) |
| `storageAdd` / `storageRemove` / `storageCount` | `storageType` (`localStorage` `sessionStorage` `windowStorage`), `actionAttributeKey`, `actionAttributeValue` |
| `clearForm` | `targetFormSelector` |

## Conditions on interactions

```json
"interactionConditions": [
  { "conditionType": "localStorage", "storageKey": "promo_dismissed", "storageCompare": "notExists" }
],
"interactionConditionsRelation": "and"
```

`storageCompare`: `exists` `notExists` `==` `!=` `>=` `<=` `>` `<` (+ `storageCompareValue`). Combine with `storageAdd` for "show once" UX.

## Animation types (Animate.css, full list)

**Entrances:** `fadeIn` `fadeInUp` `fadeInDown` `fadeInLeft` `fadeInRight` `fadeInUpBig` `fadeInDownBig` `fadeInLeftBig` `fadeInRightBig` `fadeInTopLeft` `fadeInTopRight` `fadeInBottomLeft` `fadeInBottomRight` `zoomIn` `zoomInUp` `zoomInDown` `zoomInLeft` `zoomInRight` `slideInUp` `slideInDown` `slideInLeft` `slideInRight` `backInUp` `backInDown` `backInLeft` `backInRight` `bounceIn` `bounceInUp` `bounceInDown` `bounceInLeft` `bounceInRight` `flipInX` `flipInY` `lightSpeedInLeft` `lightSpeedInRight` `rotateIn` `rotateInUpLeft` `rotateInUpRight` `rotateInDownLeft` `rotateInDownRight` `jackInTheBox` `rollIn`

**Exits:** `fadeOut*` `zoomOut*` `slideOut*` `backOut*` `bounceOut*` `flipOutX/Y` `lightSpeedOut*` `rotateOut*` `hinge` `rollOut` (mirror the In names)

**Attention:** `bounce` `flash` `pulse` `rubberBand` `shakeX` `shakeY` `headShake` `swing` `tada` `wobble` `jello` `heartBeat` `flip`

Elements whose first interaction is a `startAnimation` with an `*In*` type are hidden until triggered (`data-interaction-hidden-on-load`) — no flash of unstyled content.

## Recipes

**Scroll-reveal cards with stagger:**
```json
"_interactions": [ { "id": "rev001", "trigger": "enterView", "action": "startAnimation", "animationType": "fadeInUp", "animationDuration": "0.5s", "animationDelay": "0.15s", "target": "self", "runOnce": true } ]
```
For per-card stagger in a static grid, increase `animationDelay` per card (0s / 0.1s / 0.2s).

**Open popup on click:**
```json
[ { "id": "pop001", "trigger": "click", "action": "show", "target": "popup", "templateId": 123 } ]
```

**Exit-intent popup, once per visitor:**
```json
[
  { "id": "exi001", "trigger": "mouseleaveWindow", "action": "show", "target": "popup", "templateId": 123, "runOnce": true,
    "interactionConditions": [ { "conditionType": "localStorage", "storageKey": "exit_seen", "storageCompare": "notExists" } ] },
  { "id": "exi002", "trigger": "mouseleaveWindow", "action": "storageAdd", "storageType": "localStorage", "actionAttributeKey": "exit_seen", "actionAttributeValue": "1", "runOnce": true }
]
```

**Toggle a class (e.g. open a custom mega menu):**
```json
[ { "id": "tgl001", "trigger": "click", "action": "toggleAttribute", "actionAttributeKey": "class", "actionAttributeValue": "is-open", "target": "custom", "targetSelector": "#mega-menu" } ]
```

**Load more posts:**
```json
[ { "id": "lod001", "trigger": "click", "action": "loadMore", "loadMoreQuery": "loop01" } ]
```

**Show loader during filter AJAX:**
```json
[
  { "id": "ldr001", "trigger": "ajaxStart", "ajaxQueryId": "loop01", "action": "show", "target": "custom", "targetSelector": "#grid-loader" },
  { "id": "ldr002", "trigger": "ajaxEnd",  "ajaxQueryId": "loop01", "action": "hide", "target": "custom", "targetSelector": "#grid-loader" }
]
```

## CSS-first alternatives (prefer when sufficient)

- Hover effects → `_transform:hover` + `_cssTransition` (no JS).
- Sticky header styling → header template settings (`headerSticky`, `headerStickyScrolling*` — see templates.md).
- Parallax → `_motionElementParallax` + `_motionElementParallaxSpeedY` (2.3+), no interaction needed.
- Marquee/complex scroll-linked animation → `_cssCustom` with `@keyframes` or `animation-timeline: scroll()`.

## Notes

- Interactions also live on **global classes** (class settings `_interactions`) — applies to every element with the class.
- Popup templates can carry their own interactions in template settings.
- Don't combine `runOnce` with state toggles users may repeat.
