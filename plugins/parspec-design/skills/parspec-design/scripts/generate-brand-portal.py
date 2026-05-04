#!/usr/bin/env python3
"""
generate-brand-portal.py

Reads design-model.yaml (sibling file) and emits 4 self-contained HTML pages
into ../brand-portal/. Each page is regenerated from the YAML — manual edits
are not allowed (the brand portal v0 governance rule from R3 review).

Usage:
    python3 generate-brand-portal.py

Output:
    ../brand-portal/index.html
    ../brand-portal/color.html
    ../brand-portal/logo.html
    ../brand-portal/typography.html
    ../brand-portal/co-brand.html
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip3 install pyyaml", file=sys.stderr)
    sys.exit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
YAML_PATH = SKILL_DIR / "design-model.yaml"
OUT_DIR = SKILL_DIR / "brand-portal"

AUTOGEN_BANNER = """<!--
    AUTO-GENERATED FROM design-model.yaml — DO NOT EDIT MANUALLY
    Regenerate: python3 scripts/generate-brand-portal.py
    Generated: {timestamp}
    design-model.yaml version: {version} · brand_version: {brand_version}
-->"""


# ─── Common page chrome ────────────────────────────────────────────────────

def page_chrome(model: dict, page_title: str, body: str, current: str) -> str:
    meta = model["meta"]
    banner = AUTOGEN_BANNER.format(
        timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        version=meta["version"],
        brand_version=meta["brand_version"],
    )
    nav = nav_html(current)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{banner}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Parspec Brand Portal — {page_title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
{base_styles()}
</head>
<body>
<header class="portal-header">
  <div class="portal-header-inner">
    <div class="portal-mark">
      <strong>PARSPEC</strong>
      <span class="portal-meta">Brand Portal · v{meta['version']} · {meta['brand_version']}</span>
    </div>
    {nav}
  </div>
</header>

<main class="portal-main">
  <h1 class="page-title">{page_title}</h1>
  {body}
</main>

<footer class="portal-footer">
  <div>Auto-generated from <code>design-model.yaml</code>. Manual edits not permitted.</div>
  <div>Regenerate: <code>python3 scripts/generate-brand-portal.py</code></div>
</footer>
</body>
</html>
"""


def nav_html(current: str) -> str:
    items = [
        ("index.html", "Overview"),
        ("color.html", "Color"),
        ("logo.html", "Logo & Motifs"),
        ("typography.html", "Typography"),
        ("co-brand.html", "Co-brand Rules"),
    ]
    lis = []
    for href, label in items:
        cls = "portal-nav-item active" if href == current else "portal-nav-item"
        lis.append(f'<a class="{cls}" href="{href}">{label}</a>')
    return f'<nav class="portal-nav">{"".join(lis)}</nav>'


def base_styles() -> str:
    return """<style>
:root {
  --bg: #0F0F0F;
  --bg-2: #1A1A1A;
  --bg-3: #2E2E2E;
  --fg: #F2F2F2;
  --fg-muted: rgba(242,242,242,0.6);
  --fg-dim: rgba(242,242,242,0.4);
  --orange: #FFA72B;
  --border: rgba(242,242,242,0.12);
  --gap-sm: clamp(0.5rem, 1vw, 1rem);
  --gap-md: clamp(1rem, 2vw, 2rem);
  --gap-lg: clamp(1.5rem, 3vw, 3rem);
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--fg);
  font-family: 'Montserrat', -apple-system, sans-serif; line-height: 1.5; }
code { font-family: 'SF Mono', 'Menlo', monospace; font-size: 0.9em;
  background: rgba(255,167,43,0.1); padding: 0.1em 0.4em; border-radius: 3px;
  color: var(--orange); }
strong { font-weight: 700; }

.portal-header { position: sticky; top: 0; background: var(--bg);
  border-bottom: 1px solid var(--border); z-index: 10; padding: 1rem 0; }
.portal-header-inner { max-width: 1200px; margin: 0 auto;
  padding: 0 var(--gap-md); display: flex; justify-content: space-between;
  align-items: center; gap: var(--gap-md); flex-wrap: wrap; }
.portal-mark { display: flex; flex-direction: column; gap: 0.2rem; }
.portal-mark strong { font-weight: 900; letter-spacing: 0.08em; font-size: 1.1rem; color: var(--orange); }
.portal-meta { font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--fg-muted); }
.portal-nav { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.portal-nav-item { color: var(--fg-muted); text-decoration: none;
  font-size: 0.8rem; font-weight: 600; letter-spacing: 0.08em;
  text-transform: uppercase; padding: 0.4rem 0.8rem; border-radius: 3px;
  border: 1px solid transparent; transition: all 0.15s ease; }
.portal-nav-item:hover { color: var(--fg); border-color: var(--border); }
.portal-nav-item.active { color: var(--orange); border-color: var(--orange); }

.portal-main { max-width: 1200px; margin: 0 auto; padding: var(--gap-lg) var(--gap-md); }
.page-title { font-size: clamp(2rem, 5vw, 3.5rem); font-weight: 800;
  letter-spacing: -0.02em; margin: 0 0 var(--gap-md) 0; line-height: 1.05; }
.page-lead { color: var(--fg-muted); font-size: 1.1rem; max-width: 65ch;
  line-height: 1.5; margin-bottom: var(--gap-lg); }

h2.section { font-size: 1.5rem; font-weight: 700; letter-spacing: -0.015em;
  margin: var(--gap-lg) 0 var(--gap-md) 0; padding-top: var(--gap-md);
  border-top: 1px solid var(--border); }
h3.subsection { font-size: 1.1rem; font-weight: 700; letter-spacing: -0.005em;
  margin: var(--gap-md) 0 var(--gap-sm) 0; }
.eyebrow { font-size: 0.7rem; letter-spacing: 0.18em; text-transform: uppercase;
  font-weight: 700; color: var(--orange); margin-bottom: 0.5rem; }

.swatch-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: var(--gap-sm); margin-bottom: var(--gap-md); }
.swatch { aspect-ratio: 1.6 / 1; border-radius: 4px; padding: 1rem;
  display: flex; flex-direction: column; justify-content: space-between;
  font-size: 0.75rem; font-weight: 600; border: 1px solid rgba(0,0,0,0.06); }
.swatch .swatch-name { font-weight: 700; font-size: 0.8rem; line-height: 1.15; }
.swatch .swatch-hex { font-family: 'SF Mono', 'Menlo', monospace; font-size: 0.7rem;
  font-weight: 500; opacity: 0.85; padding: 0; background: transparent; color: inherit; }
.swatch .swatch-role { font-size: 0.7rem; opacity: 0.7; line-height: 1.3; margin-top: 0.3rem; }

.token-row { display: grid; grid-template-columns: minmax(160px, 1fr) minmax(120px, 1fr) 2fr;
  gap: var(--gap-md); padding: 0.7rem 0; border-bottom: 1px solid var(--border);
  align-items: start; font-size: 0.9rem; }
.token-row .role-name { font-weight: 700; }
.token-row .role-ref { font-family: 'SF Mono', monospace; font-size: 0.85em;
  color: var(--fg-muted); }
.token-row .role-desc { color: var(--fg-muted); line-height: 1.45; }
.token-chip { display: inline-block; width: 1em; height: 1em; vertical-align: middle;
  border-radius: 2px; margin-right: 0.4em; border: 1px solid rgba(255,255,255,0.15); }

.callout { border-left: 3px solid var(--orange); background: rgba(255,167,43,0.06);
  padding: var(--gap-md); margin: var(--gap-md) 0; border-radius: 0 4px 4px 0; }
.callout strong { color: var(--orange); }

.dontpair { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--gap-sm); margin-top: var(--gap-sm); }
.dontpair-item { background: rgba(255,255,255,0.03); border: 1px solid var(--border);
  padding: 0.8rem; border-radius: 4px; font-size: 0.85rem; }
.dontpair-item .dp-color { display: inline-block; width: 1.4em; height: 1.4em;
  border-radius: 3px; margin-right: 0.4em; vertical-align: middle;
  border: 1px solid rgba(255,255,255,0.15); }
.dontpair-item .dp-name { font-weight: 700; }
.dontpair-item .dp-reason { color: var(--fg-muted); font-size: 0.8rem;
  margin-top: 0.4rem; line-height: 1.4; }

.surface-card { background: var(--bg-2); border: 1px solid var(--border);
  border-radius: 4px; padding: var(--gap-md); margin-bottom: var(--gap-sm); }
.surface-card h3 { margin: 0 0 0.4rem 0; }
.surface-card .surface-meta { font-family: 'SF Mono', monospace; font-size: 0.8rem;
  color: var(--fg-muted); padding: 0; background: transparent; }
.surface-card .surface-rationale { color: var(--fg-muted); font-size: 0.9rem;
  line-height: 1.55; margin-top: 0.6rem; }

.portal-footer { max-width: 1200px; margin: var(--gap-lg) auto 0;
  padding: var(--gap-md); border-top: 1px solid var(--border);
  display: flex; justify-content: space-between; gap: var(--gap-md);
  font-size: 0.75rem; color: var(--fg-dim); flex-wrap: wrap; }

@media (max-width: 600px) {
  .portal-nav { width: 100%; justify-content: flex-start; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition-duration: 0.2s !important; }
}
</style>"""


def text_for_bg(hex_str: str) -> str:
    """Return #FFFFFF or #0F0F0F based on background luminance."""
    h = hex_str.lstrip("#")
    if len(h) != 6:
        return "#F2F2F2"
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    # Relative luminance approximation
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return "#0F0F0F" if lum > 140 else "#F2F2F2"


def resolve_role(value: str, primitives: dict) -> str:
    """Resolve a {ramp.step} reference to a hex value."""
    if not isinstance(value, str) or not value.startswith("{") or not value.endswith("}"):
        return value
    parts = value.strip("{}").split(".")
    cur = primitives.get("colors", {})
    for p in parts:
        if isinstance(cur, dict):
            # YAML may parse integer keys
            try:
                key = int(p)
            except ValueError:
                key = p
            cur = cur.get(key, cur.get(p, "#000000"))
        else:
            break
    return cur if isinstance(cur, str) else "#000000"


# ─── Page builders ─────────────────────────────────────────────────────────

def build_index(model: dict) -> str:
    meta = model["meta"]
    body = f"""
<p class="page-lead">Parspec brand SSoT, rendered from <code>design-model.yaml</code>. Every value on this site is auto-generated; the YAML is the only place to change anything. To regenerate after a YAML edit, run <code>python3 scripts/generate-brand-portal.py</code>.</p>

<div class="callout">
  <div class="eyebrow">Active version</div>
  <p style="margin:0;">Schema version <strong>{meta['version']}</strong> · Brand version <strong>{meta['brand_version']}</strong> · Updated <strong>{meta['updated']}</strong> by <strong>{meta['updated_by']}</strong>.</p>
</div>

<h2 class="section">What's here</h2>

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: var(--gap-md); margin-top: var(--gap-md);">
  <a href="color.html" style="text-decoration:none; color:inherit;">
    <div class="surface-card">
      <h3>Color</h3>
      <p class="surface-rationale">Primary axis, primitive ramps, role tokens, surfaces, don't-pair list.</p>
    </div>
  </a>
  <a href="logo.html" style="text-decoration:none; color:inherit;">
    <div class="surface-card">
      <h3>Logo &amp; Motifs</h3>
      <p class="surface-rationale">Locked primary axis, motif inventory, clear-space rules.</p>
    </div>
  </a>
  <a href="typography.html" style="text-decoration:none; color:inherit;">
    <div class="surface-card">
      <h3>Typography</h3>
      <p class="surface-rationale">Montserrat ladder with explicit tracking. Linear/Vercel pattern.</p>
    </div>
  </a>
  <a href="co-brand.html" style="text-decoration:none; color:inherit;">
    <div class="surface-card">
      <h3>Co-brand Rules</h3>
      <p class="surface-rationale">Sonepar/Wesco/Graybar AE-readable rules + Procore bake-off rule + 10-year lock.</p>
    </div>
  </a>
</div>

<h2 class="section">Latest changelog</h2>
<pre style="background: var(--bg-2); border: 1px solid var(--border); border-radius: 4px; padding: var(--gap-md); white-space: pre-wrap; line-height: 1.6; font-size: 0.85rem; color: var(--fg-muted); font-family: inherit;">{meta.get('notes', '').strip()}</pre>
"""
    return page_chrome(model, "Overview", body, "index.html")


def build_color(model: dict) -> str:
    primitives = model["primitives"]
    primary_axis = model["primary_axis_preserved"]
    roles = model.get("roles", {})
    surfaces = model.get("surfaces", {})
    avoid = model.get("avoid", [])

    # Primary axis swatches
    axis_swatches = []
    axis_items = [
        ("Parspec Black", primary_axis["parspec_black"], "Default brand-artifact background"),
        ("Charcoal", primary_axis["charcoal"], "Layering / secondary surface"),
        ("Off-white", primary_axis["off_white"], "Document / heavy-text surfaces"),
        ("White", primary_axis["white"], "Text on dark"),
        ("Brand Orange", primary_axis["brand_orange"], "CTA monopoly"),
    ]
    for name, hex_v, role in axis_items:
        fg = text_for_bg(hex_v)
        axis_swatches.append(
            f'<div class="swatch" style="background:{hex_v}; color:{fg}; border:1px solid rgba(0,0,0,0.1);">'
            f'<div><div class="swatch-name">{name}</div><span class="swatch-hex">{hex_v}</span></div>'
            f'<div class="swatch-role">{role}</div></div>'
        )

    # Primitive ramps
    ramps_html = []
    for ramp_name, ramp in primitives["colors"].items():
        if not isinstance(ramp, dict):
            continue
        items = []
        for step, hex_v in ramp.items():
            if not isinstance(hex_v, str):
                continue
            fg = text_for_bg(hex_v)
            label = f"{ramp_name}.{step}"
            items.append(
                f'<div class="swatch" style="background:{hex_v}; color:{fg};">'
                f'<div><div class="swatch-name" style="font-size:0.7rem;">{step}</div></div>'
                f'<span class="swatch-hex">{hex_v}</span></div>'
            )
        ramps_html.append(
            f'<h3 class="subsection"><code>primitives.colors.{ramp_name}</code></h3>'
            f'<div class="swatch-grid" style="grid-template-columns:repeat(auto-fill,minmax(120px,1fr));">{"".join(items)}</div>'
        )

    # Role tokens
    role_rows = []
    for role_name, ref in roles.items():
        resolved = resolve_role(ref, primitives) if isinstance(ref, str) else ""
        chip = f'<span class="token-chip" style="background:{resolved};"></span>' if resolved.startswith("#") else ""
        role_rows.append(
            f'<div class="token-row">'
            f'<div class="role-name">{chip}{role_name}</div>'
            f'<div class="role-ref">{ref} → {resolved}</div>'
            f'<div class="role-desc">Role token (v1.1.0 two-tier model). Every consumer references this name, not the hex.</div>'
            f'</div>'
        )

    # Surfaces
    surface_cards = []
    for surface_name, s in surfaces.items():
        bg_ref = s.get("background", "")
        bg_resolved = resolve_role(bg_ref, primitives) if isinstance(bg_ref, str) else ""
        examples = ", ".join(s.get("examples", []))
        rationale = s.get("rationale", "").strip()
        mode = s.get("mode", "")
        surface_cards.append(
            f'<div class="surface-card">'
            f'<h3>{surface_name.replace("_", " ").title()}</h3>'
            f'<div class="surface-meta">mode: <strong>{mode}</strong> · background: {bg_ref} → {bg_resolved}</div>'
            f'<div style="margin-top:0.5rem; font-size:0.85rem; color:var(--fg-muted);"><strong>Examples:</strong> {examples}</div>'
            f'<p class="surface-rationale">{rationale}</p>'
            f'</div>'
        )

    # Don't-pair
    dontpair_items = []
    for entry in avoid:
        if "color" in entry:
            color = entry["color"]
            name = entry.get("name", color)
            reason = entry.get("reason", "")
            dontpair_items.append(
                f'<div class="dontpair-item">'
                f'<span class="dp-color" style="background:{color};"></span>'
                f'<span class="dp-name">{name}</span> <code style="font-size:0.7rem;">{color}</code>'
                f'<div class="dp-reason">{reason}</div>'
                f'</div>'
            )

    body = f"""
<p class="page-lead">Two-tier token model: primitive ramps → role tokens. Every CSS variable that consumes color references a role, not a primitive directly. Polaris/Carbon precedent. Compile-time enforcement of the CTA monopoly happens because nothing in the codebase has a hex literal for actions — they all use <code>{{cta}}</code>.</p>

<h2 class="section">Primary axis (locked)</h2>
<p style="color:var(--fg-muted); margin-bottom:var(--gap-md);">These do not change. Any palette evolution modifies secondaries / tints / motifs — never these.</p>
<div class="swatch-grid">{''.join(axis_swatches)}</div>

<h2 class="section">Surfaces — mode per surface</h2>
{''.join(surface_cards)}

<h2 class="section">Roles — semantic tokens</h2>
{''.join(role_rows)}

<h2 class="section">Primitive ramps</h2>
{''.join(ramps_html)}

<h2 class="section">Don't pair · forbidden colors</h2>
<p style="color:var(--fg-muted);">Surfaced from <code>design-model.yaml</code> <code>avoid:</code> block. parspec-craft lints any HTML containing these as a hex literal.</p>
<div class="dontpair">{''.join(dontpair_items) or '<p style="color:var(--fg-muted);">None.</p>'}</div>
"""
    return page_chrome(model, "Color", body, "color.html")


def build_logo(model: dict) -> str:
    axis = model["primary_axis_preserved"]
    motifs = axis.get("motifs", [])
    motif_descs = {
        "corner-brackets": "CAD viewfinder bracket marks. Used at slide corners, KPI panels, hero anchors. Locked-primary axis.",
        "quarter-circles": "Geometric quarter-circle arcs. Section dividers, hero accents, footer flourishes.",
        "orange-line-illos": "Single-color orange line illustrations on dark. Hard hat, blueprint, distribution node, ERP gear, factory, clipboard. Lucide icon kit as fallback.",
        "drawing-block-header": "★ NEW v1.1.0 signature motif. Title / project / sheet / rev lockup at the top of every PDF. Single-handedly converts brand-evolution from token swap to positioning. Drawn by a technical illustrator with construction-document literacy.",
    }

    motif_cards = []
    for m in motifs:
        desc = motif_descs.get(m, "")
        is_signature = m == "drawing-block-header"
        border = "border-left: 3px solid var(--orange);" if is_signature else ""
        motif_cards.append(
            f'<div class="surface-card" style="{border}">'
            f'<h3>{m}{" ★ signature" if is_signature else ""}</h3>'
            f'<p class="surface-rationale">{desc}</p>'
            f'</div>'
        )

    body = f"""
<p class="page-lead">Locked anchors of the Parspec brand. The wordmark, the typography family, and the four motifs do not move across palette evolutions.</p>

<h2 class="section">Locked primary axis</h2>
<div class="token-row" style="grid-template-columns: minmax(180px, 1fr) 2fr;">
  <div class="role-name">Wordmark</div>
  <div class="role-desc">PARSPEC mark, orange + white on dark. Logo files maintained outside this portal in <code>brand-assets/</code>.</div>
</div>
<div class="token-row" style="grid-template-columns: minmax(180px, 1fr) 2fr;">
  <div class="role-name">Typography</div>
  <div class="role-desc"><strong>{axis['typography_family']}</strong> — single family across every Parspec surface. See Typography page.</div>
</div>
<div class="token-row" style="grid-template-columns: minmax(180px, 1fr) 2fr;">
  <div class="role-name">CTA color</div>
  <div class="role-desc">Brand Orange <code>{axis['cta_color']}</code> — monopoly enforced as <code>error</code>-level invariant.</div>
</div>

<h2 class="section">Signature motifs</h2>
<p style="color:var(--fg-muted);">Four motifs locked. The drawing-block header is the v1.1.0 signature — promoted from D4 personality after the 3-round design review (R3 unanimous: "the right answer is neither corner brackets nor blueprint grid — drawing-block header is").</p>
{''.join(motif_cards)}

<div class="callout">
  <div class="eyebrow">Clear-space rule (placeholder for v0)</div>
  <p style="margin:0;">Per Bluebeam partner-branding pattern: clear-space around the wordmark = x-height of the "P" in PARSPEC. AE-readable version: "give the wordmark room equal to the height of one capital letter on every side." Detailed clear-space spec deferred to brand-portal v1 with logo files in tow.</p>
</div>
"""
    return page_chrome(model, "Logo & Motifs", body, "logo.html")


def build_typography(model: dict) -> str:
    typo = model["tokens"]["typography"]

    rows = []
    for role, spec in typo.items():
        if role in ("family", "weights_used"):
            continue
        if spec is None:
            rows.append(
                f'<div class="token-row">'
                f'<div class="role-name">{role}</div>'
                f'<div class="role-ref">null</div>'
                f'<div class="role-desc">Not defined. (Parspec brand has no monospace pairing — see voice rules.)</div>'
                f'</div>'
            )
            continue

        weight = spec.get("weight", 400)
        size = spec.get("size_clamp", "1rem")
        lh = spec.get("line_height", 1.5)
        ls = spec.get("letter_spacing", "0")
        transform = spec.get("transform", "none")
        sample_text = role.upper() if transform == "uppercase" else f"The quick brown fox · {role}"

        rows.append(
            f'<div style="padding: var(--gap-md) 0; border-bottom: 1px solid var(--border);">'
            f'<div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:var(--gap-sm); margin-bottom:0.6rem; font-size:0.8rem; color:var(--fg-muted);">'
            f'<span><strong style="color:var(--fg);">{role}</strong></span>'
            f'<span><code>weight: {weight}</code> · <code>size: {size}</code> · <code>line-height: {lh}</code> · <code>letter-spacing: {ls}</code>{f" · <code>transform: {transform}</code>" if transform != "none" else ""}</span>'
            f'</div>'
            f'<div style="font-family:\'Montserrat\',sans-serif; font-weight:{weight}; font-size:{size}; line-height:{lh}; letter-spacing:{ls}; text-transform:{transform};">{sample_text}</div>'
            f'</div>'
        )

    body = f"""
<p class="page-lead"><strong>{typo.get('family', 'Montserrat')}.</strong> Single family. Locked. Weight ladder: {', '.join(str(w) for w in typo.get('weights_used', []))}.</p>

<div class="callout">
  <div class="eyebrow">v1.1.0 architectural addition</div>
  <p style="margin:0;">Explicit <code>letter_spacing</code> per scale step. Linear/Vercel pattern: tight typography carries semantic-only color without motion or illustration as a carry-layer. Required precondition for warm role-locked accents (post-CEO v2.0.0).</p>
</div>

<h2 class="section">Type scale</h2>
{''.join(rows)}

<h2 class="section">Forbidden families</h2>
<p style="color:var(--fg-muted);">parspec-craft lints any <code>font-family</code> declaration containing these names:</p>
<ul style="line-height:2; color:var(--fg-muted);">
  <li><code>Inter</code> / <code>Roboto</code> / <code>Arial</code> / <code>system-ui</code> / <code>Helvetica</code> / <code>SF Pro</code> / <code>Open Sans</code> / <code>Lato</code></li>
</ul>
<p style="color:var(--fg-muted);">Generic AI-default fonts. Montserrat is the locked Parspec choice.</p>
"""
    return page_chrome(model, "Typography", body, "typography.html")


def build_cobrand(model: dict) -> str:
    body = """
<p class="page-lead">Two AE-readable rule cards an AE can use on a Tuesday at the booth without a designer in the room. Plus the 10-year lock commitment.</p>

<h2 class="section">Card 01 — Co-brand with Sonepar / Wesco / Graybar</h2>
<div class="callout">
  <p style="margin:0; font-size:1.05rem; line-height:1.5;">
    "In any artifact with a Sonepar logo, our orange CTA is visible above the fold and our Deep Spec Blue never sits within a thumb's width of their navy."
  </p>
</div>
<p style="color:var(--fg-muted); font-size:0.9rem; margin-top:var(--gap-sm);">Borrowed from Bluebeam's partner-branding clear-space rule. AE-checkable on a phone. Solves both ΔE-collision risk (#0F2942 vs Sonepar Navy ~#0033A0) AND "looks like a knockoff" risk in one sentence.</p>

<h2 class="section">Card 02 — Bake-off vs Procore</h2>
<div class="callout">
  <p style="margin:0; font-size:1.05rem; line-height:1.5;">
    "More black, less blue. Brand Orange CTA on every action slide. Drawing-block header on every PDF."
  </p>
</div>
<p style="color:var(--fg-muted); font-size:0.9rem; margin-top:var(--gap-sm);">Procore's hero color since 2023 is <code>#FF5200</code>. Steel Blue collisions are inevitable in the category. Differentiation is structural — fewer cool surfaces, more orange action signals, drawing-block as the literacy artifact Procore can't claim.</p>

<h2 class="section">10-year lock commitment</h2>
<div style="background:var(--orange); color:var(--bg); padding:var(--gap-lg); border-radius:4px;">
  <div class="eyebrow" style="color:var(--bg); opacity:0.7;">10-Year Lock</div>
  <h3 style="margin:0; color:var(--bg); font-size:1.5rem; line-height:1.15;">Last secondary palette refresh until 2032 or post-IPO, whichever comes second.</h3>
  <p style="margin:0.6rem 0 0 0; color:var(--bg); opacity:0.85; font-size:0.9rem; line-height:1.5;">ServiceTitan held Titan Blue 8+ years through 700% revenue growth and an IPO without a typography commission. In distributor channels, refresh signals instability — a stable visual identity buys more credibility than any palette move.</p>
</div>

<h2 class="section">Deferred decisions</h2>
<div class="surface-card">
  <h3>Custom typography commission</h3>
  <div class="surface-meta">Trigger: Series C close OR $50M ARR OR platform moment, whichever first.</div>
  <p class="surface-rationale">Procore Sans came 2 years post-IPO, ~9 years after Series C. ServiceTitan still on commodity sans at IPO. Stays Montserrat.</p>
</div>
<div class="surface-card">
  <h3>Full illustration system</h3>
  <div class="surface-meta">Trigger: 2nd brand designer in seat OR international expansion (Sonepar EMEA/LATAM).</div>
  <p class="surface-rationale">Drawing-block header is the single shipped motif now.</p>
</div>
<div class="surface-card">
  <h3>Motion language doc</h3>
  <div class="surface-meta">Trigger: first marketing video &gt; 30s OR first interactive product tour OR brand designer hire #2.</div>
  <p class="surface-rationale">Static brand artifacts only now.</p>
</div>
"""
    return page_chrome(model, "Co-brand Rules", body, "co-brand.html")


# ─── Main ─────────────────────────────────────────────────────────────────

def main() -> int:
    if not YAML_PATH.exists():
        print(f"ERROR: design-model.yaml not found at {YAML_PATH}", file=sys.stderr)
        return 1

    with YAML_PATH.open() as f:
        model = yaml.safe_load(f)

    OUT_DIR.mkdir(exist_ok=True)

    pages = {
        "index.html": build_index,
        "color.html": build_color,
        "logo.html": build_logo,
        "typography.html": build_typography,
        "co-brand.html": build_cobrand,
    }

    for filename, builder in pages.items():
        html = builder(model)
        out_path = OUT_DIR / filename
        out_path.write_text(html)
        print(f"  ✓ {filename} ({len(html):,} bytes)")

    print(f"\nGenerated {len(pages)} pages → {OUT_DIR}")
    print(f"Open: file://{OUT_DIR}/index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
