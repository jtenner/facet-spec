;; WPSI conformance test: memory32/readv-cross-memory
;; Purpose: Memory32 readv scatters bytes across memories in iovec order.
;; Required profiles: core, memory32, multi-memory, filesystem
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

  (memory $a 1)
  (memory $b 1)
  (data (memory $a) (i32.const 300) "readv.bin")
  (data (memory $a) (i32.const 400) "abcDEF")
  (func $iov (param $at i32) (param $mem i32) (param $ptr i32) (param $len i32)
    (i32.store $a (local.get $at) (local.get $mem))
    (i32.store $a offset=4 (local.get $at) (local.get $ptr))
    (i32.store $a offset=8 (local.get $at) (local.get $len))
    (i32.store $a offset=12 (local.get $at) (i32.const 0)))
  (func (export "run") (result i32)
    (local $dir i32) (local $fd i32) (local $e i32) (local $n i64) (local $off i64)
    (call $scratch (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 300) (i32.const 9) (i32.const 0) (i32.const 5) (i64.const 63)) (local.set $e) (local.set $fd)
    (call $write (local.get $fd) (i32.const 0) (i32.const 400) (i32.const 6)) (local.set $e) (local.set $n)
    (call $seek (local.get $fd) (i64.const 0) (i32.const 0)) (local.set $e) (local.set $off)
    (call $iov (i32.const 0) (i32.const 0) (i32.const 100) (i32.const 3))
    (call $iov (i32.const 16) (i32.const 1) (i32.const 200) (i32.const 3))
    (call $readv (local.get $fd) (i32.const 0) (i32.const 0) (i32.const 2)) (local.set $e) (local.set $n)
    (drop (call $close (local.get $fd))) (drop (call $close (local.get $dir)))
    (i32.or (local.get $e)
      (i32.or (i64.ne (local.get $n) (i64.const 6))
        (i32.or (i32.ne (i32.load8_u $a (i32.const 100)) (i32.const 97))
                (i32.ne (i32.load8_u $b (i32.const 202)) (i32.const 70))))))
)
(assert_return (invoke "run") (i32.const 0))
