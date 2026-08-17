;; WPSI conformance test: imports/fd_pread_array_i64
;; Purpose: Exact Core signature for wpsi.fd_pread_array_i64.
;; Required profiles: gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fd_pread_array_i64" (func $fd_pread_array_i64 (param i32 i64 (ref array) i64 i64) (result i64 i32))))
