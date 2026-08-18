;; Facet conformance test: filesystem/create-rename-remove
;; Purpose: Rename removes the old name, creates the new name, and removal deletes it.
;; Required profiles: core, memory32, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fs_preopen_get" (func $scratch (param i32) (result i32 i32)))
  (import "facet" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "path_rename_mem32_i8" (func $rename (param i32 i32 i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_remove_mem32_i8" (func $remove (param i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_stat_mem32_i8" (func $stat (param i32 i32 i32 i32 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (data (i32.const 0) "old.txt") (data (i32.const 16) "new.txt")
  (func $staterr (param $dir i32) (param $ptr i32) (result i32)
    (local $e i32) (local $t i32) (local $f i32) (local $z i64) (local $ns i32)
    (call $stat (local.get $dir) (i32.const 0) (local.get $ptr) (i32.const 7) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $ns) (local.set $z) (local.set $ns) (local.set $z) (local.set $ns) (local.set $z) (local.set $f) (local.set $t)
    (local.get $e))
  (func (export "run") (result i32)
    (local $dir i32) (local $fd i32) (local $e i32)
    (call $scratch (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 7) (i32.const 0) (i32.const 1) (i64.const 63)) (local.set $e) (local.set $fd)
    (drop (call $close (local.get $fd)))
    (local.set $e (call $rename (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 7) (i32.const 0) (local.get $dir) (i32.const 0) (i32.const 16) (i32.const 7) (i32.const 0) (i32.const 1)))
    (if (local.get $e) (then (return (local.get $e))))
    (if (i32.eqz (call $staterr (local.get $dir) (i32.const 0))) (then (return (i32.const 100))))
    (if (call $staterr (local.get $dir) (i32.const 16)) (then (return (i32.const 101))))
    (local.set $e (call $remove (local.get $dir) (i32.const 0) (i32.const 16) (i32.const 7) (i32.const 0) (i32.const 1)))
    (local.get $e))
)
(assert_return (invoke "run") (i32.const 0))
