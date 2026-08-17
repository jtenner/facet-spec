;; WPSI conformance test: random/mem32-zero-length
;; Purpose: Zero-length fill at the final byte is valid and does not mutate it.
;; Required profiles: core, memory32
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "random_fill_mem32" (func $fill (param i32 i32 i32) (result i64 i32)))
  (memory 1)
  (data (i32.const 65535) "Z")
  (func (export "run") (result i64 i32 i32)
    (local $n i64) (local $e i32)
    (call $fill (i32.const 0) (i32.const 65535) (i32.const 0)) (local.set $e) (local.set $n)
    (local.get $n) (local.get $e) (i32.load8_u (i32.const 65535))))
(assert_return (invoke "run") (i64.const 0) (i32.const 0) (i32.const 90))
