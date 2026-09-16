"""
Town hall register — example deck + smoke test.

Exercises every TownHall recipe and every assets.shapes composite with
sample content (no real figures). Copy this file to start a new deck.

    python3 townhall_example.py [out.pptx]
    bash render.sh out.pptx          # soffice PNGs to eyeball
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from assets import shapes as sh  # noqa: E402
from assets.townhall import BOTTOM, TOP, X0, XW, TownHall  # noqa: E402

AGENDA = [
    ("Where we stand", "The quarter in numbers", "10 min"),
    ("Priorities", "What we're betting on", "10 min"),
    ("The plan", "How we get there", "10 min"),
    ("Q&A", "Ask anything", "15 min"),
]


def build(out: Path) -> Path:
    th = TownHall()
    pal = th.pal

    th.cover(["Quarterly", "Town Hall"], "Company update",
             [th.placeholder("[Date]"), ("  ·  Presenter, Title", {})], eyebrow="Town hall · Sample")

    th.agenda(AGENDA, blurb="45 minutes together.", eyebrow="Town hall")
    th.divider("Company Update", "(20 minutes)", strip=[a[0] for a in AGENDA[:3]], active=0)

    # KPI tiles + chip row
    s = th.content("Where We Stand", accent="This Quarter", eyebrow="Company update",
                   subtitle="Sample figures. Lead with the number the room should remember.")
    w = (XW - 0.4) / 3
    for i, (lab, val, delta) in enumerate([
        ("METRIC ONE", "$0.0M", [("+00% ", {"color": pal.good}), ("vs. last year", {})]),
        ("METRIC TWO", "0.0x", "vs. plan"),
        ("METRIC THREE", "00%", "Trailing twelve months"),
    ]):
        sh.kpi_tile(s, X0 + i * (w + 0.2), TOP, w, 1.5, lab, val, delta, pal)
    sh.label(s, X0, 3.18, 4, "Highlights", pal)
    sh.chip_row(s, X0, 3.44, XW, 1.5, [
        ("Shipped on time", "Two releases in one quarter"),
        ("New market", "First customer in a new vertical"),
        ("Team", "New hires across both offices"),
        ("Quality", "Escape rate trending down"),
    ], pal)

    # Three accent cards
    s = th.content("Three Priorities", accent="for Next Quarter", eyebrow="Company update")
    w = (XW - 0.4) / 3
    for i, (lab, head, body) in enumerate([
        ("GROW", "Exceed the new-ARR plan", "Why it matters, in one or two sentences."),
        ("BUILD", "Ship the connected platform", "Why it matters, in one or two sentences."),
        ("OPERATE", "Raise the quality bar", "Why it matters, in one or two sentences."),
    ]):
        x = X0 + i * (w + 0.2)
        sh.card(s, x, TOP, w, 2.35, pal)
        sh.label(s, x + 0.26, TOP + 0.22, w - 0.4, lab, pal)
        sh.text(s, x + 0.26, TOP + 0.48, w - 0.4, 0.6, head, size=16, bold=True)
        sh.text(s, x + 0.26, TOP + 1.2, w - 0.46, 1.0, body, size=10, color=pal.muted)

    # Process
    s = th.content("The Plan", eyebrow="Company update",
                   subtitle="A real sequence, so the stages are numbered.")
    sh.process(s, [("Discover", "Customer research"), ("Build", "Design and engineering"),
                   ("Pilot", "Two design partners"), ("Launch", "General availability"),
                   ("Scale", "Enterprise rollout")], current=2, pal=pal)

    # Funnel
    s = th.content("Pipeline", accent="Funnel", eyebrow="Go-to-market")
    sh.funnel(s, [("000", "Leads", "Sample detail line"), ("00", "Qualified", "Sample detail line"),
                  ("00", "Proposal", "Sample detail line"), ("0", "Closed", "Sample detail line")],
              pal)

    # Question cards + evidence rows
    s = th.content("What Customers Ask", eyebrow="Go-to-market")
    sh.card(s, X0, TOP, 3.55, BOTTOM - TOP, pal)
    sh.label(s, X0 + 0.28, TOP + 0.22, 3.0, "What's working", pal)
    sh.text(s, X0 + 0.28, TOP + 0.56, 3.05, 2.7, ["Point one", "Point two", "Point three"],
            size=13, bold=True, bullet=pal.accent, space_after=26)
    sh.question_cards(s, X0 + 3.75, TOP, XW - 3.75,
                      [("First question?", "Context line."), ("Second question?", "Context line."),
                       ("Third question?", "Context line.")], pal)

    s = th.content("How We Answer", eyebrow="Go-to-market")
    sh.evidence_rows(s, X0, TOP, XW, [
        ("Question one?", "Proof point headline", "Supporting detail."),
        ("Question two?", "Proof point headline", "Supporting detail."),
        ("Question three?", "Proof point headline", "Supporting detail."),
    ], pal)

    q = th.divider("Q&A", "(15 minutes)", tagline="Nothing is off-limits.",
                   footnote=[("Ask live, or anonymously: ", {}), th.placeholder("[form link]")])
    th.notes(q, "Speaker notes land here — sources and [CONFIRM] flags.")
    return th.save(out)


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/parspec-pptx-out/townhall_example.pptx")
    out.parent.mkdir(parents=True, exist_ok=True)
    p = build(out)
    print(p, "ok")
