;; WPSI conformance test: memory64/wrong-memory-width
;; Purpose: A Memory64 operation rejects a Memory32 memory with ERR_TYPE.
;; Required profiles: core, memory64, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "random_fill_mem64" (func $fill (param i32 i64 i64) (result i64 i32)))
  (memory 1)
  (func (export "run") (result i64 i32)
    (call $fill (i32.const 0) (i64.const 0) (i64.const 1))))
(assert_return (invoke "run") (i64.const 0) (i32.const 25))
