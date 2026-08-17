;; WPSI conformance test: memory32/wrong-memory-width
;; Purpose: A Memory32 operation rejects a Memory64 memory with ERR_TYPE.
;; Required profiles: core, memory32, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "random_fill_mem32" (func $fill (param i32 i32 i32) (result i64 i32)))
  (memory i64 1)
  (func (export "run") (result i64 i32)
    (call $fill (i32.const 0) (i32.const 0) (i32.const 1))))
(assert_return (invoke "run") (i64.const 0) (i32.const 25))
