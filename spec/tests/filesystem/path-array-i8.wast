;; Facet conformance test: filesystem/path-array-i8
;; Purpose: path_open_array_i8 consumes the native GC code-unit representation without linear-memory lowering.
;; Required profiles: core, gc-array, filesystem, text
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array (mut i8)))
  (import "facet" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "facet" "path_open_array_i8" (func $open (param i32 (ref array) i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "path_create_dir_array_i8" (func $mkdir (param i32 (ref array) i32 i32 i32) (result i32)))
  (import "facet" "path_remove_array_i8" (func $remove (param i32 (ref array) i32 i32 i32 i32) (result i32)))
  (import "facet" "path_rename_array_i8" (func $rename (param i32 (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32 i32) (result i32)))
  (import "facet" "path_stat_array_i8" (func $stat (param i32 (ref array) i32 i32 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "path_link_array_i8" (func $link (param i32 (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32 i32) (result i32)))
  (import "facet" "path_symlink_array_i8" (func $symlink (param (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32) (result i32)))
  (import "facet" "path_readlink_len_array_i8" (func $readlink_len (param i32 (ref array) i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_into_array_i8" (func $readlink_into (param i32 (ref array) i32 i32 i32 (ref array) i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_array_i8" (func $readlink_array (param i32 (ref array) i32 i32 i32 i32) (result (ref null $a) i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))

  (func $require-error (param $e i32)
    (if (i32.eqz (local.get $e)) (then unreachable)))

  (func $probe-errors (param $a (ref $a))
    (local $e i32)
    (call $require-error (call $mkdir (i32.const 0) (local.get $a) (i32.const 0) (i32.const 9) (i32.const 0)))
    (call $require-error (call $remove (i32.const 0) (local.get $a) (i32.const 0) (i32.const 9) (i32.const 0) (i32.const 0)))
    (call $require-error (call $rename
      (i32.const 0) (local.get $a) (i32.const 0) (i32.const 9) (i32.const 0)
      (i32.const 0) (local.get $a) (i32.const 0) (i32.const 9) (i32.const 0) (i32.const 0)))
    (call $require-error (call $link
      (i32.const 0) (local.get $a) (i32.const 0) (i32.const 9) (i32.const 0)
      (i32.const 0) (local.get $a) (i32.const 0) (i32.const 9) (i32.const 0) (i32.const 0)))
    (call $require-error (call $symlink
      (local.get $a) (i32.const 0) (i32.const 9) (i32.const 0)
      (i32.const 0) (local.get $a) (i32.const 0) (i32.const 9) (i32.const 0)))

    (call $readlink_len (i32.const 0) (local.get $a) (i32.const 0) (i32.const 9) (i32.const 0) (i32.const 0))
    (local.set $e) drop
    (call $require-error (local.get $e))
    (call $readlink_into
      (i32.const 0) (local.get $a) (i32.const 0) (i32.const 9) (i32.const 0)
      (local.get $a) (i32.const 0) (i32.const 9) (i32.const 0))
    (local.set $e) drop
    (call $require-error (local.get $e))
    (call $readlink_array (i32.const 0) (local.get $a) (i32.const 0) (i32.const 9) (i32.const 0) (i32.const 0))
    (local.set $e) drop
    (call $require-error (local.get $e))

    (call $stat (i32.const 0) (local.get $a) (i32.const 0) (i32.const 9) (i32.const 0) (i32.const 0))
    (local.set $e) drop drop drop drop drop drop drop drop drop
    (call $require-error (local.get $e)))

  (func (export "run") (result i32)
    (local $a (ref $a)) (local $dir i32) (local $fd i32) (local $e i32)
    (local.set $a (array.new_fixed $a 9
      (i32.const 99) (i32.const 97) (i32.const 102) (i32.const 195) (i32.const 169)
      (i32.const 46) (i32.const 116) (i32.const 120) (i32.const 116)))
    (call $get (i32.const 0)) (local.set $e) (local.set $dir)
    (if (local.get $e) (then (return (local.get $e))))
    (call $open (local.get $dir) (local.get $a) (i32.const 0) (i32.const 9) (i32.const 0) (i32.const 0) (i64.const 17))
    (local.set $e) (local.set $fd)
    (if (i32.eqz (local.get $e)) (then (drop (call $close (local.get $fd)))))
    (if (local.get $e) (then (return (local.get $e))))
    (call $probe-errors (local.get $a))
    (drop (call $close (local.get $dir)))
    (i32.const 0)))
(assert_return (invoke "run") (i32.const 0))
