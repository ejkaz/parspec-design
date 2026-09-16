"""
House register — example deck + smoke test.

Exercises every HouseDeck recipe and every assets.shapes composite with
sample content (no real figures). Copy this file to start a new deck.

    python3 house_example.py [--profile master|townhall] [out.pptx]
    bash render.sh out.pptx          # soffice PNGs to eyeball
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from assets import shapes as sh  # noqa: E402
from assets.house import DEFAULT_PROFILE, PROFILES, HouseDeck  # noqa: E402

AGENDA = [
    ("Where we stand", "The quarter in numbers", "10 min"),
    ("Priorities", "What we're betting on", "10 min"),
    ("The plan", "How we get there", "10 min"),
    ("Q&A", "Ask anything", "15 min"),
]


def build(profile: str, out: Path) -> Path:
    d = HouseDeck(profile)
    pal, X0, XW, TOP, BOTTOM = d.pal, d.x0, d.xw, d.top, d.bottom

    d.cover(["Quarterly", "Company Update"], date=d.placeholder("[Date]"),
            byline="Presenter, Title", eyebrow="Sample")
    d.agenda(AGENDA, blurb="45 minutes together.", eyebrow="Update")
    d.divider("Company update", "(20 minutes)", strip=[a[0] for a in AGENDA[:3]], active=0)

    # overview tiles (master) / KPI tiles + chips (both)
    s = d.content("Where we stand", accent="this quarter",
                  subtitle="Sample figures. Lead with the number the room should remember.")
    sh.tile_row(s, X0, TOP + 0.2, XW, 2.3, [
        ("Metric one", "$0.0M", [("+00% ", {"color": pal.good}), ("vs. last year", {})]),
        ("Metric two", "0.0x", "vs. plan"),
        ("Metric three", "00%", "Trailing twelve months"),
        ("Team", "000", "Across both offices"),
    ], pal)
    sh.text(s, X0, 4.25, XW, 0.5, "One-sentence takeaway in the master's closing-statement style.",
            size=12, italic=True, color=pal.subtle)

    s = d.content("Where we stand", accent="(town hall tiles)")
    w = (XW - 0.4) / 3
    for i, (lab, val, delta) in enumerate([
        ("METRIC ONE", "$0.0M", [("+00% ", {"color": pal.good}), ("vs. last year", {})]),
        ("METRIC TWO", "0.0x", "vs. plan"),
        ("METRIC THREE", "00%", "Trailing twelve months"),
    ]):
        sh.kpi_tile(s, X0 + i * (w + 0.2), TOP, w, 1.5, lab, val, delta, pal)
    sh.chip_row(s, X0, TOP + 1.9, XW, 1.5, [
        ("Shipped on time", "Two releases in one quarter"),
        ("New market", "First customer in a new vertical"),
        ("Team", "New hires across both offices"),
        ("Quality", "Escape rate trending down"),
    ], pal)

    # numbered cards
    s = d.content("Path to", accent="launch", glow=False)
    sh.numbered_cards(s, X0 - 0.06, TOP - 0.05, XW + 0.12, BOTTOM - TOP + 0.05, [
        dict(num=1, title="Discover", tag="Done", body=["Customer research", "Scope"]),
        dict(num=2, title="Build", tag="We are here", body=["Design", "Engineering"]),
        dict(num=3, title="Pilot", tag="4–6 weeks", lead="≥80%", body="of pilot workflows run in the product"),
        dict(num=4, title="Launch", tag="Q4", body=["General availability"]),
    ], pal, highlight=1, dim=(0,))

    # panel rows + stat
    s = d.content("What it", accent="means")
    sh.panel_rows(s, X0, TOP, XW, [
        ("Unchanged", "Heading in accent", "Body copy in white. One or two lines."),
        ("New", "Heading in accent", "Body copy in white. One or two lines."),
        ("Your part", "Heading in accent", "Body copy in white. One or two lines."),
    ], pal)

    # problem -> solution
    s = d.content("How we", accent="answer")
    sh.problem_solution(s, X0, TOP + 0.3, XW, [
        ("Question one?", "00%", "Proof label", "Supporting detail, one line."),
        ("Question two?", "0x", "Proof label", "Supporting detail, one line."),
        ("Question three?", "$0B", "Proof label", "Supporting detail, one line."),
    ], pal)

    # process + funnel
    s = d.content("The plan", subtitle="A real sequence, so the stages are numbered.")
    sh.process(s, [("Discover", "Customer research"), ("Build", "Design and engineering"),
                   ("Pilot", "Two design partners"), ("Launch", "General availability"),
                   ("Scale", "Enterprise rollout")], current=2, pal=pal)
    s = d.content("Pipeline", accent="funnel")
    sh.funnel(s, [("000", "Leads", "Sample detail line"), ("00", "Qualified", "Sample detail line"),
                  ("00", "Proposal", "Sample detail line"), ("0", "Closed", "Sample detail line")],
              pal, ramp="umber" if profile == "master" else "alpha")

    # questions (brackets) + evidence rows
    s = d.content("What customers", accent="ask")
    sh.bracket_box(s, X0, TOP, 3.55, BOTTOM - TOP - 0.1, pal, fill=pal.card)
    sh.label(s, X0 + 0.28, TOP + 0.25, 3.0, "What's working", pal)
    sh.text(s, X0 + 0.28, TOP + 0.6, 3.05, 2.7, ["Point one", "Point two", "Point three"],
            size=13, bold=True, bullet=pal.accent, space_after=26)
    sh.question_cards(s, X0 + 3.75, TOP, XW - 3.75,
                      [("First question?", "Context line."), ("Second question?", "Context line."),
                       ("Third question?", "Context line.")], pal)
    sh.crosshair(s, X0 + XW, TOP - 0.1, pal)

    s = d.content("How we answer", accent="(town hall rows)")
    sh.evidence_rows(s, X0, TOP, XW, [
        ("Question one?", "Proof point headline", "Supporting detail."),
        ("Question two?", "Proof point headline", "Supporting detail."),
        ("Question three?", "Proof point headline", "Supporting detail."),
    ], pal)

    # scorecard (bands + qualitative)
    s = d.content("Our Scorecard:", accent="Where We Stand", eyebrow="Readiness", style="eyebrow")
    sh.band_scorecard(s, X0, 1.42, XW, [
        dict(name="Metric one", why="Why it matters", value="000%", num=115, trend="▲ from 000%",
             bands=(100, 110, 120), bands_text=["<100%", "100–110%", "110–120%", "120%+"],
             target="Target: 120%+"),
        dict(name="Metric two", why="Lower is better", value="0.0x", num=1.8, bands=(2.0, 1.5, 1.0),
             higher_better=False, bands_text=[">2.0x", "1.5–2.0x", "1.0–1.5x", "<1.0x"]),
        dict(name="Metric three", why="Judgment override", value="00%", num=50, bands=(40, 60, 80),
             status=0, target="Target: 60%+"),
    ], pal, row_h=0.6)
    s = d.content("Our Scorecard:", accent="Beliefs", eyebrow="Readiness", style="eyebrow")
    sh.status_rows(s, X0, 1.5, XW, [
        dict(name="Belief one", evidence="Evidence with a source.", zone=3, next="Next step"),
        dict(name="Belief two", evidence="Evidence with a source.", zone=1, next="Next step"),
        dict(name="Belief three", evidence="Evidence with a source.", zone=0, next="Next step"),
    ], pal)

    q = d.divider("Ask", accent="anything", kicker="Q&A", tagline="Nothing is off-limits.",
                  footnote=[("Ask live, or anonymously: ", {}), d.placeholder("[form link]")])
    d.notes(q, "Speaker notes land here — sources and [CONFIRM] flags.")
    return d.save(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?")
    ap.add_argument("--profile", default=DEFAULT_PROFILE, choices=sorted(PROFILES))
    a = ap.parse_args()
    out = Path(a.out or f"/tmp/parspec-pptx-out/house_example_{a.profile}.pptx")
    out.parent.mkdir(parents=True, exist_ok=True)
    print(build(a.profile, out), "ok")
