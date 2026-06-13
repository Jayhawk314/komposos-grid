# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Generate the static public dashboard.

    python -m domains.grid.run_dashboard          # writes docs/index.html

Run after any report regeneration so the published page tracks the
committed findings. GitHub Pages (Settings -> Pages -> deploy from
master /docs) serves the result.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from domains.grid.dashboard import (
    build_dashboard_html,
    chpe_chart,
    corridor_value_chart,
    load_inputs,
    project_bc_chart,
    seam_trend_chart,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Static grid-waste dashboard")
    parser.add_argument("--reports-dir", default="reports")
    parser.add_argument("--out", default="docs/index.html")
    parser.add_argument("--figures-dir", default="reports/figures",
                        help="also write standalone SVG figures here")
    args = parser.parse_args(argv)

    inputs = load_inputs(args.reports_dir)
    html = build_dashboard_html(
        cards=inputs["cards"],
        studies=inputs["studies"],
        projects=inputs["projects"],
        chpe=inputs["chpe"],
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"wrote dashboard: {out} ({len(html):,} bytes)")

    figures = {
        "seam_trends.svg": seam_trend_chart(inputs["cards"]),
        "corridor_values.svg":
            corridor_value_chart(inputs["cards"], inputs["studies"]),
        "project_bc.svg": project_bc_chart(inputs["projects"]),
        "chpe_event_study.svg":
            chpe_chart(inputs["chpe"]) if inputs["chpe"] else "",
    }
    figures_dir = Path(args.figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)
    for name, svg in figures.items():
        if not svg:
            continue
        path = figures_dir / name
        path.write_text(svg, encoding="utf-8")
        print(f"wrote figure: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
