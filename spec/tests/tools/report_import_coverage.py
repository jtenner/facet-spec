#!/usr/bin/env python3
"""Require direct WAST import-declaration coverage for canonical Facet imports.

This gate answers one narrow question: which canonical imports are declared by
at least one WAST source with the exact canonical signature? A declaration does
not by itself prove that the WAST invokes the function, so this must not be
described as behavioral coverage.

Facet 0.1 requires every canonical import to participate in the WAST conformance
suite. The suite groups representation-equivalent imports into semantic matrix
tests instead of creating one import-only file per ABI symbol. Runtime execution
of those WASTs remains the behavioral proof.

The complete implementation/linkage direction is additionally enforced by the
Wago reference runtime: its canonical inventory gate checks every registered
import against spec/imports.wat, and its canonical-module integration gate
compiles and instantiates spec/imports.wat itself so all 261 canonical imports
must bind with structurally valid signatures before guest code can run.
"""

from __future__ import annotations

from pathlib import Path

from check_suite import REPO, import_signatures


def main() -> int:
    canonical_path = REPO / "spec" / "imports.wat"
    canonical = import_signatures(canonical_path)
    if not canonical:
        raise SystemExit("spec/imports.wat contains no Facet imports")

    declared: dict[str, list[str]] = {}
    for path in sorted((REPO / "spec" / "tests").rglob("*.wast")):
        for name, signature in import_signatures(path).items():
            expected = canonical.get(name)
            if expected is None:
                raise SystemExit(f"{path}: unknown Facet import {name}")
            if signature != expected:
                raise SystemExit(
                    f"{path}: signature mismatch for facet.{name}: "
                    f"got {signature}, expected {expected}"
                )
            declared.setdefault(name, []).append(str(path.relative_to(REPO)))

    missing = sorted(set(canonical) - set(declared))
    print(f"canonical imports: {len(canonical)}")
    print(f"canonical imports declared by WAST: {len(declared)}")
    print(f"canonical imports without direct WAST declarations: {len(missing)}")
    for name in missing:
        print(f"  facet.{name}")

    if missing:
        print("error: every canonical Facet import must be declared by at least one WAST source")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
