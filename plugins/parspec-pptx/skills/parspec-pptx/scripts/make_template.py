"""
Build the local town hall template from a town hall deck export.

    python3 make_template.py "Parspec Townhall - Q2.26.pptx" [--out PATH] [--master N]

Strips every slide and every master except the dark town hall master, so
the result carries only the logo, footer, page numbers and layouts. The
template is company-internal: it lives on this machine, never in the repo.

Master auto-pick: the first master that has every layout townhall.LAYOUTS
needs. Re-run after each new town hall so decks track the latest chrome.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pptx import Presentation  # noqa: E402

from assets.townhall import DEFAULT_TEMPLATE, LAYOUTS, strip_to_template  # noqa: E402


def pick_master(prs) -> int:
    need = set(LAYOUTS.values())
    for i, m in enumerate(prs.slide_masters):
        if need <= {lay.name for lay in m.slide_layouts}:
            return i
    names = [[lay.name for lay in m.slide_layouts] for m in prs.slide_masters]
    sys.exit(f"no master has all of {sorted(need)}; masters: {names} — pass --master N "
             f"and update townhall.LAYOUTS")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--out", default=str(DEFAULT_TEMPLATE))
    ap.add_argument("--master", type=int)
    a = ap.parse_args()

    prs = Presentation(a.source)
    idx = a.master if a.master is not None else pick_master(prs)
    n_slides, n_masters = len(prs.slides), len(prs.slide_masters)
    strip_to_template(prs, keep_master=idx)
    out = Path(a.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out)
    kept = [lay.name for lay in prs.slide_masters[0].slide_layouts]
    print(f"{out}  ({out.stat().st_size:,} bytes)")
    print(f"dropped {n_slides} slides and {n_masters - 1} masters; kept master {idx}: {kept}")


if __name__ == "__main__":
    main()
