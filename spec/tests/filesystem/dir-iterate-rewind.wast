;; WPSI conformance test: filesystem/dir-iterate-rewind
;; Purpose: Directory iteration visits each scratch entry once, reports regular-file types, and rewinds deterministically.
;; Required profiles: core, memory32, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_scratch" (func $scratch (result i32 i32)))
  (import "wpsi" "path_open_mem32" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "wpsi" "dir_iter_open" (func $iter-open (param i32) (result i32 i32)))
  (import "wpsi" "dir_iter_next" (func $next (param i32) (result i32 i32 i64 i32 i32)))
  (import "wpsi" "dir_iter_rewind" (func $rewind (param i32) (result i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (data (i32.const 0) "a") (data (i32.const 8) "b")
  (func $count (param $it i32) (result i32)
    (local $name i32) (local $type i32) (local $inode i64) (local $done i32) (local $e i32) (local $count i32)
    (block $done-loop
      (loop $loop
        (call $next (local.get $it)) (local.set $e) (local.set $done) (local.set $inode) (local.set $type) (local.set $name)
        (if (local.get $e) (then (return (i32.const -1))))
        (br_if $done-loop (local.get $done))
        (if (i32.ne (local.get $type) (i32.const 1)) (then (return (i32.const -2))))
        (drop (call $close (local.get $name)))
        (local.set $count (i32.add (local.get $count) (i32.const 1)))
        (br $loop)))
    (local.get $count))
  (func (export "run") (result i32 i32 i32)
    (local $dir i32) (local $fd i32) (local $it i32) (local $e i32) (local $first i32) (local $second i32)
    (call $scratch) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 1) (i32.const 1) (i32.const 5) (i64.const 17)) (local.set $e) (local.set $fd)
    (drop (call $close (local.get $fd)))
    (call $open (local.get $dir) (i32.const 0) (i32.const 8) (i32.const 1) (i32.const 1) (i32.const 5) (i64.const 17)) (local.set $e) (local.set $fd)
    (drop (call $close (local.get $fd)))
    (call $iter-open (local.get $dir)) (local.set $e) (local.set $it)
    (local.set $first (call $count (local.get $it)))
    (local.set $e (call $rewind (local.get $it)))
    (local.set $second (call $count (local.get $it)))
    (drop (call $close (local.get $it)))
    (drop (call $close (local.get $dir)))
    (local.get $first) (local.get $second) (local.get $e)))
(assert_return (invoke "run") (i32.const 2) (i32.const 2) (i32.const 0))
