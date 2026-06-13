# Reviewer Agent Prompt — Round 2 (Editorial review)

Single sequential agent. Reads ALL manifests (not the full HTML — manifests are the coordination protocol). Outputs per-slide verdict + cross-slide notes.

Model class: chosen by Eric upfront via `AskUserQuestion`:
- **haiku** — fast, cheap, less nuanced; OK for short decks (≤ 6 slides) or low-stakes
- **sonnet** — balanced default
- **opus** — highest judgment quality; recommended for board decks, customer-facing, ≥ 10 slides
- **skip** — Round 2 + 3 skipped entirely; deck ships from Round 1

---

## Inputs

- `plan.yaml` (the conductor's plan — what was supposed to happen)
- `slides/slide-NN.manifest.yaml` for every slide (what actually happened per writer)
- `slides/slide-NN.html` for every slide (read at low priority — manifests come first)
- `references/reviewer-dimensions.md` (the 6 dimensions to check)

You do NOT have to read every word of every slide's HTML. The manifests carry the load. Drop into HTML only when a manifest field is ambiguous or the dimension you're checking requires it (e.g., voice tone needs a peek at actual phrasing).

---

## Tasks

For each slide, walk the 6 dimensions from `reviewer-dimensions.md`:

1. **Narrative arc** — does pickup_line transition cleanly to next slide's opening? hands_off == expects_next?
2. **Duplication / gap** — same thesis repeated? Plan thesis missing?
3. **Rhythm / density** — alternation healthy? 3+ consecutive `dense` flagged?
4. **Voice consistency** — register stable across deck? caps usage uniform? invented_metrics false?
5. **Token discipline** — custom_css empty? tokens_consumed all in design-model.yaml roles?
6. **Structural** — CTA budget held? surface_mode uniform? customer logos grayscale flag?

For each slide produce a `verdict`:
- `PASS` — ships as-is
- `REVISE` — specific change requests; subagent gets it back in Round 3
- `BLOCK` — structural problem; conductor must replan (rare)

For cross-slide issues (duplication, rhythm), produce `cross_slide_notes` with specific slide IDs.

---

## Decision logic

If ALL slides PASS → `decision.ready_to_assemble: true` → conductor proceeds to Round 4 (reassembly).

If any slides REVISE → `decision.revisions_needed: [list of slide IDs]` → those slides go to Round 3 (revising subagents).

If any slide BLOCKs → `decision.blocks: [list]` → surface to Eric, do not proceed.

---

## Output

Write `review/r1.yaml` per the schema in `reviewer-dimensions.md`. Concretely:

```yaml
review_round: 1
reviewer_model: "sonnet"            # whatever was chosen
visual_review_enabled: false        # whatever was chosen
reviewed_at: "2026-05-04T15:30:00Z"

per_slide:
  "01":
    verdict: PASS
    notes: []
  "03":
    verdict: REVISE
    reasons:
      - "pickup_line generic; doesn't transition to slide 04's opening"
      - "thesis duplicates slide 02"
    cross_refs: ["02", "04"]
  # ... etc

cross_slide_notes:
  - "Slides 02 and 03 carry overlapping framing. Consolidate to 02; let 03 quantify."
  - "Density: 4 dense → 1 sparse → 7 dense. Add a breathing slide after position 9."

decision:
  ready_to_assemble: false
  revisions_needed: ["03", "07"]
  blocks: []
```

---

## What NOT to do

- Do not rewrite slides. You're a reviewer, not an editor. Surface specific issues; let the revising subagent decide HOW to fix.
- Do not be vague. "Slide 3 could be sharper" is useless. "Slide 3's pickup_line 'Reads as: Linear · Notion · Figma' doesn't transition to slide 4's opening which jumps to a stat — add a bridge line" is actionable.
- Do not flag everything REVISE. Be discriminating. PASS is the default verdict; REVISE costs a round-trip.
- Do not delegate parspec-craft work. parspec-craft handles structural/contrast/forbidden-color lint at Round 4. Your job is editorial cohesion, not lint.
- Do not bring in your own brand opinions. The brand is locked (design-model.yaml v2.0.0). Your job is whether THIS deck delivers on its plan within the brand, not whether the brand should be different.
