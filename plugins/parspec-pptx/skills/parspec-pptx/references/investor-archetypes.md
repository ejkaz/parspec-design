# Proposed investor and board archetypes

Select `HouseDeck(profile="investor")` explicitly. The profile is an opt-in
proposal pending ratification; `master` remains the default. Read the
[Investor & board register](motifs.md#investor--board-register) before composing.
The local gallery is a fictional fixture, not financial evidence or an approved
external presentation. Templates, decks and renders are local-only artifacts.

Use `Charts(deck)` from `assets/charts.py`. All chart methods create native
PowerPoint chart objects with editable data; `fin_table` and `heatmap_table`
create native tables. The calls below name the required primitive rather than
prescribing literal colors, fonts or unverified data. Resolve those through the
investor role tokens and the caller's source data.

The canvas is 1280 × 720 at 128 px/in on a 10 × 5.625 inch slide. Main text,
including chart ticks and labels, is at least 14px. Only BD-12 and IN-09 table
text may use 13px. The centered copyright footer is 11px. A two-line title moves
the content band down; it never causes body type to shrink.

## Board library

| ID / slide | Job | Primitive / chart call | Density limit | The one rule |
|---|---|---|---|---|
| **BD-01 · Cover** | Identify the meeting and fiscal period | Wordmark lockup, editable title and metadata, restrained house arcs | Two title lines and one template metadata line | Use a fiscal period and template metadata, without inventing a dated meeting assertion. |
| **BD-01a · Agenda & asks** | Connect the run of show to the decisions | `fin_table` for agenda; numbered editable ask text | Six agenda rows, one total and three asks | Repeat the supplied decision sentences verbatim on BD-11, with all timing explicit. |
| **BD-02 · Quarter on a page** | Make results and the shortfall visible together | Six white-value KPI tiles and two short explanation columns | Six tiles; up to six short lines below | Keep every actual value white and include the net-new miss in what changed. |
| **BD-03 · ARR bridge** | Explain the change from opening to ending ARR | `waterfall` with invisible base series | Six bars; at most three retention metrics | Totals are orange, increases teal and decreases muted red; separate every category label and start the value axis at zero or label its break. |
| **BD-04 · ARR trajectory** | Show the actual-to-plan trajectory | `column_actual_forecast` with actual/forecast chip pair and legend | Eight fiscal quarters, one legend and one callout | State the planned ending-ARR result as a plan, never as achieved performance. |
| **BD-05 · Plan vs actual** | Score performance against the board's plan | `fin_table` with Metric, Board plan, Actual and Variance columns | Six metrics and one callout; no micro-bars | Put Board plan before Actual; compute variance from the source operands and never invent a Management View reconciliation. |
| **BD-06 · P&L summary** | Show revenue through operating earnings | `fin_table` with units, status band and forecast outline | Seven rows, four quarterly columns and one annual total | Label the annual total Actual + forecast and leave padding inside the forecast-column outline. |
| **BD-07 · Cash & runway** | Show the cash path and financing event | `combo_bar_line` or `line_trend`, with three summary metrics | Twelve monthly observations, three metrics and one debt annotation | Keep runway values white and separate the financing annotation from value labels; do not extrapolate an unsupported cash-out date. |
| **BD-08 · Three cases** | Compare named cases without hiding their differences | `bar_ranked` for a common cash metric plus `fin_table` | Three cases, one chart and one compact table | Move all content below the reflowed header and retain the source horizon limitations in the appendix. |
| **BD-09 · Headcount** | Reconcile team movement to one hiring plan | `waterfall` plus `fin_table` by function | Five bars and five rows including totals | Show one grey-outlined plan bar, muted-red leavers and padding inside the plan column. |
| **BD-10 · Pipeline** | Compare weighted pipeline with the next-period target | `stacked_bar` with target reference and compact stage labels | Four stages, one chart and one comparison sentence | Keep the weighted total white and retain the Proposal + Commit comparison without methodology prose. |
| **BD-11 · Decisions** | State what the board can approve at this meeting | Large numerals and editable decision rows | Three decisions, owner and timing per row | Use the same decision sentences as BD-01a and explicit This meeting timing. |
| **BD-12 · Appendix P&L** | Hold financial detail, definitions and arithmetic policy | `fin_table` with separate income-statement and margins sections | Up to fourteen rows × eight columns; 13px table floor | Identify the actual source fixture and its rounding policy; never attribute fictional data to company accounts. |
| **BD-13 · Approval** | Isolate the authorization and its cash effect | `fin_table` with recommended-column outline and ask band | Two unit-specific comparisons and one ask | Separate US$M from months and repeat the authorization sentence verbatim, including the fiscal month. |
| **BD-14 · Risks** | Pair named risks with accountable mitigation | `fin_table` with editable Risk, Mitigation and Owner cells | Three supplied risks; at most five rows | Add full fiscal years to deadlines and do not invent unsupported impact, trigger or hiring assumptions. |
| **BD-15 · Divider** | Mark one agenda transition | House divider with title, short rule, topics and presenter | One title, up to five topics and one timing line | Reuse one divider composition and tie the agenda item and duration to the supplied agenda. |

## Investor library

| ID / slide | Job | Primitive / chart call | Density limit | The one rule |
|---|---|---|---|---|
| **IN-01 · Cover** | Open the financing discussion for its audience | Editable two-line title, optional partner lockup and restrained arcs | Two title lines, one lockup and two metadata lines | The optional partner slot uses the common lockup, with no white logo box. |
| **IN-02 · Highlights** | Establish the supplied investment proof points | Three large white metrics and one short callout | Three primary metrics and one sentence | Use a headline supported by the fixture and keep every actual statistic white. |
| **IN-03 · Growth** | Show historical growth and the forecast together | `column_actual_forecast` plus one two-year comparison bracket | All fourteen fiscal quarters, one legend and one bracket | Preserve the full history needed for the two-year claim and compute the comparison from the period endpoints. |
| **IN-04 · Retention** | Separate cohort expansion from company retention | `heatmap_table` plus company-retention metrics | Four cohorts × four years and up to three metrics | Leave unavailable cells blank and distinguish cumulative cohort expansion from trailing-period company retention. |
| **IN-05 · Unit economics** | Show efficiency and margin progression | `line_trend` plus payback and efficiency metrics | Seven fiscal quarters, one trend and up to three metrics | Keep actual values white, ticks at least 14px and the margin improvement in percentage points. |
| **IN-06 · Market** | Compare addressable scopes | `bar_ranked` with directly labeled TAM, SAM and SOM | Three categories, three labels and one sentence | Label SOM as a five-year opportunity; if a circle variant is used, scale area rather than radius. |
| **IN-07 · Competition** | Show supplied qualitative positioning | `scatter_labeled` with the Parspec point highlighted | Five supplied markers; at most ten | Mark both axes qualitative and show HIGH/LOW endpoints without implying proven exclusivity. |
| **IN-08 · Valuation** | Place the proposed multiple beside the reference set | `scatter_labeled` with highlighted company point and median references | Eight peers plus company, one horizontal median and one growth median | Label the measure Valuation / ARR (pre-money), keep ticks at least 14px and describe the position below peer median. |
| **IN-09 · Comps table** | Make the reference set and relative position inspectable | `fin_table`, optionally paired with `bar_ranked` | Nine data rows × five columns; 13px table floor | Calculate peer deltas from the unrounded median, then format the result. |
| **IN-10 · Round** | State terms and allocate proceeds | Native `doughnut` with term metrics and direct allocation labels | Four terms and four slices | Use the supplied allocations and compute new-money ownership from raise divided by post-money value. |
| **IN-11 · Milestones** | Show the outcomes the proposed capital funds | Three editable milestone rows or rail steps and a dated baseline | Three milestones and one Today baseline | Use only supplied milestone dates and outcomes; do not invent the next financing date or redefine break-even. |
| **IN-12 · Sources** | Preserve provenance, basis and limitations | `fin_table` with Source, Used for and Period / limitation | Up to ten source rows | Name the fictional fixture, actual-through/forecast-from boundary and pre-money valuation basis accurately. |
| **IN-13 · Important information** | Explain the status and limits of the material | Editable prose with short section labels | Four or five readable paragraphs | State that the template uses fictional sample data and retain the copyright footer. |
| **IN-14 · Financial plan** | Show the quarterly plan and annual financial outcomes | `fin_table`, with optional `column_actual_forecast` trajectory | Eight quarterly columns plus annual summaries, split into readable blocks if needed | Recompute net-new ARR and financial totals from source precision; FY26 annual totals are Actual + forecast. |

## Data and acceptance boundary

Recompute chart data and displayed financial amounts from the supplied fixture,
not candidate render text. Store money to two decimal places with half-up
rounding, sum those values, then format US$M to one decimal. Derive margins from
gross profit divided by revenue. Annual ending ARR is an exit value, not a sum.
Keep the median at full precision until a displayed delta is calculated.

Runway, case cash-out and company retention may be supplied assertions. A
template may label them accurately without claiming that an incomplete model
independently verifies them. Sources and limitations belong on BD-12 / IN-12;
speaker notes retain field-level provenance. Native-object and arithmetic checks
do not substitute for visual review or PM/brand acceptance.
