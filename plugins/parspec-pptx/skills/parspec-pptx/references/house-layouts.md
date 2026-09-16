# House register — layout recipes

Canvas 10 × 5.625 in. The template supplies the logo, footer and page number.
Build inside the content band `deck.top` → `deck.bottom` (master 1.35 → 5.05,
townhall 1.42 → 4.95), left edge `deck.x0` = 0.44, width `deck.xw` = 9.12.
Every recipe below runs in `scripts/house_example.py`.

```python
from assets import shapes as sh
from assets.house import HouseDeck
d = HouseDeck("master")          # or "townhall"
pal, X0, XW, TOP, BOTTOM = d.pal, d.x0, d.xw, d.top, d.bottom
```

## Shared chrome (both profiles)

| Call | master | townhall |
|---|---|---|
| `d.cover(lines, subtitle, byline, date=, eyebrow=)` | Black; wordmark top-left; 40 pt bold title; orange rule; date; "Presented by"; arcs bottom-right | Laptop-render layout; eyebrow with tick; date · byline on one line |
| `d.agenda([(title, descriptor, minutes)])` | Light 30 pt heading left; vertical hairline; rows = orange number, caps caption, 15 pt title, minutes | Orange bold heading; rows = number, bold title, italic descriptor, minutes |
| `d.divider(heading, minutes, accent=, kicker=, strip=, tagline=, footnote=)` | Glow-corner layout; 33 pt caps heading with orange phrase; kicker above | Logo + arcs; 30 pt bold heading; numbered strip |
| `d.content(title, accent=, subtitle=, eyebrow=, glow=True)` | ALL-CAPS 25 pt light title + orange phrase; full glow (`glow=False` for plain black); no eyebrow by default | 24 pt bold mixed-case + orange phrase; eyebrow recommended |

Title rule for both: one accent phrase at the end, never a single highlighted word mid-sentence.
The subtitle is the "so-what" line: one sentence, 11 pt muted.

---

## Master profile (default)

| # | Recipe | Call | Use for |
|---|---|---|---|
| M1 | Overview tiles | `sh.tile_row(s, X0, TOP+0.25, XW, 2.3, [(LABEL, value, body)]*4)` | "At a glance" / "where we stand"; add a 12 pt italic closing statement at y 4.2 |
| M2 | Numbered cards | `sh.numbered_cards(s, X0, y, XW, h, items, highlight=i, dim=(…))` | Success criteria, paths, horizons, processes (3–5 cards) |
| M3 | Panel rows | `sh.panel_rows(s, X0, TOP+0.15, XW, [(LABEL, heading, body)]*3)` | Objectives, "what it means", solution-by-product |
| M4 | Problem → solution | `sh.problem_solution(s, X0, TOP+0.45, XW, rows, headers=(…))` | Objection handling, value creation; stat + caps label per row |
| M5 | Bracketed 2×2 | `sh.bracket_box(…, fill=pal.card)` ×4 + label + quote + context | "What we've heard" — customer or stakeholder themes |
| M6 | Umber funnel | `sh.funnel(s, levels, pal, ramp="umber")` | Pipelines; the last level is the point |
| M7 | KV band | `sh.shape(RECTANGLE, fill=pal.card, line=pal.card_line)` + 3 × label/value | Timing, size, owner under a card row |
| M9 | Band scorecard | `sh.band_scorecard(s, X0, 1.42, XW, rows, row_h=0.46–0.65)` | Metrics vs a Below / Acceptable / Strong / Top-tier bar; status = shape + label |
| M10 | Belief scorecard | `sh.status_rows(s, X0, 1.5, XW, rows)` | Qualitative proven / building / unproven with evidence + next step |
| M11 | Hero cards | `sh.hero_cards(s, X0, y, XW, h, cards)` | Editorial metric cards: label, big value, meaning, basis, why / benchmark / priority. Status in words; no tracks |
| M12 | Word chip | `sh.state_chip(s, x, y, "Building")` | Evidence state without traffic-light colour (umber pill) |
| M8 | Closing | `d.divider("Ask me", accent="anything", kicker="Open Q&A", tagline=…)` | Q&A, "partner with us" |

### M2 — numbered cards

```python
sh.numbered_cards(s, X0, TOP + 0.2, XW, 2.75, [
    dict(num="I", title="Horizon one", tag="Built", body=["…", "…"]),
    dict(num="II", title="Horizon two", tag="Now", body=["…", "…", "…"]),
    dict(num="III", title="Horizon three", tag="Next", body=["…", "…"]),
], pal, gap=0.2, highlight=1, dim=(2,), number_size=30)
```

- `num` can be any short string: 1–5, roman numerals, "≥80%". Use numerals only for real sequences or ranked stages.
- `tag` sits above the rule (durations, "WE ARE HERE", "NEXT"). `lead` is an optional accent headline above the body.
- `highlight` draws the lighter panel. `dim` greys the top bar, number and text for future or out-of-scope items.
- Body is a list of bullets. Keep each bullet to one line at card width (≈ 28 characters for 3 cards, ≈ 22 for 5), or the list spills past the card; the renderer doesn't clip.

### M4 — problem → solution

```python
sh.problem_solution(s, X0, TOP + 0.45, XW, [
    ("Question in the customer's words?", "00%", "Proof label", "One-line proof."),
], pal, headers=("The question", "Our proof"))
```

The left boxes are numbered in muted grey because the rows are an ordered list, not a process. Keep the stat short (≤ 6 characters) so the caps label fits beside it.

### M5 — bracketed 2×2

```python
cw, ch = (XW - 0.3) / 2, (BOTTOM - TOP - 0.35) / 2
for i, (lab, quote, ctx) in enumerate(cells):
    x, y = X0 + (i % 2) * (cw + 0.3), TOP + 0.1 + (i // 2) * (ch + 0.25)
    sh.bracket_box(s, x, y, cw, ch, pal, fill=pal.card)
    sh.label(s, x + 0.25, y + 0.22, cw - 0.5, lab, pal, size=10)
    sh.text(s, x + 0.25, y + 0.5, cw - 0.5, 0.5, quote, size=13, bold=True)
    sh.text(s, x + 0.25, y + 1.12, cw - 0.5, ch - 1.2, ctx, size=10, color=pal.subtle)
```

Use `sh.crosshair(s, x, y, pal)` sparingly: one registration mark at a group corner, not one per card.

### Scorecards for a firmwide room (Astra design review, 2026-09-16)

- An editorial deck wants **hero cards (M11) or a 3×2 graded card grid**, not a 7×5 band table. The dense `band_scorecard` suits appendices and board packs.
- **Grade against an explicit rubric:** At reference (● green) / Building or Verify (▲ yellow) / Gap (■ red). Colour lives only in the status symbol; the orange top rule stays brand furniture. Write the rubric in a small legend plus "directional references, not pass/fail tests".
- **Don't grade what you can't compare:** show it as context (e.g. ARR with no sourced floor) or mark it VERIFY (definitions differ).
- **One reference set across slides:** the "how the bar changed" slide and the scorecard must quote the same benchmarks.

### M9 / M10 — scorecards

```python
d.content("Our Scorecard:", accent="Where We Stand", eyebrow="Series B readiness", style="eyebrow")
sh.band_scorecard(s, X0, 1.42, XW, [
    dict(name="Net revenue retention", why="Proxy for product-market fit", value="000%", num=0,
         trend="▼ from 000%", bands=(100, 110, 120), bands_text=["<100%", …], target="Hold 120%+"),
    dict(name="Burn multiple", why="Cash per $1 of new ARR", value="0.0x", num=0,
         bands=(2.0, 1.5, 1.0), higher_better=False),          # lower-is-better flips the track
], pal, row_h=0.46)                                            # ≤7 rows at 0.46; ≤5 at 0.6+
```

- `bands` = entry thresholds (acceptable, strong, top-tier). The zones draw at equal width (ordinal) and the marker sits proportionally inside its zone.
- `status=` overrides the computed zone when judgment differs (e.g. a metric judged on a different bar). Say why in the `why` line.
- Status always carries **shape + label** (● strong/top-tier, ▲ acceptable, ■ below bar) in status-role colors. The brand's amber and red fail colorblind separation, so never rely on color alone. Status labels use text ink; the shape carries the color.
- `trend` is a muted line under the value: direction only, no color.
- `style="eyebrow"` gives the master deck's second title register (orange caps eyebrow + 24 pt bold title), which matches CEO outline decks built from the master.
- Speaker notes must carry each band's source and each value's basis. Use a `BASIS` switch when two definitions compete (e.g. gross vs net new ARR).

---

## Townhall profile

| # | Recipe | Call | Use for |
|---|---|---|---|
| T1 | KPI tiles + chips | `sh.kpi_tile` × 3 + `sh.chip_row` | "Where we stand" |
| T2 | Three accent cards + KV band | `sh.card` × 3 + `sh.card(accent=None)` | Priorities, reasons, pillars |
| T3 | Process | `sh.process(stages, current, pal)` | Stages with a "we are here" marker |
| T4 | Funnel | `sh.funnel(levels, pal)` (alpha ramp) | Narrowing counts |
| T5 | Resonating + questions | `sh.card` + bullets, `sh.question_cards` | Feedback / FAQ |
| T6 | Question → evidence | `sh.evidence_rows(rows)` | Objection handling |
| T7 | Dyad + help strip | 2 × `sh.card(accent=)` + 4 chips | "What it means for you" |
| T8 | Divider with strip | `d.divider(h, "(20 minutes)", strip=[…], active=i)` | Section openers |

### T1 — KPI tiles + chips

```python
w = (XW - 0.4) / 3
for i, (lab, val, delta) in enumerate(tiles):          # ≤ 3 tiles
    sh.kpi_tile(s, X0 + i * (w + 0.2), TOP, w, 1.5, lab, val, delta, pal)
sh.label(s, X0, 3.18, 4, "Since last quarter", pal)
sh.chip_row(s, X0, 3.44, XW, 1.5, [(headline, detail)] * 4, pal)
```

`delta` can be runs: `[("+00% ", {"color": pal.good}), ("vs. last year", {})]`.
Only the favourable part gets `pal.good`; a miss stays muted text unless the slide is about the miss.

### T2 — three accent cards + KV band

```python
for i, (lab, head, body) in enumerate(cards):
    x = X0 + i * (w + 0.2)
    sh.card(s, x, TOP, w, 2.35, pal)
    sh.label(s, x + 0.26, TOP + 0.22, w - 0.4, lab, pal)
    sh.text(s, x + 0.26, TOP + 0.48, w - 0.4, 0.4, head, size=16, bold=True)
    sh.text(s, x + 0.26, TOP + 1.0, w - 0.46, 1.25, body, size=10, color=pal.muted)
sh.card(s, X0, 4.0, XW, 0.92, pal, accent=None)        # key/value band: 3 columns
```

### T3 — process

```python
sh.process(s, [(name, detail)] * 5, current=1, pal=pal)   # y=1.5, step 1.81, w 1.95
```

Done stages are accent at 35% with a deep stroke, the current stage is solid accent
with dark type, and upcoming stages are card-colored with muted type. Five stages fill
the width; for four, pass `step=2.27, w=2.4`.

### T4 — funnel

```python
sh.funnel(s, [(value, label, detail)] * 4, pal)   # widths 4.1 → 1.85, labels at x 5.0
```

Counts are cumulative: each level is a subset of the one above it. Add a 7 pt "as of" footnote at y 4.98.

### T5–T7

```python
sh.question_cards(s, X0 + 3.75, TOP, XW - 3.75, [(q, context)] * 3, pal)
sh.evidence_rows(s, X0, TOP, XW, [(question, proof_headline, detail)] * 3, pal)
sh.card(s, X0, TOP, cw, 2.2, pal, accent="accent")   # dyad left; right uses accent="muted"
```

---

## Speaker notes convention

```python
d.notes(s, """
SOURCE: <deck / file, slide, as-of date>
[CONFIRM] <figure or claim the presenter must verify>
[DISCLOSURE] <what was deliberately left off and whose call it is>
""")
```
