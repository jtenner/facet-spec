#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = ".github/scripts/rename_to_facets.py"
WORKFLOW = ".github/workflows/rename-facets.yml"


def tracked_files() -> list[Path]:
    out = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / p.decode() for p in out.split(b"\0") if p]


def rewrite_text(path: Path) -> None:
    rel = path.relative_to(ROOT).as_posix()
    if rel in {SELF, WORKFLOW}:
        return
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return

    original = text

    # Repository slug is singular facet-spec; specification/import namespace is plural Facets/facets.
    text = text.replace("jtenner/wpsi", "jtenner/facet-spec")
    text = text.replace("WPSI", "Facets")
    text = re.sub(r"\bwpsi\b", "facets", text)

    if rel == "SPEC.md":
        text = text.replace(
            "# Facets 0.1 — WebAssembly Portable System Interface",
            "# Facets 0.1",
            1,
        )
        marker = (
            "These functions perform the same semantic operation with different physical guest representations.\n"
        )
        addition = (
            marker
            + "\nThe representation-specific imported forms of one semantic system operation are called its **facets**. "
              "For example, `fd_read_mem32`, `fd_read_mem64`, and the `fd_read_array_*` family are explicit facets of the same `fd_read` operation. "
              "A facet is an ordinary Core WebAssembly import with a fixed signature; Facets does not perform runtime polymorphic dispatch between representations.\n"
        )
        if marker in text and "are called its **facets**" not in text:
            text = text.replace(marker, addition, 1)

    elif rel == "README.md":
        old = (
            "**Facets** is a small, Core-WebAssembly-native system interface designed for modern WebAssembly runtimes.\n"
        )
        new = (
            "**Facets** is a small, Core-WebAssembly-native system interface designed for modern WebAssembly runtimes. "
            "Each semantic system operation may expose multiple explicit representation **facets**—for example Memory32, Memory64, or Wasm GC-array forms—without runtime polymorphic dispatch.\n"
        )
        text = text.replace(old, new, 1)
        text = text.replace(
            "Facets is licensed under the [MIT License](LICENSE).",
            "Facets is licensed under the [MIT License](LICENSE).",
        )

    elif rel == "docs/design.md":
        anchor = "## Why a flat imported-function ABI?\n"
        section = (
            "## Why the name Facets?\n\n"
            "A system operation has one semantic meaning but may need several concrete Core Wasm signatures because the guest representation differs. "
            "Facets names those concrete forms **facets** of the operation. For example, Memory32, Memory64, and GC-array `fd_read` imports are separate explicit facets of `fd_read`.\n\n"
            "The term is deliberately not \"polymorphism\": the host does not inspect a call and choose a representation dynamically. "
            "The importing module selects a facet by importing a specific name and exact Core Wasm type. This keeps representation choice visible in the module ABI, linker diagnostics, and runtime implementation.\n\n"
        )
        if anchor in text and "## Why the name Facets?" not in text:
            text = text.replace(anchor, section + anchor, 1)

    elif rel == "CHANGELOG.md":
        marker = "### Decided\n\n"
        bullet = (
            "- The draft was renamed from WPSI to **Facets**. The Core Wasm import module is now `\"facets\"`, profiles use the `facets-*` prefix, and the repository is intended to live at `jtenner/facet-spec`. "
            "This is a pre-1.0 naming reset: `abi_version()` remains `1`, and the old `\"wpsi\"` namespace is not retained as a compatibility alias.\n"
        )
        # This bullet intentionally contains the legacy name, so rewrite it after inserting into a temporary placeholder.
        if marker in text and "pre-1.0 naming reset" not in text:
            placeholder = bullet.replace("WPSI", "<LEGACY_SPEC_NAME>").replace('`"wpsi"`', '`<LEGACY_IMPORT_NAME>`')
            text = text.replace(marker, marker + placeholder, 1)
            text = text.replace("<LEGACY_SPEC_NAME>", "the previous specification name")
            text = text.replace("<LEGACY_IMPORT_NAME>", "the previous import namespace")

    elif rel == "ROADMAP.md":
        marker = "## Phase 0 — Specification hygiene\n\n"
        bullet = "- [x] Name the specification **Facets**, use the `facets` import namespace and `facets-*` profile names, and target the `facet-spec` repository slug.\n"
        if marker in text and "target the `facet-spec` repository slug" not in text:
            text = text.replace(marker, marker + bullet, 1)

    if text != original:
        path.write_text(text, encoding="utf-8")


def main() -> None:
    for path in tracked_files():
        if path.is_file():
            rewrite_text(path)

    # The rename must be complete everywhere except this temporary migration machinery.
    remaining: list[str] = []
    legacy_upper = "WP" + "SI"
    legacy_lower = "wp" + "si"
    for path in tracked_files():
        rel = path.relative_to(ROOT).as_posix()
        if rel in {SELF, WORKFLOW} or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if legacy_upper in text or re.search(rf"\b{legacy_lower}\b", text):
            remaining.append(rel)

    if remaining:
        raise SystemExit("legacy specification naming remains in: " + ", ".join(remaining))


if __name__ == "__main__":
    main()
