;; WPSI conformance test: gc-array/zero-length-at-end
;; Purpose: A zero-length GC operation at the exact logical end succeeds and preserves the element.
;; Required profiles: core, gc-array, random
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array (mut i32)))
  (import "facet" "random_fill_array_i32" (func $fill (param (ref array) i64 i64) (result i64 i32)))
  (func (export "run") (result i64 i32 i32)
    (local $a (ref $a)) (local $n i64) (local $e i32)
    (local.set $a (array.new_fixed $a 1 (i32.const 305419896)))
    (call $fill (local.get $a) (i64.const 4) (i64.const 0)) (local.set $e) (local.set $n)
    (local.get $n) (local.get $e) (array.get $a (local.get $a) (i32.const 0))))
(assert_return (invoke "run") (i64.const 0) (i32.const 0) (i32.const 305419896))
