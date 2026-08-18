;; WPSI conformance test: imports/fd_read_array_i64
;; Purpose: Exact Core signature for facet.fd_read_array_i64.
;; Required profiles: gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fd_read_array_i64" (func $fd_read_array_i64 (param i32 (ref array) i64 i64) (result i64 i32))))
