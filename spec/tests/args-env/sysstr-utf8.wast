;; WPSI conformance test: args-env/sysstr-utf8
;; Purpose: UTF-8 sysstr length and bytes are exact and not NUL-terminated.
;; Required profiles: core, memory32, args-env
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "args_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "sysstr_len" (func $len (param i32 i32) (result i64 i32)))
  (import "wpsi" "sysstr_read_mem32" (func $read (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (func (export "run") (result i32)
    (local $h i32) (local $err i32) (local $n i64)
    (call $get (i32.const 1)) (local.set $err) (local.set $h)
    (if (i32.ne (local.get $err) (i32.const 0)) (then (return (i32.const 10))))
    (call $len (local.get $h) (i32.const 1)) (local.set $err) (local.set $n)
    (if (i32.or (i32.ne (local.get $err) (i32.const 0)) (i64.ne (local.get $n) (i64.const 5))) (then (return (i32.const 11))))
    (call $read (local.get $h) (i32.const 1) (i32.const 0) (i32.const 8) (i32.const 5)) (local.set $err) (local.set $n)
    (drop (call $close (local.get $h)))
    (if (result i32) (i32.or (i32.ne (local.get $err) (i32.const 0)) (i64.ne (local.get $n) (i64.const 5)))
      (then (i32.const 12))
      (else
        (i32.or
          (i32.ne (i32.load8_u (i32.const 8)) (i32.const 99))
          (i32.or (i32.ne (i32.load8_u (i32.const 9)) (i32.const 97))
            (i32.or (i32.ne (i32.load8_u (i32.const 10)) (i32.const 102))
              (i32.or (i32.ne (i32.load8_u (i32.const 11)) (i32.const 195))
                      (i32.ne (i32.load8_u (i32.const 12)) (i32.const 169))))))))))
(assert_return (invoke "run") (i32.const 0))
