;; Facet conformance test: memory32/multi-memory-selection
;; Purpose: The explicit memory index selects memory one while memory zero remains unchanged.
;; Required profiles: core, memory32, multi-memory
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "random_fill_mem32" (func $fill (param i32 i32 i32) (result i64 i32)))
  (memory $a 1)
  (memory $b 1)
  (data (memory $a) (i32.const 0) "A")
  (data (memory $b) (i32.const 0) "B")
  (func (export "run") (result i32)
    (local $n i64) (local $e i32)
    (call $fill (i32.const 1) (i32.const 0) (i32.const 1)) (local.set $e) (local.set $n)
    (i32.or (local.get $e)
      (i32.or (i64.ne (local.get $n) (i64.const 1))
        (i32.or (i32.ne (i32.load8_u $a (i32.const 0)) (i32.const 65))
                (i32.eq (i32.load8_u $b (i32.const 0)) (i32.const 66)))))))
(assert_return (invoke "run") (i32.const 0))
