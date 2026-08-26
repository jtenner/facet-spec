;; Facet conformance test: filesystem/path-utf16
;; Purpose: A UTF-16LE path opens a Unicode-named fixture without UTF-8 canonicalization.
;; Required profiles: core, memory32, filesystem, text
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "facet" "path_open_mem32_i16" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "path_create_dir_mem32_i16" (func $mkdir (param i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_remove_mem32_i16" (func $remove (param i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_rename_mem32_i16" (func $rename (param i32 i32 i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_stat_mem32_i16" (func $stat (param i32 i32 i32 i32 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "path_link_mem32_i16" (func $link (param i32 i32 i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_symlink_mem32_i16" (func $symlink (param i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_readlink_len_mem32_i16" (func $readlink_len (param i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_mem32_i16" (func $readlink (param i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (data (i32.const 0) "c\00a\00f\00\e9\00.\00t\00x\00t\00")

  (func $require-error (param $e i32)
    (if (i32.eqz (local.get $e)) (then unreachable)))

  (func $probe-errors
    (local $e i32)
    (call $require-error (call $mkdir (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 8) (i32.const 0)))
    (call $require-error (call $remove (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 8) (i32.const 0) (i32.const 0)))
    (call $require-error (call $rename
      (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 8) (i32.const 0)
      (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 8) (i32.const 0) (i32.const 0)))
    (call $require-error (call $link
      (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 8) (i32.const 0)
      (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 8) (i32.const 0) (i32.const 0)))
    (call $require-error (call $symlink
      (i32.const 0) (i32.const 0) (i32.const 8) (i32.const 0)
      (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 8) (i32.const 0)))
    (call $readlink_len (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 8) (i32.const 0) (i32.const 0))
    (local.set $e) drop
    (call $require-error (local.get $e))
    (call $readlink
      (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 8) (i32.const 0)
      (i32.const 0) (i32.const 256) (i32.const 16) (i32.const 0))
    (local.set $e) drop
    (call $require-error (local.get $e))
    (call $stat (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 8) (i32.const 0) (i32.const 0))
    (local.set $e) drop drop drop drop drop drop drop drop drop
    (call $require-error (local.get $e)))

  (func (export "run") (result i32)
    (local $dir i32) (local $fd i32) (local $e i32)
    (call $get (i32.const 0)) (local.set $e) (local.set $dir)
    (if (local.get $e) (then (return (local.get $e))))
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 8) (i32.const 0) (i32.const 0) (i64.const 17))
    (local.set $e) (local.set $fd)
    (if (i32.eqz (local.get $e)) (then (drop (call $close (local.get $fd)))))
    (if (local.get $e) (then (return (local.get $e))))
    (call $probe-errors)
    (i32.const 0)))
(assert_return (invoke "run") (i32.const 0))
