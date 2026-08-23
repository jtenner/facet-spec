;; Facet conformance test: memory64/file-roundtrip
;; Purpose: Memory64 paths and buffers can round-trip file data without narrowing addresses.
;; Required profiles: core, memory64, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fs_preopen_get" (func $scratch (param i32) (result i32 i32)))
  (import "facet" "path_open_mem64_i8" (func $open (param i32 i32 i64 i64 i32 i32 i64) (result i32 i32)))
  (import "facet" "fd_write_mem64" (func $write (param i32 i32 i64 i64) (result i64 i32)))
  (import "facet" "fd_read_mem64" (func $read (param i32 i32 i64 i64) (result i64 i32)))
  (import "facet" "fd_pread_mem64" (func $pread (param i32 i64 i32 i64 i64) (result i64 i32)))
  (import "facet" "fd_pwrite_mem64" (func $pwrite (param i32 i64 i32 i64 i64) (result i64 i32)))
  (import "facet" "fd_readv_mem64" (func $readv (param i32 i32 i64 i32) (result i64 i32)))
  (import "facet" "fd_writev_mem64" (func $writev (param i32 i32 i64 i32) (result i64 i32)))
  (import "facet" "fd_seek" (func $seek (param i32 i64 i32) (result i64 i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))
  (memory i64 1)
  (data (i64.const 0) "m64.bin")
  (data (i64.const 32) "memory64")

  (func (export "run") (result i32)
    (local $dir i32) (local $fd i32) (local $e i32) (local $n i64) (local $off i64)
    (call $scratch (i32.const 0)) (local.set $e) (local.set $dir)
    (if (local.get $e) (then (return (local.get $e))))
    (call $open (local.get $dir) (i32.const 0) (i64.const 0) (i64.const 7) (i32.const 0) (i32.const 5) (i64.const 63))
    (local.set $e) (local.set $fd)
    (if (local.get $e) (then (return (local.get $e))))

    (call $write (local.get $fd) (i32.const 0) (i64.const 32) (i64.const 8))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 8)))
      (then (return (i32.const 1))))
    (call $seek (local.get $fd) (i64.const 0) (i32.const 0))
    (local.set $e) (local.set $off)
    (if (i32.or (local.get $e) (local.get $off))
      (then (return (i32.const 2))))

    ;; Positional Memory64 I/O uses i64 guest addresses and leaves the sequential
    ;; file position untouched. Writing the same bytes keeps the fixture deterministic.
    (call $pwrite (local.get $fd) (i64.const 0) (i32.const 0) (i64.const 32) (i64.const 8))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 8)))
      (then (return (i32.const 3))))
    (call $pread (local.get $fd) (i64.const 0) (i32.const 0) (i64.const 80) (i64.const 8))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e)
          (i32.or (i64.ne (local.get $n) (i64.const 8))
                  (i64.ne (i64.load (i64.const 80)) (i64.const 3762328071117301101))))
      (then (return (i32.const 4))))

    ;; Empty Memory64 iovec tables are successful no-ops and still exercise the
    ;; Memory64 table-address ABI for both scatter and gather operations.
    (call $readv (local.get $fd) (i32.const 0) (i64.const 0) (i32.const 0))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (local.get $n))
      (then (return (i32.const 5))))
    (call $writev (local.get $fd) (i32.const 0) (i64.const 0) (i32.const 0))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (local.get $n))
      (then (return (i32.const 6))))

    ;; The sequential position is still zero after pwrite/pread and empty vectored I/O.
    (call $read (local.get $fd) (i32.const 0) (i64.const 64) (i64.const 8))
    (local.set $e) (local.set $n)
    (drop (call $close (local.get $fd)))
    (drop (call $close (local.get $dir)))
    (i32.or (local.get $e)
      (i32.or (i64.ne (local.get $n) (i64.const 8))
              (i64.ne (i64.load (i64.const 64)) (i64.const 3762328071117301101)))))
)
(assert_return (invoke "run") (i32.const 0))
