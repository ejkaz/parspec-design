---
name: parspec-pptx
description: "Generate Parspec-branded editable .pptx decks via python-pptx, reading the design-model.yaml SSoT. Two registers: (1) house — builds on a company deck used as a template (logo, footer, page numbers, layout backgrounds; 10in canvas). Profiles: master (default; the Sept-2026 master deck — black + warm glow, ALL-CAPS titles with an orange phrase, numbered cards, panel rows, problem→solution rows, umber funnels, CAD brackets) and townhall (Q2-26 town hall — left-bar cards, KPI tiles, chevrons, section strips). (2) brand_artifacts — 13.333in canvas, drawn chrome, L1–L12 for standalone board memos. Headless LibreOffice render + PNG verify loop (PowerPoint optional). Use when the deliverable must open or be edited in PowerPoint, Keynote or Google Slides — all-hands / town hall sections, CEO and fundraising updates, sales decks, board decks. Triggers: 'parspec pptx', 'parspec powerpoint', 'board deck for parspec', 'town hall slides', 'all-hands deck', 'use our new deck format', '/parspec-pptx', 'editable pptx with parspec brand'."
version: 0.3.0
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion]
---

# Parspec PPTX

Generate editable .pptx files with Parspec brand applied. Sibling to `parspec-slides` (HTML decks) but for the case where the recipient needs to open and edit a PowerPoint file natively.

Brand contract: reads `../parspec-design/skills/parspec-design/design-model.yaml`. Every color, font, voice rule comes from there. When the brand evolves, every deck auto-tracks on next build.

## Two registers

| Register | Canvas | Chrome | Use for | Entry point |
|---|---|---|---|---|
| **house** | 10 × 5.625 in (Google Slides default) | A company deck's own master: PARSPEC logo, confidentiality footer, page numbers, layout backgrounds | Anything internal or that sits next to company slides: all-hands sections, CEO / fundraising updates, sales decks | `assets/house.py` `HouseDeck(profile=…)` + `assets/shapes.py` · recipes in `references/house-layouts.md` |
| **brand_artifacts** | 13.333 × 7.5 in | Drawn: corner brackets, footer label | Standalone board memos, IC decks, customer attachments | `assets/builder.py` · recipes in `references/layouts.md` |

### House profiles

| Profile | Source deck | Look | Default |
|---|---|---|---|
| **master** | Sept-2026 company master deck ("Parspec Overview") | Pure black with a warm glow, ALL-CAPS 25 pt light titles with a trailing orange phrase, no eyebrow; numbered cards with orange top bars, translucent panel rows, problem → solution rows, umber layer fills, CAD corner brackets | **yes** — the current company format |
| **townhall** | Q2-26 town hall | #0F0F0F, bold mixed-case titles with an eyebrow, left-accent-bar cards, KPI tiles, chevrons, numbered section strips | legacy; use when adding to a town hall built on that master |

When the user points at a newer company deck ("use our updated formatting"), regenerate that profile's template from it first. If its layouts differ, add a profile to `PROFILES` in `assets/house.py` rather than hard-coding a one-off deck. Every color still comes from design-model.yaml roles; the umber ramp (v2.2.0) was added for the master profile's layer fills.

### House templates (company-internal — never commit them)

A template is a company deck export with its slides and every other master stripped. Templates are proprietary and this repo is public (`*.pptx` is gitignored), so they live only on the machine:

```bash
python3 scripts/make_template.py --profile master   "<master deck export>.pptx"
python3 scripts/make_template.py --profile townhall "Parspec Townhall - <quarter>.pptx"
# -> ~/Documents/Claude/Templates/parspec_{master,townhall}_template.pptx
#    overrides: $PARSPEC_PPTX_MASTER_TEMPLATE / $PARSPEC_PPTX_TEMPLATE
```

The script auto-picks the master that carries every layout the profile needs and fails loudly if they were renamed. Master-profile layouts: `TITLE_ONLY_1_1` cover, `CUSTOM_5` divider (glow corners), `CUSTOM_6_2` content (full glow), `CUSTOM_2` plain black.

Template gotchas (handled by `HouseDeck`; listed so ad-hoc code doesn't relearn them):
- Both masters' `DEFAULT` layout is **white**; the master deck's `BLANK` layout draws a second footer on top of the master's. Don't build on either.
- `add_slide` never copies the slide-number field, and the master deck's glow layouts have none. `HouseDeck.slide()` copies it from the layout or, failing that, from the master.
- Setting only `.top` on an inheriting placeholder writes `left=0`. Use `HouseDeck.place()`, which writes all four values.
- Town hall cover/divider body placeholders indent text ~0.15 in; `cover()` compensates.
- Master covers draw the logo from the master footer's full-resolution wordmark (`HouseDeck.logo()`), so no logo file is needed.
- Master-deck text uses Montserrat Light / Medium / SemiBold. Install those weights (`~/Library/Fonts`) or soffice previews substitute.

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

Style is locked by design-model.yaml; the only choices are the register and the house profile (tables above). If the user points at existing company decks for "inspiration", that means the house register: find the newest company deck, render it to a contact sheet, and regenerate or add the matching profile before building. Confirm in one sentence.

### Phase 3 — Generate

Sequential (single-agent) by default.

**house register:**

1. Copy `scripts/house_example.py` next to the deliverable (it exercises every recipe; `--profile master|townhall`)
2. Read `references/house-layouts.md`; pick a recipe per slide
3. `HouseDeck(profile).cover() / .agenda() / .divider() / .content()` give each slide its chrome; compose bodies with `assets.shapes` inside the content band (`deck.top` → `deck.bottom`, left edge `deck.x0`, width `deck.xw`)
4. Put sources and `[CONFIRM]` flags in speaker notes (`deck.notes(slide, ...)`), and unknowns on-slide as `deck.placeholder("[Round size]")`
5. Import path: set `PARSPEC_PPTX_SKILL`, or resolve the newest `~/.claude/plugins/cache/parspec-design/parspec-pptx/*/skills/parspec-pptx` that has `assets/house.py`

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
| `assets/shapes.py` | Canvas-agnostic composition + diagram primitives on the role-based `Palette`: `text`, `shape` (alpha), `rule`, `card`, `kpi_tile`, `chip_row`, `funnel` (alpha / umber), `process`, `question_cards`, `evidence_rows`, `section_strip`, `arcs`, and master-format `tile_row`, `numbered_cards`, `panel_rows`, `problem_solution`, `bracket_box`, `crosshair` |
| `assets/house.py` | `HouseDeck(profile)` + `PROFILES` — opens a local house template; `cover`, `agenda`, `divider`, `content`, `title`, `eyebrow`, `logo`, `notes`, `placeholder` |
| `assets/townhall.py` | Back-compat `TownHall` = `HouseDeck("townhall")` |
| `assets/__init__.py` | One-line package import surface |
| `references/layouts.md` | brand_artifacts recipes L1–L12 |
| `references/house-layouts.md` | house recipes: shared chrome, master M1–M8, townhall T1–T8 |
| `scripts/init_deck.py` | brand_artifacts starter — copy and edit |
| `scripts/house_example.py` | house starter + smoke test, both profiles (sample content only) |
| `scripts/make_template.py` | Company deck export → local template for a profile (slides and extra masters stripped) |
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
