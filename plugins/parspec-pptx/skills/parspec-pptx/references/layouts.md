# Layouts — parspec-pptx v0.1

Eight paste-ready layout recipes, validated against the Engineering Operating Model Transition board deck (May 2026). Every layout assumes `brand_artifacts` mode (dark) and uses the brand loader.

All recipes take a `Presentation` and a loaded `Brand` and add a single fully-styled slide. Each one is ~30–80 lines of straight composition — no abstractions to fight. Copy the recipe whole, replace the strings, ship.

## Quick start

```python
import sys
from pathlib import Path
SKILL = Path("/Users/eric/Desktop/Parspec.b/Vault/005_The_Lab/5.3_Automation_&_Scripts/parspec-design/plugins/parspec-pptx/skills/parspec-pptx")
sys.path.insert(0, str(SKILL))
from assets import load, new_deck, blank, corner_brackets, footer, add_text, add_rect, add_line, divider_rule, quarter_circle_accent, SLIDE_W, SLIDE_H
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

b = load()
prs = new_deck()
# ... apply layouts ...
prs.save("/path/to/out.pptx")
```

## Layout index

| ID | Name | When to use | Density |
|---|---|---|---|
| L1 | Cover | First slide of every deck | Eyebrow + display title + subtitle + lower-third signature |
| L2 | Section opener with paper-warm thesis | High-emotion pivot moments; closing-the-loop on a context | 1 line context + display pivot quote + thesis panel |
| L3 | Three-column claims | Strategic thesis / pillars / arguments | 1 heading + 3 cards (number + heading + body) |
| L4 | Two-card dyad | Org changes, A/B compares, dual leadership | 1 heading + 2 leadership cards |
| L5 | Section divider with 4-chip motif | Transition into a multi-vector section | 1 eyebrow + 1 big section title + subtitle + 4 chips |
| L6 | Two-column vectors | Comparing two related vectors side-by-side | 1 heading + 2 column cards (metric or shift-rows inside) |
| L7 | Talent shapes + 3-claim list | Asymmetric two-column where left is visual, right is list | 1 heading + 2 cards (one visual, one ordered list) |
| L8 | Before/after table + 3-ask chips | Closing slide: change matrix + asks | Top: 7-row 3-col table  ·  Bottom: 3 chip cards |
| L9 | KPI metric grid (3×N) | Dashboard of headline metrics | 1 heading + up to 6 tiles (one big stat each, trajectory in sub) |
| L10 | Ranked horizontal bars | Per-entity productivity / rankings | 1 heading + up to 7 labeled bars |
| L11 | Input-placeholder dyad | "What we have vs what's needed" gap slides | 1 heading + 1 dark "from model" card + 1 paper-warm "input needed" panel |
| L12 | Owner-asks (N chips) | Closing delegation slide | 1 heading + 2–3 owner cards + centered caption |

> L9–L12 validated against the Lead Edge Sales Org Overview deck (June 2026). L9 rule learned: **one big stat per tile**, put the FY26→FY27 trajectory in the sub-line — two-part values in the headline wrap and collide. Footnote y must clear the footer (compute from row count).

## Density limits (per parspec-design v2.0.0)

Per slide, NEVER exceed:
- 1 heading + 4–6 bullets OR
- 1 heading + 2 paragraphs OR
- 6 cards max (2×3 or 3×2) OR
- 8–10 lines of code OR
- 1 quote ≤ 3 lines OR
- 1 image ≤ 60vh OR
- Up to 3 large stats

Overflow signals bad layout, not bad content. **Split, never cram.**

## Voice (from design-model.yaml)

**Do**: lead with metrics; ALL CAPS section heads; name customers (Sonepar, Graybar, Rexel, Wesco, Border States); MEP vocab (quoting, submittals, O&M, ERP); terse.

**Avoid**: consumer-SaaS hype ("delight", "magic", "effortless"); generic startup verbs ("unlock", "empower", "transform"); wellness adjectives; emoji; lorem ipsum.

## Invariants enforced visually

- **CTA monopoly**: Brand Orange `b.cta` is only used for primary action / accent type on dark / signature highlights.
- **Steel = doc register**: `b.info_on_dark` / `b.info_on_light` only on engineering-doc cues.
- **Paper-warm panel only**: `b.surface_paper` used inside `b.surface_dark` slides as inset panel — never as slide background.
- **Orange-type-on-light forbidden**: never use `b.cta` as text color on light surfaces; use `b.accent_type_on_light` instead.

---

## L1 — Cover

```python
def cover(prs, b, *, eyebrow, title, subtitle, body_subtitle,
          prepared_for, presented_by, date):
    s = blank(prs, brand=b)
    corner_brackets(s, brand=b)

    add_text(s, Inches(0.85), Inches(0.85), Inches(8), Inches(0.4),
             eyebrow, size=10, weight="semibold", color=b.cta,
             letter_spacing=4, upper=True, brand=b)
    divider_rule(s, Inches(0.85), Inches(1.4), Inches(0.7),
                 color=b.cta, weight=2.5)

    add_text(s, Inches(0.85), Inches(1.7), Inches(11.6), Inches(2.0),
             title, size=58, weight="black", color=b.text_dark_primary,
             letter_spacing=-1.5, line_spacing=1.0, brand=b)

    add_text(s, Inches(0.85), Inches(3.95), Inches(11.6), Inches(0.7),
             subtitle, size=22, weight="medium", color=b.cta,
             letter_spacing=-0.3, brand=b)

    add_text(s, Inches(0.85), Inches(4.7), Inches(11.6), Inches(0.5),
             body_subtitle, size=14, weight="regular",
             color=b.text_dark_secondary, brand=b)

    # signature block — three columns
    sig_y = Inches(6.05)
    for x, label, value in [
        (Inches(0.85), "PREPARED FOR", prepared_for),
        (Inches(4.5),  "PRESENTED BY", presented_by),
        (Inches(8.3),  "DATE",         date),
    ]:
        add_text(s, x, sig_y, Inches(4), Inches(0.25), label,
                 size=8, weight="semibold", color=b.text_dark_tertiary,
                 letter_spacing=3, upper=True, brand=b)
        add_text(s, x, sig_y + Inches(0.28), Inches(5), Inches(0.35),
                 value, size=14, weight="semibold",
                 color=b.text_dark_primary, brand=b)

    quarter_circle_accent(s, Inches(11.3), Inches(0.85),
                          radius=Inches(1.2), color=b.cta, weight=2.0)
```

## L2 — Section opener with paper-warm thesis

```python
def section_with_thesis(prs, b, *, eyebrow_num, eyebrow_label,
                        context_line, pivot_white, pivot_orange,
                        thesis_label, thesis_body, page, total, label):
    s = blank(prs, brand=b)
    corner_brackets(s, brand=b)

    add_text(s, Inches(0.85), Inches(0.85), Inches(8), Inches(0.4),
             f"{eyebrow_num}  /  {eyebrow_label}",
             size=10, weight="semibold", color=b.cta,
             letter_spacing=4, upper=True, brand=b)
    divider_rule(s, Inches(0.85), Inches(1.4), Inches(0.7),
                 color=b.cta, weight=2.5)

    add_text(s, Inches(0.85), Inches(1.65), Inches(11.6), Inches(0.5),
             context_line, size=14, weight="medium",
             color=b.text_dark_tertiary, brand=b)

    add_text(s, Inches(0.85), Inches(2.4), Inches(11.6), Inches(2.6),
             pivot_white, size=36, weight="bold",
             color=b.text_dark_primary,
             letter_spacing=-0.8, line_spacing=1.1, brand=b)

    add_text(s, Inches(0.85), Inches(4.15), Inches(11.6), Inches(1.4),
             pivot_orange, size=36, weight="bold", color=b.cta,
             letter_spacing=-0.8, line_spacing=1.1, brand=b)

    # paper-warm thesis panel — signature inset
    px, py, pw, ph = Inches(0.85), Inches(5.85), Inches(11.6), Inches(0.95)
    add_rect(s, px, py, pw, ph, fill=b.surface_paper)
    add_rect(s, px, py, Inches(0.10), ph, fill=b.cta)
    add_text(s, px + Inches(0.4), py + Inches(0.12),
             pw - Inches(0.6), Inches(0.3),
             thesis_label, size=9, weight="bold",
             color=b.surface_dark, letter_spacing=3.5, upper=True, brand=b)
    add_text(s, px + Inches(0.4), py + Inches(0.40),
             pw - Inches(0.6), Inches(0.55),
             thesis_body, size=14, weight="semibold",
             color=b.surface_dark, line_spacing=1.25, brand=b)

    footer(s, label, brand=b, page=page, total=total)
```

## L3 — Three-column claims

```python
def three_claims(prs, b, *, eyebrow_num, eyebrow_label, heading,
                 claims, page, total, label):
    """claims: list of 3 tuples (number_str, headline, body)."""
    s = blank(prs, brand=b)
    corner_brackets(s, brand=b)

    add_text(s, Inches(0.85), Inches(0.85), Inches(8), Inches(0.4),
             f"{eyebrow_num}  /  {eyebrow_label}",
             size=10, weight="semibold", color=b.cta,
             letter_spacing=4, upper=True, brand=b)
    divider_rule(s, Inches(0.85), Inches(1.4), Inches(0.7),
                 color=b.cta, weight=2.5)
    add_text(s, Inches(0.85), Inches(1.65), Inches(11.6), Inches(0.75),
             heading, size=32, weight="extrabold",
             color=b.text_dark_primary, letter_spacing=-0.8, brand=b)

    col_y, col_h, gap = Inches(3.05), Inches(3.6), Inches(0.35)
    col_w = (SLIDE_W - Inches(1.7) - 2 * gap) / 3

    for i, (num, head, body) in enumerate(claims):
        x = Inches(0.85) + i * (col_w + gap)
        add_rect(s, x, col_y, col_w, col_h, fill=b.surface_dark_panel,
                 line=b.border_dark, line_w=0.75)
        add_rect(s, x, col_y, col_w, Inches(0.08), fill=b.cta)
        add_text(s, x + Inches(0.4), col_y + Inches(0.3),
                 col_w - Inches(0.8), Inches(0.9),
                 num, size=48, weight="black", color=b.cta,
                 letter_spacing=-2, brand=b)
        add_text(s, x + Inches(0.4), col_y + Inches(1.25),
                 col_w - Inches(0.8), Inches(1.0),
                 head, size=14, weight="bold", color=b.text_dark_primary,
                 letter_spacing=0.5, line_spacing=1.15, brand=b)
        add_text(s, x + Inches(0.4), col_y + Inches(2.3),
                 col_w - Inches(0.8), col_h - Inches(2.5),
                 body, size=10.5, weight="regular",
                 color=b.text_dark_secondary, line_spacing=1.4, brand=b)

    footer(s, label, brand=b, page=page, total=total)
```

## L4 — Two-card dyad

```python
def two_card_dyad(prs, b, *, eyebrow_num, eyebrow_label, heading,
                  cards, footer_line, page, total):
    """cards: list of 2 dicts {role_label, name, title, owns, built_for, accent}.

    Use b.cta for the execution card accent, b.info_on_dark for the AI card.
    """
    s = blank(prs, brand=b)
    corner_brackets(s, brand=b)

    add_text(s, Inches(0.85), Inches(0.85), Inches(10), Inches(0.4),
             f"{eyebrow_num}  /  {eyebrow_label}",
             size=10, weight="semibold", color=b.cta,
             letter_spacing=4, upper=True, brand=b)
    divider_rule(s, Inches(0.85), Inches(1.4), Inches(0.7),
                 color=b.cta, weight=2.5)
    add_text(s, Inches(0.85), Inches(1.65), Inches(11.6), Inches(0.75),
             heading, size=32, weight="extrabold",
             color=b.text_dark_primary, letter_spacing=-0.8, brand=b)

    card_y, card_h, gap = Inches(2.7), Inches(4.0), Inches(0.4)
    card_w = (SLIDE_W - Inches(1.7) - gap) / 2

    for i, c in enumerate(cards):
        x = Inches(0.85) + i * (card_w + gap)
        add_rect(s, x, card_y, card_w, card_h,
                 fill=b.surface_dark_panel, line=b.border_dark, line_w=0.75)
        add_rect(s, x, card_y, Inches(0.12), card_h, fill=c["accent"])

        add_text(s, x + Inches(0.6), card_y + Inches(0.4),
                 card_w - Inches(1.0), Inches(0.3),
                 c["role_label"], size=10, weight="semibold",
                 color=c["accent"], letter_spacing=3.5, upper=True, brand=b)
        add_text(s, x + Inches(0.6), card_y + Inches(0.85),
                 card_w - Inches(1.0), Inches(1.0),
                 c["name"], size=54, weight="black",
                 color=b.text_dark_primary, letter_spacing=-2, brand=b)
        add_text(s, x + Inches(0.6), card_y + Inches(1.95),
                 card_w - Inches(1.0), Inches(0.45),
                 c["title"], size=14, weight="semibold",
                 color=b.text_dark_secondary, brand=b)
        add_line(s, x + Inches(0.6), card_y + Inches(2.5),
                 x + card_w - Inches(0.6), card_y + Inches(2.5),
                 color=b.border_dark, weight=0.75)
        add_text(s, x + Inches(0.6), card_y + Inches(2.65),
                 card_w - Inches(1.0), Inches(0.25),
                 "OWNS", size=8, weight="bold",
                 color=b.text_dark_tertiary, letter_spacing=3.5,
                 upper=True, brand=b)
        add_text(s, x + Inches(0.6), card_y + Inches(2.92),
                 card_w - Inches(1.0), Inches(0.95),
                 c["owns"], size=12, weight="medium",
                 color=b.text_dark_primary, line_spacing=1.35, brand=b)
        tag_y = card_y + card_h - Inches(0.45)
        add_line(s, x + Inches(0.6), tag_y - Inches(0.08),
                 x + card_w - Inches(0.6), tag_y - Inches(0.08),
                 color=b.border_dark, weight=0.5)
        add_text(s, x + Inches(0.6), tag_y,
                 card_w - Inches(1.0), Inches(0.3),
                 c["built_for"], size=10, weight="bold",
                 color=c["accent"], letter_spacing=2.5, upper=True, brand=b)

    add_text(s, Inches(0.85), Inches(6.95), Inches(11.6), Inches(0.4),
             footer_line, size=10, weight="semibold", color=b.cta,
             letter_spacing=3, upper=True, align=PP_ALIGN.CENTER, brand=b)
    add_text(s, SLIDE_W - Inches(1.8), SLIDE_H - Inches(0.55),
             Inches(1.2), Inches(0.3),
             f"{page:02d} / {total:02d}", size=8, weight="semibold",
             color=b.text_dark_tertiary, align=PP_ALIGN.RIGHT,
             letter_spacing=2.5, brand=b)
```

## L5 — Section divider with 4-chip motif

```python
def section_divider(prs, b, *, eyebrow_num, eyebrow_label, big_title,
                    subtitle, chips, page, total):
    """chips: list of 4 tuples (num_str, label)."""
    s = blank(prs, brand=b)
    corner_brackets(s, brand=b)

    add_text(s, Inches(0.85), Inches(0.85), Inches(11), Inches(0.4),
             f"{eyebrow_num}  /  {eyebrow_label}",
             size=10, weight="semibold", color=b.cta,
             letter_spacing=4, upper=True, brand=b)
    divider_rule(s, Inches(0.85), Inches(1.4), Inches(0.7),
                 color=b.cta, weight=2.5)

    add_text(s, Inches(0.4), Inches(2.45), Inches(12.5), Inches(1.6),
             big_title, size=88, weight="black",
             color=b.text_dark_primary, letter_spacing=-3,
             align=PP_ALIGN.CENTER, line_spacing=1.0, brand=b)

    add_text(s, Inches(0.85), Inches(4.15), Inches(11.6), Inches(0.6),
             subtitle, size=20, weight="medium", color=b.cta,
             align=PP_ALIGN.CENTER, letter_spacing=-0.3, brand=b)

    row_y, chip_h, gap = Inches(5.35), Inches(0.95), Inches(0.3)
    chip_w = (SLIDE_W - Inches(1.7) - 3 * gap) / 4
    for i, (num, name) in enumerate(chips):
        x = Inches(0.85) + i * (chip_w + gap)
        add_rect(s, x, row_y, chip_w, chip_h, fill=b.surface_dark_panel,
                 line=b.border_dark, line_w=0.75)
        add_rect(s, x, row_y, chip_w, Inches(0.06), fill=b.cta)
        add_text(s, x + Inches(0.3), row_y + Inches(0.18),
                 chip_w - Inches(0.6), Inches(0.3),
                 num, size=10, weight="bold", color=b.cta,
                 letter_spacing=3, upper=True, brand=b)
        add_text(s, x + Inches(0.3), row_y + Inches(0.48),
                 chip_w - Inches(0.6), Inches(0.4),
                 name, size=13, weight="bold",
                 color=b.text_dark_primary, letter_spacing=0,
                 upper=True, brand=b)

    add_text(s, SLIDE_W - Inches(1.8), SLIDE_H - Inches(0.55),
             Inches(1.2), Inches(0.3),
             f"{page:02d} / {total:02d}", size=8, weight="semibold",
             color=b.text_dark_tertiary, align=PP_ALIGN.RIGHT,
             letter_spacing=2.5, brand=b)
```

## L6 — Two-column vectors

```python
def two_column_vectors(prs, b, *, eyebrow_num, eyebrow_label, heading,
                       left, right, page, total, label):
    """left, right: dict {num, name, headline, accent, render_body_fn(slide, x, y, w, h, b)}.

    The body-render function lets the caller put metrics, shift-rows, or
    visuals into the column without forcing a one-size-fits-all schema.
    """
    s = blank(prs, brand=b)
    corner_brackets(s, brand=b)

    add_text(s, Inches(0.85), Inches(0.85), Inches(11), Inches(0.4),
             f"{eyebrow_num}  /  {eyebrow_label}",
             size=10, weight="semibold", color=b.cta,
             letter_spacing=4, upper=True, brand=b)
    divider_rule(s, Inches(0.85), Inches(1.4), Inches(0.7),
                 color=b.cta, weight=2.5)
    add_text(s, Inches(0.85), Inches(1.65), Inches(11.6), Inches(0.7),
             heading, size=32, weight="extrabold",
             color=b.text_dark_primary, letter_spacing=-0.8, brand=b)

    col_y, col_h, gap = Inches(2.85), Inches(3.95), Inches(0.35)
    col_w = (SLIDE_W - Inches(1.7) - gap) / 2

    for i, col in enumerate([left, right]):
        x = Inches(0.85) + i * (col_w + gap)
        add_rect(s, x, col_y, col_w, col_h, fill=b.surface_dark_panel,
                 line=b.border_dark, line_w=0.75)
        add_rect(s, x, col_y, col_w, Inches(0.08), fill=col["accent"])
        add_text(s, x + Inches(0.45), col_y + Inches(0.3),
                 col_w - Inches(0.9), Inches(0.3),
                 f"{col['num']}  ·  {col['name']}", size=10, weight="bold",
                 color=col["accent"], letter_spacing=3, upper=True, brand=b)
        add_text(s, x + Inches(0.45), col_y + Inches(0.65),
                 col_w - Inches(0.9), Inches(0.5),
                 col["headline"], size=18, weight="bold",
                 color=b.text_dark_primary, letter_spacing=-0.3,
                 line_spacing=1.15, brand=b)
        # body rendering delegated to caller
        col["render_body"](
            s, x + Inches(0.45), col_y + Inches(1.45),
            col_w - Inches(0.9), col_h - Inches(1.6), b,
        )

    footer(s, label, brand=b, page=page, total=total)
```

## L7 — Talent shapes + 3-claim list

```python
def shapes_and_claims(prs, b, *, eyebrow_num, eyebrow_label, heading,
                      left_card, right_claims, page, total, label):
    """left_card: {num, name, headline, before_shape_label, after_shape_label, bullets}.
       right_claims: {num, name, headline, items=[(label, body), ...]}."""
    from pptx.enum.shapes import MSO_SHAPE
    s = blank(prs, brand=b)
    corner_brackets(s, brand=b)

    add_text(s, Inches(0.85), Inches(0.85), Inches(11), Inches(0.4),
             f"{eyebrow_num}  /  {eyebrow_label}",
             size=10, weight="semibold", color=b.cta,
             letter_spacing=4, upper=True, brand=b)
    divider_rule(s, Inches(0.85), Inches(1.4), Inches(0.7),
                 color=b.cta, weight=2.5)
    add_text(s, Inches(0.85), Inches(1.65), Inches(11.6), Inches(0.7),
             heading, size=32, weight="extrabold",
             color=b.text_dark_primary, letter_spacing=-0.8, brand=b)

    col_y, col_h, gap = Inches(2.85), Inches(3.95), Inches(0.35)
    col_w = (SLIDE_W - Inches(1.7) - gap) / 2

    # LEFT — visual card (pyramid → diamond)
    x = Inches(0.85)
    add_rect(s, x, col_y, col_w, col_h, fill=b.surface_dark_panel,
             line=b.border_dark, line_w=0.75)
    add_rect(s, x, col_y, col_w, Inches(0.08), fill=b.cta)
    add_text(s, x + Inches(0.45), col_y + Inches(0.3),
             col_w - Inches(0.9), Inches(0.3),
             f"{left_card['num']}  ·  {left_card['name']}",
             size=10, weight="bold", color=b.cta,
             letter_spacing=3, upper=True, brand=b)
    add_text(s, x + Inches(0.45), col_y + Inches(0.65),
             col_w - Inches(0.9), Inches(0.5),
             left_card["headline"], size=18, weight="bold",
             color=b.text_dark_primary, letter_spacing=-0.3,
             line_spacing=1.15, brand=b)

    # before / after shapes
    sy = col_y + Inches(1.55)
    sw, sh = Inches(1.4), Inches(1.3)
    sx1 = x + Inches(0.45)
    sx2 = x + col_w - Inches(0.45) - sw

    tri = s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, sx1, sy, sw, sh)
    tri.fill.solid(); tri.fill.fore_color.rgb = b.border_dark
    tri.line.color.rgb = b.body_chrome_on_dark
    tri.line.width = Pt(0.75); tri.shadow.inherit = False
    add_text(s, sx1, sy + sh + Inches(0.1), sw, Inches(0.25),
             "BEFORE", size=8, weight="bold", color=b.text_dark_tertiary,
             letter_spacing=2.5, upper=True, align=PP_ALIGN.CENTER, brand=b)
    add_text(s, sx1, sy + sh + Inches(0.32), sw, Inches(0.25),
             left_card["before_shape_label"], size=10, weight="semibold",
             color=b.text_dark_secondary, align=PP_ALIGN.CENTER, brand=b)

    dia = s.shapes.add_shape(MSO_SHAPE.DIAMOND, sx2, sy, sw, sh)
    dia.fill.solid(); dia.fill.fore_color.rgb = b.cta_active
    dia.line.color.rgb = b.cta; dia.line.width = Pt(1.5)
    dia.shadow.inherit = False
    add_text(s, sx2, sy + sh + Inches(0.1), sw, Inches(0.25),
             "AFTER", size=8, weight="bold", color=b.cta,
             letter_spacing=2.5, upper=True, align=PP_ALIGN.CENTER, brand=b)
    add_text(s, sx2, sy + sh + Inches(0.32), sw, Inches(0.25),
             left_card["after_shape_label"], size=10, weight="semibold",
             color=b.text_dark_primary, align=PP_ALIGN.CENTER, brand=b)

    add_text(s, sx1 + sw, sy + sh / 2 - Inches(0.15),
             sx2 - (sx1 + sw), Inches(0.4),
             "→", size=24, weight="bold", color=b.cta,
             align=PP_ALIGN.CENTER, brand=b)

    by = col_y + Inches(3.35)
    for i, bullet in enumerate(left_card["bullets"]):
        add_text(s, x + Inches(0.45), by + i * Inches(0.35),
                 col_w - Inches(0.9), Inches(0.4),
                 bullet, size=11, weight="medium",
                 color=b.text_dark_secondary, line_spacing=1.4, brand=b)

    # RIGHT — numbered claim list
    x2 = Inches(0.85) + col_w + gap
    add_rect(s, x2, col_y, col_w, col_h, fill=b.surface_dark_panel,
             line=b.border_dark, line_w=0.75)
    add_rect(s, x2, col_y, col_w, Inches(0.08), fill=b.info_on_dark)
    add_text(s, x2 + Inches(0.45), col_y + Inches(0.3),
             col_w - Inches(0.9), Inches(0.3),
             f"{right_claims['num']}  ·  {right_claims['name']}",
             size=10, weight="bold", color=b.info_on_dark,
             letter_spacing=3, upper=True, brand=b)
    add_text(s, x2 + Inches(0.45), col_y + Inches(0.65),
             col_w - Inches(0.9), Inches(0.5),
             right_claims["headline"], size=18, weight="bold",
             color=b.text_dark_primary, letter_spacing=-0.3,
             line_spacing=1.15, brand=b)

    my = col_y + Inches(1.85)
    for i, (lbl, body) in enumerate(right_claims["items"]):
        ry = my + i * Inches(0.78)
        add_text(s, x2 + Inches(0.45), ry, Inches(0.5), Inches(0.4),
                 f"0{i+1}", size=14, weight="black", color=b.cta, brand=b)
        add_text(s, x2 + Inches(1.0), ry, col_w - Inches(1.4), Inches(0.25),
                 lbl, size=10, weight="bold", color=b.text_dark_primary,
                 letter_spacing=1.5, upper=True, brand=b)
        add_text(s, x2 + Inches(1.0), ry + Inches(0.27),
                 col_w - Inches(1.4), Inches(0.45),
                 body, size=11, weight="medium",
                 color=b.text_dark_secondary, line_spacing=1.35, brand=b)

    footer(s, label, brand=b, page=page, total=total)
```

## L8 — Before/after table + 3-ask chips

```python
def table_and_asks(prs, b, *, eyebrow_num, eyebrow_label, table_heading,
                   rows, ask_label, ask_heading, asks, page, total, label):
    """rows: list of 7 tuples (dim, before, after).  asks: list of 3 tuples (num, head, body)."""
    s = blank(prs, brand=b)
    corner_brackets(s, brand=b)

    add_text(s, Inches(0.85), Inches(0.85), Inches(11), Inches(0.4),
             f"{eyebrow_num}  /  {eyebrow_label}",
             size=10, weight="semibold", color=b.cta,
             letter_spacing=4, upper=True, brand=b)
    divider_rule(s, Inches(0.85), Inches(1.4), Inches(0.7),
                 color=b.cta, weight=2.5)

    # ── table ──
    table_y, table_h, table_w, table_x = Inches(1.7), Inches(2.95), Inches(11.6), Inches(0.85)
    add_text(s, table_x, table_y, table_w, Inches(0.4),
             table_heading, size=20, weight="extrabold",
             color=b.text_dark_primary, letter_spacing=-0.4, brand=b)

    col_lbl_w = Inches(2.4)
    col_data_w = (table_w - col_lbl_w) / 2
    head_y, head_h = table_y + Inches(0.55), Inches(0.42)

    add_rect(s, table_x, head_y, col_lbl_w, head_h, fill=b.surface_dark_alt)
    add_rect(s, table_x + col_lbl_w, head_y, col_data_w, head_h,
             fill=b.surface_dark_alt)
    add_rect(s, table_x + col_lbl_w + col_data_w, head_y, col_data_w, head_h,
             fill=b.surface_dark_panel)
    add_rect(s, table_x + col_lbl_w + col_data_w, head_y, col_data_w,
             Inches(0.04), fill=b.cta)
    for x, txt, color in [
        (table_x + Inches(0.25), "DIMENSION", b.text_dark_tertiary),
        (table_x + col_lbl_w + Inches(0.25), "BEFORE", b.text_dark_tertiary),
        (table_x + col_lbl_w + col_data_w + Inches(0.25), "AFTER", b.cta),
    ]:
        add_text(s, x, head_y + Inches(0.10),
                 col_data_w - Inches(0.4), Inches(0.3),
                 txt, size=9, weight="bold", color=color,
                 letter_spacing=3, upper=True, brand=b)

    row_h = (table_h - Inches(0.6) - head_h) / len(rows)
    for i, (lbl, before, after) in enumerate(rows):
        ry = head_y + head_h + i * row_h
        fill_band = b.surface_dark_panel if i % 2 == 0 else b.surface_dark
        after_fill = b.surface_dark_alt if i % 2 == 0 else b.surface_dark_panel
        add_rect(s, table_x, ry, col_lbl_w, row_h, fill=fill_band)
        add_rect(s, table_x + col_lbl_w, ry, col_data_w, row_h, fill=fill_band)
        add_rect(s, table_x + col_lbl_w + col_data_w, ry, col_data_w, row_h,
                 fill=after_fill)
        add_text(s, table_x + Inches(0.25), ry + Inches(0.06),
                 col_lbl_w - Inches(0.4), row_h - Inches(0.05),
                 lbl, size=11, weight="semibold",
                 color=b.text_dark_primary, anchor=MSO_ANCHOR.MIDDLE, brand=b)
        add_text(s, table_x + col_lbl_w + Inches(0.25), ry + Inches(0.06),
                 col_data_w - Inches(0.4), row_h - Inches(0.05),
                 before, size=10.5, weight="regular",
                 color=b.text_dark_secondary, anchor=MSO_ANCHOR.MIDDLE, brand=b)
        add_text(s, table_x + col_lbl_w + col_data_w + Inches(0.25),
                 ry + Inches(0.06),
                 col_data_w - Inches(0.4), row_h - Inches(0.05),
                 after, size=10.5, weight="semibold", color=b.cta,
                 anchor=MSO_ANCHOR.MIDDLE, brand=b)

    add_rect(s, table_x, head_y, table_w, head_h + len(rows) * row_h,
             fill=b.surface_dark, line=b.border_dark, line_w=0.5).fill.background()  # outline-only via background fill
    # (the line above creates an outlined rect; if your python-pptx complains,
    # split into add_shape + .fill.background())

    # ── asks ──
    ask_y = Inches(4.85)
    add_text(s, Inches(0.85), ask_y, Inches(8), Inches(0.4),
             ask_label, size=10, weight="bold", color=b.cta,
             letter_spacing=3.5, upper=True, brand=b)
    add_text(s, Inches(0.85), ask_y + Inches(0.3), Inches(8), Inches(0.45),
             ask_heading, size=18, weight="extrabold",
             color=b.text_dark_primary, letter_spacing=-0.3, brand=b)

    chip_y, chip_h, gap = ask_y + Inches(0.95), Inches(0.95), Inches(0.3)
    chip_w = (SLIDE_W - Inches(1.7) - 2 * gap) / 3
    for i, (num, head, body) in enumerate(asks):
        cx = Inches(0.85) + i * (chip_w + gap)
        add_rect(s, cx, chip_y, chip_w, chip_h, fill=b.surface_dark_panel,
                 line=b.border_dark, line_w=0.75)
        add_rect(s, cx, chip_y, Inches(0.08), chip_h, fill=b.cta)
        add_text(s, cx + Inches(0.3), chip_y + Inches(0.1),
                 Inches(0.6), Inches(0.4),
                 num, size=18, weight="black", color=b.cta,
                 letter_spacing=-0.5, brand=b)
        add_text(s, cx + Inches(0.85), chip_y + Inches(0.13),
                 chip_w - Inches(1.0), Inches(0.4),
                 head, size=11.5, weight="bold",
                 color=b.text_dark_primary, line_spacing=1.15, brand=b)
        add_text(s, cx + Inches(0.85), chip_y + Inches(0.51),
                 chip_w - Inches(1.0), Inches(0.42),
                 body, size=10, weight="medium",
                 color=b.text_dark_secondary, line_spacing=1.3, brand=b)

    footer(s, label, brand=b, page=page, total=total)
```

---

## L9 — KPI metric grid (3×N)

```python
def metric_grid(prs, b, *, eyebrow_num, eyebrow_label, heading, tiles, page, total, label, foot=None):
    """tiles: list of up to 6 tuples (value, name, sub). ONE big stat per tile —
    put any FY26→FY27 trajectory in `sub`, never a two-part value in `value`."""
    s = blank(prs, brand=b); corner_brackets(s, brand=b)
    add_text(s, Inches(0.85), Inches(0.85), Inches(11), Inches(0.4),
             f"{eyebrow_num}  /  {eyebrow_label}", size=10, weight="semibold",
             color=b.cta, letter_spacing=4, upper=True, brand=b)
    divider_rule(s, Inches(0.85), Inches(1.4), Inches(0.7), color=b.cta, weight=2.5)
    add_text(s, Inches(0.85), Inches(1.65), Inches(11.6), Inches(0.75),
             heading, size=32, weight="extrabold", color=b.text_dark_primary,
             letter_spacing=-0.8, brand=b)

    gap, cols = Inches(0.35), 3
    card_w = (SLIDE_W - Inches(1.7) - (cols - 1) * gap) / cols
    card_h, y0, rgap = Inches(1.7), Inches(2.85), Inches(0.28)
    nrows = (len(tiles) + cols - 1) // cols
    for i, (value, name, sub) in enumerate(tiles):
        r, c = divmod(i, cols)
        x = Inches(0.85) + c * (card_w + gap)
        y = y0 + r * (card_h + rgap)
        add_rect(s, x, y, card_w, card_h, fill=b.surface_dark_panel,
                 line=b.border_dark, line_w=0.75)
        add_rect(s, x, y, card_w, Inches(0.08), fill=b.cta)
        add_text(s, x + Inches(0.35), y + Inches(0.28), card_w - Inches(0.7), Inches(0.3),
                 name, size=10, weight="semibold", color=b.text_dark_tertiary,
                 letter_spacing=2, upper=True, brand=b)
        add_text(s, x + Inches(0.35), y + Inches(0.64), card_w - Inches(0.7), Inches(0.6),
                 value, size=30, weight="black", color=b.text_dark_primary,
                 letter_spacing=-1, brand=b)
        add_text(s, x + Inches(0.35), y + Inches(1.26), card_w - Inches(0.7), Inches(0.35),
                 sub, size=10, weight="medium", color=b.cta, line_spacing=1.15, brand=b)
    if foot:
        foot_y = y0 + nrows * card_h + (nrows - 1) * rgap + Inches(0.15)
        add_text(s, Inches(0.85), foot_y, Inches(11.6), Inches(0.3), foot,
                 size=9, weight="regular", color=b.text_dark_tertiary, brand=b)
    footer(s, label, brand=b, page=page, total=total)
```

## L10 — Ranked horizontal bars

```python
def ranked_bars(prs, b, *, eyebrow_num, eyebrow_label, heading, rows, maxv,
                foot, page, total, label):
    """rows: list of up to 7 tuples (name, value, display_str). maxv scales the track."""
    s = blank(prs, brand=b); corner_brackets(s, brand=b)
    add_text(s, Inches(0.85), Inches(0.85), Inches(11), Inches(0.4),
             f"{eyebrow_num}  /  {eyebrow_label}", size=10, weight="semibold",
             color=b.cta, letter_spacing=4, upper=True, brand=b)
    divider_rule(s, Inches(0.85), Inches(1.4), Inches(0.7), color=b.cta, weight=2.5)
    add_text(s, Inches(0.85), Inches(1.65), Inches(11.6), Inches(0.75),
             heading, size=32, weight="extrabold", color=b.text_dark_primary,
             letter_spacing=-0.8, brand=b)

    y0, rh = Inches(2.95), Inches(0.56)
    track_x, track_w = Inches(3.1), Inches(8.0)
    for i, (name, value, disp) in enumerate(rows):
        y = y0 + i * rh
        add_text(s, Inches(0.85), y, Inches(2.1), Inches(0.4), name, size=12,
                 weight="semibold", color=b.text_dark_primary,
                 anchor=MSO_ANCHOR.MIDDLE, brand=b)
        add_rect(s, track_x, y + Inches(0.08), track_w, Inches(0.3), fill=b.surface_dark_alt)
        w = track_w * (value / maxv)
        add_rect(s, track_x, y + Inches(0.08), w, Inches(0.3), fill=b.cta)
        add_text(s, track_x + w + Inches(0.1), y, Inches(1.3), Inches(0.4), disp,
                 size=11, weight="bold", color=b.text_dark_primary,
                 anchor=MSO_ANCHOR.MIDDLE, brand=b)
    # foot y is computed to clear the bars and the footer
    foot_y = y0 + len(rows) * rh + Inches(0.25)
    add_text(s, Inches(0.85), foot_y, Inches(11.6), Inches(0.4), foot, size=10,
             weight="medium", color=b.cta, brand=b)
    footer(s, label, brand=b, page=page, total=total)
```

## L11 — Input-placeholder dyad

```python
def input_dyad(prs, b, *, eyebrow_num, eyebrow_label, heading,
               have, owner, need, page, total, label):
    """Left = dark 'FROM MODEL' card (have: list of strings).
       Right = paper-warm 'INPUT NEEDED · owner' panel (need: list of strings)."""
    s = blank(prs, brand=b); corner_brackets(s, brand=b)
    add_text(s, Inches(0.85), Inches(0.85), Inches(11), Inches(0.4),
             f"{eyebrow_num}  /  {eyebrow_label}", size=10, weight="semibold",
             color=b.cta, letter_spacing=4, upper=True, brand=b)
    divider_rule(s, Inches(0.85), Inches(1.4), Inches(0.7), color=b.cta, weight=2.5)
    add_text(s, Inches(0.85), Inches(1.65), Inches(11.6), Inches(0.75),
             heading, size=32, weight="extrabold", color=b.text_dark_primary,
             letter_spacing=-0.8, brand=b)

    col_y, col_h, gap = Inches(2.85), Inches(3.6), Inches(0.4)
    col_w = (SLIDE_W - Inches(1.7) - gap) / 2

    x = Inches(0.85)
    add_rect(s, x, col_y, col_w, col_h, fill=b.surface_dark_panel, line=b.border_dark, line_w=0.75)
    add_rect(s, x, col_y, col_w, Inches(0.08), fill=b.info_on_dark)
    add_text(s, x + Inches(0.45), col_y + Inches(0.32), col_w - Inches(0.9), Inches(0.3),
             "FROM MODEL", size=10, weight="bold", color=b.info_on_dark,
             letter_spacing=3, upper=True, brand=b)
    for i, line in enumerate(have):
        add_text(s, x + Inches(0.45), col_y + Inches(0.85) + i * Inches(0.5),
                 col_w - Inches(0.9), Inches(0.5), "•  " + line, size=12,
                 weight="medium", color=b.text_dark_secondary, line_spacing=1.25, brand=b)

    x2 = Inches(0.85) + col_w + gap
    add_rect(s, x2, col_y, col_w, col_h, fill=b.surface_paper)
    add_rect(s, x2, col_y, Inches(0.10), col_h, fill=b.cta)          # paper-warm inset, orange spine
    add_text(s, x2 + Inches(0.45), col_y + Inches(0.3), col_w - Inches(0.9), Inches(0.3),
             f"INPUT NEEDED  ·  {owner}", size=10, weight="bold",
             color=b.surface_dark, letter_spacing=2.5, upper=True, brand=b)
    for i, line in enumerate(need):
        add_text(s, x2 + Inches(0.45), col_y + Inches(0.85) + i * Inches(0.5),
                 col_w - Inches(0.9), Inches(0.5), "▢  " + line, size=12,
                 weight="semibold", color=b.surface_dark, line_spacing=1.25, brand=b)
    footer(s, label, brand=b, page=page, total=total)
```

## L12 — Owner-asks (N chips)

```python
def owner_asks(prs, b, *, eyebrow_num, eyebrow_label, heading, chips, caption,
               page, total, label):
    """chips: list of 2–3 tuples (who, role, items[list of str]). caption: centered CTA line."""
    s = blank(prs, brand=b); corner_brackets(s, brand=b)
    add_text(s, Inches(0.85), Inches(0.85), Inches(11), Inches(0.4),
             f"{eyebrow_num}  /  {eyebrow_label}", size=10, weight="semibold",
             color=b.cta, letter_spacing=4, upper=True, brand=b)
    divider_rule(s, Inches(0.85), Inches(1.4), Inches(0.7), color=b.cta, weight=2.5)
    add_text(s, Inches(0.85), Inches(1.65), Inches(11.6), Inches(0.75),
             heading, size=32, weight="extrabold", color=b.text_dark_primary,
             letter_spacing=-0.8, brand=b)

    col_y, col_h, gap = Inches(3.0), Inches(3.4), Inches(0.35)
    n = len(chips)
    col_w = (SLIDE_W - Inches(1.7) - (n - 1) * gap) / n
    for i, (who, role, items) in enumerate(chips):
        x = Inches(0.85) + i * (col_w + gap)
        add_rect(s, x, col_y, col_w, col_h, fill=b.surface_dark_panel, line=b.border_dark, line_w=0.75)
        add_rect(s, x, col_y, col_w, Inches(0.08), fill=b.cta)
        add_text(s, x + Inches(0.4), col_y + Inches(0.32), col_w - Inches(0.8), Inches(0.4),
                 who, size=20, weight="black", color=b.text_dark_primary, letter_spacing=-0.5, brand=b)
        add_text(s, x + Inches(0.4), col_y + Inches(0.78), col_w - Inches(0.8), Inches(0.3),
                 role, size=10, weight="semibold", color=b.cta, letter_spacing=2, upper=True, brand=b)
        for j, it in enumerate(items):
            add_text(s, x + Inches(0.4), col_y + Inches(1.3) + j * Inches(0.5),
                     col_w - Inches(0.8), Inches(0.5), "▢  " + it, size=11,
                     weight="medium", color=b.text_dark_secondary, line_spacing=1.2, brand=b)
    add_text(s, Inches(0.85), Inches(6.7), Inches(11.6), Inches(0.4), caption,
             size=10, weight="bold", color=b.cta, letter_spacing=2, upper=True,
             align=PP_ALIGN.CENTER, brand=b)
    footer(s, label, brand=b, page=page, total=total)
```

---

## Patterns the layouts share

All eight layouts use the same header pattern:
- Eyebrow at `Inches(0.85, 0.85)`, size 10, brand-orange, letter-spaced 4, ALL CAPS
- Divider rule at `Inches(0.85, 1.4)`, 0.7" wide, 2.5pt
- Heading at `Inches(0.85, 1.65)`, size 32, extrabold, white (or size 58 black on cover)

Margins are uniform: `Inches(0.85)` left + right (≈ 11.6" usable width). This matches what worked tonight.

Cards consistently use:
- Top 0.08" accent strip in role color (orange / steel / amber)
- Inner padding 0.4–0.45"
- 0.75pt slate-700 border
- charcoal panel fill

Corner brackets in `b.cta` on every slide. Page indicator bottom-right via `footer()`.
