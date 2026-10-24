# Series B story archetypes (v0.6.0)

Opt in with `HouseDeck('investor')`. `assets/story.py` accepts plain caller data.
The profile and all colors/fonts remain in the brand model. New story charts
use the existing teal/neutral investor roles; orange remains header/disclosure
chrome. These choices do not modify the older investor/board chart builders. No real company
content, proprietary templates, decks or renders belong in this public repo.

| ID | Builder | Editable construction |
|---|---|---|
| IN-20 | `wedge_workflow` | Workflow columns, buyer/job, status, shared context, next dependency; connectors |
| IN-21 | `agent_swimlanes` | Trigger, agent steps and human controls; status chips and connectors; audit path |
| IN-22 | `learning_ledger` | Request, response/spec, observed status and next test; chronology band |
| IN-23 | `reachable_revenue` | 60% operand table and 40% zero-based clustered column comparison |
| IN-24 | `labor_waterfall` | Same-unit hidden-base native waterfall and factor/evidence table |
| IN-25 | `earned_expansion` | Workflow, buyer, unit, dependency, overlap/pricing proof and readiness; separate marketplace |
| IN-26 | `pilot_package` | Proposed pilot terms plus existing distinct meters |
| IN-27 | `output_economics` | Three adjacent native columns, editable economic-difference brackets and metric table |
| IN-28 | `delivery_payback` | Full-delivery-cost waterfall and separate cumulative-GP/cost line, first crossing marked |
| IN-29 | `deployment_cohorts` | Signed/paid/live/renewed, implementation days and custom effort |
| IN-30 | `context_evidence` | Rights, evaluation and baseline/with-context matrix |
| IN-31 | `quality_leverage` | Native 100% stacked outcomes, separate aligned review/cost lines, absolute counts |

`incubation_divider()` introduces the measurement gates in five lines.
`illustrative_chip()` adds the exact top-right dummy-data chip and replaces
only the center footer. IN-23 through IN-31 and the divider always carry it.
IN-20 through IN-22 do not. The gallery's first three pages are placeholders.
Status chips accept only Live, Demo environment, Prototype or Roadmap.

## Build locally

```bash
python3 scripts/story_gallery.py
python3 scripts/story_draft.py --content /local/private/real_content.json
python3 scripts/story_draft.py --content /local/private/real_content.json --internal --out /local/private/internal_draft.pptx
python3 scripts/investor_smoke.py --data fixtures/incubation_fixture.json --story /local/gallery.pptx /local/private/draft.pptx
SOFFICE_PROFILE=file:///tmp/story_lo bash scripts/render.sh /local/gallery.pptx /local/render 128
```

The draft waits up to 20 minutes for the supplied content file. If absent, it
builds placeholders and prints/records that condition. No confidential input
path is bundled. Its default output is the local Templates/seriesb_story folder.
External partner labeling is default; `--internal` explicitly selects the
internal label. Both require the requested label to exist, never infer one.

## Input contracts

`story_gallery.placeholders()` is the generic IN20/IN21/IN22 schema. The
incubation fixture documents the plain IN23–IN31 schemas and is explicitly
fictional. Do not feed production metrics into this fixture gallery.

The local draft also accepts an authoring schema, normalized without numeric
inference:

- Top level: `as_of`, `confidentiality`, `partner_label_external`,
  `partner_label_internal`, and `IN20`, `IN21`, `IN22` (or a `slides` mapping).
- Each slide: `headline`/`title`, optional `dek`/`subtitle`, `source_notes`.
- IN20: `stages[]` with `stage`, `buyer_job`, `status`, `as_of`,
  `reusable_from_wedge`, optional `dependency`. Missing dependency stays UNKNOWN.
- IN21: `lanes.trigger[]` strings, `lanes.agent_steps[]` with `step` and
  `status`, `lanes.human_controls[]` with `control` and `why`. Control rationale
  stays in notes. Controls without a supplied status receive no inferred chip.
- IN22: `rows[]` with `request`, `product_response`, `observed_status`,
  `next_test`; `chronology[]` with `date` and `event`. Source wording stays intact.

Keep source URLs and detailed qualifications in notes. Confirm stage inventories,
rights and approved external wording before circulating populated slides.
These decks are draft shape evidence, never external or brand acceptance.

## Arithmetic and missingness

IN-23 sums unrounded operands (fixture: $301.175M), then displays $301.2M.
Its source's rounded segment displays sum to the same displayed total, but are
not arithmetic inputs. Expansion is a separate case, never added to the
serviceable headline. IN-24 holds annual US$ throughout. IN-27's benefit, price
and cost overlap, so the columns are adjacent, never stacked. Retained benefit
is before adoption cost. IN-28 includes all attempts and human delivery costs;
its example payback uses months 1–15, first crossing in month 13. Missing cohort
period, observation windows and defect rates remain UNKNOWN/TBD. The fixture
has no evidence supporting these missing fields. No quote/BOM/MAP conversion is
provided. Marketplace is separate and excluded from totals.

The smoke check independently recomputes operands, waterfalls and first crossing,
compares chart caches with embedded workbooks, enforces native chart counts,
100% outcomes and text floors, and rejects targeted corruptions. Visual review
and PowerPoint/Slides round-trip fidelity remain separate checks.

Numeric story-table cells retain native right alignment and one untracked run.
The shared table helper's per-digit width compensation rendered narrow digits
as broken numbers in LibreOffice (for example 108.0 appeared as 1 08.0). The
story wrapper removes that compensation without changing the other galleries.
