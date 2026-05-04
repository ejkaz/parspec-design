---
name: parspec-craft
description: "Lints HTML / SVG / CSS / Markdown against Parspec brand rules. Two layers — universal anti-AI-slop + color + typography + viewport invariants (in this skill), and data-driven palette enforcement that reads the active design-model.yaml. Use when reviewing a Parspec deliverable for brand compliance, evaluating proposal HTML, or auditing customer-facing artifacts. Triggers: 'lint this for parspec brand', 'is this on-brand', 'parspec craft check', 'audit this html', 'parspec compliance', '/parspec-craft'."
version: 0.1.0
allowed-tools: [Read, Glob, Grep, Bash]
---

# Parspec Craft

Brand compliance lint. Two layers, one purpose.

## How it works

| Layer | Source | What it catches |
|---|---|---|
| **Universal** | `anti-ai-slop.md`, `color.md`, `typography.md` (this skill) | Generic AI-template tells: emoji as icon, Inter/Roboto display font, trust gradients, rounded-card-with-colored-left-border, lorem ipsum |
| **Data-driven** | `../parspec-design/skills/parspec-design/design-model.yaml` `avoid:` + `primary_axis_preserved:` + `invariants:` + **`surfaces:`** + **`roles:`** | Brand-version-specific: forbidden hex codes, missing locked-axis tokens, invariant violations (no clamp(), missing reduced-motion), wrong-mode-for-surface, hex literals where role tokens should be used |

The data-driven layer is the load-bearing one. When the brand evolves, this skill auto-adapts — no code changes here.

## Workflow

When invoked on a target file (HTML / SVG / Markdown / CSS):

1. **Locate design-model.yaml.** Try in order:
   - `../parspec-design/skills/parspec-design/design-model.yaml` (sibling plugin in this repo)
   - `~/.claude/plugins/parspec-design/skills/parspec-design/design-model.yaml`
   - User-supplied path
   - If none: warn and run universal-only.

2. **Read** the target file + design-model.yaml.

3. **Universal checks** — apply rules from `anti-ai-slop.md`, `color.md`, `typography.md`. Each rule has a severity (`error` / `warning` / `info`).

4. **Data-driven checks** — for every entry in `avoid:`:

   | Field | Match | Action |
   |---|---|---|
   | `color: "#XXXXXX"` | grep target for hex (case-insensitive, with/without `#`) | Flag any match |
   | `color_family` | description names the family (e.g. consumer-purple) — scan for hex codes in the `#6366F1`/`#8B5CF6`/`#A78BFA` range | Flag any match |
   | `font_family` | grep `font-family:` declarations | Flag any match |
   | `pattern` | named pattern from anti-ai-slop matcher table | Flag any match |

5. **Invariant checks** — for every entry in `invariants:`:
   - `viewport_fitting`: every `.slide` element must declare `height: 100vh` AND `overflow: hidden`
   - `typography_scaling`: no fixed `px`/`rem` font sizes at the leaf — must use `clamp()`
   - `reduced_motion`: every output must include `@media (prefers-reduced-motion: reduce)`
   - `cta_color_monopoly`: any `<button>` or `[role="button"]` with primary-CTA semantics must use `#FFA72B`
   - `customer_logos_grayscale`: customer-logo blocks should not contain colored hex tokens (warning)
   - `density_limits`: per-slide content count vs allowed maxima (warning)

6. **Surface-mode checks (v1.1.0+)** — for every entry in `surfaces:`:
   - Detect surface type from filename / URL path / front-matter / target HTML class:
     - Decks, marketing pages, hero sections, sales PDFs, case studies → `brand_artifacts`
     - App screens, dashboards, forms → `product_ui`
     - Contracts, term sheets, invoices → `documents`
   - For each detected surface, the `<body>` (or `.slide`) background MUST match `surfaces.<surface>.background`. Different mode → `error`.
   - Examples:
     - A deck (`brand_artifacts`) with Off-white `#F2F2F2` background → ERROR (should be Parspec Black `#0F0F0F`).
     - A product-UI screen with Parspec Black background → ERROR (should be Off-white).
     - An invoice with paper-warm tint → WARNING (transactional documents must be pure White; AP systems expect this).

7. **Role-token checks (v1.1.0+)** — flag hex literals in CSS where a role token exists:
   - `background: #FFA72B` on a `[role="button"]` or `<button>` → ERROR. Should be `var(--cta)` referencing `roles.cta`.
   - `color: #F04E23` for an error message → ERROR. Should be `var(--error)` referencing `roles.error`.
   - The two-tier Polaris/Carbon precedent: every consumer of color references a role name, never a primitive directly.

6. **Primary-axis-required checks** — every locked axis token in `primary_axis_preserved:` should appear at least once if the target contains relevant chrome. Specifically:
   - Any heading or body text → font-family must resolve to Montserrat
   - Any CTA → must use Brand Orange `#FFA72B`
   - Any dark surface → should use Parspec Black `#0F0F0F` or Charcoal `#2E2E2E`

7. **Output** — punch-list grouped by severity, each item:
   - `severity:` error | warning | info
   - `rule:` short rule name (e.g. `forbidden-color`, `missing-clamp`, `no-emoji-icon`)
   - `where:` file:line or selector
   - `offending:` the matched content
   - `fix:` concrete one-line remediation

## Severity model

| Severity | Action | Examples |
|---|---|---|
| `error` | Must fix | Forbidden font (Inter, Roboto, Arial), consumer-purple, trust-gradient, viewport overflow, primary-CTA not Brand Orange, missing reduced-motion, **wrong-mode-for-surface (deck on light bg, product UI on dark bg)**, **hex literal where role token exists** |
| `warning` | Should fix | v1 secondaries (Blueprint Blue, Violet, etc.), pastel tints, AI-slop patterns, density-limit overflow, colored customer logo, **transactional document with non-white background** |
| `info` | Optional nudge | Suggestion for design-model.yaml entries (e.g. "consider tagging this brand version") |

## What this skill does NOT do

- Generate slides — that's `parspec-slides`
- Edit the brand — that's `parspec-design`
- Generic UI/UX heuristic review — that's `ui-ux-pro-max`
- Render previews — that's `parspec-design preview`

## Example invocation

```
User: "Lint /tmp/Q3_Board_Update.html against parspec-craft."
Claude: [Reads target, locates design-model.yaml, runs universal + data-driven + invariant checks]
Claude: [Outputs punch-list]
  ERROR  | line 142 | forbidden-color (Blueprint Blue v1) | bg: #6270F2 | Use Steel Blue from approved secondaries
  ERROR  | line 89  | forbidden-font | font-family: 'Inter' | Switch to 'Montserrat'
  WARN   | line 256 | density-limits  | 8 bullets in content slide | Split into two slides (max 4-6)
  WARN   | line 320 | colored-customer-logos | <img src="sonepar-color.svg"> | Use grayscale variant
```
