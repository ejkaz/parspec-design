# Subagent Writer Prompt — Round 1 (parallel × N)

One subagent per slide. All writers run in parallel. Each writes ONE `<section class="slide">` block + a sidecar manifest. No cross-talk between writers.

---

## Inputs

- **plan.yaml entry for THIS slide** (your slot — `position`, `title`, `layout`, `thesis`, `hands_off`, `expects_prev`, `expects_next`, `density`, `cta_count`)
- **plan.yaml entries for PREV and NEXT slide** (read-only context — so you know what to lead into and what to set up)
- **prelude.css** (read-only — already has `:root` populated from design-model.yaml; reference it via `var(--…)`, never re-declare)
- **design-model.yaml** (read for token authority — but use roles via prelude.css, not raw hexes)
- **references/layouts.md** entry for YOUR assigned layout (L1–L8 — paste-ready structure)

You do NOT receive other writers' slides. Coordination happens via the manifest at the end.

---

## Tasks

### 1. Read the layout

Open `references/layouts.md`, find your assigned layout (L1–L8), copy the paste-ready HTML structure verbatim. The layout already includes brackets, section-bar, slide-footer, etc. Don't recreate these.

### 2. Fill the layout with content

Write content that delivers `intent.thesis` and only that. Stay within `content.density` budget (sparse = 1 heading + 1 line; medium = 1 heading + 4–6 bullets; dense = 1 heading + 2 paragraphs OR a stat row).

- Voice register: from plan.yaml `voice.register` — typically `terse-direct`.
- Section-head style: tracked-caps Montserrat (Parspec idiom).
- Numbers: real Parspec metrics ($22.5B quoted, 300+ distributors, 52% faster bid cycle) — never invented.
- MEP vocabulary where natural (distributors, submittals, BOM, quoting, schedule).
- Customer names (Sonepar, Wesco, Border States, Rexel, Graybar) where social-proof helps.

### 3. Set up the next slide

Your `cross_refs.pickup_line` (the closing thought / final line of your slide) should hand off to `expects_next`. Don't summarize — set up the next slide's opening. Examples:

- If `expects_next: "data-payoff-with-stats"` → pickup_line should *imply* a stat is coming, e.g., *"And the data backs it."*
- If `expects_next: "customer-quote"` → pickup_line should *imply* a voice is coming, e.g., *"Here's how a Sonepar VP put it."*

### 4. Use only role tokens

Reference `var(--cta)` not `#FFA72B`. Reference `var(--cool-primary)` not `#046F73`. Reference `var(--surface-paper)` not `#FAF7F0`. The prelude resolves these — using raw hexes is a parspec-craft `error`-level violation.

### 5. Density discipline

Respect the layout's max density (per layouts.md). If you can't fit the content, RAISE A FLAG in `self_check.any_concerns` — don't push past the limit. The reviewer will decide whether to split into two slides.

### 6. Write the manifest

After writing the slide HTML, write the sidecar manifest per `manifest.schema.yaml`. Be honest:
- `content.density` — actual rendered density, not planned
- `tokens_consumed` — every `var(--…)` you actually referenced
- `custom_css` — list ANY CSS you added beyond the layout's structure
- `cross_refs.pickup_line` — your actual closing line, verbatim
- `self_check.any_concerns` — anything ambiguous, missing context, or where you compromised

---

## Output

Write to:
- `slides/slide-NN.html` — the `<section class="slide">…</section>` block
- `slides/slide-NN.manifest.yaml` — full manifest per schema

Where `NN` is your `slide.position` zero-padded.

Do NOT include the `<!DOCTYPE>`, `<html>`, `<head>`, or shared `<style>` block — the conductor stitches those in at Round 4. You only write the `<section>` and the manifest.

---

## What NOT to do

- Do not invent metrics. Real numbers only.
- Do not add custom CSS unless the layout truly requires it (and then flag it).
- Do not exceed the density limit — flag instead.
- Do not include CTAs unless plan.yaml `cta` field for your slide is `1`. CTA monopoly is locked.
- Do not summarize at the end of the slide. Hand off to the next slide instead.
- Do not reference other slides ("as we saw on slide 3"). Slides should stand alone; if cross-reference is needed, conductor decides.
- Do not mix surface modes — your slide's bg comes from `plan.yaml.deck.surface_mode`. Decks are dark; product UI mocks are light. Don't switch within a single deck.
