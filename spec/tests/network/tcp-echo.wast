;; WPSI conformance test: network/tcp-echo
;; Purpose: The WASI-compatible connect/send/recv harness can drive a WPSI TCP listener through accept and stream I/O.
;; Required profiles: core, memory32, network
;; Test kind: harness
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "stdio_stdout" (func $stdout (result i32 i32)))
  (import "wpsi" "fd_write_mem32" (func $write (param i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "fd_read_mem32" (func $read (param i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "socket_open" (func $open (param i32 i32 i32 i32) (result i32 i32)))
  (import "wpsi" "socket_bind" (func $bind (param i32 i32 i64 i64 i32 i32) (result i32)))
  (import "wpsi" "socket_listen" (func $listen (param i32 i32) (result i32)))
  (import "wpsi" "socket_accept" (func $accept (param i32 i32) (result i32 i32 i64 i64 i32 i32 i32)))
  (import "wpsi" "handle_close" (func $close (param i32) (result i32)))
  (import "wpsi" "proc_exit" (func $exit (param i32)))
  (memory 1)
  (data (i32.const 0) "127.0.0.1:32123\0a")
  (func $check (param $e i32)
    (if (local.get $e) (then (call $exit (local.get $e)))))
  (func (export "_start")
    (local $server i32) (local $client i32) (local $out i32) (local $e i32) (local $n i64)
    (local $family i32) (local $hi i64) (local $lo i64) (local $port i32) (local $scope i32)
    (call $open (i32.const 1) (i32.const 1) (i32.const 1) (i32.const 0)) (local.set $e) (local.set $server)
    (call $check (local.get $e))
    (local.set $e (call $bind (local.get $server) (i32.const 1) (i64.const 0) (i64.const 2130706433) (i32.const 32123) (i32.const 0)))
    (call $check (local.get $e))
    (local.set $e (call $listen (local.get $server) (i32.const 1)))
    (call $check (local.get $e))
    (call $stdout) (local.set $e) (local.set $out)
    (call $write (local.get $out) (i32.const 0) (i32.const 0) (i32.const 16)) (local.set $e) (local.set $n)
    (call $check (local.get $e))
    (call $accept (local.get $server) (i32.const 0)) (local.set $e) (local.set $scope) (local.set $port) (local.set $lo) (local.set $hi) (local.set $family) (local.set $client)
    (call $check (local.get $e))
    (call $read (local.get $client) (i32.const 0) (i32.const 64) (i32.const 4)) (local.set $e) (local.set $n)
    (call $check (local.get $e))
    (call $write (local.get $client) (i32.const 0) (i32.const 64) (i32.wrap_i64 (local.get $n))) (local.set $e) (local.set $n)
    (call $check (local.get $e))
    (drop (call $close (local.get $client)))
    (drop (call $close (local.get $server)))))
