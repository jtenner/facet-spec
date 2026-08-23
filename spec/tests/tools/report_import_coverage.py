#!/usr/bin/env python3
"""Report direct WAST import-declaration coverage for canonical Facet imports.

This report answers one narrow question: which canonical imports are declared by
at least one WAST source with the exact canonical signature? A declaration does
not prove that the WAST invokes the function, so this must not be described as
behavioral coverage.

The complete implementation/linkage direction is enforced by the Wago reference
runtime: its canonical inventory gate checks every registered import against
spec/imports.wat, and its canonical-module integration gate compiles and
instantiates spec/imports.wat itself so all 261 canonical imports must bind with
structurally valid signatures before guest code can run.
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
