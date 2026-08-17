;; WPSI conformance test: args-env/sysstr-array-i16
;; Purpose: sysstr_read_array_i16 writes a UTF-16 surrogate pair directly into a packed GC array.
;; Required profiles: core, gc-array, args-env
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array (mut i16)))
  (import "wpsi" "args_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "sysstr_read_array_i16" (func $read (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (func (export "run") (result i32 i32 i32 i32 i32)
    (local $a (ref $a)) (local $h i32) (local $e i32) (local $n i64)
    (local.set $a (array.new_fixed $a 4 (i32.const 30583) (i32.const 30583) (i32.const 30583) (i32.const 30583)))
    (call $get (i32.const 1)) (local.set $e) (local.set $h)
    (call $read (local.get $h) (i32.const 2) (local.get $a) (i32.const 1) (i32.const 2)) (local.set $e) (local.set $n)
    (drop (call $close (local.get $h)))
    (local.get $e)
    (i32.wrap_i64 (local.get $n))
    (array.get_u $a (local.get $a) (i32.const 0))
    (array.get_u $a (local.get $a) (i32.const 1))
    (array.get_u $a (local.get $a) (i32.const 2)))
)
(assert_return (invoke "run") (i32.const 0) (i32.const 2) (i32.const 30583) (i32.const 55357) (i32.const 56832))
