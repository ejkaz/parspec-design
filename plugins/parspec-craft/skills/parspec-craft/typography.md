# Typography — Parspec Edition

Single family. One ladder. Locked.

## The rule

**Montserrat. Only.** No other font appears anywhere in any Parspec output:

- No `Inter` / `Roboto` / `Arial` / `system-ui` / `Helvetica` / `SF Pro` / `Open Sans` / `Lato`.
- No serif pairing for display.
- No mono pairing — Parspec brand has no monospace token.
- No custom typography commission — Montserrat is the choice.

severity: `error` for any non-Montserrat declaration in display, body, or eyebrow.

## Weight ladder

| Weight | Use | Example role |
|---|---|---|
| 400 | Regular body | Paragraph text |
| 500 | Medium body | Captions, secondary text |
| 600 | Semibold | Eyebrow tags (with caps + tracking) |
| 700 | Bold | h2, h3 |
| 800 | Extrabold | h1, display, hero numbers |
| 900 | Black | (rare) — oversized hero stats |

Weight + size + tracking carry the hierarchy. Don't ever swap fonts for hierarchy.

## Type scale (clamp() mandatory)

| Role | Clamp | Line height | Letter spacing |
|---|---|---|---|
| Display | `clamp(2rem, 5.5vw, 5rem)` | 1.05 | -0.02em |
| h1 | `clamp(1.75rem, 4.5vw, 4rem)` | 1.05 | -0.015em |
| h2 | `clamp(1.25rem, 3vw, 2.5rem)` | 1.10 | -0.01em |
| h3 | `clamp(1rem, 2vw, 1.5rem)` | 1.15 | 0 |
| Body | `clamp(0.85rem, 1.4vw, 1.15rem)` | 1.5 | 0 |
| Small | `clamp(0.7rem, 1vw, 0.9rem)` | 1.4 | 0 |
| Eyebrow | `clamp(0.65rem, 0.85vw, 0.8rem)` | 1.2 | 0.18em (uppercase) |

Source values live in `design-model.yaml` under `tokens.typography.*`. parspec-slides reads from there; parspec-craft enforces against it.

severity: `error` for any fixed `px` or `rem` font-size at a leaf rule (not in `:root`).

## Hierarchy invariants

- **No more than 3 type sizes per slide** — display + body + eyebrow is the canonical pairing.
- **All-caps section headers are a Parspec idiom** — keep them. Pair with letter-spacing 0.18–0.22em.
- **Body line-length 65–75 ch** — wider than that is hard to read; narrower fragments. parspec-slides templates default to `max-width: 70ch` for prose blocks.

## Loading

- Self-host or use Google Fonts: `https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap`.
- `display: swap` is required so first paint isn't blocked.
- For PDF export (parspec-slides `scripts/export-pdf.sh`), the local HTTP server resolves Google Fonts during the Playwright render — no offline fallback needed.

## Reduced-motion accessibility

Every Parspec output must include:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.2s !important;
  }
  html { scroll-behavior: auto; }
}
```

severity: `error` if missing in any output that contains `animation` or `transition` declarations.

## Anti-patterns (parspec-craft flags these)

| Pattern | Severity | Why |
|---|---|---|
| `font-family: Inter` (display) | error | Generic AI-default. Montserrat is locked. |
| `font-family: Roboto` (display) | error | Same. |
| `font-family: 'Arial'` (display) | error | System default. Use Montserrat. |
| `font-family: system-ui` | error | Inherits OS — non-deterministic. Use Montserrat. |
| Multiple display fonts on the same surface | error | Violates single-family discipline. |
| Fixed `px` font-size in a leaf rule | error | Violates clamp() invariant. |
| All-italic body copy | warning | Reduces readability; Parspec brand uses upright Montserrat. |
| Display sizes < 24px | warning | Display loses heading impact below this. |
