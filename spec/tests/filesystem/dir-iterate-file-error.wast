;; Facet conformance test: filesystem/dir-iterate-file-error
;; Purpose: Opening a directory iterator on a regular file returns a zero handle and ERR_NOT_DIRECTORY.
;; Required profiles: core, memory32, filesystem, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fs_preopen_get" (func $scratch (param i32) (result i32 i32)))
  (import "facet" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "dir_iter_open" (func $iter (param i32) (result i32 i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (data (i32.const 0) "file")
  (func (export "run") (result i32 i32)
    (local $dir i32) (local $fd i32) (local $it i32) (local $e i32)
    (call $scratch (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 4) (i32.const 0) (i32.const 5) (i64.const 17)) (local.set $e) (local.set $fd)
    (call $iter (local.get $fd)) (local.set $e) (local.set $it)
    (drop (call $close (local.get $fd)))
    (drop (call $close (local.get $dir)))
    (local.get $it) (local.get $e)))
(assert_return (invoke "run") (i32.const 0) (i32.const 10))
