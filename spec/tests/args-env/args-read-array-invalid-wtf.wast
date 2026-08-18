;; Facet conformance test: args-env/args-read-array-invalid-wtf
;; Purpose: Allocating string reads reject non-boolean WTF selectors with null and ERR_INVALID.
;; Required profiles: core, gc-array, args-env
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array (mut i8)))
  (import "facet" "args_read_array_i8"
    (func $read (param i32 i32) (result (ref null $a) i32)))
  (func (export "run") (result i32 i32)
    (local $v (ref null $a)) (local $e i32)
    (call $read (i32.const 0) (i32.const 2)) (local.set $e) (local.set $v)
    (ref.is_null (local.get $v))
    (local.get $e)))
(assert_return (invoke "run") (i32.const 1) (i32.const 12))
