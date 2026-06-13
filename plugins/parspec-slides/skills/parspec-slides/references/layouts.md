# Parspec Slide Layouts (battle-tested 2026-05-04)

Paste-ready `<section class="slide">` blocks. Each respects density limits and uses `var(--...)` references that resolve from the populated `:root` block.

## Universal pattern — READ FIRST

Every slide is a vertical-flex 3-zone composition:

```
┌─ .slide-header (or .section-bar / .drawing-block)  ← top chrome (fixed height)
│
├─ .slide-content / .title-content / .end-content    ← MIDDLE (flex: 1, fills canvas)
│   └─ all main content goes here — never as direct .slide children
│
└─ .slide-footer                                      ← bottom chrome (fixed height, margin-top: auto)
```

**The middle wrapper is non-negotiable.** Without it, content stacks at the top with empty bottom — the slide looks half-built. The wrapper has `flex: 1; display: flex; flex-direction: column; justify-content: center;` so content distributes properly.

For content slides → `.slide-content`. For L1 covers/dividers → `.title-content` (left-aligned hero). For L8 closers → `.end-content`.

Copy the layout you need; fill in content; never inline-style anything that should come from a token.

---

## L1 — Title slide / section divider

```html
<section class="slide title-slide">
    <div class="bracket-tl"></div>
    <div class="bracket-tr"></div>
    <div class="bracket-bl"></div>
    <div class="bracket-br"></div>

    <div class="slide-header">
        <div>PARSPEC · INTERNAL</div>
        <div>YYYY-MM-DD</div>
    </div>

    <div class="title-content">
        <div class="eyebrow brand-orange">{{SECTION EYEBROW · TRACKED CAPS}}</div>
        <h1>{{Heading line one.}}<br><span class="brand-orange">{{Heading line two.}}</span></h1>
        <p class="lead">{{One-sentence subtitle, ≤ 90 chars.}}</p>
    </div>

    <div class="slide-footer">
        <div>For: {{audience}}</div>
        <div>From: {{author}}</div>
    </div>
</section>
```

**Use for**: deck cover, section dividers.
**Density**: 1 heading + 1 subtitle + 1 eyebrow.

---

## L2 — Metric slide (3 stats)

```html
<section class="slide">
    <div class="bracket-tl"></div>
    <div class="bracket-br"></div>

    <div class="section-bar">
        <span class="num">0X</span>
        <span class="label">{{Section name}}</span>
    </div>

    <div class="slide-content">
        <h2>{{Headline ≤ 50 chars.}}</h2>

        <div class="stat-row">
            <div class="stat">
                <div class="stat-num brand-orange">$XX.XB</div>
                <div class="stat-label">{{Label one.}}</div>
            </div>
            <div class="stat">
                <div class="stat-num">XXX+</div>
                <div class="stat-label">{{Label two.}}</div>
            </div>
            <div class="stat">
                <div class="stat-num">XX%</div>
                <div class="stat-label">{{Label three.}}</div>
            </div>
        </div>
    </div>

    <div class="slide-footer">
        <div>SECTION 0X · {{TITLE}}</div>
        <div>NN / NN</div>
    </div>
</section>
```

**Use for**: KPI dashboards, board metrics, customer-impact moments.
**Density**: 1 heading + 3 stats max. One stat in `--brand-orange` for emphasis (never two).

---

## L3 — Content / bullets slide

```html
<section class="slide">
    <div class="bracket-tl"></div>
    <div class="bracket-br"></div>

    <div class="section-bar">
        <span class="num">0X</span>
        <span class="label">{{Section name}}</span>
    </div>

    <div class="slide-content">
        <h2>{{Headline ≤ 50 chars.}}</h2>

        <ul class="checklist">
            <li>{{Bullet one — concrete, terse, no hedging.}}</li>
            <li>{{Bullet two.}}</li>
            <li>{{Bullet three.}}</li>
            <li>{{Bullet four.}}</li>
            <li>{{Bullet five — optional.}}</li>
            <li>{{Bullet six — optional.}}</li>
        </ul>
    </div>

    <div class="slide-footer">
        <div>SECTION 0X · {{TITLE}}</div>
        <div>NN / NN</div>
    </div>
</section>
```

**Use for**: takeaways, action items, talking-points slides.
**Density**: 1 heading + 4–6 bullets MAX. Overflow → split into two slides.

---

## L4 — Two-column comparison

```html
<section class="slide">
    <div class="bracket-tl"></div>
    <div class="bracket-br"></div>

    <div class="section-bar">
        <span class="num">0X</span>
        <span class="label">{{Section name}}</span>
    </div>

    <div class="slide-content">
        <h2>{{Headline}}</h2>

        <div class="cols-2">
            <div class="col">
                <div class="eyebrow brand-orange">{{LEFT TITLE}}</div>
                <ul class="checklist">
                    <li>{{Point one.}}</li>
                    <li>{{Point two.}}</li>
                    <li>{{Point three.}}</li>
                </ul>
            </div>
            <div class="col">
                <div class="eyebrow brand-orange">{{RIGHT TITLE}}</div>
                <ul class="checklist">
                    <li>{{Point one.}}</li>
                    <li>{{Point two.}}</li>
                    <li>{{Point three.}}</li>
                </ul>
            </div>
        </div>
    </div>

    <div class="slide-footer">
        <div>SECTION 0X · {{TITLE}}</div>
        <div>NN / NN</div>
    </div>
</section>
```

**Use for**: before/after, current/proposed, problem/solution comparisons.
**Density**: 1 heading + 2 columns × 3–4 bullets each.

---

## L5 — Customer quote / testimonial

```html
<section class="slide quote-slide">
    <div class="bracket-tl"></div>
    <div class="bracket-br"></div>

    <div class="section-bar">
        <span class="num">0X</span>
        <span class="label">Customer Voice</span>
    </div>

    <div class="slide-content">
        <blockquote class="quote">
            <p>"{{Quote ≤ 3 lines, real customer words, no embellishment.}}"</p>
            <footer class="attribution">
                <strong>{{Name}}</strong>
                <span>{{Title, Company}}</span>
            </footer>
        </blockquote>
    </div>

    <div class="slide-footer">
        <div>SECTION 0X · CUSTOMER VOICE</div>
        <div>NN / NN</div>
    </div>
</section>
```

**Use for**: customer social proof, board-deck testimonials, sales-call openers.
**Density**: 1 quote (max 3 lines) + 1 attribution.

---

## L6 — Customer logo wall

```html
<section class="slide">
    <div class="bracket-tl"></div>
    <div class="bracket-br"></div>

    <div class="section-bar">
        <span class="num">0X</span>
        <span class="label">Customers</span>
    </div>

    <div class="slide-content">
        <h2>{{Headline — e.g., "Trusted across the top of the distributor pyramid."}}</h2>

        <div class="logo-wall">
            <div class="logo-cell">SONEPAR</div>
            <div class="logo-cell">GRAYBAR</div>
            <div class="logo-cell">REXEL</div>
            <div class="logo-cell">WESCO</div>
            <div class="logo-cell">BORDER STATES</div>
            <div class="logo-cell">CRESCENT</div>
        </div>
    </div>

    <div class="slide-footer">
        <div>SECTION 0X · CUSTOMERS</div>
        <div>NN / NN</div>
    </div>
</section>
```

**Use for**: investor decks, sales decks, partner conversations.
**Density**: 1 heading + 4–8 grayscale logo cells. Always grayscale, never colored.

---

## L7 — Chart slide (bar + donut, side-by-side)

```html
<section class="slide">
    <div class="bracket-tl"></div>
    <div class="bracket-br"></div>

    <div class="section-bar">
        <span class="num">0X</span>
        <span class="label">{{Section name}}</span>
    </div>

    <div class="slide-content">
        <h2>{{Headline — what the data shows.}}</h2>

        <div class="chart-grid">
            <div class="chart-card">
                <div class="chart-title">{{Bar chart title · units}}</div>
                <div class="bar-chart">
                    <div class="bar-row"><div class="bar-label">{{Label}}</div><div class="bar-track"><div class="bar-fill" style="width: 96%;"></div></div><div class="bar-value">XX</div></div>
                    <!-- 4 more bar-row blocks -->
                </div>
            </div>
            <div class="chart-card">
                <div class="chart-title">{{Donut chart title}}</div>
                <div class="donut-row">
                    <div class="donut"></div>
                    <ul class="donut-legend">
                        <li><span></span><span>{{A}}</span><span class="pct">XX%</span></li>
                        <!-- 4 more legend rows -->
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <div class="slide-footer">
        <div>SECTION 0X · {{TITLE}}</div>
        <div>NN / NN</div>
    </div>
</section>
```

**Use for**: KPI breakdowns, regional / segment / product mix views.
**Density**: 1 heading + 1 bar + 1 donut. Brand Orange stays out of chart palette (preserves CTA monopoly). Bar fills get inset highlight for legibility.

---

## L8 — End / thank-you

```html
<section class="slide end-slide">
    <div class="bracket-tl"></div>
    <div class="bracket-tr"></div>
    <div class="bracket-bl"></div>
    <div class="bracket-br"></div>

    <div class="slide-header">
        <div>PARSPEC · INTERNAL</div>
        <div>END</div>
    </div>

    <div class="end-content">
        <div class="eyebrow brand-orange">{{TAG}}</div>
        <h1 class="brand-orange">{{Closing line.}}</h1>
        <p class="end-meta">{{contact / next step / quote}}</p>
        <div><a href="#cta" class="cta-button">{{CTA}}</a></div>
    </div>

    <div class="slide-footer">
        <div>{{Deck title · audience}}</div>
        <div>NN / NN · END</div>
    </div>
</section>
```

**Use for**: deck closer, call to action, signoff.
**Density**: 1 closing heading + 1 line + optional CTA.

---

## Reusable structural CSS (consumed by prelude.css generator)

These classes are referenced across layouts. Include verbatim after viewport-base.css.

```css
/* ─── 3-zone slide composition (fix for empty-canvas bug) ─── */
/* Slide is a flex column. Top chrome stays at top.
   Middle (.slide-content / .title-content / .end-content) has flex:1
   so it FILLS the canvas. Footer has margin-top:auto so it sticks to bottom. */

.slide-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: var(--gap-lg);
    padding: 0 clamp(1.5rem, 4vw, 4rem);
    max-height: 100%;
    overflow: hidden;
}

.title-content,
.end-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: var(--gap-lg);
    padding: 0 clamp(1.5rem, 4vw, 4rem);
    max-height: 100%;
    overflow: hidden;
}

/* Inside .slide-content, individual content blocks should NOT add their own
   horizontal padding (would double up). They inherit padding from the parent. */
.slide-content .stat-row,
.slide-content ul.checklist,
.slide-content .cols-2,
.slide-content .chart-grid,
.slide-content .logo-wall,
.slide-content .quote { padding: 0; }

/* Section bar — never as direct child of .slide; lives at slide root above .slide-content */
.section-bar {
    display: flex; align-items: center; gap: var(--gap-md);
    padding: 0 clamp(1.5rem, 4vw, 4rem);
    margin-top: clamp(2rem, 4vh, 3rem);
    margin-bottom: 0;
}
.section-bar .num { font-family: 'SF Mono', 'JetBrains Mono', ui-monospace, monospace; font-size: var(--small-size); padding: 4px 10px; border: 1px solid currentColor; opacity: 0.7; }
.section-bar .label { font-size: var(--eyebrow-size); letter-spacing: 0.22em; text-transform: uppercase; font-weight: 600; opacity: 0.6; }

/* Slide header / footer */
.slide-header, .slide-footer {
    display: flex; justify-content: space-between; align-items: center;
    font-size: var(--eyebrow-size); letter-spacing: 0.18em; text-transform: uppercase;
    font-weight: 600; opacity: 0.6;
    padding: clamp(1rem, 2.5vw, 2.5rem) clamp(1.5rem, 4vw, 4rem);
}
.slide-header { padding-bottom: 0; }
.slide-footer { margin-top: auto; }

/* Eyebrow */
.eyebrow { font-size: var(--eyebrow-size); letter-spacing: 0.22em; text-transform: uppercase; font-weight: 600; opacity: 0.85; }
.brand-orange { color: var(--brand-orange); }

/* Corner brackets — pushed inward so terminator never touches y=0 */
.bracket-tl, .bracket-tr, .bracket-bl, .bracket-br {
    position: absolute;
    width: clamp(22px, 2.6vw, 42px); height: clamp(22px, 2.6vw, 42px);
    border: 2px solid var(--brand-orange);
    pointer-events: none; z-index: 5;
}
.bracket-tl { top: clamp(1.5rem, 2.6vw, 2.6rem); left:  clamp(1.5rem, 2.6vw, 2.6rem); border-right: 0; border-bottom: 0; }
.bracket-tr { top: clamp(1.5rem, 2.6vw, 2.6rem); right: clamp(1.5rem, 2.6vw, 2.6rem); border-left:  0; border-bottom: 0; }
.bracket-bl { bottom: clamp(1.5rem, 2.6vw, 2.6rem); left:  clamp(1.5rem, 2.6vw, 2.6rem); border-right: 0; border-top:    0; }
.bracket-br { bottom: clamp(1.5rem, 2.6vw, 2.6rem); right: clamp(1.5rem, 2.6vw, 2.6rem); border-left:  0; border-top:    0; }

/* Title / End slide content — wider hero typography */
.title-slide h1 { font-size: clamp(2.5rem, 7vw, 7rem); font-weight: 900; line-height: 1.05; letter-spacing: -0.025em; }
.title-slide .lead { font-size: clamp(1.15rem, 1.8vw, 1.6rem); color: var(--text-dark-secondary); max-width: 60ch; line-height: 1.4; }
.end-slide h1    { font-size: clamp(2.5rem, 7vw, 7rem); font-weight: 900; line-height: 1.05; letter-spacing: -0.025em; }
.end-slide .end-meta { font-size: var(--body-size); color: var(--text-dark-secondary); }

/* Stat row — bigger numbers for slide rendering */
.stat-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--gap-lg); align-items: center; }
.stat-num { font-size: clamp(4rem, 11vw, 9rem); font-weight: 900; line-height: 1; letter-spacing: -0.03em; }
.stat-label { margin-top: var(--gap-sm); font-size: var(--body-size); opacity: 0.85; }

/* Checklist */
ul.checklist { list-style: none; margin: 0; display: flex; flex-direction: column; gap: var(--gap-md); }
ul.checklist li { font-size: var(--body-size); line-height: 1.45; padding-left: 1.6em; position: relative; }
ul.checklist li::before { content: ''; position: absolute; left: 0; top: 0.55em; width: 0.7em; height: 0.7em; background: var(--brand-orange); }

/* Two-column */
.cols-2 { display: grid; grid-template-columns: 1fr 1fr; gap: var(--gap-xl); flex: 1; align-items: stretch; }
.col { display: flex; flex-direction: column; justify-content: center; gap: var(--gap-md); }

/* Quote */
.quote { font-size: var(--h2-size); line-height: 1.4; font-weight: 500; max-width: 70ch; margin: auto; padding: 0; border: none; }
.quote p { margin-bottom: var(--gap-md); }
.attribution { font-size: var(--body-size); display: flex; flex-direction: column; gap: 0.2em; opacity: 0.9; }
.attribution strong { font-weight: 700; }
.attribution span { opacity: 0.7; }

/* Logo wall — grayscale invariant */
.logo-wall { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 200px), 1fr)); gap: var(--gap-md); flex: 1; align-items: center; }
.logo-cell { aspect-ratio: 16/9; display: flex; align-items: center; justify-content: center; border: 1px solid currentColor; opacity: 0.6; font-size: var(--small-size); letter-spacing: 0.15em; font-weight: 700; filter: grayscale(1); }
```

---

---

## L9 — Bento grid (KPI bento, quadrant, before/after, pull-quote-with-data)

The single most-leverageable composition for content-rich slides. 6-column grid; cells use `col-span-N` / `row-span-N` to claim space. Different cell sizes = visual hierarchy without typography tricks.

```html
<section class="slide">
    <div class="bracket-tl"></div>
    <div class="bracket-br"></div>

    <div class="section-bar">
        <span class="num">0X</span>
        <span class="label">{{Section name}}</span>
    </div>

    <div class="slide-content">
        <h2>{{Headline}}</h2>

        <div class="bento" style="--cols:6; --rows:3;">
            <!-- Hero cell — 2 cols × 2 rows. The biggest card carries the lead idea. -->
            <div class="bento-cell" style="--col-span:2; --row-span:2;">
                <div class="eyebrow brand-orange">{{LEAD METRIC}}</div>
                <div class="bento-num brand-orange">$22.5B</div>
                <div class="bento-meta">{{quoted across the platform}}</div>
            </div>

            <!-- Wide cell — 4 cols × 1 row -->
            <div class="bento-cell" style="--col-span:4; --row-span:1;">
                <div class="eyebrow">{{SUPPORTING}}</div>
                <p>{{One-line supporting claim — extends the lead idea.}}</p>
            </div>

            <!-- 4 corner cells — 2 cols × 1 row each -->
            <div class="bento-cell" style="--col-span:2; --row-span:1;">
                <div class="bento-num">300+</div><div class="bento-label">distributors</div>
            </div>
            <div class="bento-cell" style="--col-span:2; --row-span:1;">
                <div class="bento-num">52%</div><div class="bento-label">faster bid cycle</div>
            </div>
            <div class="bento-cell" style="--col-span:2; --row-span:1;">
                <div class="bento-num">71</div><div class="bento-label">2024 NPS</div>
            </div>
        </div>
    </div>

    <div class="slide-footer">
        <div>SECTION 0X · {{TITLE}}</div>
        <div>NN / NN</div>
    </div>
</section>
```

**Use for**: KPI dashboards, before/after metric comparisons, pull-quote-with-supporting-data, quadrant analyses, "five proof points" slides. ONE primitive replaces L2 (3 stats) + L7 chart for content-rich moments.

**Density**: 4–7 cells. One hero cell (col-span ≥ 2, row-span ≥ 2) + supporting cells. Hero cell carries the brand-orange accent — it's the slide's focal point.

**Variants**:
- **Quadrant**: 4 cells, each `col-span:3; row-span:1` (2×2 grid)
- **Before/after**: 2 cells `col-span:3; row-span:2` (left=current, right=future)
- **Pull-quote-with-data**: 1 cell `col-span:4; row-span:2` (quote) + 2 cells `col-span:2; row-span:1` (data)

---

## L10 — Phase-block timeline (CSS Grid)

Pure CSS Grid horizontal timeline. No JS. Use for roadmaps, pilot scoping, deal stages, deployment phases.

```html
<section class="slide">
    <div class="bracket-tl"></div>
    <div class="bracket-br"></div>

    <div class="section-bar">
        <span class="num">0X</span>
        <span class="label">{{Section name}}</span>
    </div>

    <div class="slide-content">
        <h2>{{Headline — typically a phase narrative.}}</h2>

        <div class="phase-track">
            <div class="phase" style="--from:1; --to:4;">
                <div class="phase-eyebrow">PHASE 01</div>
                <div class="phase-title">{{DISCOVERY}}</div>
                <div class="phase-meta">{{Wk 1–3 · IT + Ops scoping}}</div>
            </div>
            <div class="phase phase-current" style="--from:4; --to:9;">
                <div class="phase-eyebrow brand-orange">PHASE 02 · IN FLIGHT</div>
                <div class="phase-title">{{PILOT}}</div>
                <div class="phase-meta">{{Wk 4–8 · 2 branches · live RFQs}}</div>
            </div>
            <div class="phase" style="--from:9; --to:13;">
                <div class="phase-eyebrow">PHASE 03</div>
                <div class="phase-title">{{ROLLOUT}}</div>
                <div class="phase-meta">{{Wk 9–12 · 8 branches · ERP-bound}}</div>
            </div>
        </div>
    </div>

    <div class="slide-footer">
        <div>SECTION 0X · {{TITLE}}</div>
        <div>NN / NN</div>
    </div>
</section>
```

**Use for**: roadmaps, deployment plans, deal-cycle visualizations, before/now/next narratives.
**Density**: 3–5 phase blocks across a 12-column track. The "current" phase carries `phase-current` class (brand-orange eyebrow).

---

## L11 — Statement (single big affirmation, full-bleed)

Slidev `statement` layout. The whole slide IS one sentence at hero scale. Use sparingly — once or twice per deck for moments that need to land.

```html
<section class="slide statement-slide">
    <div class="bracket-tl"></div>
    <div class="bracket-tr"></div>
    <div class="bracket-bl"></div>
    <div class="bracket-br"></div>

    <div class="title-content">
        <p class="statement">{{Single declarative sentence — the deck's load-bearing claim. Brand-orange-emphasis on the verb or noun.}}</p>
    </div>

    <div class="slide-footer">
        <div>{{section · context}}</div>
        <div>NN / NN</div>
    </div>
</section>
```

**Use for**: thesis slides, conviction moments, conclusion line. Density: ≤ 1 sentence, ≤ 14 words.

---

## L12 — Fact (one giant number, full-bleed)

Slidev `fact` layout. One number, room-filling. The deck's most explicit "look at this." moment.

```html
<section class="slide fact-slide">
    <div class="bracket-tl"></div>
    <div class="bracket-tr"></div>
    <div class="bracket-bl"></div>
    <div class="bracket-br"></div>

    <div class="title-content">
        <div class="fact-num brand-orange">$22.5B</div>
        <p class="fact-meta">{{One-line context — what the number is.}}</p>
    </div>

    <div class="slide-footer">
        <div>{{section}}</div>
        <div>NN / NN</div>
    </div>
</section>
```

**Use for**: market-size moments, NPS reveal, deal-flow scale. One per section max.

---

## L13 / L14 — Image-left / Image-right (paired image + content)

```html
<section class="slide">
    <div class="bracket-tl"></div><div class="bracket-br"></div>
    <div class="section-bar">...</div>

    <div class="slide-content image-left">
        <figure class="image-figure">
            <img src="{{path}}" alt="{{alt}}">
        </figure>
        <div class="paired-content">
            <h2>{{Headline}}</h2>
            <ul class="checklist">
                <li>{{Bullet}}</li><li>{{Bullet}}</li><li>{{Bullet}}</li>
            </ul>
        </div>
    </div>

    <div class="slide-footer">...</div>
</section>
```

**Use for**: product UI screenshots paired with adoption proof, persona portraits paired with goals/challenges.
**Density**: 1 image + 1 heading + 3–5 bullets (or 1 stat row).

---

## Connector primitive (SVG overlay for schematic illustrations)

For architecture diagrams, integration flows, sankey-lite. Place as a sibling of `.slide-content` (absolute-positioned overlay). Two anchor elements (`id="a"` and `id="b"`); the connector resolves their bounding boxes at render time and draws an SVG path.

```html
<svg class="connector-layer" aria-hidden="true">
    <!-- Filled at render time by inline JS or precomputed coords -->
    <path d="M 320 280 C 480 280, 520 420, 680 420"
          stroke="var(--info-on-dark)" stroke-width="2" fill="none"
          stroke-dasharray="4 6" />
    <!-- Optional terminator arrow -->
    <path d="M 676 414 L 692 420 L 676 426 Z" fill="var(--info-on-dark)" />
</svg>
```

**Use for**: ERP↔Parspec↔CRM architecture diagrams, integration-flow lockups.
**Density**: ≤ 4 connectors per slide. Use steel (`var(--info-on-dark)`) for connector lines — engineering-doc register. Brand-orange terminators only on the slide's focal flow.

---

## Charts.css integration

For richer chart needs (column / line / radar / polar / multi-dataset / mixed), include Charts.css in the prelude:

```html
<link rel="stylesheet" href="assets/charts.min.css">
<table class="charts-css bar show-labels data-spacing-5" style="--color-1: var(--cool-chart-on-dark); --color-2: var(--steel-300);">
    <tbody>
        <tr><th>Q1</th><td style="--size:0.4"><span class="data">$40K</span></td></tr>
        <tr><th>Q2</th><td style="--size:0.7"><span class="data">$70K</span></td></tr>
    </tbody>
</table>
```

**Use for**: any chart beyond the bar+donut in L7. Charts.css is pure CSS, no JS, ~6KB gzip. Single CSS file vendored at `parspec-slides/skills/parspec-slides/assets/charts.min.css`.

**Brand discipline**: Brand Orange stays out of chart palettes (CTA monopoly invariant). Default chart series uses `var(--chart-1..6)` resolved from `design-model.yaml`.

---

## Reusable structural CSS (additions for L9–L14)

```css
/* L9 — Bento grid */
.bento {
    display: grid;
    grid-template-columns: repeat(var(--cols, 6), 1fr);
    grid-auto-rows: minmax(120px, 1fr);
    gap: var(--gap-md);
    flex: 1;
    align-content: stretch;
}
.bento-cell {
    grid-column: span var(--col-span, 1);
    grid-row: span var(--row-span, 1);
    background: var(--surface-dark-panel);
    border: 1px solid var(--border-dark);
    border-radius: var(--radius-component);
    padding: var(--gap-lg);
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: var(--gap-sm);
    overflow: hidden;
}
.bento-num { font-size: clamp(2.5rem, 6vw, 5rem); font-weight: 900; line-height: 1; letter-spacing: -0.025em; }
.bento-label { font-size: var(--small-size); opacity: 0.75; letter-spacing: 0.05em; text-transform: uppercase; }
.bento-meta  { font-size: var(--body-size); opacity: 0.85; }

/* L10 — Phase-block timeline */
.phase-track {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: var(--gap-sm);
    flex: 1;
    align-items: stretch;
}
.phase {
    grid-column: var(--from) / var(--to);
    background: var(--surface-dark-panel);
    border: 1px solid var(--border-dark);
    border-radius: var(--radius-component);
    padding: var(--gap-md);
    display: flex; flex-direction: column; gap: var(--gap-sm);
}
.phase-current { border-color: var(--brand-orange); border-width: 2px; }
.phase-eyebrow { font-size: var(--eyebrow-size); letter-spacing: var(--eyebrow-tracking); text-transform: uppercase; opacity: 0.75; font-weight: 600; }
.phase-title   { font-size: var(--h3-size); font-weight: 700; letter-spacing: -0.005em; }
.phase-meta    { font-size: var(--small-size); opacity: 0.7; }

/* L11 — Statement */
.statement-slide .statement {
    font-size: clamp(2.5rem, 5.5vw, 5.5rem);
    font-weight: 700;
    line-height: 1.15;
    letter-spacing: -0.02em;
    max-width: 22ch;
}

/* L12 — Fact */
.fact-slide .fact-num {
    font-size: clamp(5rem, 14vw, 16rem);
    font-weight: 900;
    line-height: 0.95;
    letter-spacing: -0.04em;
}
.fact-slide .fact-meta {
    font-size: clamp(1.15rem, 2vw, 1.8rem);
    color: var(--text-dark-secondary);
    margin-top: var(--gap-md);
    max-width: 40ch;
}

/* L13/L14 — Image paired */
.slide-content.image-left { display: grid; grid-template-columns: 1fr 1fr; gap: var(--gap-2xl); align-items: center; }
.slide-content.image-right { display: grid; grid-template-columns: 1fr 1fr; gap: var(--gap-2xl); align-items: center; }
.slide-content.image-right .image-figure { order: 2; }
.slide-content .paired-content { display: flex; flex-direction: column; gap: var(--gap-lg); }

/* Connector overlay */
.connector-layer {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 4;
}
```

---

## Notes for the writer agent

- **NEVER put content as a direct child of `.slide`** — always go through `.slide-content` (or `.title-content` / `.end-content` on L1/L8/L11/L12). Direct children break the 3-zone composition and produce empty-canvas slides.
- **Prefer L9 (bento) over L2 (stat row) for ≥ 4 metrics.** Bento gives visual hierarchy via cell-size variance; stat row is monotone.
- **Use L11 (statement) and L12 (fact) sparingly** — once or twice per deck for moments that need to land. Overuse dilutes.
- **L13/L14 (image paired)** is the right home for product UI screenshots paired with adoption proof, NOT image-figure-floating-in-empty-canvas.
- These layouts are templates, not gospel. Adapt content but keep density limits.
- One slide = one idea. If you find yourself trying to fit two ideas, split into two slides — never crowd.
- Brand Orange used > 2× per slide loses its action signal. Cap.
- Typography clamps in design-model.yaml are sized for 1920×1080 slide rendering. Don't override.
- For richer charts, use Charts.css (vendored at `assets/charts.min.css`); for sankey/flowchart/quadrant/timeline diagrams, use Mermaid CLI at build time and inject the rendered SVG.
