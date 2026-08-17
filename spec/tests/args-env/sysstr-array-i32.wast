;; WPSI conformance test: args-env/sysstr-array-i32
;; Purpose: sysstr_read_array_i32 writes the exact UTF-32 scalar into a GC array.
;; Required profiles: core, gc-array, args-env
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array (mut i32)))
  (import "wpsi" "args_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "sysstr_read_array_i32" (func $read (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (func (export "run") (result i32 i32 i32 i32)
    (local $a (ref $a)) (local $h i32) (local $e i32) (local $n i64)
    (local.set $a (array.new_fixed $a 3 (i32.const 1431655765) (i32.const 1431655765) (i32.const 1431655765)))
    (call $get (i32.const 1)) (local.set $e) (local.set $h)
    (call $read (local.get $h) (i32.const 3) (local.get $a) (i32.const 1) (i32.const 1)) (local.set $e) (local.set $n)
    (drop (call $close (local.get $h)))
    (local.get $e)
    (array.get $a (local.get $a) (i32.const 0))
    (array.get $a (local.get $a) (i32.const 1))
    (array.get $a (local.get $a) (i32.const 2)))
)
(assert_return (invoke "run") (i32.const 0) (i32.const 1431655765) (i32.const 128512) (i32.const 1431655765))
