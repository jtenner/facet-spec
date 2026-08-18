;; Facet conformance test: filesystem/path-stat
;; Purpose: path_stat reports the exact type and size without opening the file.
;; Required profiles: core, memory32, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "facet" "path_stat_mem32_i8" (func $stat (param i32 i32 i32 i32 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (data (i32.const 0) "hello.txt")
  (func (export "run") (result i32 i64 i32)
    (local $dir i32) (local $name i32) (local $type i32) (local $flags i32) (local $size i64)
    (local $as i64) (local $an i32) (local $ms i64) (local $mn i32) (local $cs i64) (local $cn i32) (local $e i32)
    (call $get (i32.const 0)) (local.set $e) (local.set $dir)
        (call $stat (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 9) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $cn) (local.set $cs) (local.set $mn) (local.set $ms) (local.set $an) (local.set $as) (local.set $size) (local.set $flags) (local.set $type)
    (drop (call $close (local.get $dir)))
    (local.get $type) (local.get $size) (local.get $e)))
(assert_return (invoke "run") (i32.const 1) (i64.const 28) (i32.const 0))
