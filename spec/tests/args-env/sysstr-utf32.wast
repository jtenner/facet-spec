;; WPSI conformance test: args-env/sysstr-utf32
;; Purpose: UTF-32 exposes the exact Unicode scalar value.
;; Required profiles: core, memory32, args-env
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "args_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "sysstr_read_mem32" (func $read (param i32 i32 i32 i32 i32) (result i64 i32)))
  (memory 1)
  (func (export "run") (result i32)
    (local $h i32) (local $err i32) (local $n i64)
    (call $get (i32.const 1)) (local.set $err) (local.set $h)
    (call $read (local.get $h) (i32.const 3) (i32.const 0) (i32.const 16) (i32.const 1)) (local.set $err) (local.set $n)
    (if (result i32) (i32.or (i32.ne (local.get $err) (i32.const 0)) (i64.ne (local.get $n) (i64.const 1)))
      (then (i32.const 10))
      (else (i32.ne (i32.load (i32.const 16)) (i32.const 128512))))))
(assert_return (invoke "run") (i32.const 0))
