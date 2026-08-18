;; WPSI conformance test: imports/fd_write_array_v128
;; Purpose: Exact Core signature for facet.fd_write_array_v128.
;; Required profiles: gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fd_write_array_v128" (func $fd_write_array_v128 (param i32 (ref array) i64 i64) (result i64 i32))))
