;; WPSI conformance test: imports/fd_write_array_i8
;; Purpose: Exact Core signature for facet.fd_write_array_i8.
;; Required profiles: gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fd_write_array_i8" (func $fd_write_array_i8 (param i32 (ref array) i64 i64) (result i64 i32))))
