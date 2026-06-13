"""
parspec-pptx — brand token loader.

Single source of truth: reads ../parspec-design/skills/parspec-design/design-model.yaml
and resolves the role tokens used by parspec-pptx builders.

Anything visual in this skill should reach for `tokens` (the resolved Brand object)
rather than hard-coding hex values. When the brand evolves in design-model.yaml,
every pptx auto-tracks on next run.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pptx.dml.color import RGBColor


# ── locate design-model.yaml ──────────────────────────────────────────
def _design_model_path() -> Path:
    """Locate sibling parspec-design plugin's design-model.yaml."""
    here = Path(__file__).resolve()
    # Walk up to find the parspec-design plugin
    # __file__ = .../plugins/parspec-pptx/skills/parspec-pptx/assets/brand.py
    # target  = .../plugins/parspec-design/skills/parspec-design/design-model.yaml
    plugins_dir = here.parents[4]
    candidate = (
        plugins_dir / "parspec-design" / "skills" / "parspec-design" /
        "design-model.yaml"
    )
    if not candidate.exists():
        raise FileNotFoundError(
            f"design-model.yaml not found at {candidate}. "
            "parspec-pptx must be installed alongside parspec-design."
        )
    return candidate


# ── reference resolver ────────────────────────────────────────────────
_REF = re.compile(r"^\{([a-zA-Z_][\w.]*)\}$")


def _get_path(root: dict, dotted: str) -> Any:
    """primitives.colors.brand.500 -> root[primitives][colors][brand][500]."""
    node = root
    for part in dotted.split("."):
        # YAML deserialises pure-int keys (e.g., 500) as int, not str
        if isinstance(node, dict):
            if part in node:
                node = node[part]
            else:
                try:
                    node = node[int(part)]
                except (KeyError, ValueError):
                    raise KeyError(f"Token path not found: {dotted}")
        else:
            raise KeyError(f"Token path not found: {dotted}")
    return node


def _resolve(value: Any, root: dict, depth: int = 0) -> Any:
    """Recursively resolve {ref.path} placeholders against the full model tree.

    Bare references like `{brand.500}` or `{neutral.950}` are treated as
    shorthand for `primitives.colors.<path>` per design-model.yaml convention.
    """
    if depth > 12:
        raise RecursionError(f"Token reference too deep: {value!r}")
    if isinstance(value, str):
        m = _REF.match(value.strip())
        if m:
            path = m.group(1)
            try:
                target = _get_path(root, path)
            except KeyError:
                # Shorthand: bare color reference → primitives.colors.<path>
                target = _get_path(root, f"primitives.colors.{path}")
            return _resolve(target, root, depth + 1)
        return value
    return value


# ── color conversion ──────────────────────────────────────────────────
def _hex_to_rgb(hex_str: str) -> RGBColor:
    s = hex_str.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    return RGBColor(int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


# ── role token catalog ────────────────────────────────────────────────
# Maps Python attribute name → roles.* key in design-model.yaml.
# Add a role here once and it becomes available throughout builders.
ROLE_TOKENS = {
    # surfaces
    "surface_dark":          "surface_dark",
    "surface_dark_panel":    "surface_dark_panel",
    "surface_dark_alt":      "surface_dark_alt",
    "surface_light":         "surface_light",
    "surface_doc":           "surface_doc",
    "surface_paper":         "surface_paper",
    # ctas + accents
    "cta":                   "cta",
    "cta_hover":             "cta_hover",
    "cta_active":            "cta_active",
    "cta_text":              "cta_text",
    "accent_type_on_dark":   "accent_type_on_dark",
    "accent_type_on_light":  "accent_type_on_light",
    # cools
    "cool_primary":          "cool_primary",
    "cool_hero":             "cool_hero",
    "cool_chart_on_dark":    "cool_chart_on_dark",
    # info / engineering doc register
    "info_on_light":         "info_on_light",
    "info_on_dark":          "info_on_dark",
    "doc_title_block":       "doc_title_block",
    # body chrome / borders
    "body_chrome_on_dark":   "body_chrome_on_dark",
    "border_dark":           "border_dark",
    "border_light":          "border_light",
    # text
    "text_dark_primary":     "text_dark_primary",
    "text_dark_secondary":   "text_dark_secondary",
    "text_dark_tertiary":    "text_dark_tertiary",
    "text_light_primary":    "text_light_primary",
    # status
    "status_error_on_dark":  "status_error_on_dark",
    "status_warn_on_dark":   "status_warn_on_dark",
}


# Convenience aliases — what tonight's hand-rolled build_deck.py used.
# Lets `from brand import BLACK, BRAND_ORANGE, ...` keep working
# while routing every constant through the SSoT.
ALIAS_MAP = {
    "BLACK":          "surface_dark",
    "CHARCOAL":       "surface_dark_panel",
    "CHARCOAL_LIGHT": "surface_dark_alt",
    "WHITE":          "text_dark_primary",
    "NEUTRAL_300":    "text_dark_secondary",
    "NEUTRAL_500":    "text_dark_tertiary",
    "BRAND_ORANGE":   "cta",
    "BRAND_BURNT":    "cta_active",
    "BRAND_HOVER":    "cta_hover",
    "STEEL_300":      "info_on_dark",
    "STEEL_500":      "info_on_light",
    "STEEL_700":      "doc_title_block",
    "TEAL_300":       "cool_chart_on_dark",
    "TEAL_500":       "cool_primary",
    "SLATE_300":      "body_chrome_on_dark",
    "SLATE_700":      "border_dark",
    "AMBER_600":      "status_warn_on_dark",
    "ERROR_RED":      "status_error_on_dark",
    "PAPER_WARM":     "surface_paper",
}


@dataclass
class Brand:
    """Resolved Parspec brand tokens, ready to drop into python-pptx."""
    version: str
    brand_version: str
    font: str
    font_weights: list[int]
    colors: dict[str, RGBColor] = field(default_factory=dict)
    voice_do: list[str] = field(default_factory=list)
    voice_avoid: list[str] = field(default_factory=list)
    avoid_fonts: list[str] = field(default_factory=list)
    raw: dict = field(default_factory=dict)

    def __getattr__(self, name: str):
        # Accessor for ALIAS_MAP names (BLACK, BRAND_ORANGE, ...)
        # Only called when normal attribute lookup fails.
        if name in self.colors:
            return self.colors[name]
        raise AttributeError(name)

    # Role tokens — lookup by role name string
    def role(self, name: str) -> RGBColor:
        return self.colors[name]


def load(path: Path | None = None) -> Brand:
    """Load + resolve design-model.yaml; return Brand object."""
    p = Path(path) if path else _design_model_path()
    raw = yaml.safe_load(p.read_text())

    # Meta
    meta = raw.get("meta", {})
    version = meta.get("version", "unknown")
    brand_version = meta.get("brand_version", "unknown")

    # Typography
    typo = raw.get("tokens", {}).get("typography", {})
    font = typo.get("family", "Montserrat")
    font_weights = typo.get("weights_used", [400, 500, 600, 700, 800, 900])

    # Voice
    voice = raw.get("voice", {})
    voice_do = voice.get("do", [])
    voice_avoid = voice.get("avoid", [])
    avoid_fonts = [
        a.get("font_family") for a in raw.get("avoid", [])
        if a.get("font_family")
    ]

    # Resolve role + alias colors
    colors: dict[str, RGBColor] = {}
    for py_name, role_key in ROLE_TOKENS.items():
        raw_val = _get_path(raw, f"roles.{role_key}")
        resolved = _resolve(raw_val, raw)
        if not isinstance(resolved, str) or not resolved.startswith("#"):
            raise ValueError(
                f"Role {role_key} did not resolve to a hex color: {resolved!r}"
            )
        colors[py_name] = _hex_to_rgb(resolved)

    # Backfill alias names → already-resolved role colors
    for alias, role_py in ALIAS_MAP.items():
        if role_py in colors:
            colors[alias] = colors[role_py]

    # OFF_WHITE — primitive, no role binding needed
    off_white = _get_path(raw, "primary_axis_preserved.off_white")
    colors["OFF_WHITE"] = _hex_to_rgb(off_white)

    return Brand(
        version=version,
        brand_version=brand_version,
        font=font,
        font_weights=font_weights,
        colors=colors,
        voice_do=voice_do,
        voice_avoid=voice_avoid,
        avoid_fonts=avoid_fonts,
        raw=raw,
    )


if __name__ == "__main__":
    b = load()
    print(f"Parspec brand v{b.version} ({b.brand_version})")
    print(f"Font: {b.font}")
    print(f"Colors loaded: {len(b.colors)}")
    print(f"CTA: {b.cta}")
    print(f"PAPER_WARM: {b.PAPER_WARM}")
    print(f"Voice DOs: {len(b.voice_do)}  AVOIDs: {len(b.voice_avoid)}")
