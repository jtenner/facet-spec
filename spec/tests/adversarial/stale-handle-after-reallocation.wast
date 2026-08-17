;; WPSI conformance test: adversarial/stale-handle-after-reallocation
;; Purpose: A closed numeric handle never aliases a subsequently allocated resource.
;; Required profiles: core, args-env, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "args_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (func (export "run") (result i32)
    (local $old i32) (local $new i32) (local $e i32)
    (call $get (i32.const 0)) (local.set $e) (local.set $old)
    (drop (call $close (local.get $old)))
    (call $get (i32.const 1)) (local.set $e) (local.set $new)
    (local.set $e (call $close (local.get $old)))
    (drop (call $close (local.get $new)))
    (local.get $e))
)
(assert_return (invoke "run") (i32.const 4))
