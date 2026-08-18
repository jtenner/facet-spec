;; Facet conformance test: filesystem/sync-datasync
;; Purpose: fd_sync and fd_datasync succeed for a writable scratch file with sync rights.
;; Required profiles: core, memory32, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fs_preopen_get" (func $scratch (param i32) (result i32 i32)))
  (import "facet" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "fd_sync" (func $sync (param i32) (result i32)))
  (import "facet" "fd_datasync" (func $datasync (param i32) (result i32)))
  (memory 1) (data (i32.const 0) "sync.bin")
  (func (export "run") (result i32 i32)
    (local $dir i32) (local $fd i32) (local $e i32)
    (call $scratch (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 8) (i32.const 0) (i32.const 5) (i64.const 127)) (local.set $e) (local.set $fd)
    (call $sync (local.get $fd)) (call $datasync (local.get $fd)))
)
(assert_return (invoke "run") (i32.const 0) (i32.const 0))
