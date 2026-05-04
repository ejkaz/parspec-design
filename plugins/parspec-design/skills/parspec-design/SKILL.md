---
name: parspec-design
description: "Parspec brand SSoT and evolution workflow. Use when the user wants to inspect, update, evolve, or roll back the Parspec brand — colors, typography, motion, voice, or the design-model.yaml itself. Triggers include 'show parspec brand', 'update parspec brand', 'evolve parspec palette', 'parspec design model', 'roll back brand to <tag>', '/parspec-design'. The skill maintains design-model.yaml — the single file every other Parspec skill (parspec-slides, parspec-craft) reads."
version: 0.1.0
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, WebFetch]
---

# Parspec Design

Brand SSoT skill. Owns `design-model.yaml` — the single file that defines Parspec's visual identity. Every other Parspec skill (parspec-slides, parspec-craft) reads this file. Brand changes happen here; downstream skills auto-adapt.

## Identity

Parspec sells AI-native operating software (quoting / submittals / project management) to **Construction Materials Distributors** — Sonepar, Wesco, Border States, Rexel, Graybar. Buyer is a 50-year-old procurement director at an industrial distributor. The brand visual register is **utility software / industrial trade**, not consumer SaaS.

## Locked primary axis (immovable)

| Token | Value | Role |
|---|---|---|
| `parspec-black` | `#0F0F0F` | Default backgrounds |
| `charcoal` | `#2E2E2E` | Layering / secondary surface |
| `off-white` | `#F2F2F2` | Document / text-heavy surfaces |
| `white` | `#FFFFFF` | Text on dark |
| `brand-orange` | `#FFA72B` | Primary CTA — monopoly. Never used elsewhere. |
| Typography | **Montserrat** (single family) | All text. No other font ever. |

Signature motifs: corner brackets (CAD viewfinder), quarter circles, single-color orange line illustrations on dark, yellow blurs over UI screenshots.

## What's in design-model.yaml

| Block | Purpose |
|---|---|
| `meta` | Version frontmatter — `version`, `brand_version`, `source`, `updated_by`, `supersedes`, `notes` |
| `primitives` | Raw color ramps (neutral 0–950, brand 50–950, semantic), spacing scale, radii |
| `tokens` | Semantic mappings — light/dark color modes, typography scale, motion, hero stage, iconography |
| `components` | Spec for buttons, cards (consumed by parspec-slides for chrome) |
| `voice` | Parspec voice rules — do / avoid (operational, MEP-industry vocabulary, no consumer-SaaS hype) |
| `avoid` | Forbidden colors / fonts / patterns — read by parspec-craft for lint |
| `primary_axis_preserved` | The locked anchors above |
| `invariants` | Hard rules (100vh viewport fitting, clamp typography, reduced-motion, CTA monopoly) |

## Operations

### Inspect

When user says "show me the Parspec brand" or similar:
1. Read `design-model.yaml`
2. Summarize `meta` (version, brand_version, supersedes, notes), `primary_axis_preserved`, secondary palette, tints, voice
3. If bundled previews exist at `previews/`, offer to open them

### Evolve

When user says "evolve to <description>" or "lock brand v2":
1. Read current `design-model.yaml`
2. Confirm changeset with user — which blocks change, which stay locked. NEVER touch `primary_axis_preserved` without explicit override.
3. Bump `meta.version` semantically (1.0.0 → 1.1.0 for tweak, 2.0.0 for major), set `meta.brand_version` (e.g., `2026-Q3-v1`), set `meta.supersedes` to prior brand_version
4. Update `primitives.*`, `tokens.colors.*`, and `avoid` list to match new direction
5. Update `meta.updated`, `meta.updated_by`, `meta.notes` (one-line rationale)
6. Run "Regenerate previews" (below)
7. Tell user: "Brand v<N> written. To lock it: `git add` + commit + `git tag brand-<version> -m '<rationale>'`"

### Roll back

When user says "roll back to <tag>":
1. `git tag --list 'brand-*'` — confirm tag exists
2. `git checkout <tag> -- plugins/parspec-design/skills/parspec-design/design-model.yaml`
3. Read the rolled-back file, summarize what reverted
4. Regenerate previews to match

### Regenerate previews

Bundled previews live at `previews/` and are committed alongside design-model.yaml so anyone can see the brand without running the skill. Templates at `references/`:

| Preview | Template |
|---|---|
| `previews/preview.html` | `references/preview-template.md` (Bento dashboard) |
| `previews/component-library.html` | `references/component-library-template.md` (sticky-TOC component spec) |
| `previews/landing-page.html` | `references/landing-page-template.md` (editorial narrative) |
| `previews/app-screen.html` | `references/app-screen-template.md` (product UI in device frame) |

Workflow:
1. Read `design-model.yaml`
2. For each preview template, fill in token values from the YAML
3. Write rendered HTML to `previews/<name>.html`
4. Open in browser for visual check
5. Each preview is self-contained — inline CSS, Montserrat from Google Fonts, no external deps

### Lint / audit

For "is this HTML on-brand?" — delegate to **parspec-craft**. That skill reads `design-model.yaml`'s `avoid` list and `primary_axis_preserved` block and applies them as lint rules to any target HTML.

## Versioning convention

| `meta.version` change | When |
|---|---|
| Patch (1.0.0 → 1.0.1) | Typo, comment, or non-token edit |
| Minor (1.0.0 → 1.1.0) | Add a new tint, adjust an existing token slightly |
| Major (1.0.0 → 2.0.0) | Replace secondaries, change typography, alter primary axis (rare) |

Tag every committed brand change:

```bash
git tag -a brand-2026-Q3-v1 -m "Q3 brand evolution: D2+D4 hybrid (Modern Industrial-Tech + Submittal personality)"
git push origin brand-2026-Q3-v1
```

## What this skill does NOT do

- Generate slides (that's `parspec-slides`)
- Lint other people's HTML (that's `parspec-craft`)
- Learn brands from URLs (this skill is single-tenant — it maintains Parspec's brand only). The "learn any brand" flow lives in upstream `dominikmartn/hue` if you ever need it.
