;; WPSI conformance test: filesystem/scratch-starts-empty
;; Purpose: Every test receives a fresh, logically empty scratch filesystem.
;; Required profiles: core, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_scratch" (func $scratch (result i32 i32)))
  (import "wpsi" "dir_iter_open" (func $open (param i32) (result i32 i32)))
  (import "wpsi" "dir_iter_next" (func $next (param i32) (result i32 i32 i64 i32 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (func (export "run") (result i32)
    (local $dir i32) (local $it i32) (local $name i32) (local $type i32)
    (local $ino i64) (local $done i32) (local $e i32)
    (call $scratch) (local.set $e) (local.set $dir)
    (call $open (local.get $dir)) (local.set $e) (local.set $it)
    (call $next (local.get $it)) (local.set $e) (local.set $done) (local.set $ino) (local.set $type) (local.set $name)
    (drop (call $close (local.get $it))) (drop (call $close (local.get $dir)))
    (i32.or (local.get $e) (i32.xor (local.get $done) (i32.const 1)))))
(assert_return (invoke "run") (i32.const 0))
