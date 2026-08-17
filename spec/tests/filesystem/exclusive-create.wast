;; WPSI conformance test: filesystem/exclusive-create
;; Purpose: OPEN_EXCLUSIVE rejects an existing path and returns a zero descriptor.
;; Required profiles: core, memory32, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_scratch" (func $scratch (result i32 i32)))
  (import "wpsi" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (memory 1) (data (i32.const 0) "exclusive.bin")
  (func (export "run") (result i32 i32)
    (local $dir i32) (local $fd i32) (local $e i32)
    (call $scratch) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 13) (i32.const 0) (i32.const 3) (i64.const 63)) (local.set $e) (local.set $fd)
    (drop (call $close (local.get $fd)))
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 13) (i32.const 0) (i32.const 3) (i64.const 63)))
)
(assert_return (invoke "run") (i32.const 0) (i32.const 9))
