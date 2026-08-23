#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"expected text not found in {path}: {old[:80]!r}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


behavior_anchor = """`path_readlink_*` returns the stored target text without resolving it.\n\nIf an externally created symbolic link contains an absolute or rooted target, `path_readlink_*` returns `ERR_PERMISSION`.\n\n## 4. Settled Wasm GC array rules\n"""
behavior_new = """`path_readlink_*` returns the stored target text without resolving it.\n\nIf an externally created symbolic link contains an absolute or rooted target, `path_readlink_*` returns `ERR_PERMISSION`.\n\n### 3.6 Final `.` and `..` components and trailing separators\n\n`path_open_*` and `path_stat_*` operate on a resolved target.\n\nFor these operations, a final `.` names the resolved current directory.\n\nA final `..` is resolved normally and returns `ERR_PERMISSION` if it would move above the supplied directory capability.\n\nFor these operations, a trailing `/` requires the resolved target to be a directory. A non-directory target returns `ERR_NOT_DIRECTORY`.\n\nEntry operations require a concrete final directory-entry name.\n\nThe following operations return `ERR_INVALID` when the final component is `.`, `..`, or empty because the path ends in `/`:\n\n- `path_create_dir_*`;\n- `path_remove_*`;\n- both source and destination of `path_rename_*`;\n- both source and destination entry positions of `path_link_*`;\n- the destination of `path_symlink_*`;\n- `path_readlink_*`.\n\nIntermediate `.` and `..` components continue to use the rules in section 3.2.\n\n### 3.7 Filesystem flag combinations\n\nFacet 0.1 fixes these combinations:\n\n- `OPEN_EXCLUSIVE` without `OPEN_CREATE` returns `ERR_INVALID`;\n- `OPEN_TRUNCATE` without requested `RIGHT_WRITE` returns `ERR_CAPABILITY`;\n- `OPEN_APPEND` without requested `RIGHT_WRITE` returns `ERR_CAPABILITY`;\n- `OPEN_DIRECTORY` combined with `OPEN_CREATE` or `OPEN_TRUNCATE` returns `ERR_INVALID`;\n- `path_remove_*` requires exactly one of `REMOVE_FILE` or `REMOVE_DIRECTORY`; zero or both bits returns `ERR_INVALID`;\n- rename flags `0` and `RENAME_REPLACE` both request ordinary replacement semantics;\n- `RENAME_NO_REPLACE` and `RENAME_EXCHANGE` are mutually exclusive with every other rename mode; any combined rename mode returns `ERR_INVALID`;\n- `fd_set_flags(fd, 0)` is a valid no-op for a preopen or directory descriptor;\n- setting `FD_APPEND` or `FD_NONBLOCK` on a preopen or directory descriptor returns `ERR_INVALID`.\n\nThese errors are scalar or authority validation results. They occur before the runtime mutates the external filesystem.\n\n### 3.8 Directory-entry inode semantics\n\nThe `inode` value returned by directory iteration is an opaque filesystem identity hint.\n\n`inode == 0` means that a stable inode-like value is unavailable.\n\nA guest MUST NOT treat zero as a real object identity.\n\nWhen a runtime returns a nonzero inode for an entry, it MUST identify the object named by that entry at the time the entry snapshot is created.\n\nFor an unchanged entry that continues to name the same object, a runtime MUST return the same nonzero inode after `dir_iter_rewind` during the lifetime of that directory resource.\n\nThe runtime MUST obtain metadata relative to the directory capability or from the directory enumeration itself. It MUST NOT resolve the entry through a process-global current working directory or another ambient namespace.\n\nIf entry enumeration succeeds but an optional descriptor-relative metadata query cannot provide an inode, the runtime MAY return inode zero rather than failing the iteration.\n\n### 3.9 Preopen authority identity\n\nA configured preopen selects one directory authority.\n\nThe runtime MUST materialize or otherwise pin that authority before guest code can observe it.\n\nAfter that authority is selected, later changes to an ambient host pathname MUST NOT cause the same Facet preopen to resolve to a different directory.\n\nTwo instances created from one activated configuration MUST NOT receive different directory authority merely because the host pathname used to configure the preopen was renamed, replaced, or retargeted between guest calls.\n\n## 4. Settled Wasm GC array rules\n"""
replace_once("spec/behavior.md", behavior_anchor, behavior_new)

old_dns = """### 7.7 DNS\n\n`dns_resolve_*` accepts `AF_UNSPEC`, `AF_INET4`, or `AF_INET6`.\n\nA name with no suitable address returns `ERR_NO_ENTRY`.\n\nA temporary resolver failure returns `ERR_AGAIN`.\n\nA permanent resolver or protocol failure returns `ERR_PROTOCOL` when that category applies.\n\nIf no more specific portable category applies, return `ERR_OTHER`.\n\nAn embedder network-policy denial returns `ERR_CAPABILITY`.\n\n`dns_next` uses an explicit `done` result.\n"""
new_dns = """### 7.7 DNS\n\n`dns_resolve_*` accepts `AF_UNSPEC`, `AF_INET4`, or `AF_INET6`.\n\nFacet 0.1 DNS names are ASCII DNS presentation strings.\n\nAfter decoding the selected `_i8`, `_i16`, or `_i32` guest representation, every code point in the DNS name MUST be in `U+0001..U+007f`. An embedded U+0000 or any non-ASCII code point returns `ERR_INVALID`.\n\nFacet 0.1 performs no implicit IDNA, UTS #46, locale, or Unicode-hostname conversion. A guest that needs an internationalized domain name MUST convert it to an ASCII IDNA form before calling Facet.\n\nThe runtime supplies the resulting ASCII name to its resolver without adding a NUL byte. Runtime resolver search-domain policy MAY still apply when the embedder permits it.\n\nA name with no suitable address returns `ERR_NO_ENTRY`.\n\nA temporary resolver failure returns `ERR_AGAIN`.\n\nA permanent resolver or protocol failure returns `ERR_PROTOCOL` when that category applies.\n\nIf no more specific portable category applies, return `ERR_OTHER`.\n\nAn embedder network-policy denial returns `ERR_CAPABILITY`.\n\n`dns_next` uses an explicit `done` result.\n"""
replace_once("spec/behavior.md", old_dns, new_dns)

# The manifest contract must preserve omission separately from an explicit empty grant.
tests_readme = Path("spec/tests/README.md")
text = tests_readme.read_text(encoding="utf-8")
manifest_note = """\n## Preopen rights omission and explicit zero authority\n\nThe host manifest distinguishes an omitted `rights` property from an explicit empty array.\n\n- If `rights` is omitted, the harness MAY apply its documented default preopen rights.\n- If `rights: []` is present, the harness MUST grant exactly zero Facet rights.\n\nA harness MUST preserve this distinction when it translates a manifest into runtime configuration. It MUST NOT treat an explicit empty array as a request for defaults.\n"""
if "## Preopen rights omission and explicit zero authority" not in text:
    tests_readme.write_text(text.rstrip() + "\n" + manifest_note, encoding="utf-8")

schema_path = Path("spec/tests/manifest.schema.json")
schema = json.loads(schema_path.read_text(encoding="utf-8"))
schema["$defs"]["preopen"]["properties"]["rights"]["description"] = (
    "Omitted selects the harness default. An explicit empty array grants exactly zero Facet rights."
)
schema_path.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")

checker = Path("spec/tests/tools/check_suite.py")
check_text = checker.read_text(encoding="utf-8")
check_text = check_text.replace(
    '        rights = preopen.get("rights", [])\n        if not isinstance(rights, list) or len(rights) != len(set(rights)):\n            fail(f"preopen rights must be a unique array: {manifest}")\n        unknown_rights = set(rights) - VALID_RIGHTS\n        if unknown_rights:\n            fail(f"unknown preopen rights in {manifest}: {sorted(unknown_rights)}")\n',
    '        # Omission and an explicit empty grant are semantically distinct.\n        # Validate a rights array only when the manifest actually contains it.\n        if "rights" in preopen:\n            rights = preopen["rights"]\n            if not isinstance(rights, list) or len(rights) != len(set(rights)):\n                fail(f"preopen rights must be a unique array: {manifest}")\n            unknown_rights = set(rights) - VALID_RIGHTS\n            if unknown_rights:\n                fail(f"unknown preopen rights in {manifest}: {sorted(unknown_rights)}")\n',
    1,
)
start = check_text.index("def check_imports(wast_paths: list[Path]) -> None:\n")
end = check_text.index("\ndef main() -> int:\n", start)
new_check_imports = '''def check_imports(wast_paths: list[Path]) -> None:\n    canonical_path = REPO / "spec" / "imports.wat"\n    if not canonical_path.exists():\n        print("warning: spec/imports.wat not present; skipped canonical import comparison")\n        return\n    canonical = import_signatures(canonical_path)\n    if not canonical:\n        fail("spec/imports.wat contains no facet function imports")\n\n    covered: dict[str, list[Path]] = {}\n    for path in wast_paths:\n        for name, signature in import_signatures(path).items():\n            expected = canonical.get(name)\n            if expected is None:\n                fail(f"test imports unknown canonical function facet.{name}: {path}")\n            if signature != expected:\n                fail(\n                    f"signature mismatch for facet.{name} in {path}: "\n                    f"got {signature}, expected {expected}"\n                )\n            covered.setdefault(name, []).append(path)\n\n    missing = sorted(set(canonical) - set(covered))\n    print(f"canonical import coverage: {len(covered)}/{len(canonical)}")\n    if missing:\n        fail(\n            "canonical Facet imports without WAST coverage: "\n            + ", ".join(f"facet.{name}" for name in missing)\n        )\n'''
check_text = check_text[:start] + new_check_imports + check_text[end:]
checker.write_text(check_text, encoding="utf-8")

# Direct regression for the release-blocking manifest distinction.
Path("spec/tests/filesystem/preopen-zero-rights.wast").write_text(''';; Facet conformance test: filesystem/preopen-zero-rights\n;; Purpose: An explicit empty preopen rights array grants exactly zero rights.\n;; Required profiles: core, filesystem, capabilities\n;;\n;; SPDX-License-Identifier: MIT\n\n(module\n  (import "facet" "fs_preopen_get" (func $get (param i32) (result i32 i32)))\n  (import "facet" "fd_rights" (func $rights (param i32) (result i64 i32)))\n  (func (export "run") (result i64 i32)\n    (local $dir i32) (local $e i32)\n    (call $get (i32.const 0))\n    (local.set $e)\n    (local.set $dir)\n    (if (i32.ne (local.get $e) (i32.const 0))\n      (then (return (i64.const 0) (local.get $e))))\n    (call $rights (local.get $dir))))\n(assert_return (invoke "run") (i64.const 0) (i32.const 0))\n''', encoding="utf-8")
Path("spec/tests/filesystem/preopen-zero-rights.json").write_text('''{\n  "version": 1,\n  "operations": [\n    {\n      "type": "run",\n      "preopens": [\n        {\n          "host": "../fixtures/readonly",\n          "guest": "/zero",\n          "rights": []\n        }\n      ]\n    },\n    {\n      "type": "wait",\n      "exit_code": 0\n    }\n  ]\n}\n''', encoding="utf-8")

replace_once(
    "README.md",
    "The repository contains 143 focused WAST tests.",
    "The repository contains 144 focused WAST tests.",
)
replace_once(
    "README.md",
    "The first reference implementation is planned as a Wago plugin.\n\nA second independent runtime prototype is planned before ABI stabilization.",
    "The first reference implementation is `jtenner/wago-facet`, a Wago plugin that executes the complete Facet 0.1 conformance suite.\n\nThe reference implementation is still being hardened for its first stable release. A second independent runtime prototype remains planned before ABI stabilization.",
)
replace_once(
    "ROADMAP.md",
    "Implement Facet as a Wago plugin.",
    "The Facet reference implementation is `jtenner/wago-facet`, implemented as a Wago plugin.",
)
replace_once(
    "ROADMAP.md",
    "- [ ] Connect the Wago plugin to the complete suite.",
    "- [x] Connect the Wago plugin to the complete suite.",
)

changelog = Path("CHANGELOG.md")
changelog_text = changelog.read_text(encoding="utf-8")
entry = """\n## Unreleased — Facet 0.1 stable-semantics hardening\n\n- Define filesystem flag-combination behavior, final path-component behavior, directory inode semantics, and preopen authority identity.\n- Define Facet 0.1 DNS names as ASCII presentation strings with no implicit IDNA conversion and reject embedded NUL.\n- Make omitted preopen rights distinct from `rights: []`; an explicit empty array grants zero rights.\n- Require bidirectional canonical-import coverage in the conformance source checker.\n- Add an explicit-zero-rights adversarial conformance test.\n\n"""
if "## Unreleased — Facet 0.1 stable-semantics hardening" not in changelog_text:
    # Preserve the existing title/header, but make the release-hardening delta prominent.
    first_break = changelog_text.find("\n", changelog_text.find("\n") + 1)
    changelog.write_text(changelog_text[: first_break + 1] + entry + changelog_text[first_break + 1 :], encoding="utf-8")

# Refresh the generated test catalog after adding the new fixture.
subprocess.run(["python3", "spec/tests/tools/generate_suite.py"], check=True)

# This staging machinery must not survive the generated commit.
Path(".release_hardening_spec.py").unlink(missing_ok=True)
Path(".github/workflows/release-hardening-spec.yml").unlink(missing_ok=True)
