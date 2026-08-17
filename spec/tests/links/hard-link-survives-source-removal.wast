;; WPSI conformance test: links/hard-link-survives-source-removal
;; Purpose: A hard link remains valid after the original directory entry is removed.
;; Required profiles: core, memory32, filesystem, links
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_preopen_get" (func $scratch (param i32) (result i32 i32)))
  (import "wpsi" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "wpsi" "path_link_mem32_i8" (func $link (param i32 i32 i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "wpsi" "path_remove_mem32_i8" (func $remove (param i32 i32 i32 i32 i32 i32) (result i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (memory 1) (data (i32.const 0) "source.bin") (data (i32.const 32) "alias.bin")
  (func (export "run") (result i32)
    (local $dir i32) (local $fd i32) (local $e i32)
    (call $scratch (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 10) (i32.const 0) (i32.const 1) (i64.const 63)) (local.set $e) (local.set $fd)
    (drop (call $close (local.get $fd)))
    (local.set $e (call $link (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 10) (i32.const 0) (local.get $dir) (i32.const 0) (i32.const 32) (i32.const 9) (i32.const 0) (i32.const 0)))
    (local.set $e (call $remove (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 10) (i32.const 0) (i32.const 1)))
    (call $open (local.get $dir) (i32.const 0) (i32.const 32) (i32.const 9) (i32.const 0) (i32.const 0) (i64.const 17)) (local.set $e) (local.set $fd)
    (if (i32.eqz (local.get $e)) (then (drop (call $close (local.get $fd)))))
    (local.get $e))
)
(assert_return (invoke "run") (i32.const 0))
