;; Facet conformance test: gc-array/immutable-source-accepted
;; Purpose: Source-only GC I/O accepts an immutable packed byte array.
;; Required profiles: core, memory32, gc-array, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array i8))
  (import "facet" "fs_preopen_get" (func $scratch (param i32) (result i32 i32)))
  (import "facet" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "fd_write_array_i8" (func $write (param i32 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_seek" (func $seek (param i32 i64 i32) (result i64 i32)))
  (import "facet" "fd_read_mem32" (func $read (param i32 i32 i32 i32) (result i64 i32)))
  (memory 1)
  (data (i32.const 0) "immutable.bin")
  (func (export "run") (result i32 i32)
    (local $a (ref $a)) (local $dir i32) (local $fd i32) (local $e i32) (local $n i64) (local $off i64)
    (local.set $a (array.new_fixed $a 3 (i32.const 65) (i32.const 66) (i32.const 67)))
    (call $scratch (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 13) (i32.const 0) (i32.const 5) (i64.const 63)) (local.set $e) (local.set $fd)
    (call $write (local.get $fd) (local.get $a) (i64.const 0) (i64.const 3)) (local.set $e) (local.set $n)
    (call $seek (local.get $fd) (i64.const 0) (i32.const 0)) (local.set $e) (local.set $off)
    (call $read (local.get $fd) (i32.const 0) (i32.const 32) (i32.const 3)) (local.set $e) (local.set $n)
    (i32.load16_u (i32.const 32))
    (i32.load8_u (i32.const 34))))
(assert_return (invoke "run") (i32.const 16961) (i32.const 67))
