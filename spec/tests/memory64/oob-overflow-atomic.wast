;; WPSI conformance test: memory64/oob-overflow-atomic
;; Purpose: Unsigned pointer-plus-length overflow is rejected before mutation.
;; Required profiles: core, memory64, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "random_fill_mem64" (func $fill (param i32 i64 i64) (result i64 i32)))
  (memory i64 1)
  (data (i64.const 0) "Z")
  (func (export "run") (result i64 i32 i32)
    (local $n i64) (local $e i32)
    (call $fill (i32.const 0) (i64.const -1) (i64.const 2)) (local.set $e) (local.set $n)
    (local.get $n) (local.get $e) (i32.load8_u (i64.const 0))))
(assert_return (invoke "run") (i64.const 0) (i32.const 24) (i32.const 90))
