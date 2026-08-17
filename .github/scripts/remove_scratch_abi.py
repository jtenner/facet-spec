#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text.rstrip() + "\n", encoding="utf-8")


def replace_section(text: str, start: str, end: str, replacement: str) -> str:
    a = text.index(start)
    b = text.index(end, a)
    return text[:a] + replacement.rstrip() + "\n\n" + text[b:]


# ---------------------------------------------------------------------------
# SPEC.md
# ---------------------------------------------------------------------------

spec = read("SPEC.md")
spec = spec.replace(
    "4. preserve capability-oriented sandboxing while giving filesystem-enabled instances private writable scratch storage by default.",
    "4. preserve capability-oriented sandboxing while exposing filesystem authority only through explicit directory capabilities and preopens.",
)
spec = spec.replace(
    "`wpsi-filesystem` defines private scratch storage, preopens, descriptors, directory iteration, and path operations.",
    "`wpsi-filesystem` defines preopens, descriptors, directory iteration, and path operations.",
)
spec = replace_section(
    spec,
    "## 10. Capabilities and scratch storage",
    "## 11. Rights and flags",
    r'''## 10. Capabilities and filesystem preopens

WPSI resource handles represent authority.

Host filesystem and networking authority MUST be explicitly granted by the embedder.

A child resource MUST NOT gain greater authority than the capability from which it was derived.

WPSI does not define a mandatory scratch filesystem, home filesystem, or other automatically allocated writable storage. A conforming filesystem implementation MAY expose no preopens at all.

Filesystem roots supplied by the embedder are ordinary directory capabilities enumerated through the preopen APIs. Their guest-visible display names do not create authority beyond the directory handle and rights that were explicitly granted.

An embedder MAY provide an ordinary preopen whose display name is exactly `~`. This is the conventional WPSI name for a guest home/private writable area when an environment wants to provide one, but the name has no special ABI behavior:

- `~` does not implicitly refer to the host user's home directory;
- it does not imply particular rights, quota, persistence, backing storage, or lifetime;
- it may be omitted entirely in constrained environments;
- if the embedder deliberately maps it to host storage, that authority exists only because the directory was explicitly preopened.

The Core WPSI path ABI remains directory-handle-relative. It does not parse or expand `~` inside path operands. Higher-level bindings, libc implementations, and language runtimes MAY interpret `~/x` by locating a preopen whose display name is `~` and issuing the ordinary WPSI path operation relative to that directory handle with `x` as the relative path.'''
)

spec = replace_section(
    spec,
    "## 16. Filesystem roots",
    "## 17. Descriptor metadata",
    r'''## 16. Filesystem preopens

```text
fs_preopen_count() -> (count: i32, errno: i32)
fs_preopen_get(index: i32) -> (directory: i32, errno: i32)

fs_preopen_name_len_i8(index: i32, wtf: i32)  -> (units: i64, errno: i32)
fs_preopen_name_len_i16(index: i32, wtf: i32) -> (units: i64, errno: i32)
fs_preopen_name_len_i32(index: i32, wtf: i32) -> (units: i64, errno: i32)

fs_preopen_name_read_mem32_i8(index: i32, wtf: i32,
                              memory: i32, pointer: i32, capacity_units: i32)
  -> (units_written: i64, errno: i32)
fs_preopen_name_read_mem32_i16(...) -> (units_written: i64, errno: i32)
fs_preopen_name_read_mem32_i32(...) -> (units_written: i64, errno: i32)

fs_preopen_name_read_mem64_i8(index: i32, wtf: i32,
                              memory: i32, pointer: i64, capacity_units: i64)
  -> (units_written: i64, errno: i32)
fs_preopen_name_read_mem64_i16(...) -> (units_written: i64, errno: i32)
fs_preopen_name_read_mem64_i32(...) -> (units_written: i64, errno: i32)

fs_preopen_name_read_into_array_i8(index: i32, wtf: i32,
                                   destination: ref array, offset: i32, capacity_units: i32)
  -> (units_written: i64, errno: i32)
fs_preopen_name_read_into_array_i16(...) -> (units_written: i64, errno: i32)
fs_preopen_name_read_into_array_i32(...) -> (units_written: i64, errno: i32)

fs_preopen_name_read_array_i8(index: i32, wtf: i32)
  -> (value: ref null $caller_i8_array, errno: i32)
fs_preopen_name_read_array_i16(index: i32, wtf: i32)
  -> (value: ref null $caller_i16_array, errno: i32)
fs_preopen_name_read_array_i32(index: i32, wtf: i32)
  -> (value: ref null $caller_i32_array, errno: i32)
```

Preopen ordering and display names MUST remain stable for the lifetime of the instance.

A preopen named `~` is optional and is otherwise indistinguishable from any other preopen. Its absence does not make a filesystem implementation nonconforming.'''
)
write("SPEC.md", spec)


# ---------------------------------------------------------------------------
# Canonical imports
# ---------------------------------------------------------------------------

imports = read("spec/imports.wat")
for line in [
    '  (import "wpsi" "fs_scratch" (func $fs_scratch (result i32 i32)))\n',
    '  (import "wpsi" "fs_scratch_limits" (func $fs_scratch_limits (result i64 i64 i32)))\n',
    '  (import "wpsi" "fs_scratch_usage" (func $fs_scratch_usage (result i64 i64 i32)))\n',
]:
    if line not in imports:
        raise SystemExit(f"missing canonical scratch import: {line.strip()}")
    imports = imports.replace(line, "", 1)
imports = imports.replace("  ;; Filesystem roots\n", "  ;; Filesystem preopens\n", 1)
write("spec/imports.wat", imports)


# ---------------------------------------------------------------------------
# Normative behavior
# ---------------------------------------------------------------------------

behavior = read("spec/behavior.md")
marker = """A path beginning with `/` is forbidden and returns `ERR_PERMISSION`.

There is no process-global host current working directory and no path operation may use an ambient host root."""
replacement = """A path beginning with `/` is forbidden and returns `ERR_PERMISSION`.

There is no process-global host current working directory and no path operation may use an ambient host root.

`~` is not special syntax in a raw WPSI path operand. If an embedder provides a preopen whose display name is `~`, a higher-level binding may resolve `~/x` by selecting that preopen and passing `x` as the relative path. Without that binding-level resolution, a `~` component is an ordinary filename component."""
if marker not in behavior:
    raise SystemExit("behavior path marker missing")
behavior = behavior.replace(marker, replacement, 1)
behavior = behavior.replace("- scratch filesystem persistence across embedder/runtime restarts;\n", "", 1)
write("spec/behavior.md", behavior)


# ---------------------------------------------------------------------------
# Informative docs
# ---------------------------------------------------------------------------

open_questions = r'''# WPSI 0.1 Open Questions

This file tracks decisions intentionally deferred while WPSI 0.1 is implemented and tested.

Resolved questions are removed from this file and recorded in the normative specification, [`spec/behavior.md`](../spec/behavior.md), or the design rationale.

## 1. Scatter/gather nested GC arrays

The current GC `readv/writev` form uses an outer array of child-array references and consumes complete logical byte views for selected children.

Questions:

- Do we need per-child slices/offsets?
- If yes, should those be represented by structs, parallel arrays, or a separate descriptor array type?
- Is full-child scatter/gather enough for 0.1?

Current preference: keep 0.1 simple and benchmark real language lowering before adding descriptors.

## 2. Async extension

Asynchronous host operations are deliberately omitted because they require retained buffer ownership/lifetime semantics.

Before adding async operations, define:

- whether guest memory/GC buffers can remain borrowed across suspension;
- how memory growth and GC movement interact with retained borrows;
- cancellation;
- resource ownership on dropped futures/continuations;
- whether async operations use handles, callbacks, stack switching, or another Core Wasm mechanism.

## 3. Profile versioning

The draft uses one `abi_version()` value and import presence as feature detection.

Questions:

- Do profiles need independent versions?
- Should there be a compact scalar feature-query API?
- Is normal missing-import failure enough for most tooling?

Current preference: keep import presence authoritative and add explicit profile versioning only if real runtime negotiation requires it.
'''
write("docs/open-questions.md", open_questions)

# Design rationale: replace the special filesystem rationale with the ordinary-preopen rationale.
design = read("docs/design.md")
design = replace_section(
    design,
    "## Why a private scratch filesystem?",
    "## Why opaque i32 resource handles?",
    r'''## Why is `~` an ordinary preopen instead of a special scratch API?

WPSI already has the primitive it needs: directory capabilities and preopens. A second resource class for temporary or private storage would add imports, quota APIs, lifetime rules, and implementation machinery without adding new authority semantics.

An embedder that wants to give a guest a convenient writable home can therefore expose a normal preopen with the display name `~`. Higher-level bindings may map `~/foo` to that directory handle plus the relative path `foo`.

Nothing about the name is magical. The preopen may be temporary, persistent, memory-backed, host-directory-backed, read-only, writable, quota-limited, or absent, according to the authority and policy the embedder explicitly supplies. In particular, `~` never means the host user's home directory unless the embedder deliberately grants that directory as a capability.

This keeps constrained runtimes free from allocating storage they do not need and keeps all filesystem authority on one mechanism.'''
)
write("docs/design.md", design)

runtime = read("docs/runtime-implementation.md")
runtime = replace_section(
    runtime,
    "## Scratch filesystem",
    "## Testing recommendations",
    r'''## Optional `~` preopen

There is no scratch-specific runtime subsystem in WPSI.

If an embedder wants to provide a private or convenient guest home directory, expose it through the ordinary preopen table with the display name `~`. Do not allocate such storage when the embedding environment does not need it.

The backing implementation is ordinary filesystem policy: it may be a host directory, memory filesystem, temporary directory, overlay, persistent store, or another directory-capability implementation. The `~` name itself grants no rights and does not imply the host user's real home directory.

A libc or language runtime that supports `~/path` should resolve the `~` preopen once and then issue normal handle-relative WPSI path operations.'''
)
write("docs/runtime-implementation.md", runtime)

readme = read("README.md")
readme = readme.replace(
    "and a private writable scratch filesystem for every filesystem-enabled instance.",
    "and capability-oriented filesystem preopens, including an optional conventional `~` guest-home preopen.",
)
readme = readme.replace(
    "- **Private scratch filesystem.** Filesystem-enabled instances always have writable private storage even when no host directory is mounted.",
    "- **No mandatory filesystem allocation.** Embedders may expose ordinary directory preopens as needed; `~` is the conventional optional guest-home/private-area name and has no special ABI semantics.",
)
readme = readme.replace(
    "strict/WTF text handling, scratch storage, preopens, filesystem rights,",
    "strict/WTF text handling, preopen conventions, filesystem rights,",
)
readme = readme.replace(
    "WPSI adds only the `preopens` and `scratch` provisioning needed for its own model.",
    "WPSI adds only the `preopens` provisioning needed for explicit multi-directory capability tests.",
)
write("README.md", readme)

roadmap = read("ROADMAP.md")
roadmap = roadmap.replace(
    "- [x] Define private scratch filesystem semantics.",
    "- [x] Define ordinary filesystem preopens and the optional `~` guest-home convention without scratch-specific ABI functions.",
)
roadmap = roadmap.replace(
    "3. `wpsi-filesystem` with private scratch storage and preopens.",
    "3. `wpsi-filesystem` with ordinary preopens and handle-relative paths.",
)
roadmap = roadmap.replace(
    "They cover scratch persistence, per-child GC scatter/gather slicing, async ownership, and profile-specific version negotiation.",
    "They cover per-child GC scatter/gather slicing, async ownership, and profile-specific version negotiation.",
)
write("ROADMAP.md", roadmap)

changelog = read("CHANGELOG.md")
changelog = changelog.replace(
    "- Automatic private scratch filesystem for filesystem-enabled instances.\n",
    "- Conventional optional `~` preopen for embedders that want to expose a guest-home/private writable area using ordinary directory-capability semantics.\n",
)
anchor = "- Resource handle encoding is entirely runtime-private. Only `0` has a standardized numeric meaning; guests may not interpret nonzero handle bits or ranges, and stale handles may never alias unrelated live resources.\n"
addition = anchor + "- Scratch-specific ABI functions and quota provisioning were removed. WPSI allocates no mandatory writable filesystem; `~` is only a conventional optional preopen display name and all storage semantics come from ordinary directory capabilities.\n"
if anchor not in changelog:
    raise SystemExit("changelog decision anchor missing")
changelog = changelog.replace(anchor, addition, 1)
changelog = changelog.replace("- Scratch persistence across runtime/embedder restarts.\n", "", 1)
write("CHANGELOG.md", changelog)

security = read("SECURITY.md")
security = security.replace(
    "The private scratch filesystem must not imply access to arbitrary host files. Host filesystem paths and network access remain explicit capabilities.",
    "A preopen named `~` must not imply ambient access to the host user's home directory. Like every filesystem root, it grants only the directory authority explicitly supplied by the embedder. Host filesystem paths and network access remain explicit capabilities.",
)
write("SECURITY.md", security)


# ---------------------------------------------------------------------------
# Test harness: scratch is no longer a provisioning primitive.
# ---------------------------------------------------------------------------

schema_path = ROOT / "spec/tests/manifest.schema.json"
schema = json.loads(schema_path.read_text(encoding="utf-8"))
schema["$defs"].pop("scratch", None)
schema["$defs"]["run"]["properties"].pop("scratch", None)
schema_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

checker = read("spec/tests/tools/check_suite.py")
checker = checker.replace(
    'allowed = {"type", "args", "env", "root", "preopens", "scratch"}',
    'allowed = {"type", "args", "env", "root", "preopens"}',
    1,
)
checker, n = re.subn(
    r'\n    scratch = operation\.get\("scratch"\)\n    if scratch is not None:\n        if not isinstance\(scratch, dict\) or set\(scratch\) - \{"byte_quota", "object_quota"\}:\n            fail\(f"invalid scratch object: \{manifest\}"\)\n        for key, value in scratch\.items\(\):\n            if not isinstance\(value, int\) or value < 0:\n                fail\(f"scratch\.\{key\} must be a nonnegative integer: \{manifest\}"\)\n',
    "\n",
    checker,
    count=1,
)
if n != 1:
    raise SystemExit("failed to remove scratch checker block")
write("spec/tests/tools/check_suite.py", checker)

suite_readme = read("spec/tests/README.md")
suite_readme = suite_readme.replace(
    "WPSI adds only two host-provisioning extensions:\n\n- `preopens`, for more than one directory capability or explicit rights;\n- `scratch`, for deterministic scratch quotas. Scratch itself always exists and\n  is never mounted from a host directory.",
    "WPSI adds one host-provisioning extension:\n\n- `preopens`, for more than one directory capability, explicit guest display names, or explicit rights.\n\nA preopen may use the guest display name `~`; this is provisioned exactly like any other preopen.",
)
suite_readme = suite_readme.replace(
    "A runner must create a fresh test context, handle table, scratch filesystem,\npoll state, network namespace, argument vector, and environment for every test.",
    "A runner must create a fresh test context, handle table, poll state, network namespace,\nargument vector, and environment for every test.",
)
suite_readme = replace_section(
    suite_readme,
    "## Scratch configuration",
    "## WAST execution",
    r'''## Optional `~` preopen

The conformance harness does not allocate scratch storage implicitly. Tests that need a private/writable guest home provision an ordinary preopen explicitly:

```json
{
  "type": "run",
  "preopens": [
    {"host": "../fixtures/root", "guest": "~", "rights": ["read", "write", "open", "create", "remove", "stat"]}
  ]
}
```

A test with no `root` and no `preopens` receives no filesystem roots. This keeps the harness aligned with WPSI's rule that writable storage is optional rather than automatically allocated.'''
)
suite_readme = suite_readme.replace(
    "filesystem/    scratch, descriptors, paths, rights, and preopens",
    "filesystem/    descriptors, paths, rights, preopens, and the optional `~` convention",
)
write("spec/tests/README.md", suite_readme)


# ---------------------------------------------------------------------------
# Replace scratch-specific conformance tests with ordinary preopen tests.
# ---------------------------------------------------------------------------

for rel in [
    "spec/tests/filesystem/scratch-quota-reported.wast",
    "spec/tests/filesystem/scratch-quota-reported.json",
    "spec/tests/filesystem/scratch-roundtrip.wast",
    "spec/tests/filesystem/scratch-starts-empty.wast",
]:
    p = ROOT / rel
    if p.exists():
        p.unlink()

write("spec/tests/filesystem/preopen-tilde-convention.wast", r''';; WPSI conformance test: filesystem/preopen-tilde-convention
;; Purpose: A `~` guest home is represented by an ordinary preopen display name.
;; Required profiles: core, memory32, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_preopen_count" (func $count (result i32 i32)))
  (import "wpsi" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "fs_preopen_name_len_i8" (func $len (param i32 i32) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_mem32_i8" (func $read (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (func (export "run") (result i32)
    (local $count i32) (local $dir i32) (local $e i32) (local $n i64)
    (call $count) (local.set $e) (local.set $count)
    (if (i32.or (local.get $e) (i32.ne (local.get $count) (i32.const 1))) (then (return (i32.const 10))))
    (call $get (i32.const 0)) (local.set $e) (local.set $dir)
    (if (local.get $e) (then (return (local.get $e))))
    (call $len (i32.const 0) (i32.const 0)) (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 1))) (then (return (i32.const 11))))
    (call $read (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 1)) (local.set $e) (local.set $n)
    (drop (call $close (local.get $dir)))
    (i32.or (local.get $e) (i32.ne (i32.load8_u (i32.const 0)) (i32.const 126)))))
(assert_return (invoke "run") (i32.const 0))''')

write("spec/tests/filesystem/preopen-tilde-convention.json", json.dumps({
    "version": 1,
    "operations": [
        {"type": "run", "preopens": [{"host": "../fixtures/root", "guest": "~", "rights": ["read", "stat", "iterate"]}]},
        {"type": "wait", "exit_code": 0},
    ],
}, indent=2))

write("spec/tests/filesystem/preopen-tilde-optional.wast", r''';; WPSI conformance test: filesystem/preopen-tilde-optional
;; Purpose: A filesystem implementation is not required to provide any preopen, including `~`.
;; Required profiles: core, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_preopen_count" (func $count (result i32 i32)))
  (func (export "run") (result i32 i32)
    (call $count)))
(assert_return (invoke "run") (i32.const 0) (i32.const 0))''')

write("spec/tests/filesystem/preopen-tilde-roundtrip.wast", r''';; WPSI conformance test: filesystem/preopen-tilde-roundtrip
;; Purpose: A writable `~` preopen uses ordinary file operations with no scratch-specific imports.
;; Required profiles: core, memory32, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "wpsi" "fd_read_mem32" (func $read (param i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "fd_write_mem32" (func $write (param i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "fd_seek" (func $seek (param i32 i64 i32) (result i64 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (data (i32.const 0) "roundtrip.cleanup")
  (data (i32.const 32) "hello")
  (func (export "run") (result i32)
    (local $dir i32) (local $fd i32) (local $e i32) (local $n i64) (local $off i64)
    (call $get (i32.const 0)) (local.set $e) (local.set $dir)
    (if (local.get $e) (then (return (local.get $e))))
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 17) (i32.const 0) (i32.const 5) (i64.const 63)) (local.set $e) (local.set $fd)
    (if (local.get $e) (then (return (local.get $e))))
    (call $write (local.get $fd) (i32.const 0) (i32.const 32) (i32.const 5)) (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 5))) (then (return (i32.const 101))))
    (call $seek (local.get $fd) (i64.const 0) (i32.const 0)) (local.set $e) (local.set $off)
    (if (local.get $e) (then (return (local.get $e))))
    (call $read (local.get $fd) (i32.const 0) (i32.const 64) (i32.const 5)) (local.set $e) (local.set $n)
    (drop (call $close (local.get $fd)))
    (drop (call $close (local.get $dir)))
    (if (result i32) (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 5)))
      (then (i32.const 102))
      (else (i32.ne (i32.load (i32.const 64)) (i32.const 1819043176))))))
(assert_return (invoke "run") (i32.const 0))''')

write("spec/tests/filesystem/preopen-tilde-roundtrip.json", json.dumps({
    "version": 1,
    "operations": [
        {"type": "run", "preopens": [{"host": "../fixtures/root", "guest": "~", "rights": ["read", "write", "seek", "tell", "stat", "set-size", "sync", "open", "create", "remove", "rename", "iterate"]}]},
        {"type": "wait", "exit_code": 0},
    ],
}, indent=2))

# Profile-surface guard should use a real filesystem import that remains in 0.1.
profile = read("spec/tests/imports/profile-surface.wast")
profile = profile.replace(
    '(import "wpsi" "fs_scratch" (func $fs (result i32 i32)))',
    '(import "wpsi" "fs_preopen_count" (func $fs (result i32 i32)))',
    1,
)
write("spec/tests/imports/profile-surface.wast", profile)


# ---------------------------------------------------------------------------
# Hygiene checks before catalog regeneration.
# ---------------------------------------------------------------------------

no_special_scratch = [
    "SPEC.md",
    "README.md",
    "ROADMAP.md",
    "SECURITY.md",
    "docs/design.md",
    "docs/open-questions.md",
    "docs/runtime-implementation.md",
    "spec/behavior.md",
    "spec/imports.wat",
    "spec/tests/README.md",
    "spec/tests/manifest.schema.json",
    "spec/tests/tools/check_suite.py",
]
for rel in no_special_scratch:
    text = read(rel).lower()
    if "fs_scratch" in text or "scratch filesystem" in text or "scratch storage" in text or '"scratch"' in text:
        raise SystemExit(f"special scratch semantics remain in {rel}")

for wast in (ROOT / "spec/tests").rglob("*.wast"):
    if "fs_scratch" in wast.read_text(encoding="utf-8"):
        raise SystemExit(f"legacy fs_scratch import remains: {wast.relative_to(ROOT)}")

for manifest in (ROOT / "spec/tests").rglob("*.json"):
    if manifest.name == "catalog.json":
        continue
    if '"scratch"' in manifest.read_text(encoding="utf-8"):
        raise SystemExit(f"legacy scratch manifest field remains: {manifest.relative_to(ROOT)}")

print("removed scratch-specific WPSI ABI and replaced it with ordinary optional ~ preopen semantics")
