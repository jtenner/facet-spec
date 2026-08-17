;; WPSI conformance test: core/double-close-sysstr
;; Purpose: Closing a handle twice reports ERR_BAD_HANDLE instead of aliasing another resource.
;; Required profiles: core, args-env
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "args_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (func (export "run") (result i32)
    (local $h i32) (local $err i32)
    (call $get (i32.const 0)) (local.set $err) (local.set $h)
    (if (result i32) (i32.ne (local.get $err) (i32.const 0))
      (then (i32.const 100))
      (else
        (drop (call $close (local.get $h)))
        (call $close (local.get $h))))))
(assert_return (invoke "run") (i32.const 4))
