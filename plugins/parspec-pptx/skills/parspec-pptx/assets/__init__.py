"""parspec-pptx assets — brand loader + builder primitives.

Usage from a deck-build script:

    import sys
    from pathlib import Path
    PPTX_SKILL = Path("/path/to/plugins/parspec-pptx/skills/parspec-pptx")
    sys.path.insert(0, str(PPTX_SKILL))
    from assets import brand, builder
    from assets.brand import load as load_brand
    from assets.builder import new_deck, blank, add_text, corner_brackets, footer

The skill ships a helper `scripts/init_deck.py` template that handles the
path-injection for you — copy + edit per deck.

Two registers:
    builder   — brand_artifacts canvas (13.333 x 7.5), corner brackets, drawn chrome
    house     — company deck templates (10 x 5.625) with their own logo/footer:
                HouseDeck(profile="master" | "townhall"); compose bodies with
                `shapes` (numbered cards, panel rows, funnel, process, ...)
"""

from . import brand, builder, house, shapes, townhall
from .brand import Brand, load
from .house import HouseDeck
from .shapes import Palette
from .townhall import TownHall
from .builder import (
    SLIDE_W, SLIDE_H,
    new_deck, blank,
    add_text, add_rect, add_line,
    corner_brackets, quarter_circle_accent, divider_rule, vector_motif,
    footer,
)

__all__ = [
    "brand", "builder", "house", "shapes", "townhall",
    "Brand", "load", "HouseDeck", "Palette", "TownHall",
    "SLIDE_W", "SLIDE_H",
    "new_deck", "blank",
    "add_text", "add_rect", "add_line",
    "corner_brackets", "quarter_circle_accent", "divider_rule",
    "vector_motif", "footer",
]
