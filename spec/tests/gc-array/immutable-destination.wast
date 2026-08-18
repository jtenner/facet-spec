;; Facet conformance test: gc-array/immutable-destination
;; Purpose: Destination operations reject immutable arrays.
;; Required profiles: core, gc-array, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array i8))
  (import "facet" "random_fill_array_i8" (func $fill (param (ref array) i64 i64) (result i64 i32)))
  (func (export "run") (result i64 i32)
    (local $a (ref $a))
    (local.set $a (array.new_fixed $a 2 (i32.const 1) (i32.const 2)))
    (call $fill (local.get $a) (i64.const 0) (i64.const 1))))
(assert_return (invoke "run") (i64.const 0) (i32.const 25))
