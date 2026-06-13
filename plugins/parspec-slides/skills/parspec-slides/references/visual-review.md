# Visual Review — Optional Phase B (toggle: `visual_review: true`)

Manifest review (Round 2) catches narrative + density + voice + token discipline. It does NOT catch *visual* issues:
- Color clashes in actual rendered output
- Contrast failures the manifest didn't predict
- Layout regressions from clamp() at extreme viewports
- Spacing collisions when content runs longer than expected
- "I caught it by eye" issues (the v2 light-bg D4/D5 problem from earlier in this project)

Visual review is the v6-style "eye check" automated.

---

## When it runs

Visual review fires AFTER Round 4 reassembly produces `deck.html`, BEFORE delivery. If `visual_review: true` in plan.yaml.toggles:

```
   Round 4 (reassembly)
        │
        ▼
   deck.html exists
        │
        ▼
   ┌────────────────────────────┐
   │  Render to PNGs            │
   │  via Playwright            │
   │  (uses scripts/export-pdf.sh
   │   pipeline; outputs            
   │   render/slide-NN.png at      
   │   1920×1080)                  
   └─────────────┬──────────────┘
                 │
                 ▼
   ┌────────────────────────────┐
   │  Vision-capable reviewer   │
   │  (model: opus or sonnet,   │
   │   must support image input)│
   │                            │
   │  Reads each PNG + the      │
   │  slide's manifest. Checks  │
   │  the visual dimensions     │
   │  below.                    │
   └─────────────┬──────────────┘
                 │
                 ▼
   review/visual-r1.yaml
```

---

## What visual review checks (5 visual dimensions)

### V1. Contrast (ground truth)

Manifest says `tokens_consumed: [var(--brand-orange)]`. Manifest doesn't know whether the orange ended up as text on Off-white (1.73:1, fail) or fill on Black (9.87:1, pass). Visual review reads the rendered PNG and checks contrast on the actual element.

**FAIL trigger**: any text-on-surface combo below 4.5:1 normal / 3:1 large.

### V2. Layout regression

clamp() typography may compress at extreme viewports. The manifest's `content.density: medium` claim is structural, not layout-tested. Visual review confirms:
- No text overflow past slide bounds
- No layout collision (heading overlapping image, footer cut off)
- Corner brackets visible at all 4 corners where used
- Mini-charts/donuts render legibly at thumbnail scale

**FAIL trigger**: visible overflow, clipped content, illegible labels at body-text size.

### V3. Color rendering vs intent

Reviewer compares the rendered slide to its manifest's intent:
- "expected paper-warm panel + orange CTA" → actual PNG should show warm panel + orange button
- "expected teal-led chart" → chart should be predominantly teal in pixel sample

**FAIL trigger**: dominant rendered color ≠ manifest intent (e.g., manifest says "teal-led" but slide reads as orange-led at thumbnail).

### V4. Cross-slide visual rhythm

Reviewer scans all PNG thumbnails as a contact sheet (12 slides at small size) and checks:
- Does the deck have visual variety, or are all slides identical-looking?
- Are dense slides actually visually denser than sparse ones?
- Does the recommended slide stand out (more orange, more emphasis)?
- Does the deck "breathe" or feel monotonous?

**REVISE trigger**: contact-sheet shows monotony (all slides look identical) or fatigue (no breathing beats).

### V5. Anti-AI-slop visual check

The reviewer scans for visual tells the manifest can't catch:
- Stock-illustration-feel vs Parspec orange-line-illustration register
- Unintended gradients (parspec-craft errors on declared trust gradients but not on accidental ones)
- Spacing that feels like default Tailwind rather than Parspec rhythm

**REVISE trigger**: deck looks generic-AI-template at thumbnail scale.

---

## Output

```yaml
# review/visual-r1.yaml
visual_review_round: 1
reviewer_model: "opus"              # vision capability required
rendered_at: "2026-05-04T15:45:00Z"

per_slide:
  "03":
    pass: false
    findings:
      - dimension: V1
        issue: "Brand Orange used as accent type on a paper-warm panel — contrast 1.9:1 (FAIL AA)"
        fix: "use brand.800 #8C5800 for accent type per orange_type_on_light_forbidden invariant"
      - dimension: V2
        issue: "Footer overlaps with chart legend at 1280×720 viewport"
        fix: "raise mini-chart height or move footer down"

cross_slide_findings:
  - "Slides 04, 05, 06 are visually identical (same layout, same colors, same density). Add visual variety — use L5 quote layout for 05."

decision:
  ready_to_ship: false
  revisions_needed: ["03"]
  conductor_action: "render slide 03 v2 + re-run visual"
```

---

## Cost / speed implications

| Toggle | Time cost | Token cost | Catches |
|---|---|---|---|
| `visual_review: false` | 0 (skipped) | 0 | manifest-level only |
| `visual_review: true`, model = sonnet | +30–60s rendering + ~10K tokens vision | medium | most visual issues |
| `visual_review: true`, model = opus | +30–60s rendering + ~20K tokens vision | high | full anti-slop visual catch |

For low-stakes internal drafts: leave OFF.
For board decks, customer-facing, social-shareable: turn ON.

---

## Implementation note

The Playwright render reuses `scripts/export-pdf.sh`'s machinery — point it at intermediate PNGs instead of PDF assembly. Subagent dispatcher passes the rendered PNG directory to the visual-reviewer prompt. No new dependencies.
