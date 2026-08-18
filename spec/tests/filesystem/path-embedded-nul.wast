;; WPSI conformance test: filesystem/path-embedded-nul
;; Purpose: Filesystem paths reject embedded NUL without truncating the name.
;; Required profiles: core, memory32, filesystem, text, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "facet" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (memory 1)
  (data (i32.const 0) "a\00b")
  (func (export "run") (result i32 i32)
    (local $dir i32) (local $name i32) (local $e i32)
    (call $get (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 3) (i32.const 0) (i32.const 0) (i64.const 1))))
(assert_return (invoke "run") (i32.const 0) (i32.const 12))
