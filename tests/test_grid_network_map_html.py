# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 James Hawkins <jhawk314@gmail.com>

"""The generated map must be valid JavaScript, not just valid Python.

An unescaped apostrophe inside a single-quoted JS string ("Each state's full
value") was shipped in a generated tooltip. It is a syntax error that breaks the
entire interactive map, and nothing caught it: the Streamlit smoke test only
checks that the HTML embeds without a *Python* exception, and never executes the
script. The map rendered as a blank panel while every test stayed green.

These tests parse the emitted script so a JS-level break fails the suite.
`node --check` is used when available for a real parse; otherwise a targeted
quote-balance check runs, so the guard degrades rather than disappearing.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
MAP = REPO / "docs" / "network_map.html"


def _script(html: str) -> str:
    blocks = re.findall(r"<script>(.*?)</script>", html, re.S)
    assert blocks, "no <script> block found in the generated map"
    return "\n".join(blocks)


@pytest.fixture(scope="module")
def script_source() -> str:
    if not MAP.exists():
        pytest.skip("network map not generated in this checkout")
    return _script(MAP.read_text(encoding="utf-8"))


def test_generated_javascript_parses(script_source, tmp_path):
    """Real parse via node when present."""
    node = shutil.which("node")
    if not node:
        pytest.skip("node not available for a real JS parse")
    js = tmp_path / "map.js"
    js.write_text(script_source, encoding="utf-8")
    result = subprocess.run([node, "--check", str(js)], capture_output=True, text=True)
    assert result.returncode == 0, (
        "generated map JavaScript does not parse:\n"
        f"{result.stderr.strip()[:800]}"
    )


def test_no_unescaped_apostrophe_inside_single_quoted_js_string(script_source):
    """The specific defect, checked without needing node.

    Flags a `'...'` literal containing a bare apostrophe between letters --
    "state's" -- which terminates the string early. Curly U+2019 and escaped
    \\' are both fine and are what the generator should emit.
    """
    offenders = [
        m.group(0)
        for m in re.finditer(r"'[^'\n\\]*[A-Za-z]'[A-Za-z][^'\n]*'", script_source)
    ]
    assert not offenders, (
        "unescaped apostrophe inside a single-quoted JS string; "
        "use \\u2019 or escape it:\n  " + "\n  ".join(offenders[:5])
    )


def test_reliability_value_is_not_presented_as_an_allocated_per_ba_figure(script_source):
    """Guards the labelling fix, not just the syntax.

    The tooltip previously read "Reliability value at stake", implying a per-BA
    share. It is the full value of every state the BA serves, counted again for
    every other BA serving those states -- a 3.5x overcount nationally.
    """
    assert "reliability_value_at_stake" not in script_source
    assert "Reliability value at stake" not in script_source, (
        "restore the 'in states served' wording -- the figure is not allocated"
    )
    if "reliability_value_states_usd" in script_source:
        assert "Not allocated to this BA" in script_source, (
            "the unallocated caveat must ship with the number"
        )


def test_daily_pulse_caption_discloses_its_age(script_source):
    """A stale pulse must not read as live; see network_map._daily_note."""
    html = MAP.read_text(encoding="utf-8")
    if "Daily pulse" in html:
        assert ("days old, not live" in html) or ("through" in html), (
            "daily pulse caption must state the date or its age"
        )
