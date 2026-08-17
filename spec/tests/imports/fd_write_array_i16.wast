;; WPSI conformance test: imports/fd_write_array_i16
;; Purpose: Exact Core signature for wpsi.fd_write_array_i16.
;; Required profiles: gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fd_write_array_i16" (func $fd_write_array_i16 (param i32 (ref array) i64 i64) (result i64 i32))))
