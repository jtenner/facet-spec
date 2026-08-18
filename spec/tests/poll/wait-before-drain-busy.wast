;; WPSI conformance test: poll/wait-before-drain-busy
;; Purpose: A second poll_wait before draining ready events returns ERR_BUSY.
;; Required profiles: core, clocks, poll, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "clock_monotonic_now" (func $now (result i64 i32)))
  (import "facet" "poll_create" (func $create (result i32 i32)))
  (import "facet" "poll_add_timer" (func $add (param i32 i64 i64) (result i32 i32)))
  (import "facet" "poll_wait" (func $wait (param i32 i64) (result i32 i32)))
  (func (export "run") (result i32 i32)
    (local $p i32) (local $e i32) (local $id i32) (local $n i32) (local $t i64)
    (call $now) (local.set $e) (local.set $t)
    (call $create) (local.set $e) (local.set $p)
    (call $add (local.get $p) (local.get $t) (i64.const 0)) (local.set $e) (local.set $id)
    (call $wait (local.get $p) (local.get $t)) (local.set $e) (local.set $n)
    (call $wait (local.get $p) (local.get $t))))
(assert_return (invoke "run") (i32.const 0) (i32.const 8))
