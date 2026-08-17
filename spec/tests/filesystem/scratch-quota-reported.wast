;; WPSI conformance test: filesystem/scratch-quota-reported
;; Purpose: Manifest-configured scratch quotas are reported exactly.
;; Required profiles: core, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_scratch_limits" (func $limits (result i64 i64 i32)))
  (func (export "run") (result i64 i64 i32) (call $limits)))
(assert_return (invoke "run") (i64.const 4096) (i64.const 16) (i32.const 0))
