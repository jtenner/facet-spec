#!/usr/bin/env python3
"""Static integrity checks for the WPSI conformance suite.

This intentionally depends only on Python's standard library. Full WAST syntax
validation is performed separately by ``parse_wast.py`` with a pinned
``wasm-tools`` binary.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent
VALID_OPS = {"run", "wait", "read", "connect", "send", "recv"}
VALID_RIGHTS = {
    "read", "write", "seek", "tell", "stat", "set-size", "sync",
    "open", "create", "remove", "rename", "link", "symlink", "readlink",
    "iterate",
}
VALID_PROTOCOLS = {"tcp", "udp", "http"}
METADATA = {
    "id": re.compile(r"^;; WPSI conformance test:\s*(\S+)\s*$", re.MULTILINE),
    "purpose": re.compile(r"^;; Purpose:\s*(.+?)\s*$", re.MULTILINE),
    "profiles": re.compile(r"^;; Required profiles:\s*(.+?)\s*$", re.MULTILINE),
}


def fail(message: str) -> None:
    raise SystemExit(message)


def reject_control_characters(path: Path, data: bytes) -> None:
    for offset, value in enumerate(data):
        if value < 0x20 and value not in {0x09, 0x0A, 0x0D}:
            fail(f"disallowed control byte 0x{value:02x} at {path}:{offset}")


def balanced_sexpr(text: str) -> bool:
    depth = 0
    in_string = False
    escaped = False
    line_comment = False
    block_depth = 0
    i = 0
    while i < len(text):
        char = text[i]
        following = text[i + 1] if i + 1 < len(text) else ""
        if line_comment:
            if char == "\n":
                line_comment = False
            i += 1
            continue
        if block_depth:
            if char == "(" and following == ";":
                block_depth += 1
                i += 2
                continue
            if char == ";" and following == ")":
                block_depth -= 1
                i += 2
                continue
            i += 1
            continue
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            i += 1
            continue
        if char == ";" and following == ";":
            line_comment = True
            i += 2
            continue
        if char == "(" and following == ";":
            block_depth = 1
            i += 2
            continue
        if char == '"':
            in_string = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                return False
        i += 1
    return depth == 0 and not in_string and block_depth == 0


def resolve_fixture(manifest: Path, value: str) -> Path:
    candidate = (manifest.parent / value).resolve()
    suite = ROOT.resolve()
    try:
        candidate.relative_to(suite)
    except ValueError as error:
        fail(f"fixture path escapes spec/tests: {manifest}: {value}")
    return candidate


def check_run(manifest: Path, operation: dict[str, Any]) -> None:
    allowed = {"type", "args", "env", "root", "preopens"}
    unknown = set(operation) - allowed
    if unknown:
        fail(f"unknown run fields in {manifest}: {sorted(unknown)}")
    if "root" in operation and "preopens" in operation:
        fail(f"run cannot contain both root and preopens: {manifest}")
    args = operation.get("args", [])
    if not isinstance(args, list) or not all(isinstance(item, str) for item in args):
        fail(f"run.args must be an array of strings: {manifest}")
    env = operation.get("env", {})
    if not isinstance(env, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in env.items()
    ):
        fail(f"run.env must map strings to strings: {manifest}")
    root = operation.get("root")
    if root is not None:
        if not isinstance(root, str):
            fail(f"run.root must be a string or null: {manifest}")
        if not resolve_fixture(manifest, root).is_dir():
            fail(f"run.root fixture directory does not exist: {manifest}: {root}")
    preopens = operation.get("preopens", [])
    if not isinstance(preopens, list):
        fail(f"run.preopens must be an array: {manifest}")
    guest_names: set[str] = set()
    for preopen in preopens:
        if not isinstance(preopen, dict):
            fail(f"preopen must be an object: {manifest}")
        unknown = set(preopen) - {"host", "guest", "rights"}
        if unknown or not {"host", "guest"} <= set(preopen):
            fail(f"invalid preopen fields in {manifest}: {preopen}")
        host, guest = preopen["host"], preopen["guest"]
        if not isinstance(host, str) or not isinstance(guest, str):
            fail(f"preopen host/guest must be strings: {manifest}")
        if guest in guest_names:
            fail(f"duplicate preopen guest display name {guest!r}: {manifest}")
        guest_names.add(guest)
        if not resolve_fixture(manifest, host).is_dir():
            fail(f"preopen fixture directory does not exist: {manifest}: {host}")
        rights = preopen.get("rights", [])
        if not isinstance(rights, list) or len(rights) != len(set(rights)):
            fail(f"preopen rights must be a unique array: {manifest}")
        unknown_rights = set(rights) - VALID_RIGHTS
        if unknown_rights:
            fail(f"unknown preopen rights in {manifest}: {sorted(unknown_rights)}")


def check_manifest(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) - {"version", "proposals", "operations"}:
        fail(f"invalid top-level manifest fields: {path}")
    if data.get("version") != 1:
        fail(f"bad manifest version: {path}")
    proposals = data.get("proposals", [])
    if not isinstance(proposals, list) or len(proposals) != len(set(proposals)) or not all(
        isinstance(item, str) for item in proposals
    ):
        fail(f"proposals must be a unique array of strings: {path}")
    operations = data.get("operations")
    if not isinstance(operations, list) or not operations:
        fail(f"manifest operations must be a nonempty array: {path}")
    if not isinstance(operations[0], dict) or operations[0].get("type") != "run":
        fail(f"manifest must start with run: {path}")

    running = False
    waited = False
    connection_ids: set[str] = set()
    for index, operation in enumerate(operations):
        if not isinstance(operation, dict):
            fail(f"operation {index} is not an object: {path}")
        operation_type = operation.get("type")
        if operation_type not in VALID_OPS:
            fail(f"unknown operation in {path}: {operation}")
        if operation_type == "run":
            if running or waited:
                fail(f"manifest may contain exactly one run operation: {path}")
            check_run(path, operation)
            running = True
        elif operation_type == "wait":
            if not running or waited:
                fail(f"wait must follow one active run: {path}")
            if set(operation) - {"type", "exit_code"}:
                fail(f"unknown wait fields: {path}")
            if "exit_code" in operation and not isinstance(operation["exit_code"], int):
                fail(f"wait.exit_code must be an integer: {path}")
            waited = True
        elif operation_type == "read":
            if not running or waited or set(operation) - {"type", "id", "payload"}:
                fail(f"invalid read operation ordering or fields: {path}")
            if operation.get("id", "stdout") not in {"stdout", "stderr"}:
                fail(f"read.id must be stdout or stderr: {path}")
            if not isinstance(operation.get("payload", ""), str):
                fail(f"read.payload must be a string: {path}")
        elif operation_type == "connect":
            if not running or waited or set(operation) - {"type", "id", "protocol_type"}:
                fail(f"invalid connect operation ordering or fields: {path}")
            connection_id = operation.get("id", "server")
            if not isinstance(connection_id, str) or connection_id in connection_ids:
                fail(f"connection ids must be unique strings: {path}")
            if operation.get("protocol_type", "tcp") not in VALID_PROTOCOLS:
                fail(f"unknown connect protocol: {path}")
            connection_ids.add(connection_id)
        else:
            if not running or waited or set(operation) - {"type", "id", "payload"}:
                fail(f"invalid {operation_type} operation ordering or fields: {path}")
            connection_id = operation.get("id")
            if connection_id not in connection_ids:
                fail(f"{operation_type} references unknown connection {connection_id!r}: {path}")
            if not isinstance(operation.get("payload", ""), str):
                fail(f"{operation_type}.payload must be a string: {path}")
    if not waited:
        fail(f"every explicit manifest run must be paired with wait: {path}")


def walk_lists(value: Any) -> Iterator[list[Any]]:
    if isinstance(value, list):
        yield value
        for item in value:
            yield from walk_lists(item)


def tokenize_sexpr(text: str) -> list[str]:
    tokens: list[str] = []
    i = 0
    while i < len(text):
        char = text[i]
        following = text[i + 1] if i + 1 < len(text) else ""
        if char.isspace():
            i += 1
        elif char == ";" and following == ";":
            i = text.find("\n", i + 2)
            if i < 0:
                break
        elif char == "(" and following == ";":
            depth = 1
            i += 2
            while i < len(text) and depth:
                following = text[i + 1] if i + 1 < len(text) else ""
                if text[i] == "(" and following == ";":
                    depth += 1
                    i += 2
                elif text[i] == ";" and following == ")":
                    depth -= 1
                    i += 2
                else:
                    i += 1
            if depth:
                fail("unterminated block comment")
        elif char in "()":
            tokens.append(char)
            i += 1
        elif char == '"':
            start = i
            i += 1
            while i < len(text):
                if text[i] == "\\":
                    i += 2
                elif text[i] == '"':
                    i += 1
                    break
                else:
                    i += 1
            else:
                fail("unterminated WAT string")
            tokens.append(text[start:i])
        else:
            start = i
            while i < len(text) and not text[i].isspace() and text[i] not in "()":
                i += 1
            tokens.append(text[start:i])
    return tokens


def parse_sexpr(text: str) -> list[Any]:
    roots: list[Any] = []
    stack: list[list[Any]] = []
    for token in tokenize_sexpr(text):
        if token == "(":
            node: list[Any] = []
            if stack:
                stack[-1].append(node)
            else:
                roots.append(node)
            stack.append(node)
        elif token == ")":
            if not stack:
                fail("unbalanced closing parenthesis")
            stack.pop()
        else:
            if not stack:
                roots.append(token)
            else:
                stack[-1].append(token)
    if stack:
        fail("unbalanced opening parenthesis")
    return roots


def quoted_atom(value: Any) -> str | None:
    if isinstance(value, str) and len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return None


def normalize_type(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(normalize_type(item) for item in value if not (isinstance(item, str) and item.startswith("$")))
    return value


def import_signatures(path: Path) -> dict[str, tuple[tuple[Any, ...], tuple[Any, ...]]]:
    roots = parse_sexpr(path.read_text(encoding="utf-8"))
    signatures: dict[str, tuple[tuple[Any, ...], tuple[Any, ...]]] = {}
    for node in walk_lists(roots):
        if len(node) < 4 or node[0] != "import":
            continue
        module = quoted_atom(node[1])
        name = quoted_atom(node[2])
        declaration = node[3]
        if module != "wpsi" or name is None or not isinstance(declaration, list) or not declaration or declaration[0] != "func":
            continue
        params: list[Any] = []
        results: list[Any] = []
        for field in declaration[1:]:
            if not isinstance(field, list) or not field:
                continue
            if field[0] == "param":
                params.extend(normalize_type(item) for item in field[1:] if not (isinstance(item, str) and item.startswith("$")))
            elif field[0] == "result":
                results.extend(normalize_type(item) for item in field[1:] if not (isinstance(item, str) and item.startswith("$")))
        signature = (tuple(params), tuple(results))
        existing = signatures.get(name)
        if existing is not None and existing != signature:
            fail(f"conflicting signatures for wpsi.{name} in {path}")
        signatures[name] = signature
    return signatures


def check_imports(wast_paths: list[Path]) -> None:
    canonical_path = REPO / "spec" / "imports.wat"
    if not canonical_path.exists():
        print("warning: spec/imports.wat not present; skipped canonical import comparison")
        return
    canonical = import_signatures(canonical_path)
    if not canonical:
        fail("spec/imports.wat contains no wpsi function imports")
    for path in wast_paths:
        for name, signature in import_signatures(path).items():
            expected = canonical.get(name)
            if expected is None:
                fail(f"test imports unknown canonical function wpsi.{name}: {path}")
            if signature != expected:
                fail(
                    f"signature mismatch for wpsi.{name} in {path}: "
                    f"got {signature}, expected {expected}"
                )


def main() -> int:
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "generate_suite.py"), "--check"],
        check=True,
    )

    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    tests = catalog.get("tests", [])
    if catalog.get("test_count") != len(tests):
        fail("catalog test_count does not match tests array")
    catalog_paths = [entry.get("path") for entry in tests]
    if len(catalog_paths) != len(set(catalog_paths)):
        fail("catalog contains duplicate test paths")
    actual_paths = sorted(ROOT.rglob("*.wast"))
    actual = {path.relative_to(REPO).as_posix() for path in actual_paths}
    expected = set(catalog_paths)
    if expected != actual:
        fail(f"catalog mismatch: missing={sorted(actual - expected)}, stale={sorted(expected - actual)}")

    for path in actual_paths:
        data = path.read_bytes()
        reject_control_characters(path, data)
        text = data.decode("utf-8")
        relative_id = path.relative_to(ROOT).with_suffix("").as_posix()
        for label, pattern in METADATA.items():
            match = pattern.search(text)
            if not match:
                fail(f"missing {label} metadata comment: {path}")
            if label == "id" and match.group(1) != relative_id:
                fail(f"test id/path mismatch: {path}: {match.group(1)!r}")
        if "SPDX-License-Identifier: MIT" not in text:
            fail(f"missing SPDX marker: {path}")
        if not balanced_sexpr(text):
            fail(f"unbalanced WAST: {path}")
        if 'import "wpsi"' not in text:
            fail(f"test has no WPSI import: {path}")
        manifest = path.with_suffix(".json")
        if manifest.exists():
            check_manifest(manifest)

    for manifest in sorted(ROOT.rglob("*.json")):
        if manifest.name in {"catalog.json", "manifest.schema.json"}:
            continue
        if not manifest.with_suffix(".wast").exists():
            fail(f"orphan test manifest: {manifest}")

    forbidden = list(ROOT.rglob("*.wasm")) + list(ROOT.rglob("*.cleanup"))
    if forbidden:
        fail(f"generated/runtime artifacts checked into source tree: {forbidden}")

    check_imports(actual_paths)
    print(f"validated {len(actual_paths)} WAST tests and their manifests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
