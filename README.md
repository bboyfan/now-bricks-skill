# now-bricks-skill

> **Bricks Builder 2.4+ AI Agent Operational Skill**
> A complete, production-hardened master manual for AI agents (Antigravity / Gemini CLI) operating Bricks Builder sites — from paste-ready JSON authoring to live MCP/Abilities database operations.

---

## What is this?

`now-bricks-skill` is a **Gemini CLI / Antigravity skill** that gives an AI agent full operational mastery of Bricks Builder 2.4+. It covers:

- **JSON authoring**: Generating clipboard-paste and template-import JSON with correct structure, style keys, and element hierarchy.
- **Live site operations**: Using the official Bricks MCP Adapter and WP-CLI Abilities API to read and write page elements, templates, theme styles, and the color palette directly to the database.
- **25+ subsystem manuals**: Every Bricks subsystem documented with exact key names, verified schemas, and anti-pattern warnings.
- **16 ready-to-use UI patterns**: Complete JSON layouts for Hero, Pricing, Cards, FAQ, Forms, Modals, and more.

This skill was built from a combination of CodeerHQ's official MCP/Abilities API architecture, WPGaurav's rapid JSON authoring methodology, and production optimizations derived from real-world site work on [Lumia 慕光婚禮所](https://lumiawedding.com).

---

## Repository Structure

```
now-bricks-skill/
├── SKILL.md                   # Main entry point — action guide, routing table, non-negotiable rules
├── README.md                  # This file
│
├── patterns/                  # 16 ready-to-use Bricks JSON layouts
│   ├── INDEX.md               # Pattern index with format and feature notes
│   ├── hero-centered.json
│   ├── hero-split-image.json
│   ├── feature-grid.json
│   ├── pricing-table.json
│   ├── testimonials-slider.json
│   ├── faq-accordion.json
│   ├── cta-section.json
│   ├── contact-section.json
│   ├── blog-archive-filters.json
│   ├── team-grid-acf.json
│   ├── bem-hero.json          # BEM workflow demo: zero visual settings on elements
│   ├── bem-card-grid.json
│   ├── bem-pricing.json
│   ├── header-template.json
│   ├── footer-template.json
│   └── popup-newsletter.json
│
├── references/                # 25+ subsystem reference manuals
│   ├── json-formats.md        # Clipboard, template export, postmeta key formats
│   ├── elements.md            # Element catalog: controls, tags, semantic overrides
│   ├── style-settings.md      # All `_` CSS panel keys with responsive colon syntax
│   ├── layout-recipes.md      # Grid, Flexbox, hero splits, sticky, overlay patterns
│   ├── theme-styles.md        # Theme Styles schema, CSS generation, loading methods
│   ├── components-classes.md  # Component definitions, global class BEM organization
│   ├── dynamic-data.md        # Built-in tags, echo functions, fallback syntax
│   ├── query-loops.md         # Post, Term, User, repeater query schemas
│   ├── query-filters.md       # Faceted filter, live search, AJAX pagination
│   ├── conditions.md          # Show/hide logic, user roles, custom field conditions
│   ├── interactions.md        # Click triggers, scroll reveals, animation timelines
│   ├── forms.md               # Form element, field mapping, email/webhook actions
│   ├── popups.md              # Popup templates, triggers, session limits
│   ├── templates.md           # Template types, conditions schema
│   ├── woocommerce.md         # Product templates, cart, checkout, custom loops
│   ├── acf-providers.md       # ACF, Meta Box, JetEngine, Pods repeaters
│   ├── custom-elements.md     # Custom elements via child theme PHP
│   ├── hooks.md               # All official Bricks PHP actions & filters
│   ├── external-assets.md     # External media URLs, SVG inlining
│   ├── assets-permissions.md  # Inline vs file CSS, builder capabilities, code signing
│   └── mcp-adapter/           # Official MCP Adapter deep-dive (5 parts)
│       ├── 01-workflow-and-routing.md
│       ├── 02-design-systems-and-styles.md
│       ├── 03-templates-layouts-and-elements.md
│       ├── 04-dynamic-data-and-queries.md
│       └── 05-custom-code-and-extensions.md
│
└── scripts/                   # Helper utilities
    ├── validate_bricks_json.py    # Validates element tree integrity, parent/children links
    ├── validate-package.mjs       # Package-level validation
    ├── bricks-skills-update-check # Check for skill updates
    ├── bricks-skills-upgrade      # Upgrade skill to latest version
    ├── parse-release-response.mjs
    └── semver-compare
```

---

## Two Operating Paths

### Path A — JSON Authoring (Offline)

Generate paste-ready or importable Bricks JSON without a live site connection.

**When to use:** Designing new page sections, creating templates to import, prototyping layouts.

**Step 1 — Pick delivery format:**
| Target | Format |
|--------|--------|
| Canvas paste (Cmd+V) | `bricksCopiedElements` clipboard format |
| WP Admin template import | Template format (`content`, `global_classes`) |
| Direct DB / WP-CLI | Pure element array (`_bricks_page_content_2`) |

**Step 2 — Compose:** Use `patterns/INDEX.md` for 16 ready-made sections. Look up element controls in `references/elements.md`, style keys in `references/style-settings.md`.

**Step 3 — Validate:**
```bash
python3 ~/.gemini/skills/bricks/scripts/validate_bricks_json.py <file.json>
```

---

### Path B — Live Site MCP Operations

Read and write page elements, theme styles, palette, and templates directly to the WordPress database via the Bricks MCP Adapter.

**When to use:** Applying changes to a live site, migrating existing elements, updating global design tokens.

**Step 1 — Read context:**
```
bricks-get-design-context  →  active palette IDs, global classes, component digests
```

**Step 2 — Execute:**
| Operation | Tool |
|-----------|------|
| Colors, Classes, Theme Styles | `bricks-commit-site-foundation` |
| Page element changes | `bricks-commit-site-edit-plan` |
| Reusable component | `create-component` |

**Step 3 — Flush & verify:**
```bash
wp cache flush && curl -X PURGE http://127.0.0.1:6081/.*
```

---

## Non-Negotiable Engineering Rules

These are enforced rules that the AI agent must never violate:

### 1. Flat Tree Integrity
The elements array is **strictly flat**. Tree hierarchy is formed exclusively via `parent` and `children` IDs. Root elements must have `parent: 0` (Sections). Never place a `section` inside a `div`.

### 2. Settings Must Be a Dictionary
`settings` is always an object `{}`. **Never emit `settings: []`**.

### 3. Custom CSS Selector Scoping
- Page elements: `#brxe-{id}` in `_cssCustom`
- Component elements: `.brxe-{id}` in `_cssCustom`
- Never leave `%root%` in programmatic output.

### 4. Component Instance Nodes
Instances (`cid: "..."`) must **omit `children`**. Pass dynamic content via `"properties": { "prop_name": "value" }`.

### 5. Verified Value Shapes
- Colors: `{"hex": "#23221e"}` or `{"raw": "var(--brand-cream)"}`
- Typography: explicit CSS property keys (`"font-size"`, `"line-height"`, `"letter-spacing"`)
- Box-shadow: nested under `values` (`{"values": {"x": "0", "y": "4px", "blur": "12px"}, "color": {...}}`)

### 6. Responsive Grammar
Use colon suffixes for breakpoints and pseudo-states:
```
_padding:tablet_portrait
_background:hover
_margin:mobile_portrait:hover
```
Default breakpoints: `tablet_portrait` (991px), `mobile_landscape` (767px), `mobile_portrait` (478px).

### 7. External Assets
Reference images and SVGs by absolute URLs or WordPress attachment IDs. Never invent non-existent IDs.

### 8. Native Links — Zero Tolerance for Fake Attributes
**Never** simulate links with `customTag: "a"` or manual `_attributes: [{name: "href"}]`.

Always use native `settings.link`:
```json
"link": {
  "type": "external",
  "url": "/about/",
  "target": "_blank",
  "rel": "noopener noreferrer"
}
```
For anchor targets: `{"type": "external", "url": "#section-id"}`.

### 9. Centralized CSS vs Panel Settings
Do **not** duplicate identical CSS across multiple pages. Put reusable layout and typography rules in `Theme Styles > css.stylesheet`. Keep user-editable content (links, images, texts, button labels) in native element controls.

### 10. WP-CLI / Programmatic Ops Guard
- Always call `wp_set_current_user(1);` before any Abilities call in CLI scripts (bypasses capability check → avoids 403).
- Standard posts/pages: omit `area` in `get-page-elements` / `set-page-elements`.
- Templates only: use `area: "header"` or `area: "footer"` with the template post ID.

---

## Installation

### Option 1: Antigravity / Gemini CLI (Recommended)

```bash
# Clone into the Bricks skills directory
git clone https://github.com/bboyfan/now-bricks-skill ~/.bricks/skills/bricks

# Symlink so Antigravity / Gemini CLI can discover it
ln -sf ~/.bricks/skills/bricks ~/.gemini/skills/bricks
```

The skill is auto-discovered when the agent starts. The agent will read `SKILL.md` as its operational entry point.

### Option 2: Manual reference

Clone anywhere and provide `SKILL.md` to any AI agent as context. The routing table in Section 2 will guide the agent to the correct reference for any task.

```bash
git clone https://github.com/bboyfan/now-bricks-skill
```

---

## Key Reference Files

| File | When to open |
|------|-------------|
| [`SKILL.md`](SKILL.md) | Entry point — action guide, full routing table, all 10 engineering rules |
| [`references/style-settings.md`](references/style-settings.md) | Looking up any `_` CSS panel key or responsive syntax |
| [`references/elements.md`](references/elements.md) | Finding element `name` values, available controls, semantic tag overrides |
| [`references/theme-styles.md`](references/theme-styles.md) | Working with Bricks 2.0+ Theme Styles schema and CSS generation |
| [`references/json-formats.md`](references/json-formats.md) | Choosing the right JSON delivery format (clipboard vs template vs postmeta) |
| [`references/mcp-adapter/01-workflow-and-routing.md`](references/mcp-adapter/01-workflow-and-routing.md) | MCP Adapter tool selection and write-tier routing |
| [`patterns/INDEX.md`](patterns/INDEX.md) | Picking a ready-to-paste UI pattern |

---

## Changelog

See [`/Users/bboyfan/Documents/慕光網站/CHANGELOG.md`](https://github.com/bboyfan/now-bricks-skill) for the full project changelog.

Key milestones:
- **2026-09-30** — Added Rules 8–10 (native links, centralized CSS, WP-CLI guard). Corrected Theme Styles schema to verified Bricks 2.0+ group nesting. Updated `style-settings.md` link control, `elements.md` anti-pattern warnings.
- **2026-09-29** — Full-site native link migration (header, footer, homepage, 12 inner pages). Theme Styles integration with `css.stylesheet`. Color palette setup. CSS consolidation (120 KB redundancy eliminated from 12 inner pages).
- **2023–2024** — Initial skill foundation (CodeerHQ MCP architecture + WPGaurav JSON authoring + 16 patterns).

---

## Credits

- **MCP / Abilities architecture**: [CodeerHQ Bricks MCP Server](https://github.com/cofeerhq/bricks-mcp)
- **JSON authoring patterns**: Inspired by WPGaurav's Bricks rapid-authoring workflow
- **Production optimizations**: Real-world site engineering on [Lumia 慕光婚禮所](https://lumiawedding.com) by WENSZU (溫釲)
- **Maintained by**: [@bboyfan](https://github.com/bboyfan)

---

## License

MIT
