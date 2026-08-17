;; WPSI conformance test: imports/fd_pread_array_i32
;; Purpose: Exact Core signature for wpsi.fd_pread_array_i32.
;; Required profiles: gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fd_pread_array_i32" (func $fd_pread_array_i32 (param i32 i64 (ref array) i64 i64) (result i64 i32))))
