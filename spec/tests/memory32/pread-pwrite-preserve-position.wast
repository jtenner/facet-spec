;; Facet conformance test: memory32/pread-pwrite-preserve-position
;; Purpose: Positional I/O modifies file data without changing the sequential descriptor position.
;; Required profiles: core, memory32, filesystem
;;
;; SPDX-License-Identifier: MIT

(module

  (import "facet" "fs_preopen_get" (func $scratch (param i32) (result i32 i32)))
  (import "facet" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "fd_read_mem32" (func $read (param i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "fd_write_mem32" (func $write (param i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "fd_pread_mem32" (func $pread (param i32 i64 i32 i32 i32) (result i64 i32)))
  (import "facet" "fd_pwrite_mem32" (func $pwrite (param i32 i64 i32 i32 i32) (result i64 i32)))
  (import "facet" "fd_readv_mem32" (func $readv (param i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "fd_writev_mem32" (func $writev (param i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "fd_seek" (func $seek (param i32 i64 i32) (result i64 i32)))
  (import "facet" "fd_tell" (func $tell (param i32) (result i64 i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))

  (memory 1)
  (data (i32.const 0) "positional.bin")
  (data (i32.const 32) "abcdefgh")
  (data (i32.const 48) "XY")
  (func (export "run") (result i32)
    (local $dir i32) (local $fd i32) (local $e i32) (local $n i64) (local $off i64)
    (call $scratch (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 14) (i32.const 0) (i32.const 5) (i64.const 63)) (local.set $e) (local.set $fd)
    (call $write (local.get $fd) (i32.const 0) (i32.const 32) (i32.const 8)) (local.set $e) (local.set $n)
    (call $pwrite (local.get $fd) (i64.const 2) (i32.const 0) (i32.const 48) (i32.const 2)) (local.set $e) (local.set $n)
    (call $tell (local.get $fd)) (local.set $e) (local.set $off)
    (if (i64.ne (local.get $off) (i64.const 8)) (then (return (i32.const 10))))
    (call $pread (local.get $fd) (i64.const 0) (i32.const 0) (i32.const 64) (i32.const 8)) (local.set $e) (local.set $n)
    (call $tell (local.get $fd)) (local.set $e) (local.set $off)
    (drop (call $close (local.get $fd))) (drop (call $close (local.get $dir)))
    (i32.or (i64.ne (local.get $off) (i64.const 8))
      (i32.or (i32.ne (i32.load (i32.const 64)) (i32.const 1482248801))
              (i32.ne (i32.load (i32.const 68)) (i32.const 1751606885)))))
)
(assert_return (invoke "run") (i32.const 0))
