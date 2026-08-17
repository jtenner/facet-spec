;; WPSI conformance test: memory32/iovec-invalid-second-atomic
;; Purpose: All iovecs are validated before writev performs a partial write.
;; Required profiles: core, memory32, multi-memory, filesystem, adversarial
;;
;; SPDX-License-Identifier: MIT

(module

  (import "wpsi" "fs_preopen_get" (func $scratch (param i32) (result i32 i32)))
  (import "wpsi" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "wpsi" "fd_read_mem32" (func $read (param i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "fd_write_mem32" (func $write (param i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "fd_pread_mem32" (func $pread (param i32 i64 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "fd_pwrite_mem32" (func $pwrite (param i32 i64 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "fd_readv_mem32" (func $readv (param i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "fd_writev_mem32" (func $writev (param i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "fd_seek" (func $seek (param i32 i64 i32) (result i64 i32)))
  (import "wpsi" "fd_tell" (func $tell (param i32) (result i64 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))

  (memory 1)
  (data (i32.const 300) "badvec.bin")
  (data (i32.const 400) "abcdef")
  (func $iov (param $at i32) (param $mem i32) (param $ptr i32) (param $len i32)
    (i32.store (local.get $at) (local.get $mem))
    (i32.store offset=4 (local.get $at) (local.get $ptr))
    (i32.store offset=8 (local.get $at) (local.get $len))
    (i32.store offset=12 (local.get $at) (i32.const 0)))
  (func (export "run") (result i64 i32)
    (local $dir i32) (local $fd i32) (local $e i32) (local $n i64)
    (call $scratch (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 300) (i32.const 10) (i32.const 0) (i32.const 5) (i64.const 63)) (local.set $e) (local.set $fd)
    (call $iov (i32.const 0) (i32.const 0) (i32.const 400) (i32.const 3))
    (call $iov (i32.const 16) (i32.const 99) (i32.const 403) (i32.const 3))
    (call $writev (local.get $fd) (i32.const 0) (i32.const 0) (i32.const 2)) (local.set $e) (local.set $n)
    (drop (call $close (local.get $fd))) (drop (call $close (local.get $dir)))
    (local.get $n) (local.get $e))
)
(assert_return (invoke "run") (i64.const 0) (i32.const 24))
