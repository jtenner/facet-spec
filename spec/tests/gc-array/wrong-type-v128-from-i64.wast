;; WPSI conformance test: gc-array/wrong-type-v128-from-i64
;; Purpose: The v128 entry point rejects a dynamic array<i64> with ERR_TYPE.
;; Required profiles: core, gc-array, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (type $actual (array (mut i64)))
  (import "facet" "random_fill_array_v128" (func $fill (param (ref array) i64 i64) (result i64 i32)))
  (func (export "run") (result i64 i32)
    (local $a (ref $actual))
    (local.set $a (array.new $actual (i64.const 0) (i32.const 2)))
    (call $fill (local.get $a) (i64.const 0) (i64.const 1))))
(assert_return (invoke "run") (i64.const 0) (i32.const 25))
