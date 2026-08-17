;; WPSI conformance test: random/u64-success
;; Purpose: random_u64 returns a scalar and an ERR_OK status without requiring guest storage.
;; Required profiles: core, random
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "random_u64" (func $random (result i64 i32)))
  (func (export "run") (result i32)
    (local $value i64) (local $e i32)
    (call $random) (local.set $e) (local.set $value)
    (local.get $e)))
(assert_return (invoke "run") (i32.const 0))
