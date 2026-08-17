;; WPSI conformance test: core/stdio-valid
;; Purpose: All standard streams resolve to nonzero descriptor handles.
;; Required profiles: core
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "stdio_stdin" (func $stdin (result i32 i32)))
  (import "wpsi" "stdio_stdout" (func $stdout (result i32 i32)))
  (import "wpsi" "stdio_stderr" (func $stderr (result i32 i32)))
  (func $one (param $which i32) (result i32)
    (local $fd i32) (local $err i32)
    (if (i32.eqz (local.get $which))
      (then (call $stdin) (local.set $err) (local.set $fd))
      (else (if (i32.eq (local.get $which) (i32.const 1))
        (then (call $stdout) (local.set $err) (local.set $fd))
        (else (call $stderr) (local.set $err) (local.set $fd)))))
    (i32.and (i32.eqz (local.get $err)) (i32.ne (local.get $fd) (i32.const 0))))
  (func (export "run") (result i32)
    (i32.and (call $one (i32.const 0))
      (i32.and (call $one (i32.const 1)) (call $one (i32.const 2))))))
(assert_return (invoke "run") (i32.const 1))
