# Town hall register — layout recipes

Canvas 10 × 5.625 in. The template supplies the logo, footer and page number;
build inside the content band `TOP`=1.42 → `BOTTOM`=4.95, left edge `X0`=0.44,
width `XW`=9.12. Every recipe below is live in `scripts/townhall_example.py`.

```python
from assets import shapes as sh
from assets.townhall import TownHall, X0, XW, TOP, BOTTOM
th = TownHall(); pal = th.pal
```

## Quick index

| # | Recipe | Call | When |
|---|---|---|---|
| T1 | Cover | `th.cover(lines, subtitle, byline, eyebrow=)` | First slide; product laptop render comes from the layout |
| T2 | Agenda | `th.agenda([(title, descriptor, minutes)], blurb=)` | ≤ 6 rows; numbered (a sequence) |
| T3 | Section divider | `th.divider(heading, "(20 minutes)", strip=[...], active=i)` | Before each section; `active` dims the other strip items |
| T4 | Closing / Q&A divider | `th.divider("Q&A", tagline=, footnote=)` | No strip; tagline in accent |
| T5 | KPI tiles + chips | `sh.kpi_tile` × 3 + `sh.chip_row` | "Where we stand" |
| T6 | Three accent cards + KV band | `sh.card` × 3 + `sh.card(accent=None)` | Priorities, reasons, pillars |
| T7 | Process | `sh.process(stages, current, pal)` | Stages with a "we are here" marker |
| T8 | Funnel | `sh.funnel(levels, pal)` | Narrowing counts; last level is the point |
| T9 | Resonating + questions | `sh.card` + bullets, `sh.question_cards` | Feedback / FAQ |
| T10 | Question → evidence | `sh.evidence_rows(rows)` | Objection handling |
| T11 | Dyad + help strip | 2 × `sh.card(accent=)` + 4 chips | "What it means for you" |

## Content slide chrome

```python
s = th.content("Where We Stand", accent="After Q2", eyebrow="Company update",
               subtitle="One-sentence takeaway.")
```

- Eyebrow: 8 pt bold accent caps at y 0.26.
- Title: 24 pt bold white; optional trailing accent phrase.
- Subtitle: 11 pt muted at y 0.98 — the "so-what" line borrowed from the board deck.

## T5 — KPI tiles + chips

```python
w = (XW - 0.4) / 3
for i, (lab, val, delta) in enumerate(tiles):          # ≤ 3 tiles
    sh.kpi_tile(s, X0 + i * (w + 0.2), TOP, w, 1.5, lab, val, delta, pal)
sh.label(s, X0, 3.18, 4, "Since last quarter", pal)
sh.chip_row(s, X0, 3.44, XW, 1.5, [(headline, detail)] * 4, pal)
```

`delta` can be runs: `[("+88% ", {"color": pal.good}), ("year over year", {})]`.
Only the favourable part gets `pal.good`; a miss stays muted text unless the slide is about the miss.

## T6 — Three accent cards + KV band

```python
for i, (lab, head, body) in enumerate(cards):
    x = X0 + i * (w + 0.2)
    sh.card(s, x, TOP, w, 2.35, pal)
    sh.label(s, x + 0.26, TOP + 0.22, w - 0.4, lab, pal)
    sh.text(s, x + 0.26, TOP + 0.48, w - 0.4, 0.4, head, size=16, bold=True)
    sh.text(s, x + 0.26, TOP + 1.0, w - 0.46, 1.25, body, size=10, color=pal.muted)
sh.card(s, X0, 4.0, XW, 0.92, pal, accent=None)        # key/value band: 3 columns
```

Body copy ≤ 30 words per card. Unknown values: `[th.placeholder("[TBD]")]`.

## T7 — Process

```python
sh.process(s, [(name, detail)] * 5, current=1, pal=pal)   # y=1.5, step 1.81, w 1.95
```

Done stages are accent at 35% with a deep stroke, the current stage is solid accent
with dark type, and upcoming stages are card-colored with muted type. Five stages
fill the width; for four, pass `step=2.27, w=2.4`. A callout card at y 3.95 fits under it.

## T8 — Funnel

```python
sh.funnel(s, [(value, label, detail)] * 4, pal)   # widths 4.1 → 1.85, labels at x 5.0
```

Upper levels step alpha 10 → 18 → 32 %. The last level is solid with dark type,
so order levels so that the last one is the point of the slide. Counts should be
cumulative: each level is a subset of the one above it. Add a 7 pt "as of" footnote at y 4.98.

## T9 — Resonating + question cards

```python
sh.card(s, X0, TOP, 3.55, BOTTOM - TOP - 0.03, pal)
sh.label(s, X0 + 0.28, TOP + 0.22, 3.0, "What's resonating", pal)
sh.text(s, X0 + 0.28, TOP + 0.56, 3.05, 2.7, points, size=13, bold=True,
        bullet=pal.accent, space_after=26)             # 3–4 points
sh.question_cards(s, X0 + 3.75, TOP, XW - 3.75, [(q, context)] * 3, pal)
```

## T10 — Question → evidence

```python
sh.evidence_rows(s, X0, TOP, XW, [(question, proof_headline, detail)] * 3, pal)
```

Keep the question ≤ 3 words, e.g. "Beyond electrical?". The headline is the proof
point in accent color and must be something already shipped or signed.

## T11 — Dyad + help strip

```python
cw = (XW - 0.2) / 2
sh.card(s, X0, TOP, cw, 2.2, pal, accent="accent")          # what doesn't change
sh.card(s, X0 + cw + 0.2, TOP, cw, 2.2, pal, accent="muted") # what you may notice
sh.label(s, X0, 3.86, 4, "How you can help", pal)
# 4 × card(accent=None) at y 4.12, h 0.8, each with a 0.08" accent square + 11 pt bold text
```

## Speaker notes convention

```python
th.notes(s, """
SOURCE: <deck / file, slide, as-of date>
[CONFIRM] <figure or claim the presenter must verify>
[DISCLOSURE] <what was deliberately left off and whose call it is>
""")
```
