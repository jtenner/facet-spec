;; WPSI conformance test: poll/remove-timer
;; Purpose: Removing a timer subscription prevents it from appearing in the next ready set.
;; Required profiles: core, clocks, poll
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "clock_monotonic_now" (func $now (result i64 i32)))
  (import "facet" "poll_create" (func $create (result i32 i32)))
  (import "facet" "poll_add_timer" (func $add (param i32 i64 i64) (result i32 i32)))
  (import "facet" "poll_remove_timer" (func $remove (param i32 i32) (result i32)))
  (import "facet" "poll_wait" (func $wait (param i32 i64) (result i32 i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))
  (func (export "run") (result i32 i32)
    (local $p i32) (local $id i32) (local $e i32) (local $n i32) (local $t i64)
    (call $now) (local.set $e) (local.set $t)
    (call $create) (local.set $e) (local.set $p)
    (call $add (local.get $p) (local.get $t) (i64.const 9)) (local.set $e) (local.set $id)
    (local.set $e (call $remove (local.get $p) (local.get $id)))
    (call $wait (local.get $p) (local.get $t)) (local.set $e) (local.set $n)
    (drop (call $close (local.get $p)))
    (local.get $n) (local.get $e)))
(assert_return (invoke "run") (i32.const 0) (i32.const 0))
