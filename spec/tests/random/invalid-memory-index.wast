;; Facet conformance test: random/invalid-memory-index
;; Purpose: An invalid memory index returns ERR_FAULT rather than selecting memory zero.
;; Required profiles: core, memory32, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "random_fill_mem32" (func $fill (param i32 i32 i32) (result i64 i32)))
  (memory 1)
  (func (export "run") (result i64 i32)
    (call $fill (i32.const 1) (i32.const 0) (i32.const 1))))
(assert_return (invoke "run") (i64.const 0) (i32.const 24))
