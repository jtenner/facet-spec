;; Facet conformance test: poll/empty-zero-deadline
;; Purpose: An empty poll set with an expired deadline returns no events and succeeds.
;; Required profiles: core, poll
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "poll_create" (func $create (result i32 i32)))
  (import "facet" "poll_wait" (func $wait (param i32 i64) (result i32 i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))
  (func (export "run") (result i32 i32)
    (local $p i32) (local $e i32) (local $n i32)
    (call $create) (local.set $e) (local.set $p)
    (call $wait (local.get $p) (i64.const 0)) (local.set $e) (local.set $n)
    (drop (call $close (local.get $p)))
    (local.get $n) (local.get $e)))
(assert_return (invoke "run") (i32.const 0) (i32.const 0))
