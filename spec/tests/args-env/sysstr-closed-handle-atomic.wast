;; WPSI conformance test: args-env/sysstr-closed-handle-atomic
;; Purpose: Reading a closed sysstr returns ERR_BAD_HANDLE, zero units, and leaves destination bytes untouched.
;; Required profiles: core, memory32, args-env, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "args_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "sysstr_read_mem32" (func $read (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (func (export "run") (result i64 i32 i32)
    (local $h i32) (local $e i32) (local $n i64)
    (i32.store8 (i32.const 8) (i32.const 170))
    (call $get (i32.const 0)) (local.set $e) (local.set $h)
    (drop (call $close (local.get $h)))
    (call $read (local.get $h) (i32.const 1) (i32.const 0) (i32.const 8) (i32.const 1)) (local.set $e) (local.set $n)
    (local.get $n) (local.get $e) (i32.load8_u (i32.const 8))))
(assert_return (invoke "run") (i64.const 0) (i32.const 4) (i32.const 170))
