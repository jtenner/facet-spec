;; WPSI conformance test: args-env/sysstr-utf16
;; Purpose: UTF-16 encodes a non-BMP scalar as the expected surrogate pair.
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
    (call $read (local.get $h) (i32.const 2) (i32.const 0) (i32.const 16) (i32.const 2)) (local.set $err) (local.set $n)
    (if (result i32) (i32.or (i32.ne (local.get $err) (i32.const 0)) (i64.ne (local.get $n) (i64.const 2)))
      (then (i32.const 10))
      (else (i32.or (i32.ne (i32.load16_u (i32.const 16)) (i32.const 55357))
                    (i32.ne (i32.load16_u (i32.const 18)) (i32.const 56832)))))))
(assert_return (invoke "run") (i32.const 0))
