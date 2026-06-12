"""Local import compatibility for the copied KOMPOSOS-IV source layout.

The source tree keeps several historical top-level packages under nested
directories so copied tests and modules can still use imports such as
``from core.category import Category``. Python imports ``sitecustomize`` during
startup when the repository root is on ``sys.path``; this keeps local runs
working without moving or deleting the copied source.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_ROOTS = (
    ROOT / "src",
    ROOT / "src" / "komposos_core",
    ROOT / "src" / "operadum",
    ROOT / "src" / "pronoia",
)

for path in reversed(SOURCE_ROOTS):
    text = str(path)
    if path.is_dir() and text not in sys.path:
        sys.path.insert(0, text)

