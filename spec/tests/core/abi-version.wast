;; WPSI conformance test: core/abi-version
;; Purpose: WPSI 0.1 reports ABI version 1.
;; Required profiles: core
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "abi_version" (func $abi_version (result i32)))
  (func (export "run") (result i32) (call $abi_version)))
(assert_return (invoke "run") (i32.const 1))
