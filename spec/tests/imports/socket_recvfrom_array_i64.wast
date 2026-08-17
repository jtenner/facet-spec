;; WPSI conformance test: imports/socket_recvfrom_array_i64
;; Purpose: Exact Core signature for wpsi.socket_recvfrom_array_i64.
;; Required profiles: gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "socket_recvfrom_array_i64" (func $socket_recvfrom_array_i64 (param i32 (ref array) i64 i64 i32) (result i64 i32 i64 i64 i32 i32 i32 i32))))
