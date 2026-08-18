;; Facet conformance test: gc-array/random-fill-i64
;; Purpose: array<i64> is recognized and only the selected logical byte range is modified.
;; Required profiles: core, gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array (mut i64)))
  (import "facet" "random_fill_array_i64" (func $fill (param (ref array) i64 i64) (result i64 i32)))
  (func (export "run") (result i32)
    (local $a (ref $a)) (local $n i64) (local $e i32)
    (local.set $a (array.new $a (i64.const 2464388554683811993) (i32.const 4)))
    (call $fill (local.get $a) (i64.const 8) (i64.const 8)) (local.set $e) (local.set $n)
    (i32.or (local.get $e)
      (i32.or (i64.ne (local.get $n) (i64.const 8))
        (i32.or
          (i32.eqz (i64.eq (array.get $a (local.get $a) (i32.const 0)) (i64.const 2464388554683811993)))
          (i32.eqz (i64.eq (array.get $a (local.get $a) (i32.const 2)) (i64.const 2464388554683811993))))))))
(assert_return (invoke "run") (i32.const 0))
