;; Facet conformance test: args-env/out-of-range-zeroes
;; Purpose: Out-of-range argument and environment indexes return zero lengths and ERR_RANGE.
;; Required profiles: core, args-env
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "args_len_i8" (func $arg (param i32 i32) (result i64 i32)))
  (import "facet" "env_len_i8" (func $env (param i32 i32 i32) (result i64 i32)))
  (func (export "arg") (result i64 i32) (call $arg (i32.const -1) (i32.const 0)))
  (func (export "env") (result i64 i32) (call $env (i32.const -1) (i32.const 0) (i32.const 0))))
(assert_return (invoke "arg") (i64.const 0) (i32.const 17))
(assert_return (invoke "env") (i64.const 0) (i32.const 17))
