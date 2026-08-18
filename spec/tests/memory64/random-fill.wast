;; Facet conformance test: memory64/random-fill
;; Purpose: Memory64 uses i64 addresses while preserving adjacent bytes.
;; Required profiles: core, memory64
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "random_fill_mem64" (func $fill (param i32 i64 i64) (result i64 i32)))
  (memory i64 1)
  (data (i64.const 7) "L") (data (i64.const 24) "R")
  (func (export "run") (result i32)
    (local $n i64) (local $e i32)
    (call $fill (i32.const 0) (i64.const 8) (i64.const 16)) (local.set $e) (local.set $n)
    (i32.or (local.get $e)
      (i32.or (i64.ne (local.get $n) (i64.const 16))
        (i32.or (i32.ne (i32.load8_u (i64.const 7)) (i32.const 76))
                (i32.ne (i32.load8_u (i64.const 24)) (i32.const 82)))))))
(assert_return (invoke "run") (i32.const 0))
