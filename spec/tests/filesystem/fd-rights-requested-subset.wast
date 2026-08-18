;; Facet conformance test: filesystem/fd-rights-requested-subset
;; Purpose: An opened descriptor receives exactly the requested rights and no ambient parent rights.
;; Required profiles: core, memory32, filesystem, capabilities
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fs_preopen_get" (func $scratch (param i32) (result i32 i32)))
  (import "facet" "path_open_mem32_i8" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "fd_rights" (func $rights (param i32) (result i64 i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (data (i32.const 0) "rights.bin")
  (func (export "run") (result i64 i32)
    (local $dir i32) (local $fd i32) (local $e i32) (local $r i64)
    (call $scratch (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 10) (i32.const 0) (i32.const 1) (i64.const 17)) (local.set $e) (local.set $fd)
    (call $rights (local.get $fd)) (local.set $e) (local.set $r)
    (drop (call $close (local.get $fd)))
    (drop (call $close (local.get $dir)))
    (local.get $r) (local.get $e)))
(assert_return (invoke "run") (i64.const 17) (i32.const 0))
