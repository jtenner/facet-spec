;; WPSI conformance test: poll/add-invalid-fd
;; Purpose: Poll registration rejects the permanently invalid descriptor zero.
;; Required profiles: core, poll, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "poll_create" (func $create (result i32 i32)))
  (import "wpsi" "poll_add_fd" (func $add (param i32 i32 i32 i64) (result i32)))
  (func (export "run") (result i32)
    (local $p i32) (local $e i32)
    (call $create) (local.set $e) (local.set $p)
    (call $add (local.get $p) (i32.const 0) (i32.const 1) (i64.const 0)))
)
(assert_return (invoke "run") (i32.const 4))
