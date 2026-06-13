---
name: parspec-pptx
description: "Generate Parspec-branded board-ready .pptx decks via python-pptx. Reads the same design-model.yaml SSoT as parspec-slides (brand_artifacts dark mode by default). Eight validated layouts (cover, section-with-thesis, three-claims, two-card dyad, section divider, two-column vectors, shapes + claims, before/after table). Includes a macOS PowerPoint render daemon (open-keep-alive) and render.sh wrapper for fast iterate-and-verify with PNG previews. Use when the deliverable must open natively in PowerPoint or Keynote — board decks, IC memos, sales-conference handouts, customer-pdf-source decks. Triggers: 'parspec pptx', 'parspec powerpoint', 'board deck for parspec', '/parspec-pptx', 'make a parspec board deck', 'editable pptx with parspec brand'."
version: 0.1.0
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion]
---

# Parspec PPTX

Generate editable .pptx files with Parspec brand applied. Sibling to `parspec-slides` (HTML decks) but for the case where the recipient needs to open and edit a PowerPoint file natively.

Brand contract: reads `../parspec-design/skills/parspec-design/design-model.yaml`. Every color, font, voice rule comes from there. When the brand evolves, every deck auto-tracks on next build.

## When to use this vs. parspec-slides

| If the user needs… | Use |
|---|---|
| Web-shareable deck, deploys to Vercel, infinite-scroll viewport | parspec-slides |
| File the board / customer / lawyer opens in PowerPoint or Keynote | **parspec-pptx** |
| Slides someone will edit content inside (not just view) | **parspec-pptx** |
| Email attachment for a hesitant-recipient context | **parspec-pptx** |
| Internal townhall, conference projector | either; default to parspec-slides |

When in doubt, ask. If the user mentions "editable", "board memo", "send to legal", "for the deck deck", "they'll want to make changes" — that's .pptx territory.

## Locked invariants (from design-model.yaml)

`parspec-craft` enforces these — this skill must produce output that passes.

1. **CTA monopoly** — Brand Orange `#FFA72B` is only used as primary CTA / accent type on dark / signature highlights. Never decorative, never for warnings.
2. **Red markup monopoly** — Engineering Red only in error/markup roles.
3. **Warn ≠ brand** — `roles.warn` resolves to Caution Amber `#B45309`, never Brand Orange.
4. **Orange-type-on-light forbidden** — Brand Orange fails AA on Off-white (1.73:1). Use `brand.800 #8C5800` for accent type on light.
5. **Paper-warm panel only** — `surface_paper #FAF7F0` only as an inset panel inside dark slides. Never as a slide background.
6. **Steel = doc register** — `steel.500 #205991` only in info / link / doc-metadata roles.
7. **Montserrat single family** — never Inter, Roboto, system-ui.
8. **Density limits** — see table below.

### Content density per slide

| Slide type | Maximum |
|---|---|
| Title | 1 heading + 1 subtitle + optional eyebrow |
| Content | 1 heading + 4–6 bullets OR 1 heading + 2 paragraphs |
| Feature grid | 1 heading + 6 cards max (2×3 or 3×2) |
| Quote | 1 quote (max 3 lines) + attribution |
| Image | 1 heading + 1 image (max 60% of slide height) |
| Metric | 1 heading + up to 3 large stats |

Overflow signals bad layout, not bad content. **Split, never cram.**

## Voice (from design-model.yaml `voice.*`)

**Do**: lead with metrics; ALL CAPS section headers; name customers (Sonepar, Graybar, Rexel, Wesco, Border States); MEP industry vocabulary (quoting, submittals, O&M, ERP); be terse.

**Avoid**: consumer-SaaS hype (`delight`, `magic`, `effortless`); generic startup verbs (`unlock`, `empower`, `transform`); wellness adjectives; emoji; lorem ipsum.

## Workflow

### Phase 0 — Detect mode

- **Mode A: New .pptx deck** (default) — Phase 1
- **Mode B: PPT enhancement** — read existing .pptx via python-pptx, lift content, re-emit through this skill's layouts

If user says "edit this deck" or "fix slide N", clarify whether they want the existing file edited in place (use python-pptx directly) or rebuilt through the skill (Mode B).

### Phase 1 — Brand load + content discovery

1. `from assets import load; b = load()` — gives a fully-resolved `Brand` object
2. Ask the user one `AskUserQuestion` to confirm:
   - Purpose (board / sales / IC memo / townhall)
   - Audience (board / CEO / customers / Series B investors / etc.)
   - Length (default ≤ 8 slides — keep board decks short)
   - Content readiness (do they have a slide-by-slide outline? or are we drafting from a brief?)
3. If user has provided a slide-by-slide spec, skip ahead to Phase 3. If not, draft 3–6 slide concepts in 1–2 sentences each and confirm.

### Phase 2 — Style is locked

Default brand_artifacts mode (dark). Skip style discovery; confirm in one sentence.

### Phase 3 — Generate

Sequential (single-agent) by default. Steps:

1. Copy `scripts/init_deck.py` to a working location (e.g. `/tmp/<deckname>.py` or alongside the deliverable)
2. Read `references/layouts.md` and pick layouts per slide
3. Each slide is ≈ 30–80 lines of straight composition — copy the layout recipe whole, replace strings
4. Run `python3 /tmp/<deckname>.py` to produce the .pptx
5. Save final to user's requested path (often `~/Documents/Claude/Projects/Board Materials/` or similar)

### Phase 4 — Render + verify

Critical step. Office's font substitution differs from Keynote's — slides that look fine in Keynote can overflow in PowerPoint.

```bash
bash /path/to/parspec-pptx/skills/parspec-pptx/scripts/render.sh /path/to/deck.pptx
```

Produces:
- `<deck>.pdf` (PowerPoint's native PDF export — exact what the board sees)
- `<deck>-N.png` per slide at 110 DPI

Read the PNGs (use the Read tool — they're rendered images). Verify:

- No text overflows its container (especially with PowerPoint's wider font fallback)
- No text overlaps page-indicators, corner brackets, or other slides' content
- Card heights accommodate the actual text — assume wider font in PowerPoint than your Python script imagines
- CTA monopoly preserved (no decorative orange)
- Density limits not exceeded

If you find issues, fix the Python source and re-run. The keep-alive daemon makes each render ~3s instead of 8s+ cold start.

### Phase 5 — Delivery

`SendUserFile` the .pptx plus PNG previews. Caption with:

- File path
- Brand version (e.g. `v2.0.0 / brand-2026-Q3-v1`)
- Slide count
- Render verification status (which slides you visually confirmed)
- Any font caveats (Montserrat install status)

### Phase 6 — Optional lint

```
parspec-craft lint <generated.pptx>
```

(Requires parspec-craft to support .pptx — currently HTML-only; this is roadmap.)

## File map

| File | Purpose |
|---|---|
| `assets/brand.py` | Loads `design-model.yaml`, resolves `{ref.path}` tokens, exposes `Brand.cta`, `Brand.surface_paper`, etc. as `RGBColor` |
| `assets/builder.py` | Low-level helpers: `new_deck`, `blank`, `add_text`, `add_rect`, `add_line`, `corner_brackets`, `footer`, motif accents |
| `assets/__init__.py` | One-line package import surface |
| `references/layouts.md` | 8 paste-ready layout recipes (L1–L8) with the exact geometry and tokens that work |
| `scripts/init_deck.py` | Starter scaffold for new decks — copy and edit |
| `scripts/render.sh` | Render via daemon → PDF → per-slide PNGs |
| `daemon/ppt_render_daemon.py` | Keep-alive PowerPoint subprocess for fast render cycles |

## Render daemon

Optional but recommended. Started automatically by `render.sh` on first use. Polls `/tmp/parspec-pptx-render/` for `*.req` files; each request is two lines (src .pptx, dst .pdf).

Manual control:
- Start: `python3 daemon/ppt_render_daemon.py &`
- Stop: `kill $(cat /tmp/parspec-pptx-render/daemon.pid)`
- Log: `tail -f /tmp/parspec-pptx-render/daemon.log`

Auto-quits PowerPoint after 30 minutes idle to free memory.

## What this skill does NOT do

- Maintain the brand — that's `parspec-design`
- Generate HTML slides — that's `parspec-slides`
- Lint output — that's `parspec-craft` (.pptx support is roadmap)
- Convert HTML → .pptx (parspec-slides' Phase 4 does .pptx → HTML, not the reverse)
- Run on Windows / Linux (the render daemon is macOS + Microsoft PowerPoint specific)
