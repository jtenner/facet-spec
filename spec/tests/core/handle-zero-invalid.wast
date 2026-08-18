;; Facet conformance test: core/handle-zero-invalid
;; Purpose: Handle zero is permanently invalid.
;; Required profiles: core
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "handle_close" (func $close (param i32) (result i32)))
  (func (export "run") (result i32) (call $close (i32.const 0))))
(assert_return (invoke "run") (i32.const 4))
