# Reviewer Dimensions — the 6 things the editorial reviewer checks

The reviewer reads the **manifests** (not the full HTML — manifests are the coordination protocol). Each dimension has a clear pass/fail rule with examples. The reviewer outputs `review/r1.yaml` with `PASS | REVISE | BLOCK` per slide plus cross-slide notes.

---

## 1. Narrative arc

**Question**: do the slide intents stitch into a coherent story?

**Check**: walk through `intent.thesis` for each slide in `slide.position` order. Each thesis should land somewhere new AND set up the next.

- Pair `intent.hands_off` of slide N with `intent.expects_next` of slide N — they should describe the same handoff.
- Pair `cross_refs.pickup_line` of slide N with the opening of slide N+1 — should transition cleanly.

**REVISE trigger**: pickup_line is generic ("In conclusion"), or doesn't match the next slide's opening, or two adjacent slides hands_off the same content.

---

## 2. Duplication / gap

**Question**: is the same idea hit twice? Is the originally-planned thesis missing entirely?

**Check**: cluster `intent.thesis` across all slides. Group near-duplicates. Diff against `plan.yaml` to see if any planned thesis got dropped.

**REVISE trigger**: two slides carry the same thesis (consolidate to one). Plan included a thesis no slide carries (assign to one).

**BLOCK trigger**: 3+ slides on the same thesis (deck is structurally repetitive — re-plan, don't revise).

---

## 3. Rhythm / density

**Question**: does the deck have alternating density? Or is it a wall of dense slides?

**Check**: look at `content.density` sequence. Healthy decks alternate dense → sparse → medium → dense, etc. Procore pattern: one tight section, one breathing section.

**REVISE trigger**: 3+ consecutive `dense` slides (audience fatigue). 3+ consecutive `sparse` slides (loss of momentum).

---

## 4. Voice consistency

**Question**: is the same voice register used across all slides?

**Check**: look at `voice.register`. Should match `design-model.yaml` `voice.do` declaration (typically `terse-direct` for Parspec).

- `voice.caps_used` should be consistent (either every section heading uses tracked-caps, or none — not mixed).
- `voice.invented_metrics: true` is an automatic REVISE.
- `voice.mep_vocabulary` should appear in at least 2 slides (deck reads as in-tribe).

**REVISE trigger**: register drift (one slide is `terse-direct`, another is `marketing-warm`). Caps usage inconsistent.

---

## 5. Token discipline

**Question**: are slides reaching off-palette, or sticking to design-model.yaml roles?

**Check**:
- `custom_css: []` should be empty for every slide (the shared prelude already has everything needed). Non-empty triggers conductor review.
- `tokens_consumed` should be a subset of `design-model.yaml` defined roles. Any hex literals (e.g., `#3A7AB8`) are violations.
- `self_check` flags should all be `true`.

**REVISE trigger**: `custom_css` non-empty without justification. Hex literals in `tokens_consumed`. `self_check.any_concerns` non-null.

---

## 6. Structural / brand-craft

**Question**: do invariants hold across the deck?

**Check** (delegated partially to `parspec-craft` — but reviewer pre-screens):
- CTA monopoly: total CTA count across deck ≤ 2 visible per fold (not per deck — per fold). Sum `content.elements.ctas`.
- Surface mode: every slide's `slide.surface_mode` == `brand_artifacts` for a deck (decks are brand artifacts, run dark). Mixed-mode is a flag.
- Customer logos: if any slide has a logo wall, `content.elements.images` > 0 with a flag for grayscale (parspec-craft enforces).

**REVISE trigger**: surface_mode mismatch (one slide marked `product_ui` in a deck context). CTA fatigue (5+ CTAs across deck).

**BLOCK trigger**: forbidden colors (delegate to parspec-craft for the actual lint, but reviewer flags if `tokens_consumed` includes legacy_v1 references).

---

## Output schema

```yaml
# review/r1.yaml — written by reviewer after reading all manifests
review_round: 1
reviewer_model: "sonnet"            # haiku | sonnet | opus per Eric's choice
visual_review_enabled: false
reviewed_at: "2026-05-04T15:30:00Z"

per_slide:
  "01":
    verdict: PASS
    notes: []
  "02":
    verdict: PASS
    notes: ["voice.caps_used inconsistent with slide 01 — minor"]
  "03":
    verdict: REVISE
    reasons:
      - "pickup_line ('Reads as: Linear · Notion · Figma') doesn't transition
         to slide 04's opening which jumps straight to a stat — add a
         one-line bridge"
      - "duplicates slide 02's framing too closely; differentiate"
    cross_refs: ["02"]
  "04":
    verdict: PASS
  # ...

cross_slide_notes:
  - "Slides 02 and 03 both make the 'consumer-SaaS' framing argument.
     Consolidate into 02; let 03 do something else (perhaps quantify)."
  - "Density profile is 4 dense → 1 sparse → 7 dense. Add a breathing
     beat after slide 09 — consider a quote or single-image slide."

decision:
  ready_to_assemble: false          # true only if all slides PASS
  revisions_needed: ["03"]
  blocks: []
```

---

## Convergence

After Round 3 (targeted revisions return), re-run reviewer (Round 2 again) on changed slides only:
- If all slides now PASS → assemble (Round 4)
- If some still REVISE → Round 5 (one more targeted revision)
- Cap at Round 5. If still not converged → surface to Eric.

Empirically: most decks converge at the first review pass (Round 2 → Round 3 → Round 4 = done).
