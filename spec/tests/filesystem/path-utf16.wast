;; WPSI conformance test: filesystem/path-utf16
;; Purpose: A UTF-16LE path opens a Unicode-named fixture without UTF-8 canonicalization.
;; Required profiles: core, memory32, filesystem, text
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "path_open_mem32" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (data (i32.const 0) "c\00a\00f\00\e9\00.\00t\00x\00t\00")
  (func (export "run") (result i32)
    (local $dir i32) (local $name i32) (local $fd i32) (local $e i32)
    (call $get (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 8) (i32.const 2) (i32.const 0) (i64.const 17)) (local.set $e) (local.set $fd)
    (if (i32.eqz (local.get $e)) (then (drop (call $close (local.get $fd)))))
    (local.get $e)))
(assert_return (invoke "run") (i32.const 0))
