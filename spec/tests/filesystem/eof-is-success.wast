;; WPSI conformance test: filesystem/eof-is-success
;; Purpose: EOF is represented as zero bytes and ERR_OK.
;; Required profiles: core, memory32, filesystem
;;
;; SPDX-License-Identifier: MIT

(module

  (import "facet" "fs_preopen_get" (func $scratch (param i32) (result i32 i32)))
  (import "facet" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "fd_read_mem32" (func $read (param i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "fd_write_mem32" (func $write (param i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "fd_seek" (func $seek (param i32 i64 i32) (result i64 i32)))
  (import "facet" "fd_tell" (func $tell (param i32) (result i64 i32)))
  (import "facet" "fd_set_size" (func $set_size (param i32 i64) (result i32)))
  (import "facet" "fd_stat" (func $stat (param i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))

  (memory 1)
  (data (i32.const 0) "eof.bin")
  (func (export "run") (result i64 i32)
    (local $dir i32) (local $fd i32) (local $e i32) (local $n i64)
    (call $scratch (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 7) (i32.const 0) (i32.const 5) (i64.const 63)) (local.set $e) (local.set $fd)
    (call $read (local.get $fd) (i32.const 0) (i32.const 32) (i32.const 8)) (local.set $e) (local.set $n)
    (drop (call $close (local.get $fd))) (drop (call $close (local.get $dir)))
    (local.get $n) (local.get $e)))
(assert_return (invoke "run") (i64.const 0) (i32.const 0))
