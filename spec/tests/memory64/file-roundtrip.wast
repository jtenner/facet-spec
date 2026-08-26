;; Facet conformance test: memory64/file-roundtrip
;; Purpose: Memory64 paths and buffers can round-trip file data without narrowing addresses.
;; Required profiles: core, memory64, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fs_preopen_get" (func $scratch (param i32) (result i32 i32)))

  (import "facet" "path_open_mem64_i8" (func $open8 (param i32 i32 i64 i64 i32 i32 i64) (result i32 i32)))
  (import "facet" "path_open_mem64_i16" (func $open16 (param i32 i32 i64 i64 i32 i32 i64) (result i32 i32)))
  (import "facet" "path_open_mem64_i32" (func $open32 (param i32 i32 i64 i64 i32 i32 i64) (result i32 i32)))
  (import "facet" "path_stat_mem64_i8" (func $stat8 (param i32 i32 i64 i64 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "path_stat_mem64_i16" (func $stat16 (param i32 i32 i64 i64 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "path_stat_mem64_i32" (func $stat32 (param i32 i32 i64 i64 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "path_create_dir_mem64_i8" (func $mkdir8 (param i32 i32 i64 i64 i32) (result i32)))
  (import "facet" "path_create_dir_mem64_i16" (func $mkdir16 (param i32 i32 i64 i64 i32) (result i32)))
  (import "facet" "path_create_dir_mem64_i32" (func $mkdir32 (param i32 i32 i64 i64 i32) (result i32)))
  (import "facet" "path_remove_mem64_i8" (func $remove8 (param i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_remove_mem64_i16" (func $remove16 (param i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_remove_mem64_i32" (func $remove32 (param i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_rename_mem64_i8" (func $rename8 (param i32 i32 i64 i64 i32 i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_rename_mem64_i16" (func $rename16 (param i32 i32 i64 i64 i32 i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_rename_mem64_i32" (func $rename32 (param i32 i32 i64 i64 i32 i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_link_mem64_i8" (func $link8 (param i32 i32 i64 i64 i32 i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_link_mem64_i16" (func $link16 (param i32 i32 i64 i64 i32 i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_link_mem64_i32" (func $link32 (param i32 i32 i64 i64 i32 i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "path_symlink_mem64_i8" (func $symlink8 (param i32 i64 i64 i32 i32 i32 i64 i64 i32) (result i32)))
  (import "facet" "path_symlink_mem64_i16" (func $symlink16 (param i32 i64 i64 i32 i32 i32 i64 i64 i32) (result i32)))
  (import "facet" "path_symlink_mem64_i32" (func $symlink32 (param i32 i64 i64 i32 i32 i32 i64 i64 i32) (result i32)))
  (import "facet" "path_readlink_len_mem64_i8" (func $readlink_len8 (param i32 i32 i64 i64 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_len_mem64_i16" (func $readlink_len16 (param i32 i32 i64 i64 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_len_mem64_i32" (func $readlink_len32 (param i32 i32 i64 i64 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_mem64_i8" (func $readlink8 (param i32 i32 i64 i64 i32 i32 i64 i64 i32) (result i64 i32)))
  (import "facet" "path_readlink_mem64_i16" (func $readlink16 (param i32 i32 i64 i64 i32 i32 i64 i64 i32) (result i64 i32)))
  (import "facet" "path_readlink_mem64_i32" (func $readlink32 (param i32 i32 i64 i64 i32 i32 i64 i64 i32) (result i64 i32)))

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
  (data (i64.const 128) "\6d\00\36\00\34\00\2e\00\62\00\69\00\6e\00")
  (data (i64.const 160) "\6d\00\00\00\36\00\00\00\34\00\00\00\2e\00\00\00\62\00\00\00\69\00\00\00\6e\00\00\00")

  (func $require-error (param $e i32)
    (if (i32.eqz (local.get $e)) (then unreachable)))

  (func $probe8 (param $ptr i64) (param $len i64)
    (local $e i32)
    (call $require-error (call $mkdir8 (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)))
    (call $require-error (call $remove8 (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0) (i32.const 0)))
    (call $require-error (call $rename8
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0) (i32.const 0)))
    (call $require-error (call $link8
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0) (i32.const 0)))
    (call $require-error (call $symlink8
      (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)))
    (call $readlink_len8 (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0) (i32.const 0))
    (local.set $e) drop
    (call $require-error (local.get $e))
    (call $readlink8
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)
      (i32.const 0) (i64.const 256) (i64.const 64) (i32.const 0))
    (local.set $e) drop
    (call $require-error (local.get $e))
    (call $stat8 (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0) (i32.const 0))
    (local.set $e) drop drop drop drop drop drop drop drop drop
    (call $require-error (local.get $e)))

  (func $probe16 (param $ptr i64) (param $len i64)
    (local $e i32)
    (call $require-error (call $mkdir16 (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)))
    (call $require-error (call $remove16 (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0) (i32.const 0)))
    (call $require-error (call $rename16
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0) (i32.const 0)))
    (call $require-error (call $link16
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0) (i32.const 0)))
    (call $require-error (call $symlink16
      (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)))
    (call $readlink_len16 (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0) (i32.const 0))
    (local.set $e) drop
    (call $require-error (local.get $e))
    (call $readlink16
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)
      (i32.const 0) (i64.const 256) (i64.const 64) (i32.const 0))
    (local.set $e) drop
    (call $require-error (local.get $e))
    (call $stat16 (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0) (i32.const 0))
    (local.set $e) drop drop drop drop drop drop drop drop drop
    (call $require-error (local.get $e)))

  (func $probe32 (param $ptr i64) (param $len i64)
    (local $e i32)
    (call $require-error (call $mkdir32 (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)))
    (call $require-error (call $remove32 (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0) (i32.const 0)))
    (call $require-error (call $rename32
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0) (i32.const 0)))
    (call $require-error (call $link32
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0) (i32.const 0)))
    (call $require-error (call $symlink32
      (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)))
    (call $readlink_len32 (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0) (i32.const 0))
    (local.set $e) drop
    (call $require-error (local.get $e))
    (call $readlink32
      (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0)
      (i32.const 0) (i64.const 256) (i64.const 64) (i32.const 0))
    (local.set $e) drop
    (call $require-error (local.get $e))
    (call $stat32 (i32.const 0) (i32.const 0) (local.get $ptr) (local.get $len) (i32.const 0) (i32.const 0))
    (local.set $e) drop drop drop drop drop drop drop drop drop
    (call $require-error (local.get $e)))

  (func (export "run") (result i32)
    (local $dir i32) (local $fd i32) (local $fd2 i32) (local $e i32)
    (local $n i64) (local $off i64)

    (call $scratch (i32.const 0)) (local.set $e) (local.set $dir)
    (if (local.get $e) (then (return (local.get $e))))

    ;; Create with UTF-8 and reopen the same path through UTF-16 and UTF-32.
    (call $open8 (local.get $dir) (i32.const 0) (i64.const 0) (i64.const 7) (i32.const 0) (i32.const 5) (i64.const 63))
    (local.set $e) (local.set $fd)
    (if (local.get $e) (then (return (local.get $e))))
    (call $open16 (local.get $dir) (i32.const 0) (i64.const 128) (i64.const 7) (i32.const 0) (i32.const 0) (i64.const 17))
    (local.set $e) (local.set $fd2)
    (if (local.get $e) (then (return (i32.const 11))))
    (drop (call $close (local.get $fd2)))
    (call $open32 (local.get $dir) (i32.const 0) (i64.const 160) (i64.const 7) (i32.const 0) (i32.const 0) (i64.const 17))
    (local.set $e) (local.set $fd2)
    (if (local.get $e) (then (return (i32.const 12))))
    (drop (call $close (local.get $fd2)))

    ;; Sequential and positional Memory64 buffer operations.
    (call $write (local.get $fd) (i32.const 0) (i64.const 32) (i64.const 8))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 8)))
      (then (return (i32.const 1))))
    (call $seek (local.get $fd) (i64.const 0) (i32.const 0))
    (local.set $e) (local.set $off)
    (if (i32.or (local.get $e) (i64.ne (local.get $off) (i64.const 0)))
      (then (return (i32.const 2))))
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

    ;; Empty Memory64 iovec tables are successful no-ops.
    (call $readv (local.get $fd) (i32.const 0) (i64.const 0) (i32.const 0))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 0)))
      (then (return (i32.const 5))))
    (call $writev (local.get $fd) (i32.const 0) (i64.const 0) (i32.const 0))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 0)))
      (then (return (i32.const 6))))

    ;; Positional calls and empty vectors must not move the sequential position.
    (call $read (local.get $fd) (i32.const 0) (i64.const 64) (i64.const 8))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e)
          (i32.or (i64.ne (local.get $n) (i64.const 8))
                  (i64.ne (i64.load (i64.const 64)) (i64.const 3762328071117301101))))
      (then (return (i32.const 7))))

    ;; Exercise every remaining Memory64 path representation with a valid encoded
    ;; path and an intentionally invalid directory capability. The representation
    ;; matrix requires failure, but does not impose an error-precedence order.
    (call $probe8 (i64.const 0) (i64.const 7))
    (call $probe16 (i64.const 128) (i64.const 7))
    (call $probe32 (i64.const 160) (i64.const 7))

    (drop (call $close (local.get $fd)))
    (drop (call $close (local.get $dir)))
    (i32.const 0)))
(assert_return (invoke "run") (i32.const 0))
