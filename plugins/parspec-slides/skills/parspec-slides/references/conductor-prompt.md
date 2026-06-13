# Conductor Agent Prompt — Round 0 (Planning)

Single sequential agent. Plans the deck before any parallel work begins. Outputs `plan.yaml` (per-slide briefs) and resolves the shared CSS prelude from `design-model.yaml`.

---

## Inputs

- Eric's brief: deck topic, audience, length, content readiness
- Toggle answers from upfront `AskUserQuestion`:
  - `reviewer_model`: haiku | sonnet | opus | skip
  - `visual_review`: true | false
- `design-model.yaml` (read for token authority + voice rules)
- `viewport-base.css` (read for invariants — full file inlined into prelude)
- `references/layouts.md` (read for the L1–L8 layout catalog)

---

## Tasks

### 1. Outline

Produce a slide-by-slide outline. For each slide:
- A short title (≤ 50 chars)
- The `intent.thesis` (the ONE idea this slide carries)
- The chosen layout (L1–L8) — pick from layouts.md
- The `intent.hands_off` (what this slide deliberately leaves for the next slide)
- The `intent.expects_prev` and `intent.expects_next` (transition expectations)

### 2. Density planning

Plan density across the deck. Healthy alternation: dense → sparse → medium → dense. Avoid 3+ consecutive dense slides. If the topic forces dense content, insert a deliberate "breathing beat" (single-quote slide, single-image slide).

### 3. Resolve the shared prelude

Resolve all `var(--…)` references from `design-model.yaml` into a concrete `:root` block. Inline `viewport-base.css` in full. This becomes `prelude.css` — every parallel writer gets the same prelude verbatim.

### 4. CTA budget

Decide the CTA budget upfront: how many primary actions (Brand Orange filled buttons) appear in this deck? Typically 0–2. Allocate them to specific slides in the plan. Other slides MUST NOT include CTAs (CTA monopoly).

### 5. Write `plan.yaml`

```yaml
deck:
  topic: "Q2 board update"
  audience: "Parspec board"
  total_slides: 12
  surface_mode: brand_artifacts        # decks are always dark
  cta_budget: 2
  cta_assigned_to: ["01", "12"]        # title + decision-asked slides
  toggles:
    reviewer_model: "sonnet"
    visual_review: false
  voice:
    register: "terse-direct"
    caps_idiom: true                   # tracked-caps section heads
  shared_prelude_path: "prelude.css"

slides:
  - position: 1
    title: "Q2 BOARD UPDATE"
    layout: L1-title
    thesis: "frame the board check-in; preview the 3 takeaways"
    density: sparse
    hands_off: ["the 3 metrics that follow"]
    expects_prev: null                 # title slide
    expects_next: "exec-summary-with-3-stats"
    cta: 1                             # title CTA, e.g. "Tap to navigate"

  - position: 2
    title: "Three takeaways"
    layout: L2-metric
    thesis: "summarize the quarter in 3 numbers"
    density: medium
    hands_off: ["the rest of the deck unpacks each"]
    expects_prev: "title-with-frame"
    expects_next: "first-takeaway-deep-dive"
    cta: 0
  # ... etc
```

### 6. Sanity-check the plan against `design-model.yaml`

- Every layout chosen exists in layouts.md (L1–L8).
- Total CTAs across plan ≤ cta_budget.
- Surface mode matches the deck class (decks → `brand_artifacts` → dark).
- No invented metrics in the thesis statements (the writer-subagent prompts will reinforce this; conductor sets the example).

---

## Output

Write to:
- `plan.yaml`
- `prelude.css` (resolved from design-model.yaml)

These become the read-only inputs to every Round 1 writer subagent.

---

## What NOT to do

- Do not write any slide HTML. That's Round 1.
- Do not over-spec content for each slide. Writer subagents need room to choose words. Give them the thesis + 3–5 supporting points; let them craft.
- Do not assign more than 2 layouts per deck if avoidable — visual rhythm is better with layout repetition than layout sprawl.
- Do not include CTAs on every slide. Hold the budget tight.
