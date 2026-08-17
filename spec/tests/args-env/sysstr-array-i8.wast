;; WPSI conformance test: args-env/sysstr-array-i8
;; Purpose: sysstr_read_array_i8 writes UTF-8 directly into a packed GC byte array and preserves sentinels.
;; Required profiles: core, gc-array, args-env
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array (mut i8)))
  (import "wpsi" "args_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "sysstr_read_array_i8" (func $read (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (func (export "run") (result i32)
    (local $a (ref $a)) (local $h i32) (local $e i32) (local $n i64)
    (local.set $a (array.new_fixed $a 7 (i32.const 126) (i32.const 126) (i32.const 126) (i32.const 126) (i32.const 126) (i32.const 126) (i32.const 126)))
    (call $get (i32.const 1)) (local.set $e) (local.set $h)
    (call $read (local.get $h) (i32.const 1) (local.get $a) (i32.const 1) (i32.const 5)) (local.set $e) (local.set $n)
    (drop (call $close (local.get $h)))
    (i32.or (local.get $e)
      (i32.or (i64.ne (local.get $n) (i64.const 5))
        (i32.or (i32.ne (array.get_u $a (local.get $a) (i32.const 0)) (i32.const 126))
          (i32.or (i32.ne (array.get_u $a (local.get $a) (i32.const 1)) (i32.const 99))
            (i32.or (i32.ne (array.get_u $a (local.get $a) (i32.const 2)) (i32.const 97))
              (i32.or (i32.ne (array.get_u $a (local.get $a) (i32.const 3)) (i32.const 102))
                (i32.or (i32.ne (array.get_u $a (local.get $a) (i32.const 4)) (i32.const 195))
                  (i32.or (i32.ne (array.get_u $a (local.get $a) (i32.const 5)) (i32.const 169))
                          (i32.ne (array.get_u $a (local.get $a) (i32.const 6)) (i32.const 126))))))))))))
(assert_return (invoke "run") (i32.const 0))
