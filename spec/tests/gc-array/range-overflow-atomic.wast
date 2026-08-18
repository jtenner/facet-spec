;; Facet conformance test: gc-array/range-overflow-atomic
;; Purpose: GC logical-byte range overflow is rejected atomically.
;; Required profiles: core, gc-array, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array (mut i32)))
  (import "facet" "random_fill_array_i32" (func $fill (param (ref array) i64 i64) (result i64 i32)))
  (func (export "run") (result i64 i32 i32)
    (local $a (ref $a)) (local $n i64) (local $e i32)
    (local.set $a (array.new $a (i32.const 287454020) (i32.const 2)))
    (call $fill (local.get $a) (i64.const -1) (i64.const 2)) (local.set $e) (local.set $n)
    (local.get $n) (local.get $e) (array.get $a (local.get $a) (i32.const 0))))
(assert_return (invoke "run") (i64.const 0) (i32.const 24) (i32.const 287454020))
