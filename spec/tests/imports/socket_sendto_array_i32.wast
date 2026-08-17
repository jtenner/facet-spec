;; WPSI conformance test: imports/socket_sendto_array_i32
;; Purpose: Exact Core signature for wpsi.socket_sendto_array_i32.
;; Required profiles: gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "socket_sendto_array_i32" (func $socket_sendto_array_i32 (param i32 (ref array) i64 i64 i32 i64 i64 i32 i32 i32) (result i64 i32))))
