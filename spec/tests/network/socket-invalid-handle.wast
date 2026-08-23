;; Facet conformance test: network/socket-invalid-handle
;; Purpose: Socket operations validate handles before host access across every buffer representation.
;; Required profiles: core, gc-array, network
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a8 (array (mut i8)))
  (type $a16 (array (mut i16)))
  (type $a32 (array (mut i32)))
  (type $a64 (array (mut i64)))
  (type $av128 (array (mut v128)))

  (import "facet" "socket_connect" (func $connect (param i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "socket_peer_address" (func $peer (param i32) (result i32 i64 i64 i32 i32 i32)))
  (import "facet" "socket_recvfrom_mem64" (func $recv64
    (param i32 i32 i64 i64 i32)
    (result i64 i32 i64 i64 i32 i32 i32 i32)))
  (import "facet" "socket_sendto_mem64" (func $send64
    (param i32 i32 i64 i64 i32 i64 i64 i32 i32 i32)
    (result i64 i32)))

  (import "facet" "socket_recvfrom_array_i8" (func $recv_i8
    (param i32 (ref array) i64 i64 i32)
    (result i64 i32 i64 i64 i32 i32 i32 i32)))
  (import "facet" "socket_recvfrom_array_i16" (func $recv_i16
    (param i32 (ref array) i64 i64 i32)
    (result i64 i32 i64 i64 i32 i32 i32 i32)))
  (import "facet" "socket_recvfrom_array_i32" (func $recv_i32
    (param i32 (ref array) i64 i64 i32)
    (result i64 i32 i64 i64 i32 i32 i32 i32)))
  (import "facet" "socket_recvfrom_array_i64" (func $recv_i64
    (param i32 (ref array) i64 i64 i32)
    (result i64 i32 i64 i64 i32 i32 i32 i32)))
  (import "facet" "socket_recvfrom_array_v128" (func $recv_v128
    (param i32 (ref array) i64 i64 i32)
    (result i64 i32 i64 i64 i32 i32 i32 i32)))

  (import "facet" "socket_sendto_array_i8" (func $send_i8
    (param i32 (ref array) i64 i64 i32 i64 i64 i32 i32 i32)
    (result i64 i32)))
  (import "facet" "socket_sendto_array_i16" (func $send_i16
    (param i32 (ref array) i64 i64 i32 i64 i64 i32 i32 i32)
    (result i64 i32)))
  (import "facet" "socket_sendto_array_i32" (func $send_i32
    (param i32 (ref array) i64 i64 i32 i64 i64 i32 i32 i32)
    (result i64 i32)))
  (import "facet" "socket_sendto_array_i64" (func $send_i64
    (param i32 (ref array) i64 i64 i32 i64 i64 i32 i32 i32)
    (result i64 i32)))
  (import "facet" "socket_sendto_array_v128" (func $send_v128
    (param i32 (ref array) i64 i64 i32 i64 i64 i32 i32 i32)
    (result i64 i32)))

  (import "facet" "socket_shutdown" (func $shutdown (param i32 i32) (result i32)))

  (func $require-bad (param $e i32)
    (if (i32.ne (local.get $e) (i32.const 4)) (then unreachable)))

  (func (export "run") (result i32)
    (local $e i32) (local $n i64)
    (local $a8 (ref $a8)) (local $a16 (ref $a16)) (local $a32 (ref $a32))
    (local $a64 (ref $a64)) (local $av128 (ref $av128))

    ;; Use a structurally valid IPv4 loopback address so handle validation is the
    ;; failing boundary rather than address decoding.
    (local.set $e
      (call $connect
        (i32.const 0) (i32.const 1) (i64.const 0) (i64.const 2130706433)
        (i32.const 0) (i32.const 0)))
    (call $require-bad (local.get $e))

    ;; Address queries zero their non-error results and report ERR_BAD_HANDLE.
    (call $peer (i32.const 0))
    (local.set $e) drop drop drop drop drop
    (call $require-bad (local.get $e))

    ;; Datagram Memory64 functions validate the resource before touching guest
    ;; memory, so this test does not need to instantiate a Memory64 memory.
    (call $recv64
      (i32.const 0) (i32.const 0) (i64.const 0) (i64.const 1) (i32.const 0))
    (local.set $e) drop drop drop drop drop drop drop
    (call $require-bad (local.get $e))

    (call $send64
      (i32.const 0) (i32.const 0) (i64.const 0) (i64.const 1)
      (i32.const 1) (i64.const 0) (i64.const 2130706433)
      (i32.const 0) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $n)
    (if (i64.ne (local.get $n) (i64.const 0)) (then unreachable))
    (call $require-bad (local.get $e))

    ;; Every GC storage class crosses the same datagram host boundary. Zero-length
    ;; concrete arrays keep the probe side-effect free while still exercising the
    ;; exact array storage class and direct host call.
    (local.set $a8 (array.new_default $a8 (i32.const 0)))
    (local.set $a16 (array.new_default $a16 (i32.const 0)))
    (local.set $a32 (array.new_default $a32 (i32.const 0)))
    (local.set $a64 (array.new_default $a64 (i32.const 0)))
    (local.set $av128 (array.new_default $av128 (i32.const 0)))

    (call $recv_i8 (i32.const 0) (local.get $a8) (i64.const 0) (i64.const 0) (i32.const 0))
    (local.set $e) drop drop drop drop drop drop drop
    (call $require-bad (local.get $e))
    (call $recv_i16 (i32.const 0) (local.get $a16) (i64.const 0) (i64.const 0) (i32.const 0))
    (local.set $e) drop drop drop drop drop drop drop
    (call $require-bad (local.get $e))
    (call $recv_i32 (i32.const 0) (local.get $a32) (i64.const 0) (i64.const 0) (i32.const 0))
    (local.set $e) drop drop drop drop drop drop drop
    (call $require-bad (local.get $e))
    (call $recv_i64 (i32.const 0) (local.get $a64) (i64.const 0) (i64.const 0) (i32.const 0))
    (local.set $e) drop drop drop drop drop drop drop
    (call $require-bad (local.get $e))
    (call $recv_v128 (i32.const 0) (local.get $av128) (i64.const 0) (i64.const 0) (i32.const 0))
    (local.set $e) drop drop drop drop drop drop drop
    (call $require-bad (local.get $e))

    (call $send_i8
      (i32.const 0) (local.get $a8) (i64.const 0) (i64.const 0)
      (i32.const 1) (i64.const 0) (i64.const 2130706433)
      (i32.const 0) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $n)
    (call $require-bad (local.get $e))
    (call $send_i16
      (i32.const 0) (local.get $a16) (i64.const 0) (i64.const 0)
      (i32.const 1) (i64.const 0) (i64.const 2130706433)
      (i32.const 0) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $n)
    (call $require-bad (local.get $e))
    (call $send_i32
      (i32.const 0) (local.get $a32) (i64.const 0) (i64.const 0)
      (i32.const 1) (i64.const 0) (i64.const 2130706433)
      (i32.const 0) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $n)
    (call $require-bad (local.get $e))
    (call $send_i64
      (i32.const 0) (local.get $a64) (i64.const 0) (i64.const 0)
      (i32.const 1) (i64.const 0) (i64.const 2130706433)
      (i32.const 0) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $n)
    (call $require-bad (local.get $e))
    (call $send_v128
      (i32.const 0) (local.get $av128) (i64.const 0) (i64.const 0)
      (i32.const 1) (i64.const 0) (i64.const 2130706433)
      (i32.const 0) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $n)
    (call $require-bad (local.get $e))

    ;; Preserve the original shutdown invalid-handle assertion as the final result.
    (call $shutdown (i32.const 0) (i32.const 3)))
)
(assert_return (invoke "run") (i32.const 4))
