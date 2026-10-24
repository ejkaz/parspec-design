# Proposed sales archetypes

Select `HouseDeck(profile="sales")` explicitly. The default stays `master` until
ratification. All examples use plain data and the role-based `Motif` object from
`assets/motif.py`; see [motif rules](motifs.md) for scale, source and chrome limits.
Coordinates below describe a 1280 × 720 design converted at 128px/in, not a
browser-to-PowerPoint pixel assumption. The gallery is a synthetic layout study.

S01–S10 are the picked gallery families. Lane letters identify candidate layout
choices; they are not quality approvals. Mandatory copy, type-floor, logo and
contrast repairs override the candidate. S11–S15 are documented composition
recipes outside the ten-slide gallery; they do not claim a picked render or
completed gallery coverage.

## S01 — Co-branded cover · pick C, compact arcs from B

**Use:** open a customer presentation with one subject and clear ownership.

**Primitive:** `m.cover_lockup(...)` includes the native quarter-disc/arcs;
profile `cover()` provides the standard two-line title construction. Call
`m.quarter_arcs(...)` separately only when composing another archetype, such as S10.

**Density:** two title lines, one lockup and at most two metadata lines. No page
number; no content cards or proof-stat strip.

**Picked composition:** wordmark and customer name form a restrained upper-left
lockup. A large two-line white title occupies the left middle; a short orange
rule and quiet metadata follow it. A small umber quarter-disc and two orange arcs
bleed from the lower-right corner. Use the actual wordmark, never reconstructed
text or glyphs; the disc is the `umber_deep` role.

## S02 — Split timed agenda · pick C, item scale from A

**Use:** an ordered run of show with explicit duration.

**Primitive:** `deck.agenda(items)` with `(title, descriptor, minutes)` rows.

**Density:** five rows in the gallery; up to six only if the 24px item scale and
14px timing floor fit. Sum approved durations; no inferred schedule.

**Picked composition:** a two-line light agenda heading fills the left third,
separated by one vertical hairline. The right holds orange two-digit indices,
white 24px agenda items and a quiet minutes column. Even rows have thin dividing
rules. Gallery timing is 10/10/10/10/5, totaling 45 minutes.

## S03 — Unified section divider · pick C, glow from B

**Use:** chapter transition with an optional preview of section contents.

**Primitive:** `m.divider(...)` or `deck.divider(heading, tagline=...)`.

**Density:** one 60px title, a short title rule and one optional dot-separated
section list. No oversized chapter number, card grid or second eyebrow.

**Picked composition:** actual wordmark upper-left, large mixed-case white title
left at vertical center, short orange rule below. Orange "IN THIS SECTION" and
a muted list sit beneath. The original glow image stays top-right. Use one
divider design throughout a deck.

## S04 — At-a-glance stat strip · pick B, label scale from A

**Use:** four independent, source-qualified overview figures.

**Primitive:** `m.stat_tile(...)` repeated four times; optional
`m.callout_bar(...)` for one distinct takeaway.

**Density:** four equal top-rule tiles, one large figure and one caption per tile;
no more than one optional band. All four figures carry footnote markers.

**Picked composition:** compact square charcoal tiles span the content band;
64px figures have room above 14px labels and 16px captions. One hero may be
orange. A separate left-bar band sits below the strip, with the source note well
above the footer. No nested card rules or decorative outlines.

## S05 — Three value cards · pick A, aligned body starts from C

**Use:** three parallel value propositions requiring short explanation.

**Primitive:** `m.bracket_card(...)` repeated three times.

**Density:** exactly three cards; 22px heading and 18px body, up to eight
short lines (about 40 words). No metrics row or unapproved proof statistic. Align headings,
hairlines and paragraph starts across all three cards.

**Picked composition:** three tall charcoal cards with selective orange TL/BR
corner ticks, a numeral, orange headline and white body. The bracket family is
specific to this archetype; it is not standard slide chrome. Use the actual
footer logo aligned to the common 56px edge.

## S06 — Native donut and task callouts · pick B, contrast from C

**Use:** explain a total and the contribution of five categories.

**Primitive:** `m.donut_callouts(...)`, followed by one `m.callout_bar(...)` when
the arithmetic supports a distinct takeaway.

**Density:** one donut, five explicit categories and one short explanation per
callout. All slice labels use the same scale at 14px minimum; center units,
basis and legend also meet the floor. One source-qualified note.

**Picked composition:** a compact donut on the left and aligned task rows on the
right. Total and units sit in the center. Orange, teal and three neutral greys
map consistently to category swatches. Black text labels orange, teal and the
lighter-grey slices; darker slices use white. Five native block-arc segments preserve
geometry editability (they are not a linked PowerPoint chart workbook). The gallery total is 65 hours; the first two categories sum to 48,
which rounds to 74%. A separate band states the takeaway.

## S07 — Rail process with decision band · pick B

**Use:** show ordered work from contracting through rollout.

**Primitive:** `m.rail_steps(...)` and `m.ask_band(...)`.

**Density:** four rail cards in the gallery, two or three short details each;
14px minimum node numerals and decision label. Rail/stems stop at card tops.

**Picked composition:** one thin orange rail connects outlined circular nodes
above equal charcoal cards. Final node is solid orange with black text; the
final card has the single destination outline. No internal card hairlines. A
full-width umber decision band sits below. The pilot is labeled "Pilot (45
days)"; the title does not promise the entire path takes 45 days. No invented
go-live dates.

## S08 — Highlighted comparison table · pick A, body scale from D

**Use:** compare three options with one explicit recommendation.

**Primitive:** `m.highlight_table(...)`.

**Density:** four main body rows plus a header and a price row in the gallery.
Keep primary cells at 17px, recommendation at 14px; split any longer table.
Finish above y=632 with a source note clear of the footer.

**Picked composition:** grey header band over zebra rows, bold row labels and
right-aligned numbers. One full-height orange outline surrounds the chosen
column, with a single recommendation label at the top. Do not add extra chips
or color every value orange. Sample pricing and onboarding terms remain visibly
synthetic; they are not a commercial offer.

## S09 — QBR KPI strip and priorities · pick A, hero from B

**Use:** compare quarter performance and state the next three actions.

**Primitive:** `m.kpi_tile(...)` repeated six times, then numbered
priorities inside one top-rule panel composed with the motif text helper.

**Density:** six KPIs maximum, each with one 40px figure, a 14px label and a 14px
directional delta. Three priorities maximum. One basis line states periods and
sample/source status.

**Picked composition:** six compact top-rule tiles across one row; only the
turnaround value is orange and other figures stay white. Triangle glyphs include
plain directional words. A larger top-rule priority panel occupies the lower half.
No second proof-summary band and no unsupported historical claim.

## S10 — Next steps and contacts · pick B, owner/date fields from C

**Use:** close with concrete actions and a contact path.

**Primitive:** `m.contact_ring(...)`, open next-step rows and optional
`m.quarter_arcs(...)`.

**Density:** three next steps, each with owner and timing at 14px minimum; two
contacts maximum. Keep contact rows separated and clear of the lower-right arcs.

**Picked composition:** the left action list and right stacked contacts each
have a direct reading path. Contacts use full orange portrait rings, bold names
and muted roles. Small arcs remain secondary. Any initials, account-executive
field or unknown date is explicitly template-only; replace and verify before
external use.

## S11 — Gantt / schedule · supplemental recipe

**Use:** a dated plan where duration, overlap and ownership matter more than a
simple sequence.

**Primitive composition:** `m.header(...)`; native rectangles and rules form the
week grid and bars, with motif text labels. Use `m.ask_band(...)` only if a
decision is required. This is not `rail_steps()` stretched into a calendar.

**Density:** four to six workstream rows, one owner column and at most eight time
columns at meaningful label size. One milestone vocabulary and one legend.
Split dense plans into phases; never conceal dates in tiny labels.

**Composition:** left workstream/owner columns, light dashed verticals, orange
active bars, neutral future bars and umber context spans. Diamond milestones and
one dashed go-live line may carry dates. No picked candidate render exists in
the ten-slide set; this recipe extends the sales geometry without claiming a
rendered gallery example.

## S12 — Pricing columns / subscription options · supplemental recipe

**Use:** three or four commercial packages, or two detailed alternatives.

**Primitive composition:** `m.top_rule_card(...)`, named text roles and one
chosen-option outline if needed; `m.highlight_table(...)` when line-by-line
comparability is the primary decision.

**Density:** up to four narrow cards with one price, one unit and at most three
short details; or two wider options with up to four breakdown rows each. Align
all prices and units; show required assumptions in a separate source note.

**Composition:** equal charcoal columns, orange sequence/option label only when
meaningful, optional umber module chips and a right-aligned total. Choose one
highlight level. No picked candidate render exists in the ten-slide set.

## S13 — Stat quad and logo wall · supplemental recipe

**Use:** pair four source-qualified proof points with bounded social proof.

**Primitive composition:** `m.stat_tile(...)` in a 2×2 grid, a selective group
bracket using native lines, and approved grayscale picture assets.

**Density:** four metrics plus six to nine logos in a regular 2×3 or 3×3 grid.
Do not add a callout band, quote cards or more metrics.

**Composition:** stat quad on the left, one vertical hairline, logo grid on the
right. Corner brackets frame the group rather than every tile. All logo artwork
keeps its proportions, without white-box treatments. No picked candidate render
exists in the ten-slide set.

## S14 — Quote cards · supplemental recipe

**Use:** sourced testimonials with clear attribution.

**Primitive composition:** `m.top_rule_card(...)`, named text roles and optional
`m.contact_ring(...)` for a genuine approved portrait.

**Density:** three cards maximum, each one quote of at most three lines and one
attribution block. A 2×2 grid is an appendix variant only when text meets the
14px floor. Split longer quotes; do not shrink or paraphrase a direct quote.

**Composition:** square charcoal panels, sparse orange quote mark or theme label,
regular/italic quote text and aligned attribution. No glow halo or extra stacked
frame. No picked candidate render exists in the ten-slide set.

## S15 — Architecture layers · supplemental recipe

**Use:** communicate ownership, third-party boundaries and data movement.

**Primitive composition:** `m.header(...)`, native rectangle/text/connector
helpers; fill Parspec/target blocks with `sales_ownership_fill` and
`sales_ownership_text`, context blocks with `sales_umber`. Use a single optional
`m.callout_bar(...)` if a routing takeaway is necessary.

**Density:** three to five horizontal layers, no more than six blocks total;
14px minimum labels. One legend decodes ownership, context and dashed boundaries.

**Composition:** orange ownership blocks use black text, umber third-party blocks
use white; straight white connectors express direction. Layer labels remain
aligned on the left. Avoid decorative connector webs. This proposed ownership
semantic still requires ratification. No picked candidate render exists in the
ten-slide set.
