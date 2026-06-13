# Jury Architecture — rationale + invariants

This is the longer-form complement to SKILL.md. SKILL.md covers what + when; this file covers why each architectural choice exists, and what NOT to change.

## Why a jury, not a single Opus pass

`parspec-slides` Round 5 currently uses a single Opus visual review of each slide. Empirical observation from running it on the 55-slide First-Call Master Deck (2026-05-04):

- The single reviewer caught 28 of 55 slides as REVISE.
- After applying CSS-level fixes (drawing-block top-clip, corner brackets, sparse-slide vertical anchoring), the deck visibly improved.
- BUT: the same single reviewer marked many slides PASS that, on user inspection, were "still basic, poorly formatted." The reviewer accepted negative space as intentional minimalism rather than broken layout.

The gap: the single reviewer reads the slide AND its manifest. The manifest tells it what was intended. The reviewer biases toward "is this consistent with the writer's intent?" rather than "is this a real B2B deck?"

The jury fix:
1. **Multiple jurors with diverse scope** — each focused on one quality axis, not a generalist
2. **Anti-priming** — one juror (anti-slop) deliberately gets only the rendered output, no intent/manifest
3. **Severity × agreement aggregation** — load-bearing findings need cross-juror confirmation; idiosyncratic single-juror takes don't auto-revise

## Why 4 jurors not 5+

Cohere's "Replacing Judges with Juries" (PoLL, arXiv:2404.18796) shows that **diversity matters more than count past 3**. The marginal juror past 4 adds tokens without juror-diversity gain on visual review tasks.

Our 4 cover:
- compositional discipline (what the slide does as design)
- chart correctness (what the slide does as data communication)
- brand fidelity (what the slide does as Parspec)
- anti-template instinct (what the slide does as a market signal)

A 5th juror would have to be either redundant or out-of-scope. (e.g., a "narrative" juror would re-litigate Round 2 editorial review.)

The roadmap mentions a v0.3.0 contact-sheet juror — but that operates on the deck-level thumbnail grid, not per-slide; it's a separate aggregation layer, not a 5th per-slide juror.

## Why anti-slop juror gets PNG only

Two reasons:

**1. ChatEval persona-diversity finding** (arXiv:2308.07201): when multiple debate agents share the same context, they converge on similar verdicts. Independence is degraded. The paper specifically tested same-persona vs diverse-persona configurations; same-persona scored worse on agreement-with-human metrics.

**2. The buyer doesn't read the manifest.** A B2B distributor CIO opens the deck cold. They see the slide as it is. Whatever the writer's intent was, if the slide LOOKS like generic AI template, the brand-perception damage is done.

Giving the anti-slop juror the manifest would prime it toward "well, the writer claims this was Parspec-disciplined, so I'll grade it on that basis." That's exactly the bias we're trying to break.

This is the load-bearing detail of the architecture. **Don't change it.**

## Why severity × agreement, not just severity-max

A single juror flagging severity=0.9 might be:
- correct (real problem, only one juror happened to look at the right region)
- wrong (juror over-confident, idiosyncratic interpretation, hallucinated finding)

We can't tell from one juror. We CAN tell when 2+ jurors flag the same cluster — that's evidence of a real problem.

Severity-max alone over-revises (any juror's worst case becomes the slide's verdict). Severity × agreement requires real evidence to escalate.

The threshold table:

| Score | Severity | Agreement | Interpretation |
|---|---|---|---|
| 1.00 | 1.0 | 4/4 | Unanimous critical — automatic BLOCK |
| 0.80 | 1.0 | 3/4 | 3-juror critical — BLOCK |
| 0.75 | 1.0 | 3/4 | 3-juror critical — BLOCK |
| 0.50 | 1.0 | 2/4 | 2-juror critical — REVISE |
| 0.40 | 0.8 | 2/4 | 2-juror serious — REVISE |
| 0.25 | 1.0 | 1/4 | 1-juror critical — REVISE (single severe overrides) |
| 0.20 | 0.8 | 1/4 | 1-juror serious — note, not actionable |
| 0.10 | 0.4 | 1/4 | 1-juror cosmetic — note |

## Why the clustering step

Without clustering, 4 jurors flagging "the orange on the paper-warm panel fails AA" produces 4 separate findings. The aggregator would see 4 things to fix when there's actually 1.

Clustering by (slide, dimension-class, region) collapses these into a single cluster with `agreement: 1.0` and one consensus issue/fix. The conductor sees a clean fix list, not a noisy aggregation.

## Why dimension-class mapping (not raw dimension match)

Each juror has its own vocabulary:
- Composition Critic: `focal_hierarchy`, `whitespace_rhythm`
- Data-Viz Critic: `chart_type_fit`, `comparison_clarity`
- Brand Fidelity: `single_accent_rule`, `cool_family_role_separation`
- Anti-Slop: tell_3 "three-col icon grid", tell_13 "centered everything"

If juror A says `focal_hierarchy: 4` and juror D says `tell_13: centered everything`, those describe the same underlying problem (no clear hierarchy because everything is symmetrically centered). They cluster. The dimension-class `hierarchy` captures both.

Without the mapping, identical findings in different vocabularies count as independent. With the mapping, they aggregate properly.

## Invariants of the architecture

These cannot change without breaking the design:

1. **Each juror is independent.** Jurors do not see each other's outputs during their pass. The aggregator sees all 4. Don't introduce inter-juror communication.
2. **Anti-slop juror is PNG-only.** Always. No exceptions. (See above.)
3. **Aggregator is text-only.** It reads juror YAMLs; it doesn't re-render the slide. This forces the jurors to write specific, concrete findings.
4. **Verdict source is severity × agreement, not vote count.** A slide with 4 PASS jurors but 1 critical-severity finding from one juror still goes REVISE if score ≥ 0.4. The aggregation isn't majority-rule.
5. **The 4 dimensions are non-overlapping by design.** If you find yourself wanting a 5th juror, check whether the new dimension fits inside an existing one or whether it duplicates Round 2 editorial review.

## What can change

- Juror model selection (Opus vs Sonnet vs Haiku per juror) — calibrate against cost/quality
- Verdict thresholds (currently 0.4 / 0.8) — tune against ground-truth labelled decks
- Specific tells in the anti-slop blacklist — the design-Twitter consensus on AI-slop signals will evolve
- Per-juror dimensions — add new sub-dimensions within a juror's lane as needed
- Output schema field names — as long as they remain compatible with parspec-slides Round 5b/5c reassembly

## What this skill does NOT cover

- Editorial review (cohesion, voice, density rhythm) — Round 2 of parspec-slides
- Structural HTML lint (forbidden colors, fonts) — parspec-craft skill
- Brand definition / token authoring — parspec-design skill (design-model.yaml is the SSoT)
- Slide generation — parspec-slides skill, Rounds 0–4

The jury sits in Round 5b, replacing the single visual review pass. Everything upstream and downstream is unchanged.
