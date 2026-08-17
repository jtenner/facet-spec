;; WPSI conformance test: filesystem/path-raw8
;; Purpose: ENC_RAW8 accepts an uninterpreted ASCII path without Unicode conversion.
;; Required profiles: core, memory32, filesystem, text
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_preopen_get" (func $get (param i32) (result i32 i32 i32)))
  (import "wpsi" "path_open_mem32" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (data (i32.const 0) "hello.txt")
  (func (export "run") (result i32)
    (local $dir i32) (local $name i32) (local $fd i32) (local $e i32)
    (call $get (i32.const 0)) (local.set $e) (local.set $name) (local.set $dir)
    (drop (call $close (local.get $name)))
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 9) (i32.const 4) (i32.const 0) (i64.const 17)) (local.set $e) (local.set $fd)
    (if (i32.eqz (local.get $e)) (then (drop (call $close (local.get $fd)))))
    (drop (call $close (local.get $dir)))
    (local.get $e)))
(assert_return (invoke "run") (i32.const 0))
