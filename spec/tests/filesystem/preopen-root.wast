;; WPSI conformance test: filesystem/preopen-root
;; Purpose: The WASI-compatible root manifest creates one preopen whose display name is `/`.
;; Required profiles: core, memory32, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_preopen_count" (func $count (result i32 i32)))
  (import "wpsi" "fs_preopen_get" (func $get (param i32) (result i32 i32 i32)))
  (import "wpsi" "sysstr_len" (func $len (param i32 i32) (result i64 i32)))
  (import "wpsi" "sysstr_read_mem32" (func $read (param i32 i32 i32 i32 i32) (result i64 i32)))
  (memory 1)
  (func (export "run") (result i32)
    (local $count i32) (local $dir i32) (local $name i32) (local $e i32) (local $n i64)
    (call $count) (local.set $e) (local.set $count)
    (if (i32.or (local.get $e) (i32.ne (local.get $count) (i32.const 1))) (then (return (i32.const 10))))
    (call $get (i32.const 0)) (local.set $e) (local.set $name) (local.set $dir)
    (call $len (local.get $name) (i32.const 1)) (local.set $e) (local.set $n)
    (call $read (local.get $name) (i32.const 1) (i32.const 0) (i32.const 0) (i32.const 1)) (local.set $e) (local.set $n)
    (i32.or (local.get $e) (i32.ne (i32.load8_u (i32.const 0)) (i32.const 47)))))
(assert_return (invoke "run") (i32.const 0))
