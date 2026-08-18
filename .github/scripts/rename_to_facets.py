#!/usr/bin/env python3
# One-shot migration for the Core Wasm import-module namespace.
# This branch runs the final validated namespace migration.
from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SELF = ".github/scripts/rename_to_facets.py"


def excluded(rel: str) -> bool:
    # GitHub Actions tokens cannot update workflow files without workflows
    # permission. Migrate those files separately after the validated PR lands.
    return rel == SELF or rel.startswith(".github/workflows/")


def tracked_files() -> list[Path]:
    out = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / part.decode() for part in out.split(b"\0") if part]


def rewrite(path: Path) -> None:
    rel = path.relative_to(ROOT).as_posix()
    if excluded(rel):
        return

    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return

    original = text

    # Change only the Core Wasm import-module namespace. Profile names and the
    # specification name are separate concepts and are intentionally untouched.
    text = text.replace('"wpsi"', '"facet"')
    text = text.replace("`wpsi`", "`facet`")
    text = text.replace("wpsi.", "facet.")
    text = text.replace("wpsi-imports", "facet-imports")

    if rel == "CHANGELOG.md":
        marker = "### Decided\n\n"
        bullet = (
            "- The Core WebAssembly import module is `facet`. "
            "The previous import-module namespace is not retained as a compatibility alias.\n"
        )
        if marker in text and "The Core WebAssembly import module is `facet`" not in text:
            text = text.replace(marker, marker + bullet, 1)

    if text != original:
        path.write_text(text, encoding="utf-8")


def main() -> None:
    for path in tracked_files():
        if path.is_file():
            rewrite(path)

    remaining: list[str] = []
    forbidden = ('"wpsi"', "`wpsi`", "wpsi.", "wpsi-imports")

    for path in tracked_files():
        rel = path.relative_to(ROOT).as_posix()
        if excluded(rel) or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if any(item in text for item in forbidden):
            remaining.append(rel)

    if remaining:
        raise SystemExit(
            "old import-module namespace remains in: " + ", ".join(remaining)
        )


if __name__ == "__main__":
    main()
