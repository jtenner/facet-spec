;; Facet conformance test: clocks/sleep-for-zero
;; Purpose: A zero-duration sleep succeeds and does not require special timer handling.
;; Required profiles: core, clocks
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "sleep_for" (func $sleep (param i64) (result i32)))
  (func (export "run") (result i32) (call $sleep (i64.const 0))))
(assert_return (invoke "run") (i32.const 0))
