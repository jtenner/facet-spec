#!/usr/bin/env python3
"""Report behavioral-test coverage for every canonical Facet import.

This is intentionally a report, not a requirement that every canonical import has
its own dedicated WAST. Exact canonical signatures are already enforced for every
import that a WAST uses. The Wago reference implementation performs the reverse
inventory check against spec/imports.wat so a canonical function cannot silently
be replaced while preserving the total binding count.
"""

from __future__ import annotations

from pathlib import Path

from check_suite import REPO, import_signatures


def main() -> int:
    canonical_path = REPO / "spec" / "imports.wat"
    canonical = import_signatures(canonical_path)
    if not canonical:
        raise SystemExit("spec/imports.wat contains no Facet imports")

    covered: dict[str, list[str]] = {}
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
            covered.setdefault(name, []).append(str(path.relative_to(REPO)))

    missing = sorted(set(canonical) - set(covered))
    print(f"canonical imports: {len(canonical)}")
    print(f"imports exercised by WAST: {len(covered)}")
    print(f"canonical imports without direct WAST coverage: {len(missing)}")
    for name in missing:
        print(f"  facet.{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
