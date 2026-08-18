;; WPSI conformance test: filesystem/seek-tell-size
;; Purpose: Tell tracks sequential writes and SEEK_END observes a truncated size.
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
  (data (i32.const 0) "position.bin")
  (data (i32.const 32) "abcdefgh")
  (func (export "run") (result i32)
    (local $dir i32) (local $fd i32) (local $e i32) (local $n i64) (local $off i64)
    (call $scratch (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 12) (i32.const 0) (i32.const 5) (i64.const 63)) (local.set $e) (local.set $fd)
    (call $write (local.get $fd) (i32.const 0) (i32.const 32) (i32.const 8)) (local.set $e) (local.set $n)
    (call $tell (local.get $fd)) (local.set $e) (local.set $off)
    (if (i64.ne (local.get $off) (i64.const 8)) (then (return (i32.const 101))))
    (local.set $e (call $set_size (local.get $fd) (i64.const 3)))
    (call $seek (local.get $fd) (i64.const 0) (i32.const 2)) (local.set $e) (local.set $off)
    (drop (call $close (local.get $fd))) (drop (call $close (local.get $dir)))
    (i32.or (local.get $e) (i64.ne (local.get $off) (i64.const 3)))))
(assert_return (invoke "run") (i32.const 0))
