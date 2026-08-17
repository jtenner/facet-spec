#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def write(path: str, text: str) -> None:
    p = ROOT / path
    p.write_text(text.rstrip() + "\n", encoding="utf-8")


write(
    "spec/tests/filesystem/preopen-root.wast",
    ''';; WPSI conformance test: filesystem/preopen-root
;; Purpose: The WASI-compatible root manifest exposes one preopen whose display name can be read directly as `/`.
;; Required profiles: core, memory32, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_preopen_count" (func $count (result i32 i32)))
  (import "wpsi" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "fs_preopen_name_len" (func $len (param i32 i32) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_mem32" (func $read (param i32 i32 i32 i32 i32) (result i64 i32)))
  (memory 1)
  (func (export "run") (result i32)
    (local $count i32) (local $dir i32) (local $e i32) (local $n i64)
    (call $count) (local.set $e) (local.set $count)
    (if (i32.or (local.get $e) (i32.ne (local.get $count) (i32.const 1))) (then (return (i32.const 10))))
    (call $get (i32.const 0)) (local.set $e) (local.set $dir)
    (call $len (i32.const 0) (i32.const 1)) (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 1))) (then (return (i32.const 11))))
    (call $read (i32.const 0) (i32.const 1) (i32.const 0) (i32.const 0) (i32.const 1)) (local.set $e) (local.set $n)
    (i32.or (local.get $e) (i32.ne (i32.load8_u (i32.const 0)) (i32.const 47)))))
(assert_return (invoke "run") (i32.const 0))''',
)

write(
    "spec/tests/filesystem/preopen-multiple-order.wast",
    ''';; WPSI conformance test: filesystem/preopen-multiple-order
;; Purpose: Multiple preopens and their source-specific display names remain in manifest order.
;; Required profiles: core, memory32, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_preopen_count" (func $count (result i32 i32)))
  (import "wpsi" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "fs_preopen_name_read_mem32" (func $read (param i32 i32 i32 i32 i32) (result i64 i32)))
  (memory 1)
  (func $first-byte (param $index i32) (param $at i32) (result i32)
    (local $dir i32) (local $e i32) (local $n i64)
    (call $get (local.get $index)) (local.set $e) (local.set $dir)
    (call $read (local.get $index) (i32.const 1) (i32.const 0) (local.get $at) (i32.const 1)) (local.set $e) (local.set $n)
    (i32.load8_u (local.get $at)))
  (func (export "run") (result i32 i32 i32)
    (local $n i32) (local $e i32)
    (call $count) (local.set $e) (local.set $n)
    (local.get $n) (call $first-byte (i32.const 0) (i32.const 0)) (call $first-byte (i32.const 1) (i32.const 1))))
(assert_return (invoke "run") (i32.const 2) (i32.const 47) (i32.const 47))''',
)

obsolete = ROOT / "spec/tests/core/double-close-sysstr.wast"
if obsolete.exists():
    obsolete.unlink()
manifest = obsolete.with_suffix(".json")
if manifest.exists():
    manifest.unlink()

remaining = []
for p in [ROOT / "SPEC.md", ROOT / "spec/behavior.md", ROOT / "spec/imports.wat", ROOT / "docs/design.md"]:
    if "sysstr" in p.read_text(encoding="utf-8"):
        remaining.append(str(p.relative_to(ROOT)))
for p in (ROOT / "spec/tests").rglob("*.wast"):
    if "sysstr" in p.read_text(encoding="utf-8"):
        remaining.append(str(p.relative_to(ROOT)))
if remaining:
    raise SystemExit("legacy sysstr references remain:\n" + "\n".join(remaining))

print("replaced remaining legacy string-handle tests")
