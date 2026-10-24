# Proposed sales motifs

Use with `HouseDeck(profile="sales")`. This is an opt-in proposal in design-model
2.3.0, pending ratification. `master` remains the default. Existing global brand
roles, invariants, exhibit surfaces and brand version remain unchanged. The
proposed `sales_ownership_fill` and sales donut palette are scoped to this profile;
they do not authorize new orange usage in other registers.

All values come from `Brand.sales` and `Brand.role("sales_<name>")`. Geometry is
measured on a 1280 × 720 canvas, mapped to 10 × 5.625 inches at 128 px/in. Font
sizes convert at 72/128 pt per px: the 42px title is 23.625pt. These are PPTX
coordinates, rather than CSS pixels at 96 DPI. Use the named primitives in
`assets/motif.py`; never paste HTML hex values or font names into a builder.

## Composition rules

| Rule | PPTX application | Governing archetypes |
|---|---|---|
| One idea per slide | Use a direct, mixed-case takeaway title where supported; preserve setup labels where the approved copy calls for them. Split when the content needs smaller text. | S04–S09, S11–S15 |
| Ground | Use `sales_ground_master` throughout a sales deck. Existing investor and exhibit profiles keep their own surfaces. | S01–S15 |
| Header | Orange bold uppercase section eyebrow near y=40; mixed-case bold title below; optional muted dek. No tracking and no rule beneath the eyebrow. Content starts at y=184. | S04–S09, S11–S15 |
| Grid | Side inset 56px; width 1168px; gutter and normal card padding 24px. Align card tops, text starts and footer edges. | S02, S04–S15 |
| Type | Cover/divider 60px; content title 42px; card headings 22–24px; preferred body 18px; meaningful text at least 14px. Only footnotes/footer may use 11px. | S01–S15 |
| Card | Square `sales_card`, one flush 4px orange top rule. No automatic outline or internal hairline. Use `sales_card_raised` only when hierarchy calls for it. | S04, S07, S09, S12, S14 |
| Brackets | TL/BR corner ticks on three value cards; optional group frame around a stat quad. Do not apply slide-wide brackets. | S05, S13 |
| Callout | One distinct takeaway in a `sales_band` panel with an orange left bar. Add the optional label only if it helps interpretation. No automatic takeaway band on every slide. | S04, S06, S08, S15 |
| Ask | One `sales_umber` band with orange label and bold white decision text. No ad-hoc umber variant or extra border. | S07, S10, S11 |
| Sequence | Two-digit numerals for agenda, process and next steps. A rail uses outlined numbered nodes and one solid-orange final node with black text. Numbered value cards retain their selected family; do not add decorative indices elsewhere. | S02, S05, S07, S10, S11 |
| Figures | Every number has units, a one-line label and a numbered source marker. Synthetic galleries label the sample explicitly; this is no evidence for real company performance. | S04, S06, S08, S09, S11–S13 |
| Tables | Band header, alternating ground/row-alt rows, bold row labels. Right-align numbers, one chosen-column outline and one recommendation label. Main cells 17px preferred, never under 14px; finish above y=632. | S08, S11 |
| Charts | Keep native editable segments and explicit category/value matching. The five-category donut uses the profile's scoped palette; other charts need an approved role recipe. Label all slices at one scale, use black text on orange/teal/light-grey segments, and include basis and units. Dashed lines denote plan. | S06, S09, S11 |
| Status | Words or small dots plus words; never color alone or emoji. KPI triangles are monochrome text plus directional words, not status icons. Warnings use warning roles rather than ownership orange. | S07, S09, S11 |
| Cover | Actual wordmark and customer name or greyscale logo; thin lockup divider; two-line title, short title rule and metadata. Native quarter-disc and two arcs bottom-right; omit page number. | S01 |
| Divider | One design: wordmark top-left, centered-height title at left, short orange rule, optional section list and original glow image top-right. No giant chapter numeral. | S03 |
| Portrait | Full orange ring for contacts/quotes; ¾ ring for team rows. Use real approved photographs when available; visibly mark placeholder initials as template-only. | S10, S14 |
| Logos | Preserve real artwork proportions. Customer logo walls are white/greyscale; no white boxes and no automatic customer logo on each content slide. | S01, S10, S13 |
| Footer | Real wordmark at x=56, 92px wide; centered copyright/confidentiality; page number at right inset. Cover omits page. Footer zone starts at y=672 and is excluded from content. | S01–S15 |
| Sources | Numbered notes above the footer, with a visible synthetic-data disclosure where appropriate. Notes and sources can occupy two columns. Do not imply an approved source for sample prices or placeholder metrics. | S04, S06, S08, S09, S11–S15 |
| Placeholders | Label template-only fields explicitly. Do not ship a blank black title slide as a placeholder. Replace or verify fields before an external deck is used. | S10 and any incomplete archetype |

## Highlight scale

Use the lowest level that communicates the relationship. These are proposed
sales-register semantics, not amendments to global CTA policy.

| Level | Treatment | Meaning | Archetypes |
|---|---|---|---|
| 1 | Bold white value | A result within the normal reading order | S04, S08, S09 |
| 2 | Orange type | One hero or result; do not color every KPI orange | S04, S08, S09 |
| 3 | One 1px orange outline | Chosen column, option or destination | S07, S08, S12 |
| 4 | Solid orange with black text | Parspec-owned object or target state | S07 final node, S08 header chip when explicitly appropriate, S15 |
| Context | Single umber fill | Ask, decision, third party or context | S07, S10–S12, S15 |

## Motif budget

At most **three chrome devices** on one slide. Repeated instances of one framing
family count once. The required footer and plain data cells do not count.

- S07: rail/nodes + destination outline + ask band = three. Remove internal card
  hairlines and do not add a duration bracket.
- S08: recommendation label + chosen-column outline + table row rules = three.
  Do not add a separate chip stack or a second framed takeaway.
- S05: selective bracket family and the aligned card divider suffice. Do not add
  an invented proof-stat row or a second takeaway panel.
- S01/S10: title rule, contact/lockup treatment and quarter-disc are already a
  complete composition. Keep arcs confined to the lower-right bleed.
- S03: glow and title rule provide the divider identity; no numeral panel.

## Do / Don't

| Do | Don't | Archetypes |
|---|---|---|
| Keep headings, labels and body starts aligned | Shrink one card's copy to force a fit | S04, S05, S07, S12, S14 |
| Keep native editable text, chart data and geometry | Use a full-slide screenshot to imitate the chosen composition | S01–S15 |
| Use the original local glow asset | Recreate a CSS gradient, blur or card halo | S03 |
| Use one consistent divider and title register | Introduce a different divider or case treatment per chapter | S03–S09 |
| Reserve quarter-discs for opening/closing | Decorate every content slide with arcs | S01, S10 |
| Split dense tables into headline and appendix slides | Put 7–9pt cells or text in the footer zone | S08, S11 |
| Retain sources and decision basis | Add unapproved proof statistics, dates or commercial terms | S04–S12 |
| Keep square panels and named roles | Add rounded panels, steel/violet/magenta accents or arbitrary umbers | S04–S15 |
| Keep sales data tables dark and sans serif | Import paper-warm panels, serif exhibit titles or universal brackets | S08, S11; all sales slides |

Paper-warm panels, serif exhibit surfaces and universal slide brackets are **not
in current sales register (0/290 slides)**. This is a scope annotation: existing
paper/serif tokens remain available to their existing registers, and selective
brackets remain valid for S05/S13. It is not a claim that the reference set had
zero selective bracket slides.
