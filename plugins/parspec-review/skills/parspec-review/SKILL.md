---
name: parspec-review
description: Design jury skill — 4 parallel vision-capable critic agents + 1 aggregator that review a rendered parspec-slides deck. Replaces the single-Opus visual review pass (Round 5b) with a juror panel that catches compositional, data-viz, brand-fidelity, and anti-AI-slop issues a single reviewer misses. Plug-in replacement for parspec-slides Round 5b.
version: 0.1.0
brand_version: "2026-Q3-v1"
status: draft
prior_art:
  - garrytan/gstack/plan-design-review (7-pass framework + AI-slop blacklist)
  - jezweb/claude-skills/design-review (7 named dimensions + thresholds)
  - calimero-network/ai-code-reviewer (5 parallel critics + severity × agreement aggregation)
  - thunlp/ChatEval (persona-diversity essential — shared persona degrades juror independence)
  - Cohere "Replacing Judges with Juries" arXiv:2404.18796 (PoLL — 3–4 small jurors > 1 big judge at 7× lower cost)
  - magicuidesign/magicui (bento-grid + animated-beam patterns)
  - ChartsCSS/charts.css (pure-CSS chart vocabulary)
  - mermaid-js/mermaid-cli (build-time SVG diagram injection)
---

# parspec-review — design jury for parspec-slides

## When to use

After parspec-slides Round 4 produces `deck.html` and Round 5 renders 55 PNGs to `render/slide-NN.png`, invoke parspec-review **instead of** the single-Opus visual reviewer. The skill orchestrates 4 specialized critic agents in parallel against each slide, then aggregates their findings with severity × agreement clustering.

Trigger: `plan.yaml` carries `toggles.visual_review_mode: jury` (vs. legacy `single`).

## What it produces

`/path/to/deck/review/visual-r1.yaml` — same schema parspec-slides Round 4/Round 5 already understand. The verdict structure is unchanged; the difference is `findings[].juror` carries a juror identifier and the verdict is computed from juror agreement, not a single model's call.

## Architecture

```
                    plan.yaml + render/slide-NN.png + manifests
                                      │
                                      ▼
        ┌─────────────────────────────────────────────────┐
        │            DESIGN JURY (parallel × N=4)         │
        │                                                 │
        │  ┌─────────────────┐  ┌─────────────────┐       │
        │  │ Composition     │  │ Data-Viz        │       │
        │  │ Critic          │  │ Critic          │       │
        │  │ (PNG+manifest)  │  │ (PNG+manifest+  │       │
        │  │                 │  │  chart data)    │       │
        │  └─────────────────┘  └─────────────────┘       │
        │  ┌─────────────────┐  ┌─────────────────┐       │
        │  │ Brand Fidelity  │  │ Anti-AI-Slop    │       │
        │  │ Critic          │  │ Critic          │       │
        │  │ (PNG+manifest+  │  │ (PNG ONLY —     │       │
        │  │  design-model)  │  │  no priming)    │       │
        │  └─────────────────┘  └─────────────────┘       │
        └─────────────────────────────────────────────────┘
                                      │
                                      ▼
        ┌─────────────────────────────────────────────────┐
        │          AGGREGATOR (Sonnet, text only)         │
        │                                                 │
        │  cluster by (slide, dimension, region)          │
        │  score = severity × juror_agreement             │
        │  BLOCK if any cluster ≥ 0.8                     │
        │  REVISE if any cluster ≥ 0.4                    │
        │  PASS otherwise                                 │
        └─────────────────────────────────────────────────┘
                                      │
                                      ▼
                          review/visual-r1.yaml
```

## The 4 jurors

| Juror | Reviews | Inputs | Why parallel | Source |
|---|---|---|---|---|
| **Composition Critic** | focal hierarchy, grid discipline, white-space rhythm, F/Z reading pattern | PNG + manifest | Layout fit varies per slide; vision sees what manifests can't | gstack 7-pass + jezweb dims |
| **Data-Viz Critic** | chart-type fit, encoding choice, label legibility, data-ink ratio | PNG + manifest + extracted chart data | Charts have correctness criteria orthogonal to layout | Tufte heuristics |
| **Brand Fidelity Critic** | token discipline rendered, single-accent rule, surface mode coherence | PNG + manifest + design-model.yaml excerpt | Brand violations only visible when rendered | Autodesk single-accent doctrine |
| **Anti-AI-Slop Critic** | template-feel, generic gradients, stock-illustration register, default-Tailwind rhythm | **PNG only — manifest deliberately withheld** | Manifest priming biases toward "looks like what was planned"; ChatEval shows shared context degrades juror independence | gstack AI-slop blacklist |

Each juror runs Opus (vision capable). Total per-slide cost ≈ 4× a single visual review pass; PoLL paper says this beats one Opus judge at 7× lower cost than scaling up to a single bigger model.

## The aggregator

Sonnet, text-only. Reads each juror's per-slide YAML output, clusters findings by `(slide_id, dimension, region)` (region = top/middle/bottom for spatial deduplication), then computes:

```python
cluster.agreement = len(distinct_jurors_in_cluster) / 4
cluster.severity  = max(finding.severity for finding in cluster.findings)
cluster.score     = cluster.severity * cluster.agreement
```

Verdict thresholds (calimero pattern, tuned for visual review):
- `score ≥ 0.8` (severity ≥ 0.8 + 4-juror agreement, OR severity = 1.0 + 3-juror) → **BLOCK** for that slide
- `score ≥ 0.4` (severity ≥ 0.5 + 2-juror agreement, OR severity ≥ 0.8 + 1-juror) → **REVISE**
- otherwise → **PASS**

A finding flagged by a single juror at low severity is informational, not actionable. A finding flagged by 3+ jurors is load-bearing — the deck has a real problem there.

## How parspec-slides invokes it

Phase 5 of parspec-slides currently runs:

```bash
node scripts/render-pngs.js deck.html render/         # already exists
# THEN: single-agent visual review of each PNG → review/visual-r1.yaml
```

Replace the second step with:

```python
# parspec-slides/scripts/run-design-jury.py
from parspec_review import DesignJury
jury = DesignJury(
    deck_dir="/path/to/deck",
    plan_yaml="plan.yaml",
    render_dir="render/",
    output="review/visual-r1.yaml",
    jurors=["composition", "dataviz", "brand-fidelity", "anti-slop"],
    aggregator="sonnet",
)
jury.run()  # dispatches 55 × 4 = 220 parallel juror calls in batches; aggregator runs after
```

The jury writes a schema-compatible `review/visual-r1.yaml` so Round 5b/5c (revisor dispatch + reassembly) work unchanged. Add `findings[].juror` and `decision.verdict_source: "jury"` for audit.

## Files in this skill

```
parspec-review/
├── SKILL.md                          (this file — what + when + architecture)
├── references/
│   ├── jury-architecture.md          (longer-form rationale + invariants)
│   ├── juror-composition.md          (Composition Critic prompt)
│   ├── juror-dataviz.md              (Data-Viz Critic prompt)
│   ├── juror-brand-fidelity.md       (Brand Fidelity Critic prompt)
│   ├── juror-anti-slop.md            (Anti-AI-Slop Critic prompt — note: PNG-only)
│   ├── aggregator-prompt.md          (Aggregator prompt + clustering rules)
│   └── verdict-schema.yaml           (output schema, compatible with parspec-slides)
└── (future) scripts/
    └── run-design-jury.py            (orchestrator — dispatcher + aggregator wrapper)
```

## Roadmap

- v0.1.0 (this draft): prompts + schema + integration spec. Manual orchestration via Agent tool calls.
- v0.2.0: `scripts/run-design-jury.py` — automated dispatch + aggregation.
- v0.3.0: contact-sheet juror — gets all 55 thumbnails as a 12-up grid, reviews cross-slide rhythm + register drift at deck scale (currently a gap; visual-review.md V4 covers this single-pass but with limited diversity).
- v0.4.0: anti-juror calibration — sample 50 known-good and 50 known-AI-slop decks; tune juror thresholds against ground truth.

## What this skill is NOT

- Not a replacement for parspec-slides editorial reviewer (Round 2). That covers narrative/voice/density. This jury covers compositional/visual quality only.
- Not a brand definition. The brand SSoT remains design-model.yaml in parspec-design.
- Not a code formatter. parspec-craft handles structural HTML lint, contrast checking, and forbidden-color/font enforcement. This jury operates on rendered output.
