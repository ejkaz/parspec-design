"""
parspec-pptx — town hall register (compatibility wrapper).

The implementation lives in `assets/house.py`; this module keeps the
`TownHall` name and the town hall geometry constants importable.
"""

from __future__ import annotations

from .house import PROFILES, HouseDeck, strip_to_template  # noqa: F401

_P = PROFILES["townhall"]
LAYOUTS = _P.layouts
DEFAULT_TEMPLATE = _P.template
TEMPLATE_ENV = _P.env
W, H = 10.0, 5.625
X0, XW, TOP, BOTTOM = _P.x0, _P.xw, _P.top, _P.bottom


class TownHall(HouseDeck):
    def __init__(self, template=None, brand=None):
        super().__init__("townhall", template=template, brand=brand)
