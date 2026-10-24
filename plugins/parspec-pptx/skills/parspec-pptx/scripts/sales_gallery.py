"""Build the proposed sales register's ten editable, synthetic archetypes.

Templates and assets stay local. Pass --glow to the supplied divider PNG;
--render uses LibreOffice with an isolated profile and a 1280x720 raster.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from assets.house import HouseDeck, TEMPLATE_DIR


def build(output: Path, template=None, glow=None):
    deck = HouseDeck("sales", template=template)
    m = deck.motif
    slides = []
    s = deck.cover(["Parspec × Northwind", "Electric Supply"], customer="Northwind Electric Supply",
                   subtitle="Partnership Proposal", date="October 2026")
    slides.append(s)

    items = ["Where you are today", "What Parspec changes", "Business case", "Path to go-live", "Commercials & next steps"]
    s = deck.agenda([(t, "", f"{n} min") for t, n in zip(items, [10, 10, 10, 10, 5])], blurb="45 minutes")
    slides.append(s)

    s = deck.divider("02 · What Parspec changes", tagline="Value creation · Where the admin hours go · What changes for quoting and submittals", glow=glow)
    slides.append(s)

    s = deck.content("Parspec at a Glance", eyebrow="COMPANY OVERVIEW",
                     subtitle="AI-native procurement platform for electrical distributors and rep agencies.")
    stats = [
        ("FOUNDED", "20XX", "Built by construction and software operators"),
        ("TEAM", "00", "Across engineering, data and customer success"),
        ("DISTRIBUTORS & REPS", "000+", "Branches and agencies live on the platform"),
        ("QUOTED VALUE", "$00B", "Cumulative project value quoted to date"),
    ]
    for i, (label, value, caption) in enumerate(stats):
        m.stat_tile(s, 56 + i * 298, 184, 274, 236, label, value, caption, source="1", hero=i == 3)
    m.callout_bar(s, 56, 448, 1168, 96,
                  "Quotes, submittals and orders on one platform, live today at 000+ distributors and rep agencies.",
                  label="WHY IT MATTERS FOR NORTHWIND")
    m.text(s, 56, 568, 1168, 24, "1. Sample figures for layout review.", style="footnote", color="ink_muted")
    slides.append(s)

    s = deck.content("A Third Less Admin Work. Here's What It Buys.", eyebrow="VALUE CREATION")
    cards = [
        ("Faster Turnaround, Higher Win Rate", "Quotes and submittals that took days go out in hours. A faster response reaches the customer while the decision is still open, and a sharper deliverable makes the bid easier to say yes to."),
        ("Win More of the Project", "One live bill of materials carries from quote to submittal to order. Every line, cross and approval stays attached to the project, so the team sells the whole package instead of the first release only."),
        ("Protect the Bottom Line", "Pricing, terms and manufacturer programs flow automatically from quote to order. Incentive tiers track in real time and short pays surface the day they happen, so less rework and more margin stay in the branch."),
    ]
    for i, (heading, body) in enumerate(cards):
        m.bracket_card(s, 56 + i * (1168 + 24) / 3, 184, (1168 - 48) / 3, 408,
                       str(i + 1), heading, body)
    m.text(s, 56, 620, 1168, 22, "1. Illustrative value proposition for layout review; quantitative headline is sample copy.", style="footnote", color="ink_muted")
    slides.append(s)

    s = deck.content("65 Hours of Admin Behind Every $100K Sold", eyebrow="THE PROBLEM",
                     subtitle="Back-office hours per $100K of goods sold, by task.")
    tasks = [
        {"label": "Quoting", "value": 30, "detail": "Rebuilding BOMs line by line and looking up pricing across price books for every RFQ."},
        {"label": "Submittals", "value": 18, "detail": "Chasing datasheets one at a time and assembling every approval package by hand."},
        {"label": "Order management", "value": 7, "detail": "Splitting POs by vendor and chasing change orders across disconnected systems."},
        {"label": "Reporting", "value": 6, "detail": "Rolling up pipeline, bid status and manufacturer rebates by hand at every check-in."},
        {"label": "Specification", "value": 4, "detail": "Reviewing product requirements."},
    ]
    m.donut_callouts(s, tasks, total=65, unit="HOURS", x=106, y=184, d=340,
                     callout_x=540, callout_w=684)
    m.callout_bar(s, 56, 564, 1168, 74,
                  "Quoting and submittals are 74% of the hours — the first two workflows Parspec automates.")
    m.text(s, 56, 645, 1168, 18, "1. Illustrative sample data.", style="footnote", color="ink_muted")
    slides.append(s)

    s = deck.content("Path to Go-Live: Contract to Every Branch Live", eyebrow="IMPLEMENTATION")
    steps = [
        {"title": "Business case review", "subtitle": "Agree the value and the scope", "bullets": ["Confirm users, modules and branches in scope", "ROI model built from Northwind's own quote volume", "Joint review with sales and operations leaders"]},
        {"title": "Contract", "subtitle": "Order form and MSA", "bullets": ["Order form: users, modules, term", "Legal, security and IT review", "Signatures and kickoff date set"]},
        {"title": "Pilot (45 days)", "subtitle": "Prove value on live quotes", "bullets": ["Data migration and price-book load, led by Parspec", "Pilot users trained by your customer success manager", "Go/no-go against the agreed success criteria"]},
        {"title": "Onboarding", "subtitle": "Every user live and trained", "bullets": ["Kickoff and role-based training by branch", "Dedicated success manager through go-live", "Quarterly business reviews against adoption targets"]},
    ]
    m.rail_steps(s, steps, x=56, y=182, w=1168, card_y=236, card_h=280)
    m.ask_band(s, 56, 540, 1168, 86, "Confirm pilot branches and an executive sponsor.", label="DECISION NEEDED")
    slides.append(s)

    s = deck.content("Three Ways to Start", eyebrow="COMMERCIALS")
    rows = [
        ["Users", "Up to 10", "Up to 50", "Unlimited"],
        ["Modules", "Quoting", "Quoting + Submittals", "All modules"],
        ["Onboarding", "Self-serve", "Guided, 2 weeks", "Dedicated CSM, 45-day pilot"],
        ["Support", "Email", "Email + chat", "Named success manager"],
        ["Annual price¹", "$24K", "$60K", "$150K"],
    ]
    m.highlight_table(s, ["", "PILOT", "TEAM", "ENTERPRISE"], rows, chosen=3,
                      x=56, y=184, w=1168, row_h=68, widths=[224, 244, 284, 380])
    m.text(s, 56, 606, 1168, 22, "1. Sample pricing for layout review.", style="footnote", color="ink_muted")
    slides.append(s)

    s = deck.content("Northwind Q3: Adoption Up, Turnaround Down", eyebrow="Q3 BUSINESS REVIEW")
    kpis = [("ACTIVE USERS", "142", "▲ 18 up"), ("QUOTES", "1,240", "▲ 22% up"),
            ("AVG TURNAROUND", "1.8d", "▼ 0.9d faster"), ("SUBMITTALS", "310", "▲ 41 up"),
            ("WIN RATE", "31%", "▲ 4 pts up"), ("HOURS SAVED", "2,950", "▲ 35% up")]
    kw = (1168 - 5 * 16) / 6
    for i, (label, value, delta) in enumerate(kpis):
        m.kpi_tile(s, 56 + i * (kw + 16), 184, kw, 136, label, value, delta, hero=i == 2)
    m.top_rule_card(s, 56, 352, 1168, 264)
    m.text(s, 84, 376, 1112, 28, "NEXT-QUARTER PRIORITIES", style="table", bold=True, color="orange")
    priorities = ["Roll out to the remaining branches", "Move submittals fully onto Parspec", "Cut turnaround below 1.5 days"]
    for i, title in enumerate(priorities):
        x = 84 + i * 376
        m.text(s, x, 434, 328, 40, f"{i+1:02d}", style="numeral", color="orange")
        m.text(s, x, 482, 328, 80, title, style="body_strong")
    m.text(s, 56, 635, 1168, 24, "Q3 vs Q2 · illustrative sample data.", style="footnote", color="ink_muted")
    slides.append(s)

    s = deck.content("Let's Build the Future of Construction Procurement", eyebrow="PARTNER WITH US")
    # Match the selected two-line closer, with action/contact separation.
    for shape in s.shapes:
        if shape.has_text_frame and shape.text.startswith("Let's Build"):
            shape.width = int(800 / 128 * 914400)
    m.text(s, 56, 228, 560, 24, "NEXT STEPS", style="label", color="orange", bold=True)
    m.rect(s, 164, 238, 452, 1, fill="hairline")
    for i, (title, owner) in enumerate([("Confirm pilot branches", "Northwind"), ("Sign order form", "Both"), ("Pilot kickoff", "Parspec")]):
        y = 272 + i * 100
        m.text(s, 56, y, 40, 34, f"{i+1:02d}", style="card_heading", color="orange")
        m.text(s, 116, y, 500, 32, title, style="body_strong")
        m.text(s, 116, y + 36, 500, 28, f"{owner} · TBD", style="label", color="ink_muted")
    m.contact_ring(s, 696, 228, 104, "[Executive Name]", "[Title], Parspec", initials="EX")
    m.contact_ring(s, 696, 368, 104, "[Account Executive]", "Enterprise Account Executive, Parspec", initials="AE")
    m.text(s, 824, 442, 400, 20, "Template-only contact and headshot placeholders", style="label", color="ink_muted")
    m.quarter_arcs(s)
    slides.append(s)
    for i, s in enumerate(slides, 1):
        deck.notes(s, f"S{i:02d} — proposed sales register. Synthetic layout-review copy only; not approved customer claims. Contact placeholders are template-only.")
    output.parent.mkdir(parents=True, exist_ok=True)
    deck.save(output)
    return output


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=TEMPLATE_DIR / "parspec_sales_gallery.pptx")
    ap.add_argument("--template", type=Path)
    ap.add_argument("--glow", type=Path, help="Local orange-glow.png divider asset")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--png-dir", type=Path, default=TEMPLATE_DIR / "sales_gallery_png")
    args = ap.parse_args()
    if args.glow is None:
        candidate = TEMPLATE_DIR / "parspec_sales_glow.png"
        args.glow = candidate if candidate.exists() else None
    output = build(args.out.expanduser(), args.template, args.glow)
    print(output)
    if args.render:
        env = dict(os.environ, PPTX_ENGINE="soffice", PPTX_DIRECT="0")
        env.setdefault("SOFFICE_PROFILE", "file:///tmp/sol_lo_profile")
        subprocess.run(["bash", str(Path(__file__).with_name("render.sh")), str(output), str(args.png_dir.expanduser()), "128"], env=env, check=True)


if __name__ == "__main__":
    main()
