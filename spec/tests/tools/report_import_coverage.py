#!/usr/bin/env python3
"""Require canonical Facet imports to be declared and directly invoked by WAST.

The declaration half of this gate proves that every canonical import appears in
at least one WAST source with the exact canonical signature. The invocation half
proves that at least one WAST contains a direct `call` or `return_call` to that
import's local function identifier. Neither metric alone proves semantic
correctness; runtime execution of the WAST assertions remains the behavioral
proof.

Facet 0.1 groups representation-equivalent imports into semantic matrix tests
instead of creating one import-only file per ABI symbol. The Wago reference
runtime additionally checks all 261 host registrations against spec/imports.wat
and instantiates the complete canonical import module before guest code runs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from check_suite import REPO, import_signatures, parse_sexpr, quoted_atom, walk_lists


def facet_import_aliases(roots: list[Any]) -> dict[str, set[str]]:
    """Return canonical import names mapped to their local WAT function ids."""
    aliases: dict[str, set[str]] = {}
    for node in walk_lists(roots):
        if len(node) < 4 or node[0] != "import":
            continue
        module = quoted_atom(node[1])
        name = quoted_atom(node[2])
        declaration = node[3]
        if (
            module != "facet"
            or name is None
            or not isinstance(declaration, list)
            or not declaration
            or declaration[0] != "func"
        ):
            continue
        local_ids = {
            item
            for item in declaration[1:]
            if isinstance(item, str) and item.startswith("$")
        }
        if local_ids:
            aliases.setdefault(name, set()).update(local_ids)
    return aliases


def direct_function_calls(roots: list[Any]) -> set[str]:
    """Return local function ids targeted by direct call/return_call instructions."""
    called: set[str] = set()
    for node in walk_lists(roots):
        for index, item in enumerate(node[:-1]):
            if not isinstance(item, str) or item not in {"call", "return_call"}:
                continue
            target = node[index + 1]
            if isinstance(target, str) and target.startswith("$"):
                called.add(target)
    return called


def main() -> int:
    canonical_path = REPO / "spec" / "imports.wat"
    canonical = import_signatures(canonical_path)
    if not canonical:
        raise SystemExit("spec/imports.wat contains no Facet imports")

    declared: dict[str, list[str]] = {}
    invoked: dict[str, list[str]] = {}
    for path in sorted((REPO / "spec" / "tests").rglob("*.wast")):
        relative = str(path.relative_to(REPO))
        signatures = import_signatures(path)
        roots = parse_sexpr(path.read_text(encoding="utf-8"))
        aliases = facet_import_aliases(roots)
        called = direct_function_calls(roots)

        for name, signature in signatures.items():
            expected = canonical.get(name)
            if expected is None:
                raise SystemExit(f"{path}: unknown Facet import {name}")
            if signature != expected:
                raise SystemExit(
                    f"{path}: signature mismatch for facet.{name}: "
                    f"got {signature}, expected {expected}"
                )
            declared.setdefault(name, []).append(relative)
            if aliases.get(name, set()) & called:
                invoked.setdefault(name, []).append(relative)

    missing_declarations = sorted(set(canonical) - set(declared))
    missing_invocations = sorted(set(canonical) - set(invoked))

    print(f"canonical imports: {len(canonical)}")
    print(f"canonical imports declared by WAST: {len(declared)}")
    print(
        "canonical imports without direct WAST declarations: "
        f"{len(missing_declarations)}"
    )
    for name in missing_declarations:
        print(f"  facet.{name}")

    print(f"canonical imports directly invoked by WAST: {len(invoked)}")
    print(
        "canonical imports without direct WAST invocation: "
        f"{len(missing_invocations)}"
    )
    for name in missing_invocations:
        print(f"  facet.{name}")

    if missing_declarations:
        print(
            "error: every canonical Facet import must be declared by at least "
            "one WAST source"
        )
        return 1
    if missing_invocations:
        print(
            "error: every canonical Facet import must be directly invoked by at "
            "least one WAST source"
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
