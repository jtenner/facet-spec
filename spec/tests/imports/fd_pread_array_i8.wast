;; Facet conformance test: imports/fd_pread_array_i8
;; Purpose: Exact Core signature for facet.fd_pread_array_i8.
;; Required profiles: gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "fd_pread_array_i8" (func $fd_pread_array_i8 (param i32 i64 (ref array) i64 i64) (result i64 i32))))
