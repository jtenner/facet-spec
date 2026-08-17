;; WPSI conformance test: args-env/args-read-mem32-utf8
;; Purpose: Arguments copy directly into caller-owned Memory32 without an intermediate string handle.
;; Required profiles: core, memory32, args-env, text
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "args_read_mem32" (func $read (param i32 i32 i32 i32 i32) (result i64 i32)))
  (memory 1)
  (func (export "run") (result i32)
    (local $n i64) (local $e i32)
    (call $read (i32.const 0) (i32.const 1) (i32.const 0) (i32.const 16) (i32.const 5))
    (local.set $e) (local.set $n)
    (i32.or (local.get $e)
      (i32.or (i64.ne (local.get $n) (i64.const 5))
              (i32.ne (i32.load8_u (i32.const 16)) (i32.const 97)))))
)
(assert_return (invoke "run") (i32.const 0))
