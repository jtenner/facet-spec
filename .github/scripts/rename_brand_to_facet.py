#!/usr/bin/env python3
# One-shot migration from the old WPSI project branding to Facet.
from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SELF = ".github/scripts/rename_brand_to_facet.py"


def excluded(rel: str) -> bool:
    # Workflow files are updated separately because GitHub Actions tokens cannot
    # modify them without workflows permission.
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

    # The old expansion was tied to the WPSI initialism. Keep the meaning, but
    # make it a descriptive subtitle under the Facet name.
    text = text.replace(
        "WebAssembly Portable System Interface",
        "Portable System Interface for Core WebAssembly",
    )

    # Complete public and internal documentation branding migration.
    text = text.replace("WPSI", "Facet")
    text = text.replace("wpsi", "facet")

    if text != original:
        path.write_text(text, encoding="utf-8")


def main() -> None:
    for path in tracked_files():
        if path.is_file():
            rewrite(path)

    remaining: list[str] = []
    forbidden = ("WPSI", "wpsi", "WebAssembly Portable System Interface")

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
            "old project branding remains in: " + ", ".join(sorted(remaining))
        )


if __name__ == "__main__":
    main()
