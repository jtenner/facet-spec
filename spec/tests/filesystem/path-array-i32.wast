;; Facet conformance test: filesystem/path-array-i32
;; Purpose: path_open_array_i32 consumes the native GC code-unit representation without linear-memory lowering.
;; Required profiles: core, gc-array, filesystem, text
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array (mut i32)))
  (import "facet" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "facet" "path_open_array_i32" (func $open (param i32 (ref array) i32 i32 i32 i32 i64) (result i32 i32)))
  (import "facet" "path_create_dir_array_i32" (func $mkdir (param i32 (ref array) i32 i32 i32) (result i32)))
  (import "facet" "path_remove_array_i32" (func $remove (param i32 (ref array) i32 i32 i32 i32) (result i32)))
  (import "facet" "path_rename_array_i32" (func $rename (param i32 (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32 i32) (result i32)))
  (import "facet" "path_stat_array_i32" (func $stat (param i32 (ref array) i32 i32 i32 i32) (result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)))
  (import "facet" "path_link_array_i32" (func $link (param i32 (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32 i32) (result i32)))
  (import "facet" "path_symlink_array_i32" (func $symlink (param (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32) (result i32)))
  (import "facet" "path_readlink_len_array_i32" (func $readlink_len (param i32 (ref array) i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_into_array_i32" (func $readlink_into (param i32 (ref array) i32 i32 i32 (ref array) i32 i32 i32) (result i64 i32)))
  (import "facet" "path_readlink_array_i32" (func $readlink_array (param i32 (ref array) i32 i32 i32 i32) (result (ref null $a) i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))

  (func $probe-errors (param $a (ref $a)) (result i32)
    (local $e i32) (local $n i64) (local $out (ref null $a))
    (local.set $e (call $mkdir (i32.const 0) (local.get $a) (i32.const 0) (i32.const 5) (i32.const 0)))
    (if (i32.ne (local.get $e) (i32.const 4)) (then (return (i32.const 1))))
    (local.set $e (call $remove (i32.const 0) (local.get $a) (i32.const 0) (i32.const 5) (i32.const 0) (i32.const 0)))
    (if (i32.ne (local.get $e) (i32.const 4)) (then (return (i32.const 2))))
    (local.set $e (call $rename
      (i32.const 0) (local.get $a) (i32.const 0) (i32.const 5) (i32.const 0)
      (i32.const 0) (local.get $a) (i32.const 0) (i32.const 5) (i32.const 0) (i32.const 0)))
    (if (i32.ne (local.get $e) (i32.const 4)) (then (return (i32.const 3))))
    (local.set $e (call $link
      (i32.const 0) (local.get $a) (i32.const 0) (i32.const 5) (i32.const 0)
      (i32.const 0) (local.get $a) (i32.const 0) (i32.const 5) (i32.const 0) (i32.const 0)))
    (if (i32.ne (local.get $e) (i32.const 4)) (then (return (i32.const 4))))
    (local.set $e (call $symlink
      (local.get $a) (i32.const 0) (i32.const 5) (i32.const 0)
      (i32.const 0) (local.get $a) (i32.const 0) (i32.const 5) (i32.const 0)))
    (if (i32.ne (local.get $e) (i32.const 4)) (then (return (i32.const 5))))
    (call $readlink_len (i32.const 0) (local.get $a) (i32.const 0) (i32.const 5) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $n)
    (if (i32.ne (local.get $e) (i32.const 4)) (then (return (i32.const 6))))
    (call $readlink_into
      (i32.const 0) (local.get $a) (i32.const 0) (i32.const 5) (i32.const 0)
      (local.get $a) (i32.const 0) (i32.const 5) (i32.const 0))
    (local.set $e) (local.set $n)
    (if (i32.ne (local.get $e) (i32.const 4)) (then (return (i32.const 7))))
    (call $readlink_array (i32.const 0) (local.get $a) (i32.const 0) (i32.const 5) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $out)
    (if (i32.or (i32.ne (local.get $e) (i32.const 4)) (i32.eqz (ref.is_null (local.get $out))))
      (then (return (i32.const 8))))
    (call $stat (i32.const 0) (local.get $a) (i32.const 0) (i32.const 5) (i32.const 0) (i32.const 0))
    (local.set $e)
    drop drop drop drop drop drop drop drop drop
    (if (i32.ne (local.get $e) (i32.const 4)) (then (return (i32.const 9))))
    (i32.const 0))

  (func (export "run") (result i32)
    (local $a (ref $a)) (local $dir i32) (local $fd i32) (local $e i32)
    (local.set $a (array.new_fixed $a 5
      (i32.const 128512) (i32.const 46) (i32.const 116) (i32.const 120) (i32.const 116)))
    (call $get (i32.const 0)) (local.set $e) (local.set $dir)
    (if (local.get $e) (then (return (local.get $e))))
    (call $open (local.get $dir) (local.get $a) (i32.const 0) (i32.const 5) (i32.const 0) (i32.const 0) (i64.const 17))
    (local.set $e) (local.set $fd)
    (if (i32.eqz (local.get $e)) (then (drop (call $close (local.get $fd)))))
    (if (local.get $e) (then (return (local.get $e))))
    (local.set $e (call $probe-errors (local.get $a)))
    (drop (call $close (local.get $dir)))
    (local.get $e)))
(assert_return (invoke "run") (i32.const 0))
