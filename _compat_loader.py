"""Helpers for top-level compatibility packages."""

from __future__ import annotations

from pathlib import Path
from typing import MutableMapping


ROOT = Path(__file__).resolve().parent


def load_package(namespace: MutableMapping[str, object], relative_dir: str) -> None:
    package_dir = ROOT / relative_dir
    namespace["__path__"] = [str(package_dir)]
    namespace["__file__"] = str(package_dir / "__init__.py")

    init_path = package_dir / "__init__.py"
    if init_path.exists():
        code = compile(init_path.read_text(encoding="utf-8"), str(init_path), "exec")
        exec(code, namespace)


def load_module(namespace: MutableMapping[str, object], relative_file: str) -> None:
    module_path = ROOT / relative_file
    namespace["__file__"] = str(module_path)
    code = compile(module_path.read_text(encoding="utf-8"), str(module_path), "exec")
    exec(code, namespace)
