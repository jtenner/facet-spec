;; Facet conformance test: gc-array/random-fill-v128
;; Purpose: array<v128> exposes 16-byte elements and preserves nonselected elements.
;; Required profiles: core, gc-array, simd
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array (mut v128)))
  (import "facet" "random_fill_array_v128" (func $fill (param (ref array) i64 i64) (result i64 i32)))
  (func (export "run") (result i32)
    (local $a (ref $a)) (local $n i64) (local $e i32)
    (local.set $a (array.new $a (v128.const i32x4 1 2 3 4) (i32.const 3)))
    (call $fill (local.get $a) (i64.const 16) (i64.const 16)) (local.set $e) (local.set $n)
    (i32.or (local.get $e)
      (i32.or (i64.ne (local.get $n) (i64.const 16))
        (i32.or
          (i32.ne (i32x4.extract_lane 0 (array.get $a (local.get $a) (i32.const 0))) (i32.const 1))
          (i32.ne (i32x4.extract_lane 0 (array.get $a (local.get $a) (i32.const 2))) (i32.const 1)))))))
(assert_return (invoke "run") (i32.const 0))
