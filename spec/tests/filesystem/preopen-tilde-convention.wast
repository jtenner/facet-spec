;; Facet conformance test: filesystem/preopen-tilde-convention
;; Purpose: A `~` guest home is represented by an ordinary preopen display name.
;; Required profiles: core, memory32, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fs_preopen_count" (func $count (result i32 i32)))
  (import "facet" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "facet" "fs_preopen_name_len_i8" (func $len (param i32 i32) (result i64 i32)))
  (import "facet" "fs_preopen_name_read_mem32_i8" (func $read (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))
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
(assert_return (invoke "run") (i32.const 0))
