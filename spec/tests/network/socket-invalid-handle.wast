;; Facet conformance test: network/socket-invalid-handle
;; Purpose: Socket operations validate handles before host access.
;; Required profiles: core, network
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "socket_connect" (func $connect (param i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "socket_peer_address" (func $peer (param i32) (result i32 i64 i64 i32 i32 i32)))
  (import "facet" "socket_recvfrom_mem64" (func $recv64
    (param i32 i32 i64 i64 i32)
    (result i64 i32 i64 i64 i32 i32 i32 i32)))
  (import "facet" "socket_sendto_mem64" (func $send64
    (param i32 i32 i64 i64 i32 i64 i64 i32 i32 i32)
    (result i64 i32)))
  (import "facet" "socket_shutdown" (func $shutdown (param i32 i32) (result i32)))

  (func (export "run") (result i32)
    (local $e i32) (local $n i64)

    ;; Use a structurally valid IPv4 loopback address so handle validation is the
    ;; failing boundary rather than address decoding.
    (local.set $e
      (call $connect
        (i32.const 0) (i32.const 1) (i64.const 0) (i64.const 2130706433)
        (i32.const 0) (i32.const 0)))
    (if (i32.ne (local.get $e) (i32.const 4))
      (then (return (i32.const 1))))

    ;; Address queries zero their non-error results and report ERR_BAD_HANDLE.
    (call $peer (i32.const 0))
    (local.set $e)
    drop drop drop drop drop
    (if (i32.ne (local.get $e) (i32.const 4))
      (then (return (i32.const 2))))

    ;; Datagram Memory64 functions validate the resource before touching guest
    ;; memory, so this test does not need to instantiate a Memory64 memory.
    (call $recv64
      (i32.const 0) (i32.const 0) (i64.const 0) (i64.const 1) (i32.const 0))
    (local.set $e)
    drop drop drop drop drop drop drop
    (if (i32.ne (local.get $e) (i32.const 4))
      (then (return (i32.const 3))))

    (call $send64
      (i32.const 0) (i32.const 0) (i64.const 0) (i64.const 1)
      (i32.const 1) (i64.const 0) (i64.const 2130706433)
      (i32.const 0) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $n)
    (if (i32.or (i64.ne (local.get $n) (i64.const 0))
                (i32.ne (local.get $e) (i32.const 4)))
      (then (return (i32.const 4))))

    ;; Preserve the original shutdown invalid-handle assertion as the final result.
    (call $shutdown (i32.const 0) (i32.const 3)))
)
(assert_return (invoke "run") (i32.const 4))
