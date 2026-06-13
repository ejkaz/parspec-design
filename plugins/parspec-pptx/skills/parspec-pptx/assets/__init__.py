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
"""

from . import brand, builder
from .brand import Brand, load
from .builder import (
    SLIDE_W, SLIDE_H,
    new_deck, blank,
    add_text, add_rect, add_line,
    corner_brackets, quarter_circle_accent, divider_rule, vector_motif,
    footer,
)

__all__ = [
    "brand", "builder",
    "Brand", "load",
    "SLIDE_W", "SLIDE_H",
    "new_deck", "blank",
    "add_text", "add_rect", "add_line",
    "corner_brackets", "quarter_circle_accent", "divider_rule",
    "vector_motif", "footer",
]
