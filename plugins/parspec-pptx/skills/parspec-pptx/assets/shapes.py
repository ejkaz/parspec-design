"""
parspec-pptx — diagram + composition primitives.

Canvas-agnostic: every coordinate is a float in inches, so the same
primitives work on the 13.333" brand_artifacts canvas and the 10" town hall
canvas. Colors come from a `Palette` resolved off design-model.yaml roles.

Primitives
    text()             multi-paragraph, multi-run text box (or fills a placeholder)
    shape()            autoshape with optional fill/line alpha, rotation, adjustments
    card()             dark card with optional left accent bar
    kpi_tile()         label / big value / delta line
    chip_row()         N equal cards: bold headline + muted detail
    funnel()           stacked trapezoids (alpha-stepped or umber ramp), labels right
    process()          pentagon + chevrons with a "we are here" marker
    question_cards()   stacked quote cards
    evidence_rows()    question card -> arrow -> answer card
    section_strip()    orange rule + numbered labels (divider slides)
    arcs()             triple-arc signature motif, bleeding off a corner

    master-format composites (Sept-2026 master deck):
    tile_row()         overview tiles: accent top rule, caps label, big value, body
    numbered_cards()   top accent bar, big numeral, title, tag, rule, body
    panel_rows()       translucent rounded rows: caps label | heading + body
    problem_solution() numbered problem boxes -> connector -> umber stat panels
    bracket_box()      CAD corner brackets around a region
    crosshair()        CAD registration "+" mark
"""

from __future__ import annotations

from dataclasses import dataclass

from lxml import etree
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

from .brand import Brand, load as load_brand

FONT = "Montserrat"
ALIGN = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}
ANCHOR = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}


@dataclass(frozen=True)
class Palette:
    """Dark-surface composition palette. Every value is a design-model role.

    Values observed in the Q2-26 town hall deck are noted for traceability;
    each is within a shade of the role it resolves to.
    """
    bg: RGBColor           # surface_dark          (town hall #0F0F0F)
    card: RGBColor         # surface_dark_alt      (town hall #1A1A1D)
    card_line: RGBColor    # surface_dark_panel    (town hall #2A2A2E)
    accent: RGBColor       # cta                   (town hall #FFA72B)
    accent_deep: RGBColor  # accent_type_on_light  (town hall #8C5E22 funnel stroke)
    text: RGBColor         # text_dark_primary
    muted: RGBColor        # text_dark_tertiary    (town hall #9CA3AF / #9E9E9E)
    good: RGBColor         # status_success_on_dark (town hall #4ADE80)
    panel: RGBColor        # surface_dark_panel    (master #2E2E2E rows at 35%)
    subtle: RGBColor       # text_dark_secondary   (master #C9C9C9 captions)
    layer: RGBColor        # layer_fill_on_dark          (master theme accent3 #5A3F1C)
    layer_deep: RGBColor   # layer_fill_on_dark_deep     (accent4 #392917)
    layer_deepest: RGBColor  # layer_fill_on_dark_deepest (accent5 #261E15)

    @classmethod
    def from_brand(cls, b: Brand | None = None) -> "Palette":
        b = b or load_brand()
        return cls(
            bg=b.surface_dark, card=b.surface_dark_alt, card_line=b.surface_dark_panel,
            accent=b.cta, accent_deep=b.accent_type_on_light, text=b.text_dark_primary,
            muted=b.text_dark_tertiary, good=b.status_success_on_dark,
            panel=b.surface_dark_panel, subtle=b.text_dark_secondary,
            layer=b.layer_fill_on_dark, layer_deep=b.layer_fill_on_dark_deep,
            layer_deepest=b.layer_fill_on_dark_deepest,
        )


# ── base primitives ──────────────────────────────────────────────────
def _alpha(parent, pct: float):
    clr = parent.find(qn("a:srgbClr"))
    etree.SubElement(clr, qn("a:alpha")).set("val", str(int(pct * 1000)))


def shape(slide, kind, x, y, w, h, *, fill=None, line=None, lw=0.75,
          fill_alpha=None, line_alpha=None, rot=None, adj=None):
    """Autoshape. fill/line None = no fill/line. Alphas are 0–100 (% opaque)."""
    sh = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.shadow.inherit = False
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
        if fill_alpha is not None:
            _alpha(sh._element.spPr.find(qn("a:solidFill")), fill_alpha)
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(lw)
        if line_alpha is not None:
            _alpha(sh._element.spPr.find(qn("a:ln")).find(qn("a:solidFill")), line_alpha)
    if rot is not None:
        sh.rotation = rot
    for i, v in enumerate(adj or ()):
        sh.adjustments[i] = v
    return sh


def _bullet(p, color: RGBColor, indent=0.16):
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(Inches(indent)))
    pPr.set("indent", str(-Inches(indent)))
    clr = etree.SubElement(pPr, qn("a:buClr"))
    etree.SubElement(clr, qn("a:srgbClr")).set("val", str(color))
    etree.SubElement(pPr, qn("a:buSzPct")).set("val", "100000")
    etree.SubElement(pPr, qn("a:buFont")).set("typeface", "Arial")
    etree.SubElement(pPr, qn("a:buChar")).set("char", "•")


def text(slide, x, y, w, h, paras, *, size=11, color=None, bold=False,
         italic=False, align="l", anchor="t", space_after=0, bullet=None,
         line_spacing=None, font=FONT, target=None):
    """Text box with zero insets.

    paras: "one\\ntwo" | ["para", [(run_text, {size,color,bold,italic,font}), ...]]
    bullet: RGBColor for an orange/grey bullet on every paragraph.
    target: an existing shape/placeholder to fill instead of a new text box.
    """
    color = color or RGBColor(0xFF, 0xFF, 0xFF)
    tb = target or slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = ANCHOR[anchor]
    if isinstance(paras, str):
        paras = paras.split("\n")
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = ALIGN[align]
        if bullet is not None:
            _bullet(p, bullet)
        if space_after and i < len(paras) - 1:
            p.space_after = Pt(space_after)
        if line_spacing:
            p.line_spacing = line_spacing
        for t, o in ([(para, {})] if isinstance(para, str) else para):
            r = p.add_run()
            r.text = t
            f = r.font
            f.name = o.get("font", font)
            f.size = Pt(o.get("size", size))
            f.bold = o.get("bold", bold)
            f.italic = o.get("italic", italic)
            f.color.rgb = o.get("color", color)
    return tb


def runs(x) -> list:
    """Normalize str | (text, style) | [(text, style), ...] to a run list."""
    if isinstance(x, str):
        return [(x, {})]
    if isinstance(x, tuple):
        return [x]
    return list(x)


def placeholder(t: str, pal: Palette):
    """Run style for content the presenter still has to supply: '[Round size]'."""
    return (t, {"color": pal.muted, "italic": True})


def card(slide, x, y, w, h, pal: Palette, *, accent="accent"):
    """Dark card. accent: 'accent' (orange bar), 'muted' (grey bar) or None."""
    shape(slide, MSO_SHAPE.RECTANGLE, x, y, w, h, fill=pal.card, line=pal.card_line)
    if accent:
        shape(slide, MSO_SHAPE.RECTANGLE, x, y, 0.06, h, fill=getattr(pal, accent))


def label(slide, x, y, w, s, pal: Palette, *, color=None, size=8):
    """Small caps section label ('WHAT DOESN'T CHANGE')."""
    return text(slide, x, y, w, 0.2, s.upper(), size=size, bold=True, color=color or pal.accent)


# ── composites ───────────────────────────────────────────────────────
def kpi_tile(slide, x, y, w, h, lab, value, delta, pal: Palette, *, value_size=30):
    """delta: str, or runs [(text, {...})]; use {'color': pal.good} for the good part."""
    card(slide, x, y, w, h, pal)
    label(slide, x + 0.26, y + 0.2, w - 0.4, lab, pal, color=pal.muted)
    text(slide, x + 0.26, y + 0.46, w - 0.4, 0.55, value, size=value_size, bold=True,
         color=pal.accent)
    text(slide, x + 0.26, y + h - 0.4, w - 0.4, 0.22, [runs(delta)], size=9, color=pal.muted)


def chip_row(slide, x, y, w, h, items, pal: Palette, *, gap=0.15, head_size=12.5):
    """items: [(headline, detail)] as equal-width accent-less cards."""
    cw = (w - gap * (len(items) - 1)) / len(items)
    for i, (head, detail) in enumerate(items):
        cx = x + i * (cw + gap)
        card(slide, cx, y, cw, h, pal, accent=None)
        text(slide, cx + 0.18, y + 0.18, cw - 0.34, 0.5, head, size=head_size, bold=True,
             color=pal.text)
        text(slide, cx + 0.18, y + 0.76, cw - 0.34, h - 0.9, detail, size=9, color=pal.muted)


def funnel(slide, levels, pal: Palette, *, cx=2.55, top=1.42, h=0.8, gap=0.08,
           widths=(4.1, 3.35, 2.6, 1.85), label_x=5.0, label_w=4.5, ramp="alpha",
           proportional=False, min_width=1.2):
    """Narrowing funnel. levels: [(value, label, detail)], widest first.

    ramp="alpha": accent at stepped alpha (town hall 10/18/32%).
    ramp="umber": solid umber deepest -> layer (master deck theme).
    Either way the last level is solid accent with dark type — the stage the
    slide is about.
    proportional=True scales each top width to its numeric value (widest =
    widths[0]), floored at min_width so the label still fits — honest encoding
    when the counts are the message.
    """
    if proportional:
        vals = [float(str(v).replace(",", "").lstrip("$").rstrip("%+")) for v, _, _ in levels]
        widths = [max(min_width, widths[0] * v / max(vals)) for v in vals]
    n = len(levels) - 1
    if ramp == "umber":
        fills = [pal.layer_deepest, pal.layer_deep, pal.layer][-n:] if n <= 3 else \
            [pal.layer_deepest] * (n - 3) + [pal.layer_deepest, pal.layer_deep, pal.layer]
        styles = [dict(fill=f) for f in fills]
    else:
        styles = [dict(fill=pal.accent, fill_alpha=a) for a in [10, 18, 32, 45, 55][:n]]
    styles.append(dict(fill=pal.accent))
    for i, (value, lab, detail) in enumerate(levels):
        w, y, last = widths[i], top + i * (h + gap), i == len(levels) - 1
        shape(slide, MSO_SHAPE.TRAPEZOID, cx - w / 2, y, w, h, line=pal.accent_deep, lw=1.0,
              rot=180, adj=[0.2], **styles[i])
        text(slide, cx - 0.6, y, 1.2, h, value, size=24, bold=True,
             color=pal.bg if last else pal.text, align="c", anchor="m")
        text(slide, label_x, y + 0.1, label_w, 0.3, lab, size=13, bold=True,
             color=pal.accent if last else pal.text)
        text(slide, label_x, y + 0.42, label_w, 0.3, detail, size=9, color=pal.muted)


def process(slide, stages, current, pal: Palette, *, x=0.44, y=1.5, step=1.81,
            w=1.95, h=0.72, marker="WE ARE HERE"):
    """Pentagon + chevrons. stages: [(name, detail)]. current: index or None.

    Done stages: accent at 35% with a deep stroke. Current: solid accent,
    dark type. Upcoming: card fill, muted type. Numbers are shown because
    a process is a real sequence.
    """
    for i, (name, detail) in enumerate(stages):
        sx = x + i * step
        kind = MSO_SHAPE.PENTAGON if i == 0 else MSO_SHAPE.CHEVRON
        if current is not None and i < current:
            style = dict(fill=pal.accent, fill_alpha=35, line=pal.accent_deep)
            tc = pal.text
        elif i == current:
            style, tc = dict(fill=pal.accent), pal.bg
        else:
            style, tc = dict(fill=pal.card, line=pal.card_line), pal.muted
        shape(slide, kind, sx, y, w, h, **style)
        pad = 0.18 if i == 0 else 0.42
        text(slide, sx + pad, y, w - pad - 0.3, h,
             [[(f"{i + 1:02d}  ", {"size": 9}), (name, {})]],
             size=12, bold=True, color=tc, anchor="m")
        done_or_now = current is not None and i <= current
        text(slide, sx + 0.12, y + h + 0.18, w - 0.35, 0.7, detail, size=9,
             color=pal.text if done_or_now else pal.muted, line_spacing=1.1)
    if current is not None and marker:
        mx = x + current * step + w / 2 - 0.1
        shape(slide, MSO_SHAPE.ISOSCELES_TRIANGLE, mx - 0.09, y + h + 0.98, 0.18, 0.14,
              fill=pal.accent)
        text(slide, mx - 0.8, y + h + 1.16, 1.6, 0.2, marker, size=8, bold=True,
             color=pal.accent, align="c")


def question_cards(slide, x, y, w, items, pal: Palette, *, h=1.1, gap=0.1):
    """items: [(question, context)] stacked, grey bar + accent quote mark."""
    for i, (q, ctx) in enumerate(items):
        cy = y + i * (h + gap)
        card(slide, x, cy, w, h, pal, accent="muted")
        text(slide, x + 0.24, cy + 0.08, 0.5, 0.5, "“", size=34, bold=True, color=pal.accent)
        text(slide, x + 0.72, cy + 0.2, w - 0.95, 0.35, q, size=13, bold=True, color=pal.text)
        text(slide, x + 0.72, cy + 0.6, w - 0.95, 0.35, ctx, size=9, color=pal.muted)


def evidence_rows(slide, x, y, w, rows, pal: Palette, *, q_w=2.45, h=1.05, gap=0.14):
    """rows: [(question, answer_headline, answer_detail)] as Q card -> arrow -> A card."""
    a_w = w - q_w - 0.55
    for i, (q, head, detail) in enumerate(rows):
        cy = y + i * (h + gap)
        card(slide, x, cy, q_w, h, pal, accent="muted")
        text(slide, x + 0.24, cy, q_w - 0.4, h, q, size=13, bold=True, color=pal.text,
             anchor="m")
        shape(slide, MSO_SHAPE.RIGHT_ARROW, x + q_w + 0.13, cy + h / 2 - 0.11, 0.3, 0.22,
              fill=pal.accent)
        ax = x + q_w + 0.55
        card(slide, ax, cy, a_w, h, pal)
        text(slide, ax + 0.26, cy + 0.2, a_w - 0.45, 0.3, head, size=12.5, bold=True,
             color=pal.accent)
        text(slide, ax + 0.26, cy + 0.54, a_w - 0.45, 0.45, detail, size=9.5, color=pal.text,
             line_spacing=1.1)


def section_strip(slide, items, pal: Palette, *, active=None, x=0.18, y=4.43, w=9.76):
    """Numbered agenda strip under an accent rule. active dims every other item."""
    shape(slide, MSO_SHAPE.RECTANGLE, x, y, w, 0.02, fill=pal.accent)
    colw = w / len(items)
    for i, lab in enumerate(items):
        cx = x + i * colw
        dim = active is not None and i != active
        text(slide, cx, y + 0.13, colw - 0.1, 0.2, f"{i + 1:02d}", size=9, bold=True,
             color=pal.muted if dim else pal.accent)
        text(slide, cx, y + 0.35, colw - 0.1, 0.3, lab, size=10.5,
             color=pal.muted if dim else pal.text)


def arcs(slide, pal: Palette, *, x=7.795, y=-1.848, d=4.044, corner="tr"):
    """Triple-arc motif (outer stroke, faint inner stroke, 42% disc) bleeding off a corner.

    corner="tr": town hall dividers (defaults: 10" canvas top-right).
    corner="br": master deck cover — e.g. x=8.67, y=4.41, d=2.18.
    Shift x by +3.333 for the 13.333" canvas.
    """
    inner = 0.818 * d
    shape(slide, MSO_SHAPE.OVAL, x, y, d, d, line=pal.accent, lw=0.53)
    shape(slide, MSO_SHAPE.OVAL, x + (d - inner) / 2, y + (d - inner) / 2, inner, inner,
          line=pal.accent, lw=0.27, line_alpha=42)
    dx, dy = (0.182, 0.036) if corner == "tr" else (0.147, 0.179)
    shape(slide, MSO_SHAPE.OVAL, x + dx * d, y + dy * d, inner, inner,
          fill=pal.accent, fill_alpha=42)


def rule(slide, x, y, w, color, *, h=0.01):
    """Hairline as a thin rectangle (renders identically in PowerPoint, Keynote, Slides)."""
    return shape(slide, MSO_SHAPE.RECTANGLE, x, y, w, h, fill=color)


# ── master-format composites ─────────────────────────────────────────
def crosshair(slide, x, y, pal: Palette, *, size=0.21, color=None):
    """CAD registration '+' centred on (x, y)."""
    c = color or pal.accent
    rule(slide, x - size / 2, y - 0.005, size, c)
    shape(slide, MSO_SHAPE.RECTANGLE, x - 0.005, y - size / 2, 0.01, size, fill=c)


def bracket_box(slide, x, y, w, h, pal: Palette, *, arm=0.18, color=None, fill=None,
                weight=0.018):
    """Corner brackets (CAD viewfinder) around a region, optional fill behind."""
    c = color or pal.accent
    if fill is not None:
        shape(slide, MSO_SHAPE.RECTANGLE, x, y, w, h, fill=fill)
    t = weight
    for cx, cy, sx, sy in ((x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
        hx = cx if sx > 0 else cx - arm
        vy = cy if sy > 0 else cy - arm
        shape(slide, MSO_SHAPE.RECTANGLE, hx, cy if sy > 0 else cy - t, arm, t, fill=c)
        shape(slide, MSO_SHAPE.RECTANGLE, cx if sx > 0 else cx - t, vy, t, arm, fill=c)


def tile_row(slide, x, y, w, h, tiles, pal: Palette, *, gap=0.3, value_size=26, emphasis=None):
    """Overview tiles: tiles=[(LABEL, value, body)]. Master 'at a glance' pattern.

    emphasis: index of the lead metric — its value renders in accent and larger.
    """
    tw = (w - gap * (len(tiles) - 1)) / len(tiles)
    for i, (lab, value, body) in enumerate(tiles):
        tx = x + i * (tw + gap)
        shape(slide, MSO_SHAPE.RECTANGLE, tx, y, tw, h, fill=pal.card, line=pal.card_line)
        rule(slide, tx, y - 0.005, tw, pal.accent, h=0.02)
        label(slide, tx + 0.18, y + 0.25, tw - 0.3, lab, pal, size=10)
        lead = i == emphasis
        text(slide, tx + 0.18, y + 0.62, tw - 0.3, 0.55, value,
             size=value_size * (1.25 if lead else 1), bold=True,
             color=pal.accent if lead else pal.text)
        text(slide, tx + 0.18, y + 1.35, tw - 0.3, h - 1.45, [runs(body)], size=10,
             color=pal.subtle, line_spacing=1.1)


def numbered_cards(slide, x, y, w, h, items, pal: Palette, *, gap=0.15, highlight=None,
                   dim=(), number_size=36, focus=False):
    """Success-criteria / path-to-go-live cards.

    items: [dict(num, title, tag=None, lead=None, body=str|list)].
    `tag` sits between title and rule (durations, 'WE ARE HERE');
    `lead` is an accent headline above the body ('≥80%').
    highlight: index drawn on the lighter panel; dim: indices drawn muted.
    focus=True (with highlight): only the highlighted card keeps the accent;
    the others get a neutral bar and white numeral, so "where we are" is the
    single orange signal. Leave False for flat lists (success criteria).
    """
    cw = (w - gap * (len(items) - 1)) / len(items)
    for i, it in enumerate(items):
        cx = x + i * (cw + gap)
        muted = i in dim
        neutral = focus and highlight is not None and i != highlight and not muted
        shape(slide, MSO_SHAPE.RECTANGLE, cx, y, cw, h,
              fill=pal.panel if i == highlight else pal.card, line=pal.card_line)
        acc = pal.muted if (muted or neutral) else pal.accent
        rule(slide, cx, y, cw, acc, h=0.06)
        text(slide, cx + 0.18, y + 0.17, cw - 0.3, 0.62, str(it["num"]), size=number_size,
             bold=True, color=pal.text if neutral else acc)
        text(slide, cx + 0.18, y + 0.8, cw - 0.3, 0.55, it["title"], size=13, bold=True,
             color=pal.muted if muted else pal.text, line_spacing=1.05)
        if it.get("tag"):
            text(slide, cx + 0.18, y + 1.36, cw - 0.3, 0.2, it["tag"].upper(), size=8,
                 bold=True, color=acc)
        rule(slide, cx + 0.18, y + 1.62, cw - 0.36, pal.card_line)
        by = y + 1.78
        if it.get("lead"):
            text(slide, cx + 0.18, by, cw - 0.3, 0.3, it["lead"], size=15, bold=True, color=acc)
            by += 0.36
        body = it.get("body") or []
        text(slide, cx + 0.18, by, cw - 0.32, y + h - by - 0.12,
             [body] if isinstance(body, str) else body, size=10,
             color=pal.muted if muted else pal.text,
             bullet=None if isinstance(body, str) else acc, space_after=6, line_spacing=1.08)


def panel_rows(slide, x, y, w, rows, pal: Palette, *, h=1.1, gap=0.14, label_w=1.75):
    """Translucent rounded rows: rows=[(LABEL, heading, body)]."""
    for i, (lab, head, body) in enumerate(rows):
        ry = y + i * (h + gap)
        shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, ry, w, h, fill=pal.panel, fill_alpha=35,
              adj=[0.08])
        text(slide, x + 0.2, ry, label_w - 0.3, h, lab.upper(), size=12, bold=True,
             color=pal.accent, anchor="m", line_spacing=1.05)
        shape(slide, MSO_SHAPE.RECTANGLE, x + label_w, ry + 0.16, 0.01, h - 0.32,
              fill=pal.muted)
        tx = x + label_w + 0.2
        text(slide, tx, ry + 0.17, w - label_w - 0.4, 0.3, head, size=15, color=pal.accent)
        text(slide, tx, ry + 0.52, w - label_w - 0.4, h - 0.6, body, size=11.5,
             color=pal.text, line_spacing=1.08)


def problem_solution(slide, x, y, w, rows, pal: Palette, *, h=1.02, gap=0.13, left_w=3.45,
                     headers=("PROBLEM", "SOLUTION")):
    """rows=[(problem_text, stat, stat_label, solution_body)].

    Left: numbered dark boxes. Right: umber panels with an accent border,
    big stat + caps label, light body. Accent connector between.
    """
    rx, rw = x + left_w + 0.55, w - left_w - 0.55
    if headers:
        label(slide, x, y - 0.32, left_w, headers[0], pal, color=pal.muted, size=10)
        label(slide, rx, y - 0.32, rw, headers[1], pal, size=10)
    for i, (prob, stat, stat_lab, body) in enumerate(rows):
        ry = y + i * (h + gap)
        shape(slide, MSO_SHAPE.RECTANGLE, x, ry, left_w, h, fill=pal.bg, line=pal.card_line)
        text(slide, x + 0.16, ry + 0.12, 0.5, 0.3, f"{i + 1:02d}", size=11, bold=True,
             color=pal.muted)
        text(slide, x + 0.16, ry + 0.38, left_w - 0.3, h - 0.45, prob, size=12, bold=True,
             color=pal.text, line_spacing=1.05)
        rule(slide, x + left_w, ry + h / 2, 0.55, pal.accent, h=0.012)
        shape(slide, MSO_SHAPE.RECTANGLE, rx, ry, rw, h, fill=pal.layer_deepest,
              line=pal.accent, lw=0.75)
        text(slide, rx + 0.2, ry + 0.12, rw - 0.35, 0.42,
             [[(stat + "  ", {"size": 24}), (stat_lab.upper(), {"size": 10})]],
             bold=True, color=pal.accent, anchor="b")
        text(slide, rx + 0.2, ry + 0.58, rw - 0.35, h - 0.62, body, size=10.5,
             color=pal.text, line_spacing=1.08)
