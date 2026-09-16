---
name: parspec-pptx
description: "Generate Parspec-branded editable .pptx decks via python-pptx, reading the design-model.yaml SSoT. Two registers: (1) brand_artifacts — 13.333in canvas, corner brackets, 12 layouts (L1–L12) for board memos and IC decks; (2) townhall — builds on the company's own town hall Google Slides template (logo, footer, page numbers; 10in canvas) with a diagram library: KPI tiles, funnels, process chevrons, question cards, question-to-evidence rows, numbered section strips, the triple-arc motif. Headless LibreOffice render + PNG verify loop (PowerPoint daemon optional). Use when the deliverable must open or be edited natively in PowerPoint, Keynote or Google Slides — board decks, all-hands / town hall sections, CEO updates, IC memos. Triggers: 'parspec pptx', 'parspec powerpoint', 'board deck for parspec', 'town hall slides', 'all-hands deck', '/parspec-pptx', 'editable pptx with parspec brand'."
version: 0.3.0
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion]
---

# Parspec PPTX

Generate editable .pptx files with Parspec brand applied. Sibling to `parspec-slides` (HTML decks) but for the case where the recipient needs to open and edit a PowerPoint file natively.

Brand contract: reads `../parspec-design/skills/parspec-design/design-model.yaml`. Every color, font, voice rule comes from there. When the brand evolves, every deck auto-tracks on next build.

## Two registers

| Register | Canvas | Chrome | Use for | Entry point |
|---|---|---|---|---|
| **townhall** | 10 × 5.625 in (Google Slides default) | The company's own town hall master: PARSPEC logo, confidentiality footer, page numbers | All-hands / town hall sections, CEO updates, anything that gets pasted into the company Google Slides deck or edited there | `assets/townhall.py` `TownHall` + `assets/shapes.py` · recipes in `references/townhall-layouts.md` |
| **brand_artifacts** | 13.333 × 7.5 in | Drawn: corner brackets, footer label | Board memos, IC decks, customer attachments that stand alone | `assets/builder.py` · recipes in `references/layouts.md` |

Default to **townhall** when the deck is internal or will live next to existing company slides — it matches what people already see. Both registers take every color from design-model.yaml roles.

### The town hall template (company-internal — never commit it)

The template is the latest town hall export with its slides and extra masters stripped. It is proprietary and this repo is public, so it lives only on the machine:

```bash
# export the latest town hall from Google Slides as .pptx, then:
python3 scripts/make_template.py "Parspec Townhall - <quarter>.pptx"
# -> ~/Documents/Claude/Templates/parspec_townhall_template.pptx  (override: $PARSPEC_PPTX_TEMPLATE)
```

Re-run it after each town hall so decks track the current chrome. The script auto-picks the master that has every layout in `townhall.LAYOUTS` and fails loudly if Google renamed them.

Template gotchas (already handled by `TownHall`, listed so ad-hoc code doesn't relearn them):
- The master's `DEFAULT` layout is **white**. Use `blank` (`CUSTOM_2`) for a dark footer-only slide.
- `add_slide` never copies the slide-number field; `TownHall.slide()` re-adds it.
- Setting only `.top` on an inheriting placeholder writes `left=0`. Use `TownHall.place()`, which writes all four values.
- The cover/divider body placeholders indent their text ~0.15 in; `cover()` compensates so subtitles align with the title.

## When to use this vs. parspec-slides

| If the user needs… | Use |
|---|---|
| Web-shareable deck, deploys to Vercel, infinite-scroll viewport | parspec-slides |
| File the board / customer / lawyer opens in PowerPoint or Keynote | **parspec-pptx** |
| Slides someone will edit content inside (not just view) | **parspec-pptx** |
| Email attachment for a hesitant-recipient context | **parspec-pptx** |
| Town hall / all-hands section, or slides that paste into the company deck | **parspec-pptx, townhall register** |
| Conference projector, web link | parspec-slides |

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

## Composition principles

Borrowed from Anthropic's `frontend-design` skill where they don't collide with the brand. **Precedence: design-model.yaml wins** on color, type and motifs (frontend-design would pick a new typeface and calls "near-black + one bright accent" a tell — that *is* the locked Parspec axis). frontend-design governs everything else:

- One idea per slide; the subtitle states the takeaway in one sentence ("so-what line").
- Numbered markers (01/02/03) only for real sequences: agendas, processes, section strips. Parallel ideas get accent bars, not numbers.
- Structure encodes information: orange bar = the point, grey bar = the counterpoint or question, no bar = supporting chips.
- One accent phrase per title at most (town hall house style), never a single emphasized word mid-sentence.
- Unknowns are visible placeholders (`[Round size]`), never invented numbers; every figure has a source in the notes.

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

### Phase 2 — Pick the register

Style is locked by design-model.yaml; the only choice is the register (table above). If the user points at existing company decks for "inspiration", that means townhall — regenerate the template from the newest export first. Confirm in one sentence.

### Phase 3 — Generate

Sequential (single-agent) by default.

**townhall register:**

1. Copy `scripts/townhall_example.py` next to the deliverable (it exercises every recipe)
2. Read `references/townhall-layouts.md`; pick a recipe per slide (T1–T11)
3. `TownHall().cover() / .agenda() / .divider() / .content()` give each slide its chrome; compose bodies with `assets.shapes` inside the content band (`TOP`=1.42 to `BOTTOM`=4.95 in)
4. Put sources and `[CONFIRM]` flags in speaker notes (`th.notes(slide, ...)`), and unknowns on-slide as `th.placeholder("[Round size]")`
5. Import path: set `PARSPEC_PPTX_SKILL`, or resolve the newest `~/.claude/plugins/cache/parspec-design/parspec-pptx/*/skills/parspec-pptx` (see the example's header)

**brand_artifacts register:**

1. Copy `scripts/init_deck.py` to a working location (e.g. `/tmp/<deckname>.py` or alongside the deliverable)
2. Read `references/layouts.md` and pick layouts per slide
3. Each slide is ≈ 30–80 lines of straight composition — copy the layout recipe whole, replace strings
4. Run `python3 /tmp/<deckname>.py` to produce the .pptx
5. Save final to user's requested path (often `~/Documents/Claude/Projects/Board Materials/` or similar)

### Phase 4 — Render + verify

Critical step. Office's font substitution differs from Keynote's — slides that look fine in Keynote can overflow in PowerPoint.

```bash
bash /path/to/parspec-pptx/skills/parspec-pptx/scripts/render.sh /path/to/deck.pptx [out_dir] [dpi]
```

Engines (`PPTX_ENGINE`):
- `soffice` (default) — headless LibreOffice. Reliable in agent sessions. Needs Montserrat installed (`~/Library/Fonts`) or it substitutes a wider font; the script warns.
- `daemon` / `PPTX_DIRECT=1` — Microsoft PowerPoint via AppleScript, the exact PDF PowerPoint would export. AppleScript `open` can hang in agent sessions; use it only for a final fidelity check.

Produces `<deck>.pdf` and `<deck>-N.png` per slide (110 DPI default). Stitch the PNGs into a contact sheet to review the whole deck at once.

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
- Brand version (e.g. `v2.1.0 / brand-2026-Q3-v1`) and register
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
| `assets/shapes.py` | Canvas-agnostic composition + diagram primitives and the role-based `Palette`: `text`, `shape` (alpha), `card`, `kpi_tile`, `chip_row`, `funnel`, `process`, `question_cards`, `evidence_rows`, `section_strip`, `arcs` |
| `assets/townhall.py` | `TownHall` — opens the local town hall template; `cover`, `agenda`, `divider`, `content`, `eyebrow`, `title`, `notes`, `placeholder` |
| `assets/__init__.py` | One-line package import surface |
| `references/layouts.md` | brand_artifacts recipes L1–L12 |
| `references/townhall-layouts.md` | townhall recipes T1–T11 |
| `scripts/init_deck.py` | brand_artifacts starter — copy and edit |
| `scripts/townhall_example.py` | townhall starter + smoke test (sample content only) |
| `scripts/make_template.py` | Town hall export → local template (slides and extra masters stripped) |
| `scripts/render.sh` | .pptx → PDF → per-slide PNGs (soffice default; PowerPoint optional) |
| `daemon/ppt_render_daemon.py` | Keep-alive PowerPoint subprocess for fast render cycles |

## Render daemon (PowerPoint engine only)

Optional; `PPTX_ENGINE=daemon`. Started automatically by `render.sh` on first use. Polls `/tmp/parspec-pptx-render/` for `*.req` files; each request is two lines (src .pptx, dst .pdf).

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
- Ship the company town hall template — it stays local (see above)
- Run the PowerPoint engines off macOS (the soffice engine is portable)
