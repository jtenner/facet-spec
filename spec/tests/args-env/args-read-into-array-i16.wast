;; Facet conformance test: args-env/args-read-into-array-i16
;; Purpose: UTF-16 arguments can be copied directly into an existing mutable array<i16>.
;; Required profiles: core, gc-array, args-env, text
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array (mut i16)))
  (import "facet" "args_read_into_array_i16" (func $read (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (func (export "run") (result i32)
    (local $a (ref $a)) (local $n i64) (local $e i32)
    (local.set $a (array.new_default $a (i32.const 5)))
    (call $read (i32.const 0) (i32.const 0) (local.get $a) (i32.const 0) (i32.const 5))
    (local.set $e) (local.set $n)
    (i32.or (local.get $e)
      (i32.or (i64.ne (local.get $n) (i64.const 5))
              (i32.ne (array.get_u $a (local.get $a) (i32.const 0)) (i32.const 97)))))
)
(assert_return (invoke "run") (i32.const 0))
