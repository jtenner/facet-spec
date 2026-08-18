;; WPSI conformance test: gc-array/fd-write-logical-byte-view-i8
;; Purpose: fd_write_array_i8 uses the normative little-endian logical byte view.
;; Required profiles: core, memory32, gc-array, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array i8))
  (import "facet" "fs_preopen_get" (func $scratch (param i32) (result i32 i32)))
  (import "facet" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "fd_write_array_i8" (func $writea (param i32 (ref array) i64 i64) (result i64 i32)))
  (import "facet" "fd_read_mem32" (func $read (param i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "fd_seek" (func $seek (param i32 i64 i32) (result i64 i32)))
  (memory 1)
  (data (i32.const 0) "view-i8.bin")
  (func (export "run") (result i32)
    (local $a (ref $a)) (local $dir i32) (local $fd i32) (local $e i32) (local $n i64) (local $off i64)
    (local.set $a (array.new_fixed $a 4 (i32.const 17) (i32.const 34) (i32.const 51) (i32.const 68)))
    (call $scratch (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 11) (i32.const 0) (i32.const 5) (i64.const 63)) (local.set $e) (local.set $fd)
    (call $writea (local.get $fd) (local.get $a) (i64.const 0) (i64.const 4)) (local.set $e) (local.set $n)
    (call $seek (local.get $fd) (i64.const 0) (i32.const 0)) (local.set $e) (local.set $off)
    (call $read (local.get $fd) (i32.const 0) (i32.const 128) (i32.const 4)) (local.set $e) (local.set $n)
    (i32.or (local.get $e) (i32.ne (i32.load (i32.const 128)) (i32.const 1144201745))))
)
(assert_return (invoke "run") (i32.const 0))
