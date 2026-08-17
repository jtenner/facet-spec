;; WPSI conformance test: filesystem/dir-iterate-file-error
;; Purpose: Opening a directory iterator on a regular file returns a zero handle and ERR_NOT_DIRECTORY.
;; Required profiles: core, memory32, filesystem, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_scratch" (func $scratch (result i32 i32)))
  (import "wpsi" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "wpsi" "dir_iter_open" (func $iter (param i32) (result i32 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (data (i32.const 0) "file")
  (func (export "run") (result i32 i32)
    (local $dir i32) (local $fd i32) (local $it i32) (local $e i32)
    (call $scratch) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 4) (i32.const 0) (i32.const 5) (i64.const 17)) (local.set $e) (local.set $fd)
    (call $iter (local.get $fd)) (local.set $e) (local.set $it)
    (drop (call $close (local.get $fd)))
    (drop (call $close (local.get $dir)))
    (local.get $it) (local.get $e)))
(assert_return (invoke "run") (i32.const 0) (i32.const 10))
