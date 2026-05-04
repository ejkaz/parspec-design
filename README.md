# Parspec Design

A composable Claude Code plugin stack that applies Parspec brand consistently across slides today and additional surfaces tomorrow. One install for every Parspec employee; one `design-model.yaml` as the brand source of truth.

Built for **Construction Materials Distributors** — Sonepar, Wesco, Border States, Rexel, Graybar.

## What's in this repo

Three plugins shipped from one marketplace:

| Plugin | Job |
|---|---|
| **`parspec-design`** | Maintains `design-model.yaml` — the single file every other Parspec skill reads. Versioned via YAML frontmatter and git tags; rollback is one command. |
| **`parspec-slides`** | Generates zero-dependency HTML decks with Parspec brand applied. Reads tokens from `parspec-design`. Forked from [`zarazhangrui/frontend-slides`](https://github.com/zarazhangrui/frontend-slides) — preserves viewport invariants, density limits, PPT/PDF/Vercel pipeline. |
| **`parspec-craft`** | Lints HTML against Parspec brand rules. Two layers: universal anti-AI-slop / color / typography (in this skill) + data-driven palette enforcement that reads the active `design-model.yaml`. |

The `design-model.yaml` is the contract. Brand evolution = yaml diff + git tag. Downstream skills auto-adapt.

## Install

```bash
/plugin marketplace add ejkaz/parspec-design
/plugin install parspec-design@parspec-design
/plugin install parspec-slides@parspec-design
/plugin install parspec-craft@parspec-design
```

Then in any Claude Code session:

| You say | Skill activates |
|---|---|
| "Make a Q2 board update deck" | `parspec-slides` |
| "Show me the current Parspec brand" | `parspec-design` |
| "Lint this HTML for Parspec brand" | `parspec-craft` |
| "Roll back to brand-2026-Q1-original" | `parspec-design` |

## Architecture

```
parspec-design/
├── .claude-plugin/marketplace.json         declares 3 plugins
├── plugins/
│   ├── parspec-design/                     Brand SSoT
│   │   └── skills/parspec-design/
│   │       ├── SKILL.md                    inspect / evolve / roll back / regenerate previews
│   │       ├── design-model.yaml           ★ active brand version (frontmatter + tokens + avoid + invariants)
│   │       └── references/                 hue templates (hero-stage, icon-kits, preview templates)
│   ├── parspec-slides/                     Slide generation
│   │   └── skills/parspec-slides/
│   │       ├── SKILL.md                    Phase 0–7 workflow (read design-model → generate → lint)
│   │       ├── viewport-base.css           hard invariants (100vh, clamp, reduced-motion)
│   │       ├── animation-patterns.md
│   │       ├── html-template.md
│   │       ├── assets/template.html        Parspec brand seed
│   │       ├── references/
│   │       │   ├── layouts.md              8 paste-ready Parspec slide layouts
│   │       │   └── legacy-presets.md       12 non-brand styles (Mode D / --preset)
│   │       └── scripts/                    extract-pptx.py · deploy.sh · export-pdf.sh
│   └── parspec-craft/                      Lint
│       └── skills/parspec-craft/
│           ├── SKILL.md                    universal + data-driven workflow
│           ├── anti-ai-slop.md             10 cardinal sins + soft tells
│           ├── color.md                    contrast + palette discipline + ICP register
│           └── typography.md               Montserrat-only + clamp() + ladder
└── README.md
```

## Locked primary axis

The immovable Parspec brand anchors. Any palette evolution may change secondaries / tints / motifs — but never these:

| Token | Hex | Role |
|---|---|---|
| Parspec Black | `#0F0F0F` | Default backgrounds |
| Charcoal | `#2E2E2E` | Layering / secondary surface |
| Off-white | `#F2F2F2` | Document / text-heavy surfaces |
| White | `#FFFFFF` | Text on dark |
| Brand Orange | `#FFA72B` | Primary CTA monopoly |
| Typography | **Montserrat** | All text — single family |

Signature motifs: corner brackets (CAD viewfinder), quarter circles, single-color orange line illustrations on dark, yellow blurs over UI screenshots.

## How to evolve the brand

1. Edit `plugins/parspec-design/skills/parspec-design/design-model.yaml`
2. Bump `meta.version` and `meta.brand_version`; set `meta.supersedes`
3. Update `primitives.*`, `tokens.colors.*`, and `avoid:` list
4. Commit + tag:
   ```bash
   git tag -a brand-2026-Q3-v1 -m "Q3 brand evolution: <rationale>"
   git push origin main brand-2026-Q3-v1
   ```
5. Teammates run `/plugin update` — every downstream skill picks up the new tokens automatically

## How to roll back

```bash
git checkout brand-2026-Q1-original -- plugins/parspec-design/skills/parspec-design/design-model.yaml
```

Or pin a specific deck to a brand version: it's just `git checkout <tag> -- design-model.yaml` before generation.

## Brand version history

| Tag | Date | Notes |
|---|---|---|
| `brand-2026-Q1-original` | 2026-03 | Original brand from March 2026 PDF. Secondaries (Blueprint Blue, Violet, Deep Rose) and pastel tints flagged for evolution — see CEO proposal in [Parspec_Brand_Evolution](../Parspec_Brand_Evolution/Artifacts/CEO_Proposal_2026-05-04.pdf) |

## Sharing decks

Generated decks are single self-contained HTML files. Two share paths:

```bash
# Live URL via Vercel
bash plugins/parspec-slides/skills/parspec-slides/scripts/deploy.sh ./my-deck.html

# PDF export via Playwright
bash plugins/parspec-slides/skills/parspec-slides/scripts/export-pdf.sh ./my-deck.html
```

## Requirements

- [Claude Code](https://claude.ai/claude-code) CLI
- For PPT conversion: Python with `python-pptx`
- For URL deployment: Node.js + Vercel account (free tier)
- For PDF export: Node.js (Playwright installs automatically)

## Credits

Built on three excellent open-source skills:

- [`zarazhangrui/frontend-slides`](https://github.com/zarazhangrui/frontend-slides) — slide generation foundation, kept as the upstream of `parspec-slides`
- [`dominikmartn/hue`](https://github.com/dominikmartn/hue) — design-model.yaml schema and brand-learning patterns, vendored selectively into `parspec-design`
- [`nexu-io/open-design`](https://github.com/nexu-io/open-design) — skill + design-system + craft stacking pattern, anti-AI-slop rules adapted into `parspec-craft`

## License

MIT — same as the upstream skills it's built on.
