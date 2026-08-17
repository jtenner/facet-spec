#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TESTS = ROOT / "spec/tests"

SKIP = {
    "filesystem/scratch-quota-reported.wast",
    "filesystem/scratch-roundtrip.wast",
    "filesystem/scratch-starts-empty.wast",
    "imports/profile-surface.wast",
}

FULL_RIGHTS = [
    "read", "write", "seek", "tell", "stat", "set-size", "sync",
    "open", "create", "remove", "rename", "link", "symlink", "readlink",
    "iterate",
]

SCRATCH_IMPORT = re.compile(
    r'\(import "wpsi" "fs_scratch" \(func (\$[^\s()]+) \(result i32 i32\)\)\)'
)


def load_manifest(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "version": 1,
        "operations": [
            {"type": "run"},
            {"type": "wait", "exit_code": 0},
        ],
    }


def provision_tilde(manifest: dict) -> int:
    operations = manifest.setdefault("operations", [])
    run = next((op for op in operations if isinstance(op, dict) and op.get("type") == "run"), None)
    if run is None:
        raise SystemExit("manifest has no run operation")

    tilde = {
        "host": "../fixtures/write",
        "guest": "~",
        "rights": FULL_RIGHTS,
    }

    if "preopens" in run:
        preopens = run["preopens"]
        if not isinstance(preopens, list):
            raise SystemExit("run.preopens is not a list")
        for index, preopen in enumerate(preopens):
            if isinstance(preopen, dict) and preopen.get("guest") == "~":
                return index
        preopens.append(tilde)
        return len(preopens) - 1

    if "root" in run:
        root = run.pop("root")
        preopens = []
        if root is not None:
            preopens.append({"host": root, "guest": "/"})
        preopens.append(tilde)
        run["preopens"] = preopens
        return len(preopens) - 1

    run["preopens"] = [tilde]
    return 0


def convert_wast(path: Path) -> bool:
    rel = str(path.relative_to(TESTS))
    if rel in SKIP:
        return False

    text = path.read_text(encoding="utf-8")
    matches = list(SCRATCH_IMPORT.finditer(text))
    if not matches:
        return False

    manifest_path = path.with_suffix(".json")
    manifest = load_manifest(manifest_path)
    tilde_index = provision_tilde(manifest)

    locals_: list[str] = []
    for match in matches:
        local = match.group(1)
        locals_.append(local)
        replacement = (
            f'(import "wpsi" "fs_preopen_get" '
            f'(func {local} (param i32) (result i32 i32)))'
        )
        text = text.replace(match.group(0), replacement, 1)

    for local in locals_:
        call = re.compile(rf'\(call\s+{re.escape(local)}\s*\)')
        text, count = call.subn(f"(call {local} (i32.const {tilde_index}))", text)
        if count == 0:
            raise SystemExit(f"no calls found for converted {local} in {rel}")

    path.write_text(text, encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"converted {rel} -> ~ preopen index {tilde_index}")
    return True


write_fixture = TESTS / "fixtures/write"
write_fixture.mkdir(parents=True, exist_ok=True)
(write_fixture / ".gitkeep").write_text(
    "Writable preopen fixture template. Test runners must provide an isolated per-test view.\n",
    encoding="utf-8",
)

converted = 0
for wast in sorted(TESTS.rglob("*.wast")):
    if convert_wast(wast):
        converted += 1

if converted == 0:
    raise SystemExit("no incidental scratch consumers were converted")

# Writable fixture templates must never be mutated in place by a runner. This makes
# repeated conformance runs deterministic without introducing a scratch-specific
# manifest primitive.
readme = TESTS / "README.md"
text = readme.read_text(encoding="utf-8")
marker = """Supported manifest right names are:

```text
read write seek tell stat set-size sync
open create remove rename link symlink readlink iterate
```
"""
addition = marker + """
A preopen that grants mutation rights MUST be backed by an isolated per-test view
of its fixture directory. Runners MUST NOT mutate the checked-in fixture tree in
place. A fresh run starts from the committed fixture contents; copying, overlay
filesystems, temporary directories, or equivalent isolation are all acceptable.
"""
if marker not in text:
    raise SystemExit("conformance README rights marker not found")
readme.write_text(text.replace(marker, addition, 1), encoding="utf-8")

print(f"converted {converted} ordinary tests from fs_scratch to explicit preopens")
