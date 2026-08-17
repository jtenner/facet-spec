;; WPSI conformance test: clocks/system-nanoseconds-range
;; Purpose: System clock nanoseconds are always less than one billion.
;; Required profiles: core, clocks
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "clock_system_now" (func $now (result i64 i32 i32)))
  (func (export "run") (result i32)
    (local $s i64) (local $ns i32) (local $err i32)
    (call $now) (local.set $err) (local.set $ns) (local.set $s)
    (i32.and (i32.eqz (local.get $err))
      (i32.lt_u (local.get $ns) (i32.const 1000000000)))))
(assert_return (invoke "run") (i32.const 1))
