;; WPSI conformance test: network/socket-bind-ephemeral
;; Purpose: Binding UDP to port zero assigns a nonzero local port.
;; Required profiles: core, network
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "socket_open" (func $open (param i32 i32 i32 i32) (result i32 i32)))
  (import "facet" "socket_bind" (func $bind (param i32 i32 i64 i64 i32 i32) (result i32)))
  (import "facet" "socket_local_address" (func $local (param i32) (result i32 i64 i64 i32 i32 i32)))
  (func (export "run") (result i32)
    (local $fd i32) (local $e i32) (local $fam i32) (local $hi i64) (local $lo i64) (local $port i32) (local $scope i32)
    (call $open (i32.const 1) (i32.const 2) (i32.const 2) (i32.const 0)) (local.set $e) (local.set $fd)
    (local.set $e (call $bind (local.get $fd) (i32.const 1) (i64.const 0) (i64.const 2130706433) (i32.const 0) (i32.const 0)))
    (call $local (local.get $fd)) (local.set $e) (local.set $scope) (local.set $port) (local.set $lo) (local.set $hi) (local.set $fam)
    (i32.or (local.get $e) (i32.eqz (local.get $port))))
)
(assert_return (invoke "run") (i32.const 0))
