;; WPSI conformance test: memory64/file-roundtrip
;; Purpose: Memory64 paths and buffers can round-trip file data without narrowing addresses.
;; Required profiles: core, memory64, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_scratch" (func $scratch (result i32 i32)))
  (import "wpsi" "path_open_mem64_i8" (func $open (param i32 i32 i64 i64 i32 i32 i64) (result i32 i32)))
  (import "wpsi" "fd_write_mem64" (func $write (param i32 i32 i64 i64) (result i64 i32)))
  (import "wpsi" "fd_read_mem64" (func $read (param i32 i32 i64 i64) (result i64 i32)))
  (import "wpsi" "fd_seek" (func $seek (param i32 i64 i32) (result i64 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (memory i64 1)
  (data (i64.const 0) "m64.bin")
  (data (i64.const 32) "memory64")
  (func (export "run") (result i32)
    (local $dir i32) (local $fd i32) (local $e i32) (local $n i64) (local $off i64)
    (call $scratch) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i64.const 0) (i64.const 7) (i32.const 0) (i32.const 5) (i64.const 63)) (local.set $e) (local.set $fd)
    (call $write (local.get $fd) (i32.const 0) (i64.const 32) (i64.const 8)) (local.set $e) (local.set $n)
    (call $seek (local.get $fd) (i64.const 0) (i32.const 0)) (local.set $e) (local.set $off)
    (call $read (local.get $fd) (i32.const 0) (i64.const 64) (i64.const 8)) (local.set $e) (local.set $n)
    (drop (call $close (local.get $fd))) (drop (call $close (local.get $dir)))
    (i32.or (local.get $e)
      (i32.or (i64.ne (local.get $n) (i64.const 8))
        (i32.ne (i64.load (i64.const 64)) (i64.const 3761688987575706989)))))
)
(assert_return (invoke "run") (i32.const 0))
