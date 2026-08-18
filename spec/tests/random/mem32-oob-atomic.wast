;; Facet conformance test: random/mem32-oob-atomic
;; Purpose: An out-of-bounds fill is rejected atomically and returns zero bytes written.
;; Required profiles: core, memory32, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "random_fill_mem32" (func $fill (param i32 i32 i32) (result i64 i32)))
  (memory 1)
  (data (i32.const 65534) "XY")
  (func (export "run") (result i64 i32 i32 i32)
    (local $n i64) (local $e i32)
    (call $fill (i32.const 0) (i32.const 65535) (i32.const 2)) (local.set $e) (local.set $n)
    (local.get $n) (local.get $e)
    (i32.load8_u (i32.const 65534)) (i32.load8_u (i32.const 65535))))
(assert_return (invoke "run") (i64.const 0) (i32.const 24) (i32.const 88) (i32.const 89))
