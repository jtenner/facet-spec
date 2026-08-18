;; Facet conformance test: clocks/resolution-positive
;; Purpose: Monotonic clock resolution is a positive duration.
;; Required profiles: core, clocks
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "clock_monotonic_resolution" (func $res (result i64 i32)))
  (func (export "run") (result i32)
    (local $r i64) (local $e i32)
    (call $res) (local.set $e) (local.set $r)
    (i32.and (i32.eqz (local.get $e)) (i64.gt_u (local.get $r) (i64.const 0)))))
(assert_return (invoke "run") (i32.const 1))
