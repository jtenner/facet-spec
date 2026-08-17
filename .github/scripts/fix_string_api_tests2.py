#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

path = ROOT / "spec/tests/filesystem/scratch-starts-empty.wast"
path.write_text(''';; WPSI conformance test: filesystem/scratch-starts-empty
;; Purpose: Every test receives a fresh, logically empty scratch filesystem.
;; Required profiles: core, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_scratch" (func $scratch (result i32 i32)))
  (import "wpsi" "dir_iter_open" (func $open (param i32) (result i32 i32)))
  (import "wpsi" "dir_iter_next_len" (func $next (param i32 i32) (result i64 i32 i64 i32 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (func (export "run") (result i32)
    (local $dir i32) (local $it i32) (local $units i64) (local $type i32)
    (local $ino i64) (local $done i32) (local $e i32)
    (call $scratch) (local.set $e) (local.set $dir)
    (call $open (local.get $dir)) (local.set $e) (local.set $it)
    (call $next (local.get $it) (i32.const 1))
      (local.set $e) (local.set $done) (local.set $ino) (local.set $type) (local.set $units)
    (drop (call $close (local.get $it))) (drop (call $close (local.get $dir)))
    (i32.or (local.get $e) (i32.xor (local.get $done) (i32.const 1)))))
(assert_return (invoke "run") (i32.const 0))
''', encoding="utf-8")

legacy = (
    '"args_get"', '"env_get"', '"sysstr_len"', '"sysstr_read_mem32"',
    '"sysstr_read_mem64"', '"sysstr_read_array_i8"', '"sysstr_read_array_i16"',
    '"sysstr_read_array_i32"', '"dir_iter_next"',
)
remaining = []
for candidate in (ROOT / "spec/tests").rglob("*.wast"):
    text = candidate.read_text(encoding="utf-8")
    # dir_iter_next_* names are current; only exact old import spellings count.
    if any(f'(import "wpsi" {name}' in text for name in legacy):
        remaining.append(str(candidate.relative_to(ROOT)))
if remaining:
    raise SystemExit("legacy host-string imports remain:\n" + "\n".join(sorted(remaining)))

print("migrated remaining directory string-source coverage")
