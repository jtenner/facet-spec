#!/usr/bin/env python3
"""Regenerate the deterministic Facet conformance-test catalog.

The WAST files are the canonical test sources. Their first metadata comments
encode the stable test id, purpose, required profiles, and optional test kind.
This tool derives ``catalog.json`` from those sources so contributors never
need to maintain two independent inventories.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent
ID_RE = re.compile(r"^;; Facet conformance test:\s*(\S+)\s*$", re.MULTILINE)
PURPOSE_RE = re.compile(r"^;; Purpose:\s*(.+?)\s*$", re.MULTILINE)
PROFILES_RE = re.compile(r"^;; Required profiles:\s*(.+?)\s*$", re.MULTILINE)
KIND_RE = re.compile(r"^;; Test kind:\s*(\S+)\s*$", re.MULTILINE)
VALID_KINDS = {"wast", "link", "harness"}


def metadata(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    test_id = ID_RE.search(text)
    purpose = PURPOSE_RE.search(text)
    profiles = PROFILES_RE.search(text)
    if not (test_id and purpose and profiles):
        raise SystemExit(f"missing canonical metadata comments: {path}")

    rel = path.relative_to(REPO).as_posix()
    expected_id = path.relative_to(ROOT).with_suffix("").as_posix()
    if test_id.group(1) != expected_id:
        raise SystemExit(
            f"test id/path mismatch in {path}: {test_id.group(1)!r} != {expected_id!r}"
        )

    kind_match = KIND_RE.search(text)
    if kind_match:
        kind = kind_match.group(1)
    elif expected_id.startswith("imports/"):
        kind = "link"
    else:
        kind = "wast"
    if kind not in VALID_KINDS:
        raise SystemExit(f"unknown test kind {kind!r}: {path}")

    profile_list = [item.strip() for item in profiles.group(1).split(",") if item.strip()]
    if not profile_list:
        raise SystemExit(f"empty profile list: {path}")

    return {
        "id": expected_id,
        "path": rel,
        "profiles": profile_list,
        "purpose": purpose.group(1),
        "kind": kind,
    }


def render() -> str:
    tests = [metadata(path) for path in sorted(ROOT.rglob("*.wast"))]
    catalog = {
        "version": 1,
        "specification": "Facet 0.1",
        "test_count": len(tests),
        "tests": tests,
    }
    return json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when catalog.json differs from the generated catalog",
    )
    args = parser.parse_args()

    destination = ROOT / "catalog.json"
    generated = render()
    if args.check:
        current = destination.read_text(encoding="utf-8") if destination.exists() else ""
        if current != generated:
            raise SystemExit(
                "catalog.json is stale; run "
                "python3 spec/tests/tools/generate_suite.py"
            )
        print(f"catalog is current ({len(list(ROOT.rglob('*.wast')))} tests)")
        return 0

    destination.write_text(generated, encoding="utf-8")
    print(f"wrote {destination.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
