;; Facet conformance test: core/stdio-output
;; Purpose: Standard output and error descriptors integrate with WASI-compatible read operations in the host manifest.
;; Required profiles: core, memory32
;; Test kind: harness
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "stdio_stdout" (func $stdout (result i32 i32)))
  (import "facet" "stdio_stderr" (func $stderr (result i32 i32)))
  (import "facet" "fd_write_mem32" (func $write (param i32 i32 i32 i32) (result i64 i32)))
  (memory 1)
  (data (i32.const 0) "out\0aerr\0a")
  (func (export "_start")
    (local $fd i32) (local $e i32) (local $n i64)
    (call $stdout) (local.set $e) (local.set $fd)
    (call $write (local.get $fd) (i32.const 0) (i32.const 0) (i32.const 4)) (local.set $e) (local.set $n)
    (call $stderr) (local.set $e) (local.set $fd)
    (call $write (local.get $fd) (i32.const 0) (i32.const 4) (i32.const 4)) (local.set $e) (local.set $n)))
