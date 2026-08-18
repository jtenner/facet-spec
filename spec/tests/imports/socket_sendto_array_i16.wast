;; Facet conformance test: imports/socket_sendto_array_i16
;; Purpose: Exact Core signature for facet.socket_sendto_array_i16.
;; Required profiles: gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "socket_sendto_array_i16" (func $socket_sendto_array_i16 (param i32 (ref array) i64 i64 i32 i64 i64 i32 i32 i32) (result i64 i32))))
