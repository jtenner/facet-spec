;; WPSI conformance test: args-env/args-read-insufficient-capacity
;; Purpose: A too-small string destination returns ERR_RANGE and remains unmodified.
;; Required profiles: core, memory32, args-env, text, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "args_read_mem32_i8" (func $read (param i32 i32 i32 i32 i32) (result i64 i32)))
  (memory 1)
  (data (i32.const 16) "Z")
  (func (export "run") (result i32)
    (local $n i64) (local $e i32)
    (call $read (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 16) (i32.const 4))
    (local.set $e) (local.set $n)
    (i32.and
      (i32.and (i64.eqz (local.get $n)) (i32.eq (local.get $e) (i32.const 17)))
      (i32.eq (i32.load8_u (i32.const 16)) (i32.const 90))))
)
(assert_return (invoke "run") (i32.const 1))
