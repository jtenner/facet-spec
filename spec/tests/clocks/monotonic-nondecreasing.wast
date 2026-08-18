;; Facet conformance test: clocks/monotonic-nondecreasing
;; Purpose: Successive monotonic clock observations never move backwards.
;; Required profiles: core, clocks
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "clock_monotonic_now" (func $now (result i64 i32)))
  (func (export "run") (result i32)
    (local $a i64) (local $b i64) (local $e1 i32) (local $e2 i32)
    (call $now) (local.set $e1) (local.set $a)
    (call $now) (local.set $e2) (local.set $b)
    (i32.and (i32.eqz (i32.or (local.get $e1) (local.get $e2)))
             (i64.ge_u (local.get $b) (local.get $a)))))
(assert_return (invoke "run") (i32.const 1))
