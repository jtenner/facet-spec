;; Facet conformance test: args-env/counts
;; Purpose: Arguments and environment are provisioned exactly by the manifest.
;; Required profiles: core, args-env
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "args_count" (func $args (result i32 i32)))
  (import "facet" "env_count" (func $env (result i32 i32)))
  (func (export "args") (result i32 i32) (call $args))
  (func (export "env") (result i32 i32) (call $env)))
(assert_return (invoke "args") (i32.const 4) (i32.const 0))
(assert_return (invoke "env") (i32.const 3) (i32.const 0))
