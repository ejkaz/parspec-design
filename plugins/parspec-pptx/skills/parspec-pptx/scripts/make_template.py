"""
Build a local house template from a company deck export.

    python3 make_template.py --profile master "<master deck export>.pptx"
    python3 make_template.py --profile townhall "Parspec Townhall - Q2.26.pptx"
    [--out PATH] [--master N]

Strips every slide and every master except the one that carries the
profile's layouts, so the result keeps only the logo, footer, page numbers,
layout backgrounds and theme. Templates are company-internal: they live on
this machine (default ~/Documents/Claude/Templates/), never in the repo.

Master auto-pick: the first master that has every layout the profile needs.
Re-run whenever the company deck changes so generated decks track it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pptx import Presentation  # noqa: E402

from assets.house import DEFAULT_PROFILE, PROFILES, pick_master, strip_to_template  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--profile", default=DEFAULT_PROFILE, choices=sorted(PROFILES))
    ap.add_argument("--out")
    ap.add_argument("--master", type=int)
    a = ap.parse_args()
    prof = PROFILES[a.profile]

    prs = Presentation(a.source)
    idx = a.master if a.master is not None else pick_master(prs, prof)
    if idx is None:
        names = [[lay.name for lay in m.slide_layouts] for m in prs.slide_masters]
        sys.exit(f"no master has all of {sorted(prof.required)}; masters: {names} — pass "
                 f"--master N and update PROFILES['{a.profile}'].layouts")
    n_slides, n_masters = len(prs.slides), len(prs.slide_masters)
    strip_to_template(prs, keep_master=idx)
    out = Path(a.out or prof.template).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out)
    kept = [lay.name for lay in prs.slide_masters[0].slide_layouts]
    print(f"{out}  ({out.stat().st_size:,} bytes)")
    print(f"profile {prof.name}: dropped {n_slides} slides and {n_masters - 1} masters; "
          f"kept master {idx}: {kept}")


if __name__ == "__main__":
    main()
