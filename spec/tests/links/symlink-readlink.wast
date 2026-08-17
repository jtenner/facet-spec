;; WPSI conformance test: links/symlink-readlink
;; Purpose: A symbolic-link target round-trips directly into caller-owned linear memory.
;; Required profiles: core, memory32, filesystem, links
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_preopen_get" (func $scratch (param i32) (result i32 i32)))
  (import "wpsi" "path_symlink_mem32_i8" (func $symlink (param i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "wpsi" "path_readlink_mem32_i8" (func $readlink (param i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (memory 1)
  (data (i32.const 0) "target.txt") (data (i32.const 32) "link.txt")
  (func (export "run") (result i32)
    (local $dir i32) (local $e i32) (local $n i64)
    (call $scratch (i32.const 0)) (local.set $e) (local.set $dir)
    (local.set $e (call $symlink (i32.const 0) (i32.const 0) (i32.const 10) (i32.const 0) (local.get $dir) (i32.const 0) (i32.const 32) (i32.const 8) (i32.const 0)))
    (call $readlink (local.get $dir)
      (i32.const 0) (i32.const 32) (i32.const 8) (i32.const 0)
      (i32.const 0) (i32.const 64) (i32.const 10) (i32.const 0))
    (local.set $e) (local.set $n)
    (i32.or (local.get $e)
      (i32.or (i64.ne (local.get $n) (i64.const 10))
        (i32.or (i32.ne (i32.load (i32.const 64)) (i32.const 1735549300))
                (i32.ne (i32.load16_u (i32.const 72)) (i32.const 29752))))))
)
(assert_return (invoke "run") (i32.const 0))
