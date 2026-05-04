# Color — Parspec Edition

Universal color discipline. Palette-specific tokens (current secondaries, current tints) live in `design-model.yaml` and are loaded at runtime. This file holds rules that apply regardless of brand version.

## Locked primary axis (never violate)

| Role | Token | Hex | Notes |
|---|---|---|---|
| Default background | parspec-black | `#0F0F0F` | Dark surfaces dominate |
| Layering surface | charcoal | `#2E2E2E` | Card backgrounds, secondary panels |
| Document surface | off-white | `#F2F2F2` | Long-form text, document layouts |
| Text on dark | white | `#FFFFFF` | Body and headings on dark |
| Brand color / CTA | brand-orange | `#FFA72B` | **Primary CTA monopoly** |

Any output must include `parspec-black`, `brand-orange`, and Montserrat to be recognizable as Parspec. parspec-craft enforces this when relevant chrome (CTAs, body text, dark surfaces) is present.

## Universal color rules

### Contrast (severity: error)

- **WCAG AA body text**: ≥ 4.5:1 contrast against background.
- **Graphical elements** (chart bars, donut slices, icon glyphs, status badges): ≥ 3:1 contrast against the surface they sit on.
- **Brand-orange on parspec-black**: 8.0:1 — passes.
- **Off-white text on parspec-black**: 17.0:1 — passes.

### Charts on dark (severity: error)

When chart bars or donut slices sit on a dark slide background:

- Add 1px inset highlight outline (`box-shadow: inset 0 0 0 1px rgba(255,255,255,0.2)`) to give every fill a visible boundary regardless of color.
- Bar tracks use ≥ 18% white (rgba) so dark fills have contrast against the unfilled portion.
- Avoid placing two adjacent dark slices in a donut without a separator stroke.

### Charts on light (severity: error)

When charts sit on light surfaces (off-white, paper-warm, cream):

- Add 1px inset dark outline (`rgba(15,41,66,0.18)`) for fill boundary.
- Avoid yellow / pastel fills on cream — contrast collapses.

### Brand Orange discipline (severity: error)

- Brand Orange `#FFA72B` is the **only** primary CTA color across every Parspec surface.
- A secondary action or a ghost button may use a non-orange color.
- Brand Orange used 6+ times per screen erodes its action-signal value. Cap at 2 visible uses per fold.

### Customer logos (severity: warning)

- Always grayscale, never colored. Reduces visual noise in social-proof rows. The brand-orange CTA stays the eye-anchor.

### Pastel rules (severity: warning, becomes error if marked in design-model.yaml `avoid`)

- No `#FFE___` peach / rose family.
- No `#E2E2FF` / `#C7C7FF` lavender / soft violet.
- No `#C6E1DA` mint / soft pastel green.
- 0 of 27 ICP brands surveyed use these — they are out-of-register for industrial.

### Consumer purple family (severity: error)

- Forbidden hex range: `#6366F1`, `#4F46E5`, `#4338CA`, `#3730A3`, `#8B5CF6`, `#7C3AED`, `#A855F7`, `#6270F2`. The Tailwind-indigo / Linear / Notion register.
- Trust-gradient atmospherics (purple → blue, indigo → pink) are forbidden categorically.

### Token references (severity: warning)

- Hex values should live in `:root` / CSS variables, not inlined repeatedly. Reference `design-model.yaml` semantic tokens via `var(--...)`.
- More than 12 raw hex literals outside `:root` indicates tokens were not honored.

## Reference: ICP visual register

What construction-materials-distributor buyers see daily (good color register):

| Family | Examples | Notes |
|---|---|---|
| Deep navy | Sonepar `#0033A0`, Bluebeam `#0083DB`, Wesco `#004684` | 60% of ICP brands |
| Saturated industrial orange / red | Procore `#FF5200`, Cummins `#DA291C`, Milwaukee `#C92A28` | Always warm/rust, never rose |
| Black / near-black | Cat, Stanley, Deere, Procore | Co-primary, not a tint |
| Earthy / saturated green | Deere `#367C2B`, Wesco green | Forest register, never mint |
| Hi-vis yellow | CAT, Stanley, Autodesk Hello Yellow | Bright safety yellow, never buttery |

What is unrepresented in this world (avoid):
- Pastels (lavender, peach, rose, soft violet, mint)
- Consumer purple (`#6366F1` family)
- Iridescent / mesh gradients
- Fashion / lifestyle pinks (`#BE123C` Deep Rose register)
