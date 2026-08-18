;; WPSI conformance test: filesystem/preopen-tilde-optional
;; Purpose: A filesystem implementation is not required to provide any preopen, including `~`.
;; Required profiles: core, filesystem
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fs_preopen_count" (func $count (result i32 i32)))
  (func (export "run") (result i32 i32)
    (call $count)))
(assert_return (invoke "run") (i32.const 0) (i32.const 0))
