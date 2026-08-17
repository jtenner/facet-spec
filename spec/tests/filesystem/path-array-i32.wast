;; WPSI conformance test: filesystem/path-array-i32
;; Purpose: path_open_array_i32 consumes the native GC code-unit representation without linear-memory lowering.
;; Required profiles: core, gc-array, filesystem, text
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array (mut i32)))
  (import "wpsi" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "path_open_array_i32" (func $open (param i32 (ref array) i32 i32 i32 i32 i64) (result i32 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (func (export "run") (result i32)
    (local $a (ref $a)) (local $dir i32) (local $name i32) (local $fd i32) (local $e i32)
    (local.set $a (array.new_fixed $a 5 (i32.const 128512) (i32.const 46) (i32.const 116) (i32.const 120) (i32.const 116)))
    (call $get (i32.const 0)) (local.set $e) (local.set $dir)
        (call $open (local.get $dir) (local.get $a) (i32.const 0) (i32.const 5) (i32.const 3) (i32.const 0) (i64.const 17)) (local.set $e) (local.set $fd)
    (if (i32.eqz (local.get $e)) (then (drop (call $close (local.get $fd)))))
    (drop (call $close (local.get $dir)))
    (local.get $e)))
(assert_return (invoke "run") (i32.const 0))
