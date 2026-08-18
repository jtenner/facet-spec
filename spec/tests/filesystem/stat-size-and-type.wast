;; Facet conformance test: filesystem/stat-size-and-type
;; Purpose: fd_stat reports a regular file and exact byte size.
;; Required profiles: core, memory32, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fs_preopen_get" (func $scratch (param i32) (result i32 i32)))
  (import "facet" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "fd_write_mem32" (func $write (param i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "fd_stat" (func $stat (param i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (memory 1)
  (data (i32.const 0) "stat.bin") (data (i32.const 32) "12345")
  (func (export "run") (result i32 i64 i32)
    (local $dir i32) (local $fd i32) (local $e i32) (local $n i64)
    (local $type i32) (local $flags i32) (local $size i64)
    (local $as i64) (local $ans i32) (local $ms i64) (local $mns i32) (local $cs i64) (local $cns i32)
    (call $scratch (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 8) (i32.const 0) (i32.const 5) (i64.const 63)) (local.set $e) (local.set $fd)
    (call $write (local.get $fd) (i32.const 0) (i32.const 32) (i32.const 5)) (local.set $e) (local.set $n)
    (call $stat (local.get $fd))
    (local.set $e) (local.set $cns) (local.set $cs) (local.set $mns) (local.set $ms)
    (local.set $ans) (local.set $as) (local.set $size) (local.set $flags) (local.set $type)
    (local.get $type) (local.get $size) (local.get $e))
)
(assert_return (invoke "run") (i32.const 1) (i64.const 5) (i32.const 0))
