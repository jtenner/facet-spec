;; WPSI conformance test: core/proc-exit-nonzero
;; Purpose: proc_exit terminates execution with the exact unsigned exit code supplied by the guest.
;; Required profiles: core
;; Test kind: harness
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "proc_exit" (func $exit (param i32)))
  (func (export "_start")
    (call $exit (i32.const 7))))
