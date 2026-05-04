# Parspec Slide Layouts

Paste-ready `<section class="slide">` blocks. Each respects density limits and uses `var(--...)` references that resolve from the populated `:root` block.

Copy the layout you need; fill in content; never inline-style anything that should come from a token.

---

## L1 — Title slide

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
        <div class="eyebrow brand-orange">{{section eyebrow}}</div>
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

    <h2>{{Headline ≤ 50 chars.}}</h2>

    <ul class="checklist">
        <li>{{Bullet one — concrete, terse, no hedging.}}</li>
        <li>{{Bullet two.}}</li>
        <li>{{Bullet three.}}</li>
        <li>{{Bullet four.}}</li>
        <li>{{Bullet five — optional.}}</li>
        <li>{{Bullet six — optional.}}</li>
    </ul>

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

    <blockquote class="quote">
        <p>"{{Quote ≤ 3 lines, real customer words, no embellishment.}}"</p>
        <footer class="attribution">
            <strong>{{Name}}</strong>
            <span>{{Title, Company}}</span>
        </footer>
    </blockquote>

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

    <h2>{{Headline — e.g., "Trusted across the top of the distributor pyramid."}}</h2>

    <div class="logo-wall">
        <div class="logo-cell">SONEPAR</div>
        <div class="logo-cell">GRAYBAR</div>
        <div class="logo-cell">REXEL</div>
        <div class="logo-cell">WESCO</div>
        <div class="logo-cell">BORDER STATES</div>
        <div class="logo-cell">CRESCENT</div>
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

    <h2>{{Headline — what the data shows.}}</h2>

    <div class="chart-grid">
        <div class="chart-card">
            <div class="chart-title">{{Bar chart title · units}}</div>
            <div class="bar-chart">
                <div class="bar-row"><div class="bar-label">{{Label}}</div><div class="bar-track"><div class="bar-fill" style="width: 96%; background: var(--secondary-1);"></div></div><div class="bar-value">XX</div></div>
                <!-- 4 more bar-row blocks -->
            </div>
        </div>
        <div class="chart-card">
            <div class="chart-title">{{Donut chart title}}</div>
            <div class="donut-row">
                <div class="donut" style="--c1: var(--secondary-1); --c2: var(--secondary-2); --c3: var(--secondary-3); --c4: var(--secondary-4); --c5: var(--secondary-5);"></div>
                <ul class="donut-legend">
                    <li><span style="background: var(--secondary-1);"></span><span>{{A}}</span><span class="pct">XX%</span></li>
                    <!-- 4 more legend rows -->
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

    <div class="end-content">
        <div class="eyebrow brand-orange">{{TAG}}</div>
        <h1 class="brand-orange">{{Closing line.}}</h1>
        <p class="end-meta">{{contact / next step / quote}}</p>
    </div>

    <div class="slide-footer">
        <div>{{Deck title · audience}}</div>
        <div>NN / NN · END</div>
    </div>
</section>
```

**Use for**: deck closer, call to action, signoff.
**Density**: 1 closing heading + 1 line.

---

## Reusable structural CSS

These classes are referenced across layouts. Include in every generated deck (after viewport-base.css).

```css
/* Section bar */
.section-bar { display: flex; align-items: center; gap: var(--gap-md); margin-bottom: var(--gap-md); }
.section-bar .num { font-family: 'SF Mono', monospace; font-size: var(--small-size); padding: 4px 10px; border: 1px solid currentColor; opacity: 0.7; }
.section-bar .label { font-size: var(--eyebrow-size); letter-spacing: 0.22em; text-transform: uppercase; font-weight: 600; opacity: 0.6; }

/* Slide header / footer */
.slide-header, .slide-footer { display: flex; justify-content: space-between; align-items: center; font-size: var(--eyebrow-size); letter-spacing: 0.18em; text-transform: uppercase; font-weight: 600; opacity: 0.6; }
.slide-footer { margin-top: auto; padding-top: var(--gap-md); }

/* Eyebrow */
.eyebrow { font-size: var(--eyebrow-size); letter-spacing: 0.22em; text-transform: uppercase; font-weight: 600; opacity: 0.65; margin-bottom: var(--gap-md); }
.brand-orange { color: var(--brand-orange); }

/* Corner brackets */
.bracket-tl, .bracket-tr, .bracket-bl, .bracket-br { position: absolute; width: clamp(20px, 2.5vw, 40px); height: clamp(20px, 2.5vw, 40px); border: 2px solid var(--brand-orange); pointer-events: none; }
.bracket-tl { top: clamp(1rem, 2vw, 2rem); left:  clamp(1rem, 2vw, 2rem); border-right: 0; border-bottom: 0; }
.bracket-tr { top: clamp(1rem, 2vw, 2rem); right: clamp(1rem, 2vw, 2rem); border-left: 0;  border-bottom: 0; }
.bracket-bl { bottom: clamp(1rem, 2vw, 2rem); left:  clamp(1rem, 2vw, 2rem); border-right: 0; border-top: 0; }
.bracket-br { bottom: clamp(1rem, 2vw, 2rem); right: clamp(1rem, 2vw, 2rem); border-left: 0;  border-top: 0; }

/* Stat row */
.stat-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--gap-lg); flex: 1; align-items: center; }
.stat-num { font-size: clamp(3rem, 8vw, 7rem); font-weight: 900; line-height: 1; }
.stat-label { margin-top: var(--gap-sm); font-size: var(--body-size); opacity: 0.85; }

/* Checklist */
ul.checklist { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: var(--gap-sm); }
ul.checklist li { font-size: var(--body-size); line-height: 1.45; padding-left: 1.6em; position: relative; }
ul.checklist li::before { content: ''; position: absolute; left: 0; top: 0.5em; width: 0.7em; height: 0.7em; background: var(--brand-orange); }

/* Two-column */
.cols-2 { display: grid; grid-template-columns: 1fr 1fr; gap: var(--gap-xl); flex: 1; align-items: stretch; }
.col { display: flex; flex-direction: column; justify-content: center; gap: var(--gap-md); }

/* Quote */
.quote { font-size: var(--h2-size); line-height: 1.4; font-weight: 500; max-width: 70ch; margin: auto; padding: 0; border: none; }
.quote p { margin-bottom: var(--gap-md); }
.attribution { font-size: var(--body-size); display: flex; flex-direction: column; gap: 0.2em; }
.attribution strong { font-weight: 700; }
.attribution span { opacity: 0.7; }

/* Logo wall */
.logo-wall { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 200px), 1fr)); gap: var(--gap-md); flex: 1; align-items: center; }
.logo-cell { aspect-ratio: 16/9; display: flex; align-items: center; justify-content: center; border: 1px solid currentColor; opacity: 0.6; font-size: var(--small-size); letter-spacing: 0.15em; font-weight: 700; }
```

---

## Notes for the agent

- These layouts are templates, not gospel. Adapt content but keep density limits.
- When extracting from PPTX in Phase 4, map source slides to these layouts by content shape.
- One slide = one idea. If you find yourself trying to fit two ideas, split into two slides — never crowd.
- Brand Orange used > 2× per slide loses its action signal. Cap.
