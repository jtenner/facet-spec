;; WPSI conformance test: gc-array/fd-write-logical-byte-view-v128
;; Purpose: fd_write_array_v128 exposes the same 16 bytes as v128.store.
;; Required profiles: core, memory32, gc-array, simd, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array v128))
  (import "wpsi" "fs_scratch" (func $scratch (result i32 i32)))
  (import "wpsi" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "wpsi" "fd_write_array_v128" (func $writea (param i32 (ref array) i64 i64) (result i64 i32)))
  (import "wpsi" "fd_read_mem32" (func $read (param i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "fd_seek" (func $seek (param i32 i64 i32) (result i64 i32)))
  (memory 1)
  (data (i32.const 0) "view-v128.bin")
  (func (export "run") (result i32)
    (local $a (ref $a)) (local $dir i32) (local $fd i32) (local $e i32) (local $n i64) (local $off i64)
    (local.set $a (array.new_fixed $a 1 (v128.const i8x16 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15)))
    (call $scratch) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 13) (i32.const 0) (i32.const 5) (i64.const 63)) (local.set $e) (local.set $fd)
    (call $writea (local.get $fd) (local.get $a) (i64.const 0) (i64.const 16)) (local.set $e) (local.set $n)
    (call $seek (local.get $fd) (i64.const 0) (i32.const 0)) (local.set $e) (local.set $off)
    (call $read (local.get $fd) (i32.const 0) (i32.const 128) (i32.const 16)) (local.set $e) (local.set $n)
    (i32.or (local.get $e)
      (i32.or (i64.ne (i64.load (i32.const 128)) (i64.const 506097522914230528))
              (i64.ne (i64.load (i32.const 136)) (i64.const 1084818905618843912)))))
)
(assert_return (invoke "run") (i32.const 0))
