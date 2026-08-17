;; WPSI conformance test: filesystem/preopen-multiple-order
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
(assert_return (invoke "run") (i32.const 2) (i32.const 47) (i32.const 47))
