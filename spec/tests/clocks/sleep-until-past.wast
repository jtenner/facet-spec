;; Facet conformance test: clocks/sleep-until-past
;; Purpose: Sleeping until a deadline that has already arrived succeeds immediately.
;; Required profiles: core, clocks
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "clock_monotonic_now" (func $now (result i64 i32)))
  (import "facet" "sleep_until" (func $sleep (param i64) (result i32)))
  (func (export "run") (result i32)
    (local $t i64) (local $e i32)
    (call $now) (local.set $e) (local.set $t)
    (if (result i32) (local.get $e)
      (then (local.get $e))
      (else (call $sleep (local.get $t))))))
(assert_return (invoke "run") (i32.const 0))
