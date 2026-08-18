;; WPSI conformance test: network/dns-localhost-terminates
;; Purpose: DNS iteration for localhost yields at least one address and terminates.
;; Required profiles: core, memory32, network
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "dns_resolve_mem32_i8" (func $resolve (param i32 i32 i32 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_next" (func $next (param i32) (result i32 i64 i64 i32 i32 i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))
  (memory 1)
  (data (i32.const 0) "localhost")
  (func (export "run") (result i32)
    (local $r i32) (local $e i32) (local $family i32) (local $hi i64) (local $lo i64)
    (local $scope i32) (local $done i32) (local $i i32)
    (call $resolve (i32.const 0) (i32.const 0) (i32.const 9) (i32.const 0) (i32.const 0) (i32.const 0)) (local.set $e) (local.set $r)
    (if (local.get $e) (then (return (local.get $e))))
    (block $finished
      (loop $again
        (call $next (local.get $r)) (local.set $e) (local.set $done) (local.set $scope) (local.set $lo) (local.set $hi) (local.set $family)
        (if (local.get $e) (then (return (local.get $e))))
        (br_if $finished (local.get $done))
        (local.set $i (i32.add (local.get $i) (i32.const 1)))
        (if (i32.gt_u (local.get $i) (i32.const 32)) (then (return (i32.const 100))))
        (br $again)))
    (drop (call $close (local.get $r)))
    (i32.eqz (local.get $i))))
(assert_return (invoke "run") (i32.const 0))
