;; WPSI conformance test: filesystem/create-remove-directory
;; Purpose: A newly created empty directory can be removed, and a second removal reports ERR_NO_ENTRY.
;; Required profiles: core, memory32, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_scratch" (func $scratch (result i32 i32)))
  (import "wpsi" "path_create_dir_mem32" (func $mkdir (param i32 i32 i32 i32 i32) (result i32)))
  (import "wpsi" "path_remove_mem32" (func $remove (param i32 i32 i32 i32 i32 i32) (result i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (data (i32.const 0) "dir")
  (func (export "run") (result i32 i32 i32)
    (local $dir i32) (local $e0 i32) (local $e1 i32) (local $e2 i32)
    (call $scratch) (local.set $e0) (local.set $dir)
    (local.set $e0 (call $mkdir (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 3) (i32.const 1)))
    (local.set $e1 (call $remove (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 3) (i32.const 1) (i32.const 2)))
    (local.set $e2 (call $remove (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 3) (i32.const 1) (i32.const 2)))
    (drop (call $close (local.get $dir)))
    (local.get $e0) (local.get $e1) (local.get $e2)))
(assert_return (invoke "run") (i32.const 0) (i32.const 0) (i32.const 2))
