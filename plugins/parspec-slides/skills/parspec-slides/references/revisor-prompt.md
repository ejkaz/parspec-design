# Revisor Subagent Prompt — Round 3 (targeted revisions)

One subagent per slide marked REVISE in Round 2. Runs in parallel × |revisions_needed|. Same identity as the original Round 1 writer where possible (preserves voice continuity).

---

## Inputs

- **Your original `plan.yaml` entry** for this slide (the conductor's brief — unchanged)
- **Your v1 outputs**: `slides/slide-NN.html` + `slides/slide-NN.manifest.yaml`
- **Your reviewer feedback**: `review/r1.yaml` `per_slide["NN"]` block specifically
  - `reasons` — specific issues to address
  - `cross_refs` — IDs of other slides you should peek at (read-only)
- **Cross-referenced slides' manifests** (read-only — for context on transitions)
- **prelude.css** (unchanged — same shared CSS prelude as Round 1)
- **references/layouts.md** (your assigned layout — unchanged)
- **design-model.yaml** (token authority — unchanged)

You do NOT receive feedback for OTHER slides. Stay scoped to your own.

---

## Tasks

### 1. Read your reviewer feedback carefully

Each reason in `review.reasons` is an actionable change request. Examples:

| Reason | Change |
|---|---|
| "pickup_line generic; doesn't transition to slide 04's opening" | Rewrite the closing line so it sets up slide 04's stat |
| "thesis duplicates slide 02" | Re-angle the thesis; don't repeat what 02 already said |
| "density: medium claimed but actually dense (3 paragraphs)" | Cut content to fit; raise concern in self_check if can't |
| "voice.caps_used inconsistent with rest of deck" | Apply tracked-caps to your section header |

### 2. Make MINIMAL changes

You are revising, not rewriting. Preserve as much of v1 as the feedback allows. Voice, structure, layout — keep them. Only change what the reviewer flagged.

### 3. Re-check your manifest

After updating the HTML, re-write the manifest. Update:
- `cross_refs.pickup_line` if you changed the closing line
- `content.word_count` and `content.elements.*` if content changed
- `revision.round` to `1`
- `revision.parent` to a reference to the v1 manifest (`slides/slide-NN.manifest.yaml`)
- `revision.changes_applied` — one line per change you made, mapping back to a `review.reasons` entry

### 4. Self-check before returning

- Does your pickup_line now transition to `expects_next`?
- Does your thesis differentiate from any cross_refs slides?
- Is `custom_css` still empty?
- Did you avoid raw hex literals?
- Does `content.density` still match the layout's allowed range?

If any check fails, raise it in `self_check.any_concerns` rather than pushing through.

---

## Output

Write to:
- `slides/slide-NN.v2.html`
- `slides/slide-NN.v2.manifest.yaml`

The conductor will pick `v2` over `v1` at reassembly time when both exist.

Do NOT modify or delete `slides/slide-NN.html` or `slides/slide-NN.manifest.yaml` — keep v1 for audit.

---

## What NOT to do

- Do not rewrite the slide from scratch unless reviewer says BLOCK (which goes to conductor, not you).
- Do not address feedback for OTHER slides. Your scope is YOUR slide only.
- Do not introduce new content not in the original brief. The reviewer asked for sharpening, not expansion.
- Do not increase density beyond the layout limit, even if the new content is "better."
- Do not change `slide.layout`. The conductor planned the layout; if it's wrong, that's a BLOCK case.

---

## Convergence note

If you've revised once and still get a REVISE in Round 5 (the final review), the subagent dispatcher should consider escalation:
- Try a fresh subagent (different identity, fresh take)
- Or escalate to Eric for direction
- Cap loops at Round 5 — never auto-revise more than twice
