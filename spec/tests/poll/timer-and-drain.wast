;; WPSI conformance test: poll/timer-and-drain
;; Purpose: An expired timer produces one timer event with exact userdata.
;; Required profiles: core, clocks, poll
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "clock_monotonic_now" (func $now (result i64 i32)))
  (import "facet" "poll_create" (func $create (result i32 i32)))
  (import "facet" "poll_add_timer" (func $add (param i32 i64 i64) (result i32 i32)))
  (import "facet" "poll_wait" (func $wait (param i32 i64) (result i32 i32)))
  (import "facet" "poll_next" (func $next (param i32) (result i32 i32 i32 i64 i32 i32)))
  (func (export "run") (result i32)
    (local $p i32) (local $e i32) (local $id i32) (local $n i32) (local $t i64)
    (local $kind i32) (local $source i32) (local $events i32) (local $data i64) (local $done i32)
    (call $now) (local.set $e) (local.set $t)
    (call $create) (local.set $e) (local.set $p)
    (call $add (local.get $p) (local.get $t) (i64.const 1234)) (local.set $e) (local.set $id)
    (call $wait (local.get $p) (local.get $t)) (local.set $e) (local.set $n)
    (if (i32.ne (local.get $n) (i32.const 1)) (then (return (i32.const 10))))
    (call $next (local.get $p)) (local.set $e) (local.set $done) (local.set $data) (local.set $events) (local.set $source) (local.set $kind)
    (i32.or (local.get $e)
      (i32.or (i32.ne (local.get $kind) (i32.const 2))
        (i32.or (i32.ne (local.get $source) (local.get $id))
          (i64.ne (local.get $data) (i64.const 1234)))))))
(assert_return (invoke "run") (i32.const 0))
