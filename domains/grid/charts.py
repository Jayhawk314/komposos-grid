# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins / Komposos-Labs

"""Pure-Python SVG charts for the grid-waste reports and dashboard.

No matplotlib, no JavaScript: charts are generated as inline SVG so
the dashboard stays a single static file and the markdown reports can
embed crisp figures GitHub renders natively. Palette and typography
match the report CSS.
"""

from __future__ import annotations

import math
from html import escape
from typing import Dict, List, Mapping, Sequence

PALETTE = ["#1f6feb", "#1f8f5f", "#b45309", "#7c3aed", "#be185d", "#0e7490"]
INK = "#17202a"
MUTED = "#5b6673"
LINE = "#d8dee6"
FONT = "font-family=\"Arial, Helvetica, sans-serif\""


def nice_max(value: float) -> float:
    """Round up to a 1/2/5 x 10^k ceiling so axis ticks look sane."""
    if value <= 0:
        return 1.0
    exp = math.floor(math.log10(value))
    base = value / (10 ** exp)
    for step in (1.0, 2.0, 5.0, 10.0):
        if base <= step:
            return step * (10 ** exp)
    return 10.0 ** (exp + 1)


def line_chart(
    x_labels: Sequence[object],
    series: Mapping[str, Sequence[float | None]],
    *,
    title: str,
    y_label: str,
    width: int = 720,
    height: int = 320,
    value_fmt: str = "{:.2f}",
) -> str:
    """Multi-series line chart. None values create gaps in a series."""
    left, right, top, bottom = 56, 16, 44, 56
    plot_w, plot_h = width - left - right, height - top - bottom
    values = [v for vs in series.values() for v in vs if v is not None]
    y_max = nice_max(max(values) if values else 1.0)
    n = max(len(x_labels), 1)

    def x_at(i: int) -> float:
        return left + (plot_w * (i + 0.5) / n)

    def y_at(v: float) -> float:
        return top + plot_h * (1.0 - v / y_max)

    parts = [_frame(width, height, title, y_label, y_max, y_at, left, plot_w)]
    for i, label in enumerate(x_labels):
        parts.append(_text(x_at(i), height - bottom + 18, str(label),
                           anchor="middle", fill=MUTED, size=12))
    label_ys: Dict[int, List[float]] = {}
    legend_x = left
    for idx, (name, vals) in enumerate(series.items()):
        color = PALETTE[idx % len(PALETTE)]
        points = [(i, x_at(i), y_at(v), v) for i, v in enumerate(vals)
                  if v is not None]
        if len(points) >= 2:
            path = " ".join(f"{x:.1f},{y:.1f}" for _, x, y, _ in points)
            parts.append(f'<polyline points="{path}" fill="none" '
                         f'stroke="{color}" stroke-width="2.5"/>')
        for i, x, y, v in points:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" '
                         f'fill="{color}"/>')
            # nudge the value label below the point if another series
            # already labelled nearby at this x position
            label_y = y - 9
            if any(abs(label_y - prior) < 13 for prior in
                   label_ys.get(i, [])):
                label_y = y + 19
            label_ys.setdefault(i, []).append(label_y)
            parts.append(_text(x, label_y, value_fmt.format(v),
                               anchor="middle", fill=INK, size=11))
        parts.append(f'<rect x="{legend_x}" y="{height - 26}" width="11" '
                     f'height="11" fill="{color}" rx="2"/>')
        parts.append(_text(legend_x + 16, height - 16, name, fill=MUTED,
                           size=12))
        legend_x += 16 + 7 * len(name) + 24
    return _svg(width, height, parts)


def bar_chart(
    categories: Sequence[str],
    series: Mapping[str, Sequence[float]],
    *,
    title: str,
    y_label: str,
    ref_line: float | None = None,
    ref_label: str = "",
    width: int = 720,
    height: int = 320,
    value_fmt: str = "{:.2f}",
) -> str:
    """Grouped vertical bars with an optional reference line."""
    left, right, top, bottom = 56, 16, 44, 96
    plot_w, plot_h = width - left - right, height - top - bottom
    values = [v for vs in series.values() for v in vs]
    if ref_line is not None:
        values.append(ref_line)
    y_max = nice_max(max(values) if values else 1.0)

    def y_at(v: float) -> float:
        return top + plot_h * (1.0 - v / y_max)

    n_cat, n_ser = max(len(categories), 1), max(len(series), 1)
    slot = plot_w / n_cat
    bar_w = min(slot * 0.7 / n_ser, 48)

    parts = [_frame(width, height, title, y_label, y_max, y_at, left, plot_w)]
    for ci, cat in enumerate(categories):
        group_w = bar_w * n_ser
        x0 = left + slot * ci + (slot - group_w) / 2
        for si, (name, vals) in enumerate(series.items()):
            v = vals[ci]
            x = x0 + bar_w * si
            parts.append(
                f'<rect x="{x:.1f}" y="{y_at(v):.1f}" width="{bar_w:.1f}" '
                f'height="{(y_at(0) - y_at(v)):.1f}" '
                f'fill="{PALETTE[si % len(PALETTE)]}" rx="2"/>')
            parts.append(_text(x + bar_w / 2, y_at(v) - 5,
                               value_fmt.format(v), anchor="middle",
                               fill=INK, size=11))
        parts.append(_wrapped_label(left + slot * (ci + 0.5),
                                    height - bottom + 16, cat))
    if ref_line is not None:
        y = y_at(ref_line)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" '
                     f'x2="{left + plot_w}" y2="{y:.1f}" stroke="#be185d" '
                     'stroke-width="1.5" stroke-dasharray="6 4"/>')
        if ref_label:
            parts.append(_text(left + plot_w, y - 6, ref_label,
                               anchor="end", fill="#be185d", size=11))
    legend_x = left
    for si, name in enumerate(series):
        parts.append(f'<rect x="{legend_x}" y="{height - 22}" width="11" '
                     f'height="11" fill="{PALETTE[si % len(PALETTE)]}" '
                     'rx="2"/>')
        parts.append(_text(legend_x + 16, height - 12, name, fill=MUTED,
                           size=12))
        legend_x += 16 + 7 * len(name) + 24
    return _svg(width, height, parts)


def _frame(width, height, title, y_label, y_max, y_at, left, plot_w):
    parts = [_text(left, 22, title, fill=INK, size=15, weight="bold"),
             _text(left, 38, y_label, fill=MUTED, size=12)]
    ticks = 4
    for t in range(ticks + 1):
        v = y_max * t / ticks
        y = y_at(v)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" '
                     f'x2="{left + plot_w}" y2="{y:.1f}" stroke="{LINE}" '
                     'stroke-width="1"/>')
        label = f"{v:g}" if y_max < 1000 else f"{v:,.0f}"
        parts.append(_text(left - 8, y + 4, label, anchor="end",
                           fill=MUTED, size=11))
    return "".join(parts)


def _wrapped_label(x: float, y: float, text: str) -> str:
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > 20 and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    lines.append(current)
    return "".join(
        _text(x, y + 13 * i, line, anchor="middle", fill=MUTED, size=11)
        for i, line in enumerate(lines[:4])
    )


def _text(x, y, content, *, anchor="start", fill=INK, size=12,
          weight="normal") -> str:
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'fill="{fill}" font-size="{size}" font-weight="{weight}" '
            f'{FONT}>{escape(str(content))}</text>')


def _svg(width: int, height: int, parts: Sequence[str]) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {width} {height}" role="img" '
            f'style="max-width:100%;height:auto;background:#ffffff">'
            + "".join(parts) + "</svg>")
