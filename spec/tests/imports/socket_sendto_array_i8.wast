;; WPSI conformance test: imports/socket_sendto_array_i8
;; Purpose: Exact Core signature for wpsi.socket_sendto_array_i8.
;; Required profiles: gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "socket_sendto_array_i8" (func $socket_sendto_array_i8 (param i32 (ref array) i64 i64 i32 i64 i64 i32 i32 i32) (result i64 i32))))
