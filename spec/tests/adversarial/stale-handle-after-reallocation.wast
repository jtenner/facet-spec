;; WPSI conformance test: adversarial/stale-handle-after-reallocation
;; Purpose: A closed numeric handle never aliases a subsequently allocated resource.
;; Required profiles: core, poll, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "poll_create" (func $create (result i32 i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))
  (func (export "run") (result i32)
    (local $old i32) (local $new i32) (local $e i32)
    (call $create) (local.set $e) (local.set $old)
    (if (local.get $e) (then (return (local.get $e))))
    (drop (call $close (local.get $old)))
    (call $create) (local.set $e) (local.set $new)
    (if (local.get $e) (then (return (local.get $e))))
    (local.set $e (call $close (local.get $old)))
    (drop (call $close (local.get $new)))
    (local.get $e))
)
(assert_return (invoke "run") (i32.const 4))
