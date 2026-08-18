;; Facet conformance test: filesystem/path-parent-escape-rejected
;; Purpose: Parent traversal cannot escape a directory capability.
;; Required profiles: core, memory32, filesystem, capabilities, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "facet" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (memory 1)
  (data (i32.const 0) "../outside.txt")
  (func (export "run") (result i32)
    (local $dir i32) (local $name i32) (local $fd i32) (local $e i32)
    (call $get (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 14) (i32.const 0) (i32.const 0) (i64.const 1)) (local.set $e) (local.set $fd)
    (i32.and (i32.eqz (local.get $fd)) (i32.ne (local.get $e) (i32.const 0)))))
(assert_return (invoke "run") (i32.const 1))
