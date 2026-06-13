# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""One-page, emailable summary: all four charts + plain-English text.

    python -m domains.grid.run_one_pager

Writes two self-contained files (attach either to an email):

- reports/figures/findings_one_pager.html  (opens in any browser)
- reports/figures/findings_one_pager.pdf   (one Letter page, needs PyMuPDF)

Charts are generated fresh from the committed reports, same as the
dashboard, and inlined — the files have no external references.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from domains.grid.dashboard import (
    chpe_chart,
    corridor_value_chart,
    load_inputs,
    project_bc_chart,
    seam_trend_chart,
)

TITLE = "US Grid Waste — The Findings in Four Pictures"
INTRO = (
    "Where the US electric grid loses money, what would fix it, and "
    "whether the fix pays for itself — measured from public data. "
    "Companion to the Master Guide; every chart is generated from the "
    "data, nothing is drawn by hand."
)

SECTIONS = [
    ("1. The problem is getting worse, fast",
     "Each line is a border between two grid operators; the height is "
     "the hourly price gap congestion creates there — a toll that "
     "traffic jams quietly charge on electricity. The blue New York-PJM "
     "toll more than tripled in one year. Rising line = fuller wires = "
     "customers paying more."),
    ("2. What each bottleneck costs per year",
     "The toll multiplied by the electricity that actually crossed: "
     "total dollars lost per year, per border. New York-PJM is about "
     "$160M/yr; the Midwest wind belt $31M/yr. A fix costing less per "
     "year than its bar pays for itself on congestion savings alone."),
    ("3. Does the named fix pay for itself?",
     "Real projects with published price tags, scored as benefit / cost. "
     "Above the dashed line, the project pays for itself. The two right "
     "bars are the same approved $164M North Dakota line under generous "
     "(1.65) and stingy (0.85) assumptions — truth in between, and its "
     "other benefits aren't counted. The tiny bar: the $6B Canada-NYC "
     "cable, fine for other reasons, never justifiable by border "
     "congestion alone."),
    ("4. Did the big new cable help New York?",
     "A 1,250 MW cable from Canada switched on 2026-05-13. Price gaps "
     "always grow from spring into summer, so compare 2026's growth "
     "against 2025's: it was slightly smaller — the cable helps, about "
     "$0.31/MWh so far — but the bars are still taller than last year. "
     "One cable did not cure the import problem. September's summer "
     "data decides."),
]

FOOTER = (
    "Reproduce every number yourself: "
    "github.com/Jayhawk314/komposos-grid (see REPRODUCE.md). "
    "Trust levels and caveats: MASTER_GUIDE.md section 6."
)


def build_charts() -> list[str]:
    inputs = load_inputs("reports")
    return [
        seam_trend_chart(inputs["cards"]),
        corridor_value_chart(inputs["cards"], inputs["studies"]),
        project_bc_chart(inputs["projects"]),
        chpe_chart(inputs["chpe"]) if inputs["chpe"] else "",
    ]


def build_html(charts: list[str]) -> str:
    cells = []
    for (heading, text), svg in zip(SECTIONS, charts):
        cells.append(
            f'<section class="cell"><h2>{heading}</h2>{svg}'
            f"<p>{text}</p></section>"
        )
    return (
        "<!doctype html>\n"
        '<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{TITLE}</title><style>{_CSS}</style></head><body>"
        f'<main><header><h1>{TITLE}</h1><p class="intro">{INTRO}</p></header>'
        f'<div class="grid">{"".join(cells)}</div>'
        f'<footer>{FOOTER}</footer></main></body></html>\n'
    )


_CSS = """
* { box-sizing: border-box; }
body { margin: 0; background: #fff; color: #17202a;
  font: 13px/1.45 Arial, Helvetica, sans-serif; }
main { max-width: 1060px; margin: 0 auto; padding: 18px; }
h1 { font-size: 22px; margin: 0 0 4px; }
h2 { font-size: 14px; margin: 0 0 6px; }
.intro, footer { color: #5b6673; font-size: 12px; margin: 0 0 10px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.cell { border: 1px solid #d8dee6; border-radius: 8px; padding: 10px; }
.cell svg { width: 100%; height: auto; }
.cell p { margin: 6px 0 0; color: #374151; }
footer { border-top: 1px solid #d8dee6; padding-top: 8px; margin-top: 14px; }
@media print {
  main { padding: 0; }
  .grid { gap: 8px; }
  .cell { break-inside: avoid; }
}
@media (max-width: 700px) { .grid { grid-template-columns: 1fr; } }
"""


def _ascii(text: str) -> str:
    """Base-14 PDF fonts are latin-1; swap typographic punctuation."""
    return (text.replace("—", "-").replace("–", "-")
                .replace("‘", "'").replace("’", "'")
                .replace("“", '"').replace("”", '"'))


def build_pdf(charts: list[str], out_path: Path) -> Path:
    """Compose a single Letter-size PDF page: title, 2x2 charts, captions."""
    import fitz

    page_w, page_h, margin = 612.0, 792.0, 30.0
    doc = fitz.open()
    page = doc.new_page(width=page_w, height=page_h)

    ink, muted = (0.09, 0.13, 0.16), (0.36, 0.40, 0.45)
    page.insert_textbox(
        fitz.Rect(margin, margin, page_w - margin, margin + 30),
        _ascii(TITLE), fontsize=15, fontname="hebo", color=ink)
    page.insert_textbox(
        fitz.Rect(margin, margin + 26, page_w - margin, margin + 62),
        _ascii(INTRO), fontsize=8, fontname="helv", color=muted)

    grid_top = margin + 64
    cell_w = (page_w - 2 * margin - 12) / 2
    chart_h = cell_w * 320.0 / 720.0  # chart aspect ratio
    caption_h = 86.0
    cell_h = 16 + chart_h + caption_h

    for idx, ((heading, text), svg) in enumerate(zip(SECTIONS, charts)):
        col, row = idx % 2, idx // 2
        x0 = margin + col * (cell_w + 12)
        y0 = grid_top + row * (cell_h + 14)
        page.insert_textbox(
            fitz.Rect(x0, y0, x0 + cell_w, y0 + 14),
            _ascii(heading), fontsize=9.5, fontname="hebo", color=ink)
        if svg:
            pix = fitz.open(stream=svg.encode("utf-8"),
                            filetype="svg").load_page(0).get_pixmap(
                                matrix=fitz.Matrix(2, 2))
            page.insert_image(
                fitz.Rect(x0, y0 + 16, x0 + cell_w, y0 + 16 + chart_h),
                pixmap=pix)
        page.insert_textbox(
            fitz.Rect(x0, y0 + 20 + chart_h, x0 + cell_w, y0 + cell_h + 8),
            _ascii(text), fontsize=7.8, fontname="helv",
            color=(0.22, 0.26, 0.32))

    page.insert_textbox(
        fitz.Rect(margin, page_h - margin - 16, page_w - margin, page_h - 8),
        _ascii(FOOTER), fontsize=7.5, fontname="helv", color=muted)
    doc.save(out_path)
    return out_path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Emailable one-page summary")
    parser.add_argument("--out-html",
                        default="reports/figures/findings_one_pager.html")
    parser.add_argument("--out-pdf",
                        default="reports/figures/findings_one_pager.pdf")
    parser.add_argument("--skip-pdf", action="store_true",
                        help="HTML only (no PyMuPDF needed)")
    args = parser.parse_args(argv)

    charts = build_charts()
    html_path = Path(args.out_html)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(build_html(charts), encoding="utf-8")
    print(f"wrote one-pager HTML: {html_path}")

    if not args.skip_pdf:
        try:
            pdf_path = build_pdf(charts, Path(args.out_pdf))
            print(f"wrote one-pager PDF: {pdf_path}")
        except ImportError:
            print("PyMuPDF not installed; skipped PDF (pip install pymupdf)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
