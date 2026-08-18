;; WPSI conformance test: gc-array/random-fill-i16
;; Purpose: array<i16> is recognized and only the selected logical byte range is modified.
;; Required profiles: core, gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array (mut i16)))
  (import "facet" "random_fill_array_i16" (func $fill (param (ref array) i64 i64) (result i64 i32)))
  (func (export "run") (result i32)
    (local $a (ref $a)) (local $n i64) (local $e i32)
    (local.set $a (array.new $a (i32.const 8755) (i32.const 4)))
    (call $fill (local.get $a) (i64.const 2) (i64.const 2)) (local.set $e) (local.set $n)
    (i32.or (local.get $e)
      (i32.or (i64.ne (local.get $n) (i64.const 2))
        (i32.or
          (i32.eqz (i32.eq (array.get_u $a (local.get $a) (i32.const 0)) (i32.const 8755)))
          (i32.eqz (i32.eq (array.get_u $a (local.get $a) (i32.const 2)) (i32.const 8755))))))))
(assert_return (invoke "run") (i32.const 0))
