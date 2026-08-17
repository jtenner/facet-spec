;; WPSI conformance test: args-env/out-of-range-zeroes
;; Purpose: Out-of-range indexes return zero handles and ERR_RANGE.
;; Required profiles: core, args-env
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "args_get" (func $arg (param i32) (result i32 i32)))
  (import "wpsi" "env_get" (func $env (param i32) (result i32 i32 i32)))
  (func (export "arg") (result i32 i32) (call $arg (i32.const -1)))
  (func (export "env") (result i32 i32 i32) (call $env (i32.const -1))))
(assert_return (invoke "arg") (i32.const 0) (i32.const 17))
(assert_return (invoke "env") (i32.const 0) (i32.const 0) (i32.const 17))
