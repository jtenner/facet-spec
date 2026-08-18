;; Facet conformance test: gc-array/writev-nested-i8
;; Purpose: GC writev traverses a nested array in outer-index order.
;; Required profiles: core, memory32, gc-array, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (type $bytes (array i8))
  (type $buffers (array (mut (ref null $bytes))))
  (import "facet" "fs_preopen_get" (func $scratch (param i32) (result i32 i32)))
  (import "facet" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "fd_writev_array_i8" (func $writev (param i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "fd_read_mem32" (func $read (param i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "fd_seek" (func $seek (param i32 i64 i32) (result i64 i32)))
  (memory 1)
  (data (i32.const 0) "nested.bin")
  (func (export "run") (result i32)
    (local $x (ref $bytes)) (local $y (ref $bytes)) (local $b (ref $buffers))
    (local $dir i32) (local $fd i32) (local $e i32) (local $n i64) (local $off i64)
    (local.set $x (array.new_fixed $bytes 3 (i32.const 97) (i32.const 98) (i32.const 99)))
    (local.set $y (array.new_fixed $bytes 3 (i32.const 68) (i32.const 69) (i32.const 70)))
    (local.set $b (array.new_default $buffers (i32.const 2)))
    (array.set $buffers (local.get $b) (i32.const 0) (local.get $x))
    (array.set $buffers (local.get $b) (i32.const 1) (local.get $y))
    (call $scratch (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 10) (i32.const 0) (i32.const 5) (i64.const 63)) (local.set $e) (local.set $fd)
    (call $writev (local.get $fd) (local.get $b) (i32.const 0) (i32.const 2)) (local.set $e) (local.set $n)
    (call $seek (local.get $fd) (i64.const 0) (i32.const 0)) (local.set $e) (local.set $off)
    (call $read (local.get $fd) (i32.const 0) (i32.const 64) (i32.const 6)) (local.set $e) (local.set $n)
    (i32.or (local.get $e)
      (i32.or (i32.ne (i32.load (i32.const 64)) (i32.const 1145258561))
              (i32.ne (i32.load16_u (i32.const 68)) (i32.const 17989)))))
)
(assert_return (invoke "run") (i32.const 0))
