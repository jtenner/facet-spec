;; WPSI conformance test: gc-array/fd-read-partial-i16
;; Purpose: A partial i16 read overlays bytes while preserving unselected bytes in boundary elements.
;; Required profiles: core, memory32, gc-array, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array (mut i16)))
  (import "wpsi" "fs_scratch" (func $scratch (result i32 i32)))
  (import "wpsi" "path_open_mem32" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "wpsi" "fd_write_mem32" (func $write (param i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "fd_read_array_i16" (func $reada (param i32 (ref array) i64 i64) (result i64 i32)))
  (import "wpsi" "fd_seek" (func $seek (param i32 i64 i32) (result i64 i32)))
  (memory 1)
  (data (i32.const 0) "partial.bin")
  (data (i32.const 32) "\aa\bb\cc")
  (func (export "run") (result i32 i32 i32 i32)
    (local $a (ref $a)) (local $dir i32) (local $fd i32) (local $e i32) (local $n i64) (local $off i64)
    (local.set $a (array.new_fixed $a 3 (i32.const 4386) (i32.const 13124) (i32.const 21862)))
    (call $scratch) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 11) (i32.const 1) (i32.const 5) (i64.const 63)) (local.set $e) (local.set $fd)
    (call $write (local.get $fd) (i32.const 0) (i32.const 32) (i32.const 3)) (local.set $e) (local.set $n)
    (call $seek (local.get $fd) (i64.const 0) (i32.const 0)) (local.set $e) (local.set $off)
    (call $reada (local.get $fd) (local.get $a) (i64.const 1) (i64.const 3)) (local.set $e) (local.set $n)
    (local.get $e)
    (array.get_u $a (local.get $a) (i32.const 0))
    (array.get_u $a (local.get $a) (i32.const 1))
    (array.get_u $a (local.get $a) (i32.const 2)))
)
(assert_return (invoke "run") (i32.const 0) (i32.const 43554) (i32.const 52411) (i32.const 21862))
