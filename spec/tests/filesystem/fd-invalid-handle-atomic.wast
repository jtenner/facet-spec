;; WPSI conformance test: filesystem/fd-invalid-handle-atomic
;; Purpose: fd_read validates an invalid descriptor before touching the destination buffer.
;; Required profiles: core, memory32, filesystem, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fd_read_mem32" (func $read (param i32 i32 i32 i32) (result i64 i32)))
  (memory 1)
  (func (export "run") (result i64 i32 i32)
    (local $n i64) (local $e i32)
    (i32.store8 (i32.const 16) (i32.const 170))
    (call $read (i32.const 0) (i32.const 0) (i32.const 16) (i32.const 1)) (local.set $e) (local.set $n)
    (local.get $n) (local.get $e) (i32.load8_u (i32.const 16))))
(assert_return (invoke "run") (i64.const 0) (i32.const 4) (i32.const 170))
