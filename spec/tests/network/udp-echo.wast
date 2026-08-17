;; WPSI conformance test: network/udp-echo
;; Purpose: The WASI-compatible connect/send/recv harness can drive WPSI datagram receive and reply operations.
;; Required profiles: core, memory32, network
;; Test kind: harness
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "stdio_stdout" (func $stdout (result i32 i32)))
  (import "wpsi" "fd_write_mem32" (func $write (param i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "socket_open" (func $open (param i32 i32 i32 i32) (result i32 i32)))
  (import "wpsi" "socket_bind" (func $bind (param i32 i32 i64 i64 i32 i32) (result i32)))
  (import "wpsi" "socket_recvfrom_mem32" (func $recv (param i32 i32 i32 i32 i32) (result i64 i32 i64 i64 i32 i32 i32 i32)))
  (import "wpsi" "socket_sendto_mem32" (func $send (param i32 i32 i32 i32 i32 i64 i64 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (import "wpsi" "proc_exit" (func $exit (param i32)))
  (memory 1)
  (data (i32.const 0) "127.0.0.1:32124\0a")
  (func $check (param $e i32)
    (if (local.get $e) (then (call $exit (local.get $e)))))
  (func (export "_start")
    (local $fd i32) (local $out i32) (local $e i32) (local $n i64)
    (local $family i32) (local $hi i64) (local $lo i64) (local $port i32) (local $scope i32) (local $flags i32)
    (call $open (i32.const 1) (i32.const 2) (i32.const 2) (i32.const 0)) (local.set $e) (local.set $fd)
    (call $check (local.get $e))
    (local.set $e (call $bind (local.get $fd) (i32.const 1) (i64.const 0) (i64.const 2130706433) (i32.const 32124) (i32.const 0)))
    (call $check (local.get $e))
    (call $stdout) (local.set $e) (local.set $out)
    (call $write (local.get $out) (i32.const 0) (i32.const 0) (i32.const 16)) (local.set $e) (local.set $n)
    (call $check (local.get $e))
    (call $recv (local.get $fd) (i32.const 0) (i32.const 64) (i32.const 4) (i32.const 0))
    (local.set $e) (local.set $flags) (local.set $scope) (local.set $port) (local.set $lo) (local.set $hi) (local.set $family) (local.set $n)
    (call $check (local.get $e))
    (call $send (local.get $fd) (i32.const 0) (i32.const 64) (i32.wrap_i64 (local.get $n)) (local.get $family) (local.get $hi) (local.get $lo) (local.get $port) (local.get $scope) (i32.const 0)) (local.set $e) (local.set $n)
    (call $check (local.get $e))
    (drop (call $close (local.get $fd)))))
