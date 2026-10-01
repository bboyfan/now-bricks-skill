# Bricks Reference: 05 Custom Code And Extensions



---

## Module: bricks-custom-code

# Bricks: custom code

Bricks has eight places code can live. Each has different capability gates, different security properties, and different silent-failure modes. Get the extension point wrong and the code either doesn't run, runs in the wrong context, or opens a remote-code-execution hole. Use it to choose the right extension point and apply the right rules.

## The eight extension points

| Point | What | Gated by | Runs |
|-------|------|----------|------|
| Echo tag `{echo:fn()}` | PHP function call inside dynamic data | Global code execution + allow-list; builder preview also checks Execute code cap | Per-tag render, server-side |
| Hooks | WP actions/filters in functions.php / plugin | None (it's just WP) | Globally, wherever the hook fires |
| Code element: PHP mode | PHP inside a Bricks Code element | Global code execution + valid signature; authoring/signing checks Execute code cap | Element render, server-side |
| Code element: snippet mode | Escaped HTML/CSS/JS shown as a code sample | Normal editing permissions | Element render, displayed in `<pre>` |
| Theme style CSS | CSS tied to a theme style | None | Concatenated into page `<head>` |
| Page / element custom CSS | CSS scoped to a page or one element | None | Inline `<style>` in header |
| Settings > Custom code | Header/body/footer HTML/JS/CSS | Admin-only | Globally, on every page |
| Custom Query PHP | PHP inside the query-loop PHP editor | Global code execution + valid signature; authoring/signing checks Execute code cap | Query run, server-side |

## "Execute code" capability: what it gates

For builder authoring, the user role needs the `bricks_execute_code` capability to add or keep executable code paths such as Code element PHP mode, SVG source code, Custom Query PHP, and builder-preview echo execution. On the frontend, saved executable code is governed by global code execution, code signatures, and the echo allow-list, not the visitor's role.

- Set globally at `Bricks > Settings > Custom code > Code execution`.
- Per-role via the Bricks role manager.
- Canonical check inside your PHP: `Capabilities::current_user_can_execute_code()`: use this, not role-name comparison.
- **Never grant to Editor-tier roles on a site where staff isn't fully trusted**: it's direct RCE for them.

Code elements display escaped snippets when Execute code is absent. Their execution mode requires global code execution even for CSS/JS-only output (`includes/elements/code.php::render`). This is distinct from native style controls and `_cssCustom`, which do not require PHP opt-in. Save-time security also depends on the caller’s effective capabilities. Site-wide Settings > Custom code is an admin settings surface, not normal post editing.

## Code authoring through abilities

Bricks 2.4 distinguishes CSS, JavaScript, and PHP authoring in
`includes/abilities/code-authoring.php` and `elements.php`:

- CSS follows the target's editing permissions. JavaScript and unsafe raw HTML
  require WordPress `unfiltered_html`; a role name is not a capability check.
- Code elements keep their native execution-mode gate. A PHP/HTML field in execution
  mode still needs signing even when its current text contains only HTML. Dynamic
  code sources also stay on the PHP authorization path.
- Creating or changing signed PHP in Code elements or Query editors through abilities
  requires `BRICKS_ENABLE_PHP_ABILITIES === true`, Bricks abilities and global code
  execution enabled, unlocked signature generation, `manage_options`, the Bricks
  Execute code capability, and an authenticated WordPress Application Password
  request. The old prerelease `BRICKS_ENABLE_EXECUTE_PHP_ABILITY` name is not used.
- Authorized writers generate signatures. Do not fabricate or copy signatures, and
  do not reconstruct redacted source. Unchanged protected code can be preserved
  while editing permitted neighboring settings.
- `bricks/execute-php` uses the same PHP authorization contract. It executes supplied
  statements on the server without sandboxing; use it only for the user's requested
  work, including authorized PHP configuration or diagnostics. Do not use it to
  grant itself missing permissions or bypass a disabled ability.

For an import rejected by these checks, rewrite unsupported content or report the
missing prerequisite. The HTML/CSS page importer may retain a permitted partial
result; inspect `partial` and `omittedElements` as described in
[bricks-html-css-to-bricks](../bricks-html-css-to-bricks/SKILL.md).

## Render order: why your override loses

Bricks builds several CSS buckets first, then concatenates them in a fixed order in `Assets::generate_inline_css()`. Use the actual concatenation order, not the setup-comment order (`includes/assets.php:832-909`). Later buckets win at equal specificity:

1. **Global variables**: `:root` variable CSS from the variable manager
2. **Theme styles**: concatenated theme-style CSS
3. **Utility classes**: style-manager utility classes when CSS loading is inline
4. **Global CSS classes**: site-wide class definitions
5. **Color vars**: palette custom properties, including dark-mode vars
6. **Page custom CSS**: page settings CSS
7. **Header**: header-template element CSS
8. **Content**: page/content-template element CSS
9. **Footer**: footer-template element CSS
10. **Popup**: active popup template CSS
11. **Template CSS**: template settings CSS
12. **Global custom CSS**: Settings > Custom code global CSS

Inline `style` attributes and later stylesheets still participate in the CSS cascade. A style rule emitted by an executing Code element does not automatically win merely because it sits inside the body.

Two implications:
- If your theme-style CSS isn't winning, something later won on specificity or used `!important`. Don't escalate with more `!important`: fix the source.
- Settings > Custom code global CSS is appended late, so it can override page and element CSS at equal specificity. Use it for true global overrides only; otherwise prefer theme styles, global classes, page CSS, or element CSS based on the scope of the change.

JavaScript: Settings > Custom code body/footer runs on every page, in document order. JavaScript from an executing Code element runs where its script is emitted. Initialize against the correct document-ready state; snippet mode only displays code.

## Echo tag: `{echo:function_name()}`

Echo calls a PHP function from content, so keep its allow-list limited to the functions needed by the site.

### The allow-list filter

Echo is unavailable unless global code execution is enabled. Once enabled, each `{echo:...}` call still returns an empty string until the function passes `bricks/code/echo_function_names`:

```php
add_filter( 'bricks/code/echo_function_names', function() {
    return [
        '@^my_theme_',          // regex prefix (1.9.8+): whitelist your own helpers
        'wp_get_attachment_image',
        'get_the_date',
        'get_post_meta',
    ];
} );
```

Return shapes:
- **Array of literal names**: exact-match allow-list.
- **Array with `@` prefix entries**: regex (1.9.8+). `'@^brx_'` matches anything starting with `brx_`.
- **Boolean `true`**: allow-all. **Never in production**: that's the pre-1.9.7 RCE surface.

### Argument parsing (from `provider-wp.php:1260-1318`)

- Single quotes delimit strings. `{echo:foo('bar')}` passes `'bar'`.
- Commas separate args at the top level.
- No nested functions, objects, arrays, or double-quoted strings: write a wrapper function if you need them.
- Unquoted args pass as strings. `{echo:foo(42)}` passes `"42"`, not integer 42.

### Never allow-list

- **Callable-accepting functions**: `call_user_func`, `call_user_func_array`, `array_map`, `usort`, `preg_replace_callback`. Universal RCE pivots.
- **Command execution**: `shell_exec`, `exec`, `system`, `passthru`, `proc_open`, `popen`.
- **Code evaluators**: `eval`, `assert`, `create_function`, `preg_replace` with `/e` modifier.
- **Deserializers on attacker input**: `unserialize`, `maybe_unserialize`. JSON is usually fine.
- **Filesystem / network**: `file_get_contents`, `fopen`, `curl_exec`, `glob`, `scandir`, `readfile`, `file_put_contents`.

### Other echo rules

- **`bricks/code/echo_everywhere`** (undocumented filter): by default echo runs only in text-ish fields (heading, rich text). Setting this to `true` opens it to style values, URLs, etc. Expands the attack surface; only do it with a reason.
- **Builder-preview guard (1.12.2+)**: unauthorized users can't *add* new echo calls via the UI even when the function is allow-listed. Blocks staff-role privilege escalation.
- **Code Review tool**: `Bricks > Settings > Custom code`, button `Start: Code review`. It scans Code elements, SVG source code, Query editor snippets, and echo functions. Run it before shipping an echo allow-list. Academy: https://academy-preview.bricksbuilder.io/builder/features/code-review/

### Defensive wrapping

Wrap functions with explicit argument validation before adding them to the allow-list:

```php
function my_theme_post_title_by_id( $id ) {
    $id = absint( $id );
    if ( ! $id ) return '';
    return esc_html( get_the_title( $id ) );
}
```

Allow-list `my_theme_post_title_by_id`, not `get_the_title`. The wrapper validates and escapes.

## Hooks: the PHP extension point

Hooks don't need Bricks capability gating: they're WordPress actions/filters. Three things go wrong most often:

1. **Filters must return.** Callback forgets `return $value` and the filter value becomes `null`, breaking everything downstream.
2. **Priority contention.** Bricks fires many of its own hooks at priority 10. If you're overriding (not just observing), use priority 20+.
3. **Scope to the loop/element.** Most Bricks hooks pass a context object (`$query`, `$element`) with `element_id`. Branch on `element_id` inside the callback to avoid mutating every loop/element on the page.

See the `bricks-hooks-reference` skill for a curated hook index.

## Code element: snippet versus execution mode

Two modes:

- **Snippet mode** (default): HTML, CSS, and JavaScript fields are escaped and displayed as code samples. They do not run.
- **Execute code**: PHP/HTML is verified and evaluated, CSS is emitted in a style element, and JavaScript in a script element. Global code execution must be enabled. Authoring requires Execute code; the PHP/HTML field additionally needs a valid signature.

If a snippet appears as text, first decide whether the user intended a code example
or running content. Do not enable execution just to hide the symptom. For running
content through abilities, follow the authorization rules above. For styling native
elements, prefer native controls or `_cssCustom` instead of an executing Code element.
For site-wide JavaScript, use the authorized global custom-code surface or an enqueue.

## Custom Query (PHP) in query loops

Last-resort query-loop option when the UI can't express the query. Gated by `bricks_execute_code`. Expects a PHP array of query args for normal object queries. Non-array output is ignored after validation and may fall back to the remaining query vars or produce an empty loop depending on context.

**Prefer `bricks/posts/query_vars` hook.** Keep shared query logic in version-controlled PHP using this hook.

## MCP: `_cssCustom` requires a selector wrapper

When setting element custom CSS via the MCP (`set-page-elements`, `add-element`, `update-element`), write a complete CSS rule with the persisted Bricks selector. The selector is part of the saved data.

### Which selector to use

| Context | Selector form | Example |
|---|---|---|
| Standalone page element | `#brxe-{id}` | `#brxe-wxb5dn { ... }` |
| Element inside a component | `.brxe-{id}` | `.brxe-wxb5dn { ... }` |
| Global class | `.{class-name}` | `.button { ... }` |

Standalone elements render with an `id="brxe-{id}"` attribute, so the ID selector is correct and more specific. Elements inside a component use the class selector because component instances may not have a unique ID in the same way.

The element ID (`wxb5dn`) comes from the internal 6-character `id` field in `get-page-elements` output, or from the response of `add-element` / `set-page-elements`. This same id powers the default frontend selector `#brxe-{id}`. Only set `settings._cssId` when a custom HTML id is explicitly needed.

### Format: use newlines, not single-line strings

```css
/* Correct */
#brxe-wxb5dn {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-lg);
}

/* Correct for a global class */
.button {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
}

/* Wrong selector type for a standalone page element */
.brxe-wxb5dn { display: grid; }
```

In JSON strings, use `\n` for newlines and two-space indent: `"#brxe-wxb5dn {\n  display: grid;\n  grid-template-columns: repeat(3, 1fr);\n  gap: var(--space-lg);\n}"`

## Silent-failure debug order

"My code doesn't run" or "output is empty." Check in order:

1. **Execution gate**: Settings > Custom code > Code execution toggled on. In the builder, also confirm the user's role has Execute code.
2. **Allow-list** (echo only): check whether the exact intended function is permitted by `bricks/code/echo_function_names`. Do not enable every function as a diagnostic shortcut.
3. **Mode toggle** (Code element only): Execute Code on/off correct for the content type.
4. **Hook plumbing**: filter callback is returning (not just mutating). Priority not being overwritten by something later.
5. **Runtime failure handling**: echo catches `Exception`, `ParseError`, and `Error`, then logs to `error_log()` (`provider-wp.php:1381-1394`). Code element PHP catches `Throwable` and either shows the error or suppresses output based on the element setting (`code.php:235-251`). Custom Query PHP echoes the caught error message during query building (`query.php:410-420`).
6. **CSS losing cascade**: DevTools -> Rules panel -> find the overriding selector. Usually element-level CSS trumping theme style, or specificity elsewhere.

## Decision tree: "I want to X"

| Want | Reach for |
|------|-----------|
| Show dynamic value in text | Dynamic data tag (prefer built-in tags over `{echo:}`) |
| Call a custom PHP function in text | Echo tag + allow-list entry |
| Site-wide analytics / pixels | Settings > Custom code (header/body/footer) |
| Per-page tracking snippet | Page settings -> custom code, or a Code element on that page |
| Global CSS tweak | Theme style CSS (not per-element) |
| One-off page CSS | Page custom CSS |
| Single element styling | Element custom CSS: last resort |
| Modify a loop's query args | `bricks/posts/query_vars` hook, not Custom Query PHP |
| Modify element render output | `bricks/element/render_*` hook |
| Inject HTML conditionally | Template element with conditions, not a Code element |
| Reusable PHP logic | Child theme / plugin with hooks, not scattered Code elements |

## Never trust builder input from low-privileged roles

Even inside Bricks, staff-tier users can modify element fields. If a filter or hook trusts a field value raw and passes it to `eval`, `include`, a callable, or shell-exec, that's RCE for staff. Treat any field that could originate from a non-admin editor as untrusted.

## Never do

- `return true` from `bricks/code/echo_function_names` in production. Ever.
- Allow-list callable-taking, filesystem, network, deserialize, or code-eval functions.
- Enable `bricks/code/echo_everywhere` "because a tag isn't rendering." Find the real reason first.
- Let `{echo:...}` arguments come from user input: URL params, form fields, REST payloads.
- Put PHP in a Code element when a hook would work: it's hiding from version control and audit tools.
- Stack `!important` in element CSS to win a cascade battle. Fix the actual specificity.
- Grant `bricks_execute_code` to Editor-tier roles on multi-tenant sites.


---

## Module: bricks-custom-elements

# Bricks: custom elements

A **custom element** is a PHP class extending `\Bricks\Element` that adds a new element type to the Bricks builder's element panel. Ship it through a child theme or plugin.

## The minimal element

```php
<?php
namespace MyTheme\Bricks;

if ( ! defined( 'ABSPATH' ) ) exit;

class Pricing_Card extends \Bricks\Element {
    public $category     = 'general';       // Element panel category
    public $name         = 'pricing-card';  // Unique slug
    public $icon         = 'ti-layout-grid3-alt'; // Themify Icons class
    public $css_selector = '.pricing-card'; // Root selector for CSS rules
    public $scripts      = [ 'bricksPricingCard' ]; // frontend JS callbacks (optional)

    public function get_label() {
        return esc_html__( 'Pricing Card', 'my-theme' );
    }

    public function set_control_groups() {
        $this->control_groups['plan'] = [
            'title' => esc_html__( 'Plan', 'my-theme' ),
            'tab'   => 'content',
        ];
    }

    public function set_controls() {
        $this->controls['planName'] = [
            'group' => 'plan',
            'label' => esc_html__( 'Plan name', 'my-theme' ),
            'type'  => 'text',
            'default' => 'Pro',
        ];
        $this->controls['price'] = [
            'group' => 'plan',
            'label' => esc_html__( 'Price', 'my-theme' ),
            'type'  => 'text',
            'default' => '$29/mo',
        ];
    }

    public function render() {
        $name  = isset( $this->settings['planName'] ) ? $this->settings['planName']: '';
        $price = isset( $this->settings['price'] ) ? $this->settings['price']: '';

        $this->set_attribute( '_root', 'class', 'pricing-card' );
        $root = $this->render_attributes( '_root' );

        echo "<div {$root}>";
        echo '<h3>' . esc_html( $name ) . '</h3>';
        echo '<p class="price">' . esc_html( $price ) . '</p>';
        echo '</div>';
    }
}
```

Save as `your-theme/bricks/elements/pricing-card.php`.

## Registration

Hook into `bricks/load_elements/after`: fires in `includes/elements.php:263` after Bricks has loaded its own elements.

```php
add_action( 'bricks/load_elements/after', function() {
    require_once get_stylesheet_directory() . '/bricks/elements/pricing-card.php';
    \Bricks\Elements::register_element(
        get_stylesheet_directory() . '/bricks/elements/pricing-card.php',
        'pricing-card',
        'MyTheme\\Bricks\\Pricing_Card'
    );
} );
```

`Elements::register_element()` signature (`elements.php:219`):
- Arg 1: absolute file path (for reload detection)
- Arg 2: element name (must match class's `$name`)
- Arg 3: fully-qualified class name

**If you omit args 2 & 3**, Bricks auto-discovers the class via `get_declared_classes()`: works but is fragile. Explicit registration is better.

## Methods to override

The base `Element` class provides defaults. Override only what the element needs:

| Method | File:line | Purpose |
|---|---|---|
| `get_label()` | base.php | Return the translated element name. The base fallback derives a label from `$name`. |
| `set_control_groups()` | base.php:239 | Optional. Populate `$this->control_groups` array when you need custom groups. |
| `set_controls()` | base.php:246 | Populate `$this->controls` array for element settings. |
| `render()` | base.php:2772 | Frontend HTML output and PHP AJAX builder output for elements without an x-template. |
| `render_builder()` | base.php:2779 | Optional static method. Echoes the builder x-template script when you want a Vue-rendered preview. |

**Most elements override only** `get_label()` + `set_controls()` + `render()`. `set_control_groups()` only if you want tabs beyond the default `content` / `style`.

## Public properties

| Property | Type | Purpose |
|---|---|---|
| `$category` | string | `'general'` / `'layout'` / `'media'` / `'seo'` / `'woocommerce'` / custom: element panel group |
| `$name` | string | Unique slug (hyphen-case). Must match `register_element`'s arg 2. |
| `$icon` | string | Themify Icons class (default icon set in Bricks) |
| `$css_selector` | string | Selector used by Bricks' CSS generator to scope controls: usually the element's root class |
| `$scripts` | array | Names of JS callbacks Bricks should call on frontend init |
| `$nestable` | bool | Whether this element accepts arbitrary children. Default `false` (base.php:57) |
| `$tag` | string | Default HTML tag for the root wrapper (`'div'` typically) |
| `$controls` | array | Populated by `set_controls()` |
| `$settings` | array | Resolved settings for the current instance (populated by Bricks at render time) |
| `$is_frontend` | bool | True on frontend, false in builder context (base.php:40, 72) |

## Render parity: the builder-vs-frontend trap

Your `render()` method runs on the frontend. In the builder, Bricks chooses one of two render paths:

- If a script with ID `tmpl-bricks-element-{name}` exists, the iframe uses the Vue x-template (`src/vue/store/actions.js:2446`).
- If no x-template exists, the iframe uses `bricks-element-php`, which renders through PHP AJAX (`src/vue/store/actions.js:2451`, `src/vue/iframe.js:71`).

Two options:

### Option 1: Server-rendered in both contexts

Omit `render_builder()`. Bricks will not print an x-template for the element, so the builder falls back to the PHP render path.

Tradeoff: slower builder (round-trip per edit), but guaranteed visual parity.

### Option 2: Mirror logic in Vue x-template

Override static `render_builder()` and echo a script template that reproduces your PHP render logic client-side. `Builder::element_x_templates()` calls each registered element class's `render_builder()` in the builder iframe (`includes/builder.php:186`).

```html
<script type="text/x-template" id="tmpl-bricks-element-pricing-card">
    <div class="pricing-card">
        <h3>{{ settings.planName }}</h3>
        <p class="price">{{ settings.price }}</p>
    </div>
</script>
```

Tradeoff: faster builder, but you maintain two render paths.

**Rule of thumb:** if your element has heavy PHP logic (queries, complex formatting), use Option 1. If it's mostly presentation, use Option 2.

## Dynamic data inside custom elements

To support `{post_title}` inside your element's text control:

```php
$name = $this->render_dynamic_data( $this->settings['planName'] );
```

This runs the value through Bricks' dynamic-data pipeline. Without it, `{post_title}` renders literally.

## Root attributes: `render_attributes()`

Bricks generates classes, `id`, custom attributes from the element's panel (ID/Class control, custom attributes control). Emit via:

```php
$root_attrs = $this->render_attributes( '_root' );
echo "<div {$root_attrs}>...</div>";
```

`_root` is the default selector key. For non-root wrappers, define additional selectors in your controls with a `css` key and call `render_attributes('my-custom-selector')`.

## Frontend JS integration

Use the element's `enqueue_scripts()` method for its assets and declare a named
initializer in `$scripts` for Bricks' render/update lifecycle. The initializer must
handle repeated calls and newly inserted nodes without duplicating listeners.

```js
function examplePricingCard() {
  bricksQuerySelectorAll(document, '.pricing-card').forEach((element) => {
    if (element.dataset.examplePricingCardReady) return
    element.dataset.examplePricingCardReady = 'true'
    // Attach the element's actual event handlers here.
  })
}
```

`bricksQuerySelectorAll` takes `(parentNode, selector)`. Register
`public $scripts = [ 'examplePricingCard' ];` and enqueue the file with the
`bricks-scripts` dependency. For stateful widgets, update existing instances or
clean them up before rebuilding when settings change; a ready marker alone is
sufficient only for initialization that remains valid for the existing node.

See [custom element lifecycle](https://academy.bricksbuilder.io/developer/elements/create-your-own-elements/).

## Control types available (recap)

See the `bricks-custom-controls` skill for the complete list. The big ones: `text, textarea, number, select, checkbox, color, typography, background, border, box-shadow, spacing, dimensions, icon, image, repeater, code, query, query-list, link`.

## Common patterns

### Control visibility: `required`

Show one control only when another has a specific value:

```php
'highlightColor' => [
    'label'    => 'Highlight color',
    'type'     => 'color',
    'required' => [ 'highlight', '=', true ],  // only when `highlight` control is true
],
```

### Default value + CSS property binding

```php
'cardPadding' => [
    'label'   => 'Padding',
    'type'    => 'dimensions',
    'css'     => [
        [
            'property' => 'padding',
            'selector' => '',  // empty = apply to the css_selector root
        ],
    ],
    'default' => [ 'top' => '20px', 'right' => '20px', 'bottom' => '20px', 'left' => '20px' ],
],
```

Bricks generates CSS from `css` entries automatically: no need to emit style in `render()`.

## Nestable custom elements

Set `$this->nestable = true;` in the constructor (pre-1.9) or as a class property (1.9+). Then override `get_nestable_item()` to return the default child template.

See `bricks-nestable-elements` skill for the full contract.

## Silent-failure debug order

1. **Element doesn't appear in builder panel?**
   a. `register_element()` not called. Check the hook firing.
   b. Class namespace wrong. Fully-qualified name required.
   c. File not loaded: `require_once` path wrong.

2. **Element shows in builder but blank?**
   a. `render()` missing or empty.
   b. `render()` calling undefined methods / throwing. Check `wp-content/debug.log`.

3. **Dynamic tags render literally (`{post_title}` as text)?**
   a. Missing `render_dynamic_data( $value )` wrap.

4. **Controls show but changes don't persist?**
   a. Control name mismatch: the key in `set_controls()` must match what you read in `render()` via `$this->settings[key]`.

5. **Builder preview looks broken; frontend fine?**
   a. The x-template returned by `render_builder()` does not match `render()`, or the PHP fallback throws during the builder AJAX render.

6. **CSS from `css` controls not applying?**
   a. Selector in `css` entry doesn't match what `render()` emits. Bricks scopes to `.brxe-{name}` by default: verify the root class.

## Testing

- Local install with `WP_DEBUG` + `WP_DEBUG_LOG` on.
- Add the element to a test page.
- Frontend view -> check HTML output matches expectations.
- Builder view -> check preview matches frontend.
- Save -> reload builder -> values persist.
- MCP: `get-page-elements` includes your element in the tree, and `get-element-schema` returns its controls when the element is registered.

## Never do

- Echo `<script>` tags inside `render()`. Use proper enqueue via `wp_enqueue_script`.
- Skip `esc_html`/`esc_attr` on user-provided settings values. Bricks' settings pipeline sanitizes at save time but values can drift.
- Hard-code strings without `__()` / `esc_html__()`. Bricks is multi-lingual.
- Call WP template-loading functions (`get_header`, `get_footer`) inside `render()`: you're inside the page already.
- Register elements on plugins-loaded or similar early hooks. `bricks/load_elements/after` is the right moment.
- Override `$this->settings` directly in `render()`: it's populated by Bricks; treat as read-only.
- Skip `render_attributes('_root')` when emitting the root element. You lose the ID/Class panel bindings.

## Related skills

- `bricks-custom-controls`: control type reference and patterns.
- `bricks-custom-code`: where element PHP fits among the 7 extension points.
- `bricks-hooks-reference`: hooks like `bricks/element/render_attributes` for post-render tweaks.
- `bricks-child-theme-patterns`: where to put element files in a child theme.


---

## Module: bricks-custom-controls

# Bricks: custom controls

Controls are the panel inputs users see when they select an element. Each control maps to a `type` from Bricks' registry. Use this as the reference: what types exist, how to bind them to CSS automatically, how to conditionally show them, and how to enable dynamic data.

Pair with `custom-elements` for the full element-authoring flow.

> **If a `bricks/*` ability is not available as a direct tool**: first check whether it is outside the fast path and call it through `mcp-adapter-execute-ability` with `ability_name: "bricks/<name>"`. If the dispatcher also rejects it, call `bricks-list-ability-status` to check whether a site admin disabled it under Bricks > AI.

## Getting the canonical type list

The list below is the durable set, but exact shape and option list per type depend on the Bricks version. Canonical sources, in order of authority:

1. **Runtime MCP schema:** call `mcp-adapter-execute-ability` with `ability_name: "bricks/get-element-schema"` and `parameters: { "elementName": "<name>" }`. It returns the full control tree for one element and is dispatcher-only on the default Bricks MCP server.
2. **`includes/html-to-bricks/control-index.generated.php`**: every CSS-bound control across the element library, generated by `scripts/generate-control-index.mjs`.
3. **Grep `/includes/elements/*.php` for `'type' =>`**: source of truth, but noisy: you'll hit sub-control values (`'type' => 'monthly'` inside a select option) mixed with real control types.

## The ~40 control types

As of Bricks 2.x (verified by running the grep in sections 1-3 above against `/includes/elements/*.php`):

### Input controls
- `text`: single-line string input
- `textarea`: multi-line string
- `email`: email-validated input
- `number`: numeric input (`min`, `max`, `step` supported)
- `code`: CodeMirror editor (common modes include `css`, `javascript`, `text/html`, `htmlmixed`, `application/json`, and `application/x-httpd-php-open`)
- `editor`: TinyMCE rich text editor

### Choice controls
- `checkbox`: boolean toggle
- `select`: dropdown (pass `options` array)

### Style tokens
- `color`: color picker, integrates with theme palette
- `background`: background composite (color, gradient, image)
- `gradient`: gradient picker
- `border`: border composite (width, style, color, radius)
- `box-shadow`: shadow picker (multiple shadows supported)
- `text-shadow`: text shadow picker
- `typography`: composite (font-family, size, line-height, weight, letter-spacing, style)
- `text-decoration`: text decoration composite
- `spacing`: spacing shorthand
- `dimensions`: 4-side dimensions (top / right / bottom / left)
- `transform`: CSS transform composite (translate / rotate / scale / skew)
- `separator`: visual separator in the panel (not an input)

### Alignment
- `text-align`: left / center / right / justify
- `align-items`: flex align-items
- `justify-content`: flex justify-content
- `direction`: flex direction / orientation

### Media & assets
- `image`: single image (media library)
- `image-gallery`: multiple images
- `audio`: audio URL / media picker
- `video`: video URL / media picker
- `svg`: SVG upload with sanitization
- `icon`: Themify Icons / custom icon library
- `link`: link picker (internal / external / dynamic)

### Structural
- `repeater`: array of items with sub-controls
- `info`: static informational text (not an input)
- `apply`: action button (triggers a save action)

### Advanced
- `query`: query-builder UI (returns query args)
- `query-list`: dropdown of queries on the current page
- `filters`: CSS filters composite
- `datepicker`: date picker (Flatpickr)
- `comment`: comment editor used by the Post Comments element

For additional control types, search `/includes/elements/*.php` and `/includes/theme-styles/controls/*.php` for `'type' =>` to see live usage. Do not assume `radio` exists as a standalone control type unless the target schema shows it.

## Control shape

```php
$this->controls['myControl'] = [
    'group'    => 'style',          // control group tab/panel
    'label'    => 'My control',
    'type'     => 'color',
    'default'  => [ 'hex' => '#ff0000' ],
    'css'      => [ /* CSS binding: see below */ ],
    'required' => [ /* conditional visibility: see below */ ],
    'description' => 'Shown under the control as help text',
    'info'     => 'Shown above: for warnings/notes',
];
```

Keys beyond `type` are optional, but `label` + `type` are minimum. `group` references a key you defined in `set_control_groups()`: omit to put the control in the default `content` tab.

## CSS binding: the magic

Bricks generates frontend CSS from control values **automatically** when you add a `css` entry:

```php
'bgColor' => [
    'label' => 'Background',
    'type'  => 'color',
    'css'   => [
        [
            'property' => 'background-color',
            'selector' => '',  // empty = root (`.css_selector`)
        ],
    ],
],
```

For non-root selectors:

```php
'iconColor' => [
    'label' => 'Icon color',
    'type'  => 'color',
    'css'   => [
        [
            'property' => 'color',
            'selector' => '.icon-wrapper i',
        ],
    ],
],
```

You do **not** emit `<style>` in `render()`. Bricks collects every `css` entry across all controls, generates a stylesheet, and loads it (inline or file, see `bricks-performance` skill).

**Composite controls** auto-bind to multiple properties. `typography` writes `font-family`, `font-size`, `line-height`, etc.: one entry covers them all:

```php
'cardTypography' => [
    'type' => 'typography',
    'css'  => [
        [
            'property' => 'font',
            'selector' => '',
        ],
    ],
],
```

The special `'property' => 'font'` treats the typography composite as a full font shorthand.

## Conditional visibility: `required`

Show a control only when another has a specific value:

```php
'highlight' => [ 'type' => 'checkbox', 'label' => 'Highlight' ],
'highlightColor' => [
    'type'     => 'color',
    'label'    => 'Highlight color',
    'required' => [ 'highlight', '=', true ],
],
```

Syntax: `[ control_name, operator, value ]`.

Operators (confirmed from real usage across elements):
- `=` / `==`: equals
- `!=`: not equals
- `===`: strict equals
- `!==`: strict not equals

Value can be:
- Scalar (`true`, `'email'`, `42`)
- Array (matches any: `[ 'email', 'tel', 'url' ]`)

Multiple conditions (AND):

```php
'required' => [
    [ 'type', '=', 'password' ],
    [ 'passwordToggle', '=', true ],
],
```

**Nested paths supported**: dot-notation to access composite values:

```php
'required' => [ 'icon.icon', '!=', '' ],  // icon composite's inner `icon` key
```

Example from `accordion.php:143`.

## Dynamic data support: the flag

By default, most text-like controls accept dynamic data. To disable:

```php
'internalId' => [
    'type'            => 'text',
    'label'           => 'Internal ID',
    'hasDynamicData'  => false,  // blocks the dynamic-data picker
],
```

From `text.php:69`. Useful for config fields that must remain literal (selectors, attribute names).

Rule: leave it default (omit the key) for content fields. Explicitly `false` for structural IDs / selectors that shouldn't be runtime-interpolated.

## Defaults: the cascade

`default` value applies when a new element instance is added. For composite controls, `default` is an array:

```php
'padding' => [
    'type'    => 'dimensions',
    'default' => [ 'top' => '20px', 'right' => '20px', 'bottom' => '20px', 'left' => '20px' ],
],
```

**Default values are not re-applied on version bumps.** If you change a default, existing sites keep their old value. Plan accordingly.

## Placeholder

Some controls support `placeholder`: shown when empty:

```php
'heading' => [
    'type'        => 'text',
    'placeholder' => 'Enter heading',
],
```

For composites, `placeholder` can also be an array (e.g., `dimensions`).

## `info` and `description`

- `info`: shows **above** the control, styled like a warning. Use for important rules ("Requires SSL").
- `description` / `desc`: shows **below**, styled like help text. Use for "Learn more" links or clarifications.
- `content` (for `info` type controls only): the text to display for a stand-alone info block.

## Repeater controls

Array of sub-controls:

```php
'features' => [
    'type'          => 'repeater',
    'label'         => 'Features',
    'titleProperty' => 'name',   // shown in the collapsed row
    'placeholder'   => 'Feature',
    'fields'        => [
        'name'    => [ 'type' => 'text', 'label' => 'Name' ],
        'icon'    => [ 'type' => 'icon', 'label' => 'Icon' ],
        'color'   => [ 'type' => 'color', 'label' => 'Color' ],
    ],
],
```

Access in `render()`:

```php
$features = $this->settings['features'] ?? [];
foreach ( $features as $feature ) {
    echo '<div>' . esc_html( $feature['name'] ?? '' ) . '</div>';
}
```

## Query controls

- `query`: full query-builder UI (user picks post type, taxonomy, etc.).
- `query-list`: dropdown that lists queries present on the current page; returns the target query's `_id`.

Use `query-list` for elements that target existing queries (filters, pagination elements pointing at a loop).

## Link control

```php
'myLink' => [
    'type'  => 'link',
    'label' => 'Link',
],
```

Returns array:

```php
[
    'type'   => 'internal',  // or 'external', 'dynamic', 'media'
    'url'    => '...',
    'newTab' => true,
]
```

Use Bricks' `render_attributes` helper or manually construct `<a href>` + `target`.

## Icon control

Picks from Themify Icons (default) or custom icon set. Returns:

```php
[
    'library' => 'themify',
    'icon'    => 'ti-star',
    'custom'  => '',  // if library = 'custom', holds SVG markup
]
```

Emit:

```php
$icon = $this->settings['myIcon'] ?? [];
if ( ! empty( $icon['icon'] ) ) {
    echo '<i class="' . esc_attr( $icon['icon'] ) . '"></i>';
}
```

## Code control

```php
'customCss' => [
    'type' => 'code',
    'label' => 'Custom CSS',
    'mode' => 'css',
],
```

Modes are CodeMirror modes, not Bricks execution modes. Current source uses values such as `css`, `javascript`, `text/html`, `htmlmixed`, `application/json`, and `application/x-httpd-php-open` (`includes/elements/code.php:97`, `includes/elements/html.php:22`, `includes/settings/settings-page.php:531`).

A custom `code` control is just an editor unless your render logic executes the stored value. If you execute stored PHP or JS, gate that execution explicitly and follow the `bricks-custom-code` skill. `executeCode` and `signCode` enable signing UI only for controls that opt into that contract; they do not make arbitrary custom controls safe by themselves (`src/vue/components/main/panel/controls/ControlCode.vue:8`, `src/vue/components/main/panel/controls/ControlCode.vue:273`).

## Silent-failure debug order

1. **Control doesn't appear in panel?**
   a. Parent group not declared in `set_control_groups()`.
   b. `required` condition never evaluates true.

2. **CSS binding doesn't apply?**
   a. Selector in `css` entry doesn't match rendered HTML.
   b. Control has no value (default not set, user hasn't interacted).
   c. Another control with higher specificity overrides (composite wins over composite-leaf).

3. **Value from control not reaching `render()`?**
   a. Control key mismatch: `$this->controls['foo']` vs `$this->settings['bar']`.
   b. Builder not saved after control edit.

4. **Dynamic data picker missing on a text control?**
   a. `hasDynamicData` explicitly set to false somewhere in the control chain.

5. **Repeater values not persisting?**
   a. Missing `fields` array.
   b. Sub-control names conflict with parent control names (namespace collision).

## Never do

- Emit inline `<style>` from `render()` when `css` bindings can do the same. Bricks' CSS generator handles it: duplicating in PHP fights the system.
- Use `required` with a non-existent control key. Silent truthy fallback leads to always-visible controls.
- Skip `hasDynamicData: false` on structural ID / selector fields: users will type `{post_title}` and wonder why layout breaks.
- Execute values from a `code` control without your own capability gate. The control type provides an editor; your render path decides whether the value is executable.
- Ship a control with no `label`: it renders as a blank row in the panel.

## Related skills

- `custom-elements`: where controls live, full element authoring.
- `dynamic-data`: how `hasDynamicData` fits into the tag pipeline.
- `custom-code`: security model for places where Bricks actually executes stored code.


---

## Module: bricks-hooks-reference

# Bricks: hooks reference

Use this index to find a hook, then check its signature and call site in the target Bricks version before implementing a callback.

To confirm any hook and see its context in the current version, grep the source:

```bash
rg -n "apply_filters\(\s*['\"]bricks/hook_name_here" includes/
rg -n "do_action\(\s*['\"]bricks/hook_name_here" includes/
```

## The three rules that trip up every callback

1. **Filters must return**: forgetting `return $value` in a filter callback makes the value `null` for every downstream consumer. `bricks/element/render_attributes` is the most common foot-gun.
2. **Choose priority from the lifecycle**: inspect which callback must run first. A universal 20+ rule can miss registration or run after the value has already been consumed.
3. **Scope by `element_id` or post ID**: most render/query hooks pass a context object (`$query`, `$element`, `$post`). Use the ID supplied by that particular hook inside the callback to avoid mutating every loop/element on the page.

## Find the relevant hook

Read [the hook catalog](references/hooks.md) for the specific family: queries,
rendering, dynamic data, forms, filters, templates, assets or Builder events. Source
paths are optional lookup hints for a local checkout; customers can use the public
[developer reference](https://academy.bricksbuilder.io/developer/).

Check the actual callback arguments, return type and lifecycle before implementing.
`bricks/element/render` is a Boolean gate; `bricks/frontend/render_element` receives
HTML. Test both matching and unrelated targets so a scoped customization does not
change every element/query on the site.


---

## Module: bricks-child-theme-patterns

# Bricks: child theme patterns

Keep theme-specific customizations in the existing child theme so parent updates
preserve them. A plugin can own functionality that should survive a theme change;
do not move working plugin code merely to enforce a directory preference.

## Minimal child theme

The child directory needs `style.css` with `Template: bricks` (the parent directory
name), and `functions.php` for the hooks actually used. Follow the existing layout;
extra autoloaders, build pipelines and empty include files are unnecessary.

```css
/*
Theme Name: Example Bricks Child
Template: bricks
Version: 1.0.0
Text Domain: example-bricks-child
*/
```

Enqueue the real child stylesheet, excluding the Builder panel:

```php
<?php
if ( ! defined( 'ABSPATH' ) ) exit;

add_action( 'wp_enqueue_scripts', function() {
    if ( bricks_is_builder_main() ) return;
    wp_enqueue_style(
        'example-bricks-child',
        get_stylesheet_directory_uri() . '/style.css',
        [ 'bricks-frontend' ],
        wp_get_theme()->get( 'Version' )
    );
}, 20 );
```

Add JavaScript/include files only when needed. With a build pipeline, enqueue
compiled output; retain source in development/version control and package runtime
assets. See the [child-theme guide](https://academy.bricksbuilder.io/developer/guides/child-theme/).

## Choose the extension lifecycle

| Task | Route |
|---|---|
| Custom element | `bricks/load_elements/after`, then `Bricks\Elements::register_element()` with real file/class; **bricks-custom-elements** |
| Element-specific assets | Its `enqueue_scripts()` method; a named `$scripts` initializer for Builder updates |
| Custom dynamic tags | Public picker, individual-tag and content-render filters; **bricks-custom-dynamic-data-providers** |
| Query customization | Appropriate hook scoped with its passed element ID; **bricks-hooks-reference** |
| Echo tag or Code element PHP | **bricks-custom-code** for execution and allow-list contracts |

Do not call `Providers::register()` with instances or invoke it late in `init`.
It takes slugs, constructs Bricks provider classes and schedules registration before
tags. Ordinary custom tags should use public filters. There is no
`Bricks\Helpers::post_has_element()` helper in Bricks 2.4; use the element asset
lifecycle instead. Choose hook priority from its actual dependencies, not a generic
before/after-10 rule. Restrict autoloaders to the project's own namespace.

## Focused query customization

Replace `qypost` with the actual six-character element ID, not its Structure label.

```php
add_filter( 'bricks/posts/query_vars', function( $args, $settings, $element_id ) {
    if ( $element_id === 'qypost' ) {
        $args['posts_per_page'] = 6;
    }
    return $args;
}, 10, 3 );
```

Preserve existing `meta_query`/`tax_query` clauses when adding constraints. Obtain
Woo featured-product semantics from its supported query/taxonomy contract instead
of assuming legacy `_featured` post meta.

## Echo allow-list

The initial `bricks/code/echo_function_names` value can be the requested callback
string. Merge only an existing array with explicitly approved public helpers:

```php
add_filter( 'bricks/code/echo_function_names', function( $allowed ) {
    $allowed = is_array( $allowed ) ? $allowed : [];
    return array_merge( $allowed, [ 'example_public_label' ] );
} );
```

Define the named helper before using it. Do not cast incoming strings to arrays:
that would allow the caller's requested function. Avoid broad prefixes or unrestricted
metadata access when only one public value is needed.

## Overrides and troubleshooting

For a Woo template override, mirror the path below the plugin's `templates/`
directory under the child's `woocommerce/`. Prefer Bricks elements/hooks when they
cover the request; track override compatibility with WooCommerce updates.

Check activation/header, PHP errors, actual paths/class names and registration
lifecycle. For styles, inspect loaded files, selectors and cascade before changing
specificity. Verify custom elements/tags on the frontend and Builder update path;
PHP syntax checks alone do not establish those behaviors.


---

## Module: bricks-import-export

# Bricks: unified import / export via MCP

Use the unified transfer-package format for site-to-site migration.

Use these abilities:

- `bricks/list-transfer-items`: read the current site's export selector and exact item IDs.
- `bricks/export-transfer-package`: create a base64 ZIP package from explicit selected item IDs.
- `bricks/inspect-transfer-package`: inspect a ZIP before import; returns conflicts, warnings, and `zipHash`.
- `bricks/import-transfer-package`: import selected manifest items. Requires `expectedZipHash` from inspection.

Supported transfer types: `color-palettes`, `theme-styles`, `classes`, `variables`, `custom-fonts`, `breakpoints`, `global-queries`, `components`, `templates`, `settings`, `custom-capabilities`.

## Normal site-to-site flow

1. On the source site, call `bricks/list-transfer-items`.
2. Choose explicit item IDs from the response.
3. Call `bricks/export-transfer-package` with:

```json
{
  "types": ["classes", "components", "templates"],
  "items": {
    "classes": ["abc123"],
    "components": ["hero-card"],
    "templates": ["100", "101"]
  }
}
```

4. On the target site, call `bricks/inspect-transfer-package` with the returned `zipBase64`.
5. Review `manifest.types.*.items`, especially `conflict` and `warning`.
6. Call `bricks/import-transfer-package` with the same `zipBase64`, the inspected `zipHash` as `expectedZipHash`, and explicit manifest item IDs:

```json
{
  "zipBase64": "UEsDBBQ...",
  "expectedZipHash": "sha256-from-inspect",
  "types": ["classes", "components"],
  "items": {
    "classes": ["abc123"],
    "components": ["hero-card"]
  },
  "conflictMode": "skip"
}
```

## Safety rules

- Always inspect before import. The import ability requires `expectedZipHash` so the imported ZIP matches the package you reviewed.
- `conflictMode` defaults to `skip`. Use `replace` only when overwriting is requested, and pass `allowOverwrite: true`.
- Per-item replacements live in `conflictDecisions`, keyed by type and item ID; any `replace` value also requires `allowOverwrite: true`.
- Sensitive settings tabs require explicit user intent and `allowSensitiveSettings: true`. The `custom-code` tab can be exported with that acknowledgement, but `import-transfer-package` rejects importing it even when acknowledged (`includes/abilities/import-export.php`).
- Template image import is off by default. Use `importImages: true` only when media migration is intended and the user can upload files.
- MCP ZIP payloads are capped for JSON transport. If a package is too large, split by type or item selection.
- Code-bearing templates, components, component properties, and global queries follow the caller’s code-authoring permissions. PHP imports need the complete PHP authorization contract in [bricks-custom-code](../bricks-custom-code/SKILL.md#code-authoring-through-abilities). Inspect redacted exports and rejected payloads; do not reconstruct hidden source or assume HTML-page partial omission applies to transfer packages.

## Notes

- `items` is required for each selected type. Do not omit it and assume "everything".
- For singleton `breakpoints`, use `items: { "breakpoints": ["all"] }`.
- For settings, pass tab IDs such as `builder`, `performance`, `api-keys`, or `custom-code`.
- Transfer packages include `manifest.json`; template-only legacy ZIPs without a manifest are not accepted by the unified import flow.

## Tool availability

If a `bricks/*` ability is not available as a direct tool, first check whether it is outside the fast path and call it through `mcp-adapter-execute-ability` with `ability_name: "bricks/<name>"`. If the dispatcher also rejects it, call `bricks-list-ability-status` to check whether a site admin disabled it under Bricks > AI.


---

## Module: bricks-role-permissions

# Bricks: role permissions (via MCP)

Builder access uses two stores:

1. Custom builder capability definitions live in `BRICKS_DB_CAPABILITIES_PERMISSIONS` (`bricks_capabilities_permissions`). Each row is `{ label, description, permissions }` and is keyed by a WordPress capability id.
2. Role access lives on WordPress roles. A role gets builder access when it has `bricks_edit_content`, `bricks_full_access`, or a custom builder capability id.

Use the dedicated permission abilities. Do not use `bricks/set-global-settings` for builder permissions.

These abilities are disabled by default in `Bricks > AI`. If one is disabled, follow [bricks-ai-tab](../bricks-ai-tab/SKILL.md) to enable it within the user’s authorization.

## Abilities

These are long-tail abilities. If the direct hyphenated tool is not available, call them through `mcp-adapter-execute-ability`.

- `bricks/list-builder-permissions`: read permission sections, default/custom capability definitions, role assignments, and the capability choices shown in the Builder access role select.
- `bricks/upsert-builder-capability`: create or update one custom builder capability definition.
- `bricks/set-builder-role-access`: assign existing builder access capabilities to WordPress roles. Empty string means no builder access. `administrator` is not writable because Bricks always treats administrators as full access.
- `bricks/delete-builder-capability`: delete one custom capability definition and remove that WordPress capability from all roles.

## Permission keys

Source of truth: `includes/builder-permissions.php`.

Do not guess keys. Start with `bricks/list-builder-permissions` and use the returned `permissionSections`.

Common sections:

- Post type access: `access_builder_{post_type}`, for example `access_builder_page`.
- General: `access_breakpoints_manager`, `access_page_settings`, `access_template_settings`, `access_revisions`, `delete_revisions`, `access_font_manager`, `access_icon_manager`.
- Templates: `create_templates`, `edit_templates`, `delete_templates`, `insert_templates`, `access_remote_templates`, `import_export_templates`.
- Global styles and settings: `edit_color_palettes`, `access_class_manager`, `access_variable_manager`, `access_theme_styles`, `access_query_manager`, `create_global_classes`, `edit_global_classes`, `delete_global_classes`, `assign_unassign_global_classes`, `lock_unlock_global_classes`, `copy_paste_global_classes_styles`, `access_pseudo_selectors`.
- Components: `insert_components`, `set_component_props`, `edit_components`, `create_components`, `delete_components`, `import_export_components`.
- Element editing: `access_element_content`, `access_element_styles`, `access_query_loop_builder`, `access_element_hide`, `access_element_conditions`, `access_element_interactions`, `duplicate_elements`, `delete_elements`, `move_elements`, `copy_paste_elements`, `copy_paste_element_styles`, `copy_paste_element_conditions`, `copy_paste_element_interactions`, `copy_paste_element_attributes`, `pin_unpin_elements`.
- Element-specific permissions are generated from registered elements: `add_element_{elementName}` and `edit_element_{elementName}`.

Keys such as `use_builder`, `template_manager`, `upload_json`, `use_components`, and `use_global_elements` are not current builder permission keys unless `list-builder-permissions` returns them.

## Create a custom access level

Create a capability definition first:

```json
{
  "ability_name": "bricks/upsert-builder-capability",
  "parameters": {
    "id": "bricks_marketer_access",
    "label": "Marketing access",
    "description": "Can edit content and insert templates, without design-system management.",
    "permissions": [
      "access_builder_page",
      "access_element_content",
      "access_revisions",
      "insert_templates"
    ]
  }
}
```

The id is a WordPress capability id. It must not be `bricks_full_access`, `bricks_edit_content`, or `bricks_no_access`.

## Assign roles

Assign an existing builder access capability to each role you want to change:

```json
{
  "ability_name": "bricks/set-builder-role-access",
  "parameters": {
    "roleAccess": {
      "editor": "bricks_marketer_access",
      "author": ""
    }
  }
}
```

The response includes `beforeSnapshot` and the resulting `roleAccess`. Report both when the change affects a real site.

## Code-execution configuration is separate

`executeCodeEnabled` and `executeCodeCapabilities` are excluded from Bricks settings abilities. The actual WP capabilities are `bricks_execute_code` and `bricks_execute_code_off` (`includes/capabilities.php`). These control custom PHP through echo tags, Code element PHP mode, SVG source code, and Custom Query PHP.

These role-management abilities do not grant code execution. PHP authoring and `bricks/execute-php` are available only under the separate opt-in and authorization contract in [bricks-custom-code](../bricks-custom-code/SKILL.md#code-authoring-through-abilities). If the user explicitly authorizes a configuration change, use an available admin/configuration workflow.

## Do not

- Do not use `bricks/set-global-settings` for builder permissions.
- Do not send made-up permission keys. Read `list-builder-permissions` first.
- Do not assign a custom capability id before creating it.
- Do not try to change administrator builder access through MCP.
- Do not flip code-execution capabilities through MCP.


---

## Module: bricks-ai-tab

# Bricks: AI screen

Bricks exposes its abilities to MCP clients through `Bricks > AI`. This screen is the admin control panel for Bricks abilities. MCP clients cannot change these settings. The screen affects which Bricks abilities are callable.

## What the screen controls

1. **Enable Bricks abilities**: master toggle. Off means zero Bricks abilities register. Even diagnostic abilities such as `bricks-list-ability-status` are absent.
2. **Per-ability enable/disable**: registered abilities grouped by category. Most tools default on; security-sensitive groups can default off and require explicit opt-in. An unfiltered summary hides disabled rows by default. Request exact `abilityNames`, set `includeDisabled: true`, or use `responseFormat: "detailed"` to inspect them. Execution of a disabled ability returns `bricks_ability_disabled`.
3. **Adapter status**: informational. If the WordPress MCP Adapter plugin or the WordPress Abilities API is inactive, Bricks cannot expose abilities even with the toggle on.

## Direct tools vs dispatcher

Do not treat `tools/list` as the complete Bricks ability list.

Current Bricks source keeps only high-frequency abilities on the default MCP server as direct tools (`includes/abilities/manager.php`). The rest are enabled abilities but must be called through:

```
mcp-adapter-execute-ability
  ability_name: "bricks/<ability-name>"
  parameters: { ... }
```

So a missing direct tool can mean either:

- the ability is enabled but outside the fast path, or
- the admin disabled it, in which case dispatcher execution returns `bricks_ability_disabled`, or
- Bricks abilities are unavailable.

Check status before concluding the ability does not exist.

## The default model

The storage option `bricks_mcp_settings` is shaped:

```json
{
  "enabled": true,
  "disabledAbilities": [ "bricks/delete-post", "bricks/upload-media" ],
  "enabledAbilities": [ "bricks/list-builder-permissions" ]
}
```

`disabledAbilities` opts out of default-on abilities. `enabledAbilities` opts into default-off abilities. Permission-management tools are default off and control builder access for WordPress roles.

## Checking ability status

For a compact enabled inventory, call:

```
bricks-list-ability-status
```

For disabled-state diagnosis, use one of:

```
bricks-list-ability-status({ abilityNames: ["bricks/delete-global-class"] })
bricks-list-ability-status({ includeDisabled: true })
bricks-list-ability-status({ responseFormat: "detailed" })
```

Summary rows contain only `name`, `category`, `enabled`, and `defaultEnabled`.
Detailed rows additionally contain labels, descriptions, annotations, and the full
registry. Example compact response shape for the current ability surface (counts can
change as abilities are added or disabled):

```json
{
  "abilities": [
    { "name": "bricks/add-element", "enabled": true, "defaultEnabled": true, "category": "bricks-elements" }
  ],
  "total": 164,
  "enabled": 163,
  "disabled": 1
}
```

If `enabled: false`, a site admin either disabled the ability or has not opted into a default-off group. You cannot route around it. If enabling it is within the user’s authorized request, use the Bricks > AI admin UI when available; otherwise ask the site owner. A disabled ability cannot enable itself through MCP.

Also call:

```
bricks-get-mcp-version
```

Selected response fields (the runtime may return additional counters):

```json
{
  "bricksVersion": "2.4.0",
  "bricksAbilitiesVersion": "2.0.0",
  "adapterVersion": null,
  "wordpressVersion": "6.8",
  "abilitiesApiActive": true,
  "disabledAbilityCount": 1
}
```

There is no `abilityCount` field in `get-mcp-version`; use `list-ability-status.total` when you need the count.

## Error codes you'll see

- **`bricks_ability_disabled`**: the dispatcher or a diagnostic path reached an ability name that the admin disabled. Do not retry. Call `bricks-list-ability-status` to confirm state.
- **Master toggle off**: no dedicated error code. With Bricks MCP disabled, no `bricks/*` abilities register at all. Tell the user to enable Bricks abilities under `Bricks > AI`.
- **`bricks_setting_excluded`** / **`bricks_setting_unknown`**: these come from the settings registry, not the AI screen. See the `bricks-settings` skill.

## How the screen interacts with call-time checks

The AI screen is an exposure deny-list, not a role editor:

- An enabled ability can still fail at call time. Use the returned error to decide what to do next.
- A disabled ability registers as an inspectable shim. The caller cannot bypass the deny-list by using the dispatcher; execution returns `bricks_ability_disabled`.

## PHP abilities

PHP is a separate opt-in, not a normal per-ability toggle. Bricks 2.4 uses
`BRICKS_ENABLE_PHP_ABILITIES`; the prerelease
`BRICKS_ENABLE_EXECUTE_PHP_ABILITY` name no longer enables it. An enabled master
switch or an administrator role alone is insufficient. See
[bricks-custom-code](../bricks-custom-code/SKILL.md#code-authoring-through-abilities)
for execution, signing, effective-capability, and Application Password prerequisites.
Do not enable PHP just to author ordinary CSS.

## What's not in the tab

These settings have no dedicated Bricks MCP write route. Use an authorized admin UI or configuration workflow if the user requested the change and that access is available; otherwise identify the prerequisite for the site owner:

- **License activation**: admin UI only.
- **Credential/API settings**: keys matching `apiKey*`, `apiSecretKey*`, or `license*`, plus access tokens and template passwords, are excluded from Bricks settings abilities. Use `bricks-list-credential-status` to check whether a credential is configured without reading its value. Other provider settings, such as `adobeFontsProjectId`, are only writable if `bricks/list-settings-schema` exposes them.
- **Code-execution settings**: `executeCodeEnabled`, `executeCodeCapabilities`, `codeSignaturesLocked`, `codeExecutionMode`, and `htmlExecutionMode` are excluded from Bricks settings abilities (`includes/abilities/settings.php`).
- **Code-signature regeneration**: admin UI only.

Do not treat permission to edit content as permission to change these settings. Preserve an explicit user authorization for a configuration change; do not ask them to repeat it merely because the work uses another available transport.

## Typical flow: an expected ability is missing

```
# Expected bricks/delete-global-class but it is not in tools/list.

bricks-list-ability-status({ abilityNames: ["bricks/delete-global-class"] })
  -> { abilities: [{ name: "bricks/delete-global-class", enabled: false, category: "bricks-design" }], ... }

# Admin disabled it. Tell the user:
# "The site owner has disabled delete-global-class on this Bricks install.
#  Re-enable it under Bricks > AI."
```

## Don't

- Don't assume tool availability is stable across sites. Check `list-ability-status` when an expected ability is missing.
- Don't retry on `bricks_ability_disabled`. The deny-list is explicit.
- Don't bypass the AI screen by editing `bricks_mcp_settings` directly. The UI is the contract.
- Don't assume a missing `tools/list` entry means the ability is disabled. Many enabled Bricks abilities are dispatcher-only.


---

## Module: bricks-performance

# Bricks: performance

Measure the affected page before changing settings. Use request timing, rendered assets, query timings, and interaction profiles to identify the bottleneck, then compare the same page after the change.

## CSS loading

Setting: `Bricks > Settings > Performance > CSS loading method`. Stored as `cssLoading` in the Bricks settings registry (`includes/abilities/settings.php`) and used by the asset loader (`includes/assets.php`).

| Mode | Value | Tradeoff |
|---|---|---|
| Inline (default) | `''` (empty string) | One less HTTP request. CSS ships in `<style>` blocks inside `<head>`. Repeated across all pages: not cached by browser. |
| External file | `'file'` | Separate `.css` files per template / global style. Browser-cacheable. Tiny HTTP request but cold-load pays for it. |

Compare cold loads and repeat navigation with both modes on representative pages.

**File-mode regeneration:** files are written to `wp-content/uploads/bricks/css/` at save time. After a bulk update (site-wide CSS change, theme-style swap, class rename), regenerate all via `Bricks > Settings > Performance > Regenerate CSS files`. Without this, stale CSS serves until each template is manually saved.

**Filter:** `bricks/generate_css_file`: intercept per-file generation.

## The loop-marker preservation trap

Bricks query loops rely on loop markers for AJAX pagination, Load More, Infinite Scroll, and Query Filters.

Current source flow: server render adds `data-brx-loop-start`, then frontend JS converts it to a comment shaped like `<!--brx-loop-start-{queryId}-->`.

Optimization plugins and cache layers that remove Bricks markers can break AJAX swaps. Configure them to preserve Bricks `brx-loop` markers.

**Diagnostic:** inspect both page source and the live DOM on a page with a loop. Page source should contain `data-brx-loop-start`; the live DOM should contain a `brx-loop-start` comment. If either disappears after optimization, fix the plugin config and flush cache.

## Random seed TTL: pagination stability

Query loops with `orderby: rand` need a stable seed across paginated pages, or the same item shows on page 1 and page 3.

Setting: random seed TTL (in minutes). Stored as `randomSeedTtl` in query vars. Default: 60 min (`query.php:2566-2567`).

Keep a positive TTL for random-order loops with pagination. Choose the duration according to how often the order should change.

**Storage:** Bricks sets a transient keyed by `bricks_query_loop_random_seed_{element_id}` (`includes/query.php:2584`). The seed is shared by queries for the same element until the transient expires. Bricks also deletes it when the random-seed setting changes.

## Query caching

Setting: `Bricks > Settings > Performance > Cache query loops` (checkbox `cacheQueryLoops` at `admin/admin-screen-settings.php:1962`).

Uses WordPress object cache through `wp_cache_get()` / `wp_cache_set()` (`includes/query.php`). A persistent object cache such as Redis or Memcached makes it useful across requests. Without one, the cache is request-local and the benefit is much smaller.

Caches query results for one minute, keyed by element id, query vars, parent loop object id, and any language-specific cache-key filters.

**Invalidation:** current source uses a short object-cache TTL (`MINUTE_IN_SECONDS`) rather than a broad explicit invalidation graph for every content change. If a persistent object cache serves stale loop results, clear the object cache or adjust the query cache key through `bricks/query/cache_key` for the context you need.

## Images and fonts

Inspect the network waterfall and rendered markup:

- Check the LCP image’s loading behavior, dimensions, and responsive sources. Avoid lazy-loading the image responsible for initial visible content.
- Check font downloads and the styles that request them. Use `bricks-custom-fonts` when self-hosting fonts is part of the chosen fix.
- Confirm changes to image or font controls against the target site's element schema.

## Interactions

Interaction payload and event-handling work grow with the number of rendered elements. Profile repeated grids and expensive callbacks. Global-class interactions centralize authoring; each matching element still inherits the interaction rows.

Use CSS for simple visual states and consider delegated JavaScript handlers when profiling shows repeated event handling is costly. See `bricks-interactions` for storage and inheritance behavior.

## Frontend assets

The Bricks frontend source is `src/assets/js/frontend.js`; the compiled runtime is enqueued as `bricks-scripts` from `assets/js/bricks.min.js`. It handles interactions, popups, sliders, accordions, and filter helpers.

Inspect script loading and compression in the network response before changing optimization settings. After changing asset optimization, verify affected interactions, AJAX loops, and responsive styles.

## Verification

Compare the same page and interaction under matching cache and device conditions. Record the measured change and any remaining bottleneck. Preserve query-loop markers and exclude personalized cart and checkout responses from shared full-page caching.

## Related skills

- `custom-code`: CSS cascade order, where custom CSS lives.
- `interactions`: interaction cost details.
- `query-loops`: loop-specific performance (include/exclude, include-query).
- `site-audit`: full-site scan includes performance signals.
