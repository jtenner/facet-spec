;; WPSI conformance test: poll/next-exhausted
;; Purpose: poll_next reports done after an empty wait result.
;; Required profiles: core, poll
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "poll_create" (func $create (result i32 i32)))
  (import "wpsi" "poll_wait" (func $wait (param i32 i64) (result i32 i32)))
  (import "wpsi" "poll_next" (func $next (param i32) (result i32 i32 i32 i64 i32 i32)))
  (func (export "run") (result i32 i32)
    (local $p i32) (local $e i32) (local $n i32) (local $kind i32) (local $id i32) (local $events i32) (local $data i64) (local $done i32)
    (call $create) (local.set $e) (local.set $p)
    (call $wait (local.get $p) (i64.const 0)) (local.set $e) (local.set $n)
    (call $next (local.get $p)) (local.set $e) (local.set $done) (local.set $data) (local.set $events) (local.set $id) (local.set $kind)
    (local.get $done) (local.get $e))
)
(assert_return (invoke "run") (i32.const 1) (i32.const 0))
