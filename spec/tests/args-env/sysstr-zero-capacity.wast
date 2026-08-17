;; WPSI conformance test: args-env/sysstr-zero-capacity
;; Purpose: A zero-capacity sysstr read succeeds and preserves the destination sentinel.
;; Required profiles: core, memory32, args-env
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "args_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "sysstr_read_mem32" (func $read (param i32 i32 i32 i32 i32) (result i64 i32)))
  (memory 1)
  (data (i32.const 8) "Z")
  (func (export "run") (result i32)
    (local $h i32) (local $err i32) (local $n i64)
    (call $get (i32.const 0)) (local.set $err) (local.set $h)
    (call $read (local.get $h) (i32.const 1) (i32.const 0) (i32.const 8) (i32.const 0)) (local.set $err) (local.set $n)
    (i32.or (i32.ne (local.get $err) (i32.const 0))
      (i32.or (i64.ne (local.get $n) (i64.const 0))
              (i32.ne (i32.load8_u (i32.const 8)) (i32.const 90))))))
(assert_return (invoke "run") (i32.const 0))
