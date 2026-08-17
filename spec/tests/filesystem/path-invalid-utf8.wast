;; WPSI conformance test: filesystem/path-invalid-utf8
;; Purpose: Overlong UTF-8 is rejected as an illegal sequence.
;; Required profiles: core, memory32, filesystem, text, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (memory 1)
  (data (i32.const 0) "\c0\af")
  (func (export "run") (result i32 i32)
    (local $dir i32) (local $name i32) (local $fd i32) (local $e i32)
    (call $get (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 2) (i32.const 0) (i32.const 0) (i64.const 1))))
(assert_return (invoke "run") (i32.const 0) (i32.const 23))
