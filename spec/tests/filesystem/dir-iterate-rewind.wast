;; WPSI conformance test: filesystem/dir-iterate-rewind
;; Purpose: Directory iteration uses the iterator as the stable name source and rewind resets pending state.
;; Required profiles: core, gc-array, filesystem, text
;;
;; SPDX-License-Identifier: MIT

(module
  (type $s (array (mut i8)))
  (import "facet" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "facet" "dir_iter_open" (func $open (param i32) (result i32 i32)))
  (import "facet" "dir_iter_next_array_i8" (func $next (param i32 i32) (result (ref null $s) i32 i64 i32 i32)))
  (import "facet" "dir_iter_rewind" (func $rewind (param i32) (result i32)))
  (func (export "run") (result i32)
    (local $dir i32) (local $iter i32) (local $e i32)
    (local $name (ref null $s)) (local $type i32) (local $inode i64) (local $done i32)
    (call $get (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir)) (local.set $e) (local.set $iter)
    (call $next (local.get $iter) (i32.const 0))
      (local.set $e) (local.set $done) (local.set $inode) (local.set $type) (local.set $name)
    (if (i32.eqz (local.get $e)) (then (local.set $e (call $rewind (local.get $iter)))))
    (local.get $e))
)
(assert_return (invoke "run") (i32.const 0))
