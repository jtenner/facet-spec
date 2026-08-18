;; WPSI conformance test: filesystem/path-utf32
;; Purpose: A UTF-32LE path opens a Unicode-named fixture without UTF-8 canonicalization.
;; Required profiles: core, memory32, filesystem, text
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "facet" "path_open_mem32_i32" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (data (i32.const 0) "\00\f6\01\00.\00\00\00t\00\00\00x\00\00\00t\00\00\00")
  (func (export "run") (result i32)
    (local $dir i32) (local $name i32) (local $fd i32) (local $e i32)
    (call $get (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 5) (i32.const 0) (i32.const 0) (i64.const 17)) (local.set $e) (local.set $fd)
    (if (i32.eqz (local.get $e)) (then (drop (call $close (local.get $fd)))))
    (local.get $e)))
(assert_return (invoke "run") (i32.const 0))
