;; Facet conformance test: filesystem/path-utf32
;; Purpose: A UTF-32LE path opens a Unicode-named fixture without UTF-8 canonicalization.
;; Required profiles: core, memory32, filesystem, text
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "facet" "path_open_mem32_i32" (func $open (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "path_create_dir_mem32_i32" (func $mkdir (param i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_remove_mem32_i32" (func $remove (param i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_rename_mem32_i32" (func $rename (param i32 i32 i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_stat_mem32_i32" (func $stat (param i32 i32 i32 i32 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "path_link_mem32_i32" (func $link (param i32 i32 i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_symlink_mem32_i32" (func $symlink (param i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "facet" "path_readlink_len_mem32_i32" (func $readlink_len (param i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_mem32_i32" (func $readlink (param i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (data (i32.const 0) "\00\f6\01\00.\00\00\00t\00\00\00x\00\00\00t\00\00\00")

  (func $probe-errors (result i32)
    (local $e i32) (local $n i64)
    (local.set $e (call $mkdir (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 5) (i32.const 0)))
    (if (i32.ne (local.get $e) (i32.const 4)) (then (return (i32.const 1))))
    (local.set $e (call $remove (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 5) (i32.const 0) (i32.const 0)))
    (if (i32.ne (local.get $e) (i32.const 4)) (then (return (i32.const 2))))
    (local.set $e (call $rename
      (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 5) (i32.const 0)
      (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 5) (i32.const 0) (i32.const 0)))
    (if (i32.ne (local.get $e) (i32.const 4)) (then (return (i32.const 3))))
    (local.set $e (call $link
      (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 5) (i32.const 0)
      (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 5) (i32.const 0) (i32.const 0)))
    (if (i32.ne (local.get $e) (i32.const 4)) (then (return (i32.const 4))))
    (local.set $e (call $symlink
      (i32.const 0) (i32.const 0) (i32.const 5) (i32.const 0)
      (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 5) (i32.const 0)))
    (if (i32.ne (local.get $e) (i32.const 4)) (then (return (i32.const 5))))
    (call $readlink_len (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 5) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $n)
    (if (i32.ne (local.get $e) (i32.const 4)) (then (return (i32.const 6))))
    (call $readlink
      (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 5) (i32.const 0)
      (i32.const 0) (i32.const 256) (i32.const 16) (i32.const 0))
    (local.set $e) (local.set $n)
    (if (i32.ne (local.get $e) (i32.const 4)) (then (return (i32.const 7))))
    (call $stat (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 5) (i32.const 0) (i32.const 0))
    (local.set $e)
    drop drop drop drop drop drop drop drop drop
    (if (i32.ne (local.get $e) (i32.const 4)) (then (return (i32.const 8))))
    (i32.const 0))

  (func (export "run") (result i32)
    (local $dir i32) (local $fd i32) (local $e i32)
    (call $get (i32.const 0)) (local.set $e) (local.set $dir)
    (if (local.get $e) (then (return (local.get $e))))
    (call $open (local.get $dir) (i32.const 0) (i32.const 0) (i32.const 5) (i32.const 0) (i32.const 0) (i64.const 17))
    (local.set $e) (local.set $fd)
    (if (i32.eqz (local.get $e)) (then (drop (call $close (local.get $fd)))))
    (if (local.get $e) (then (return (local.get $e))))
    (call $probe-errors))
)
(assert_return (invoke "run") (i32.const 0))
