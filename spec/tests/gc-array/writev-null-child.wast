;; WPSI conformance test: gc-array/writev-null-child
;; Purpose: A selected null child is rejected before scatter/gather I/O.
;; Required profiles: core, gc-array, filesystem, adversarial
;; Test kind: harness
;;
;; SPDX-License-Identifier: MIT

(module
  (type $bytes (array i8))
  (type $buffers (array (mut (ref null $bytes))))
  (import "facet" "fd_writev_array_i8" (func $writev (param i32 (ref array) i32 i32) (result i64 i32)))
  (func (export "run") (param $fd i32) (result i32)
    (local $b (ref $buffers)) (local $n i64) (local $e i32)
    (local.set $b (array.new_default $buffers (i32.const 1)))
    (call $writev (local.get $fd) (local.get $b) (i32.const 0) (i32.const 1)) (local.set $e) (local.set $n)
    (i32.and (i64.eqz (local.get $n)) (i32.ne (local.get $e) (i32.const 0))))
)
