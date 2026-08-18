;; Facet conformance test: network/socket-open-close
;; Purpose: A TCP/IPv4 socket is an ordinary closeable Facet resource.
;; Required profiles: core, network
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "socket_open" (func $open (param i32 i32 i32 i32) (result i32 i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))
  (func (export "run") (result i32)
    (local $fd i32) (local $e i32)
    (call $open (i32.const 1) (i32.const 1) (i32.const 1) (i32.const 0)) (local.set $e) (local.set $fd)
    (if (result i32) (local.get $e) (then (local.get $e)) (else (call $close (local.get $fd)))))
)
(assert_return (invoke "run") (i32.const 0))
