;; WPSI conformance test: core/proc-yield
;; Purpose: A cooperative yield succeeds without changing guest-visible state.
;; Required profiles: core
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "proc_yield" (func $yield (result i32)))
  (func (export "run") (result i32) (call $yield)))
(assert_return (invoke "run") (i32.const 0))
