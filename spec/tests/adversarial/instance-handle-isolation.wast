;; WPSI conformance test: adversarial/instance-handle-isolation
;; Purpose: Resource handles are instance-local and cannot be reused by another module instance.
;; Required profiles: core, filesystem, adversarial
;; Test kind: harness
;;
;; SPDX-License-Identifier: MIT

(module $A
  (import "facet" "fs_preopen_get" (func $scratch (param i32) (result i32 i32)))
  (func (export "acquire-valid") (result i32)
    (local $h i32) (local $e i32)
    (call $scratch (i32.const 0)) (local.set $e) (local.set $h)
    (i32.and (i32.eqz (local.get $e)) (i32.ne (local.get $h) (i32.const 0)))))
(module $B
  (import "facet" "handle_close" (func $close (param i32) (result i32)))
  (func (export "probe") (param $foreign i32) (result i32)
    (call $close (local.get $foreign))))
(assert_return (invoke $A "acquire-valid") (i32.const 1))
;; A catalog-aware runner additionally passes A's raw handle to B.probe and
;; requires ERR_BAD_HANDLE. Standard WAST cannot feed one invoke result into a
;; later invoke, so the cross-instance step is a documented harness assertion.
