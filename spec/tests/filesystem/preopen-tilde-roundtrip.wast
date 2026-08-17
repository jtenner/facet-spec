;; WPSI conformance test: filesystem/preopen-tilde-roundtrip
;; Purpose: A writable `~` preopen uses ordinary file operations with no scratch-specific imports.
;; Required profiles: core, memory32, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "wpsi" "fd_read_mem32" (func $read (param i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "fd_write_mem32" (func $write (param i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "fd_seek" (func $seek (param i32 i64 i32) (result i64 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (data (i32.const 0) "roundtrip.cleanup")
  (data (i32.const 32) "hello")
  (func (export "run") (result i32)
    (local $dir i32) (local $fd i32) (local $e i32) (local $n i64) (local $off i64)
    (call $get (i32.const 0)) (local.set $e) (local.set $dir)
    (if (local.get $e) (then (return (local.get $e))))
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 17) (i32.const 0) (i32.const 5) (i64.const 63)) (local.set $e) (local.set $fd)
    (if (local.get $e) (then (return (local.get $e))))
    (call $write (local.get $fd) (i32.const 0) (i32.const 32) (i32.const 5)) (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 5))) (then (return (i32.const 101))))
    (call $seek (local.get $fd) (i64.const 0) (i32.const 0)) (local.set $e) (local.set $off)
    (if (local.get $e) (then (return (local.get $e))))
    (call $read (local.get $fd) (i32.const 0) (i32.const 64) (i32.const 5)) (local.set $e) (local.set $n)
    (drop (call $close (local.get $fd)))
    (drop (call $close (local.get $dir)))
    (if (result i32) (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 5)))
      (then (i32.const 102))
      (else (i32.ne (i32.load (i32.const 64)) (i32.const 1819043176))))))
(assert_return (invoke "run") (i32.const 0))
