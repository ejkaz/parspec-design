"""
Starter scaffold for a new Parspec .pptx deck.

Copy this file to wherever you want the deck source to live, edit the
strings + layouts, then `python3 your_deck.py` to build.

The render daemon is invoked separately via `scripts/render.sh deck.pptx`
to get per-slide PNG previews you can hand to a vision review.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ── wire up parspec-pptx ──────────────────────────────────────────────
PPTX_SKILL = Path(
    "/Users/eric/Desktop/Parspec.b/Vault/005_The_Lab/5.3_Automation_&_Scripts"
    "/parspec-design/plugins/parspec-pptx/skills/parspec-pptx"
)
sys.path.insert(0, str(PPTX_SKILL))

from assets import (  # noqa: E402
    load, new_deck, blank, corner_brackets, footer,
    add_text, add_rect, add_line,
    divider_rule, quarter_circle_accent, vector_motif,
    SLIDE_W, SLIDE_H,
)
from pptx.util import Inches, Pt  # noqa: E402
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR  # noqa: E402


# ── build ──────────────────────────────────────────────────────────────
def build():
    b = load()  # reads design-model.yaml v2.0.0 by default
    prs = new_deck()

    # Example cover — replace with layout recipes from references/layouts.md
    s = blank(prs, brand=b)
    corner_brackets(s, brand=b)
    add_text(s, Inches(0.85), Inches(0.85), Inches(8), Inches(0.4),
             "PARSPEC  ·  YOUR DECK NAME",
             size=10, weight="semibold", color=b.cta,
             letter_spacing=4, upper=True, brand=b)
    divider_rule(s, Inches(0.85), Inches(1.4), Inches(0.7),
                 color=b.cta, weight=2.5)
    add_text(s, Inches(0.85), Inches(1.7), Inches(11.6), Inches(2.0),
             "YOUR TITLE\nHERE",
             size=58, weight="black", color=b.text_dark_primary,
             letter_spacing=-1.5, line_spacing=1.0, brand=b)

    out = Path("/tmp/deck.pptx")
    prs.save(out)
    print(f"wrote {out}  ({out.stat().st_size:,} bytes, {len(prs.slides)} slides)")
    return out


if __name__ == "__main__":
    build()
