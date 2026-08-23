;; Facet conformance test: network/dns-localhost-terminates
;; Purpose: DNS iteration for localhost yields at least one address and terminates.
;; Required profiles: core, memory32, network
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a8 (array (mut i8)))
  (type $a16 (array (mut i16)))
  (type $a32 (array (mut i32)))

  (import "facet" "dns_resolve_mem32_i8" (func $resolve_mem32_i8 (param i32 i32 i32 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_resolve_mem32_i16" (func $resolve_mem32_i16 (param i32 i32 i32 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_resolve_mem32_i32" (func $resolve_mem32_i32 (param i32 i32 i32 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_resolve_mem64_i8" (func $resolve_mem64_i8 (param i32 i64 i64 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_resolve_mem64_i16" (func $resolve_mem64_i16 (param i32 i64 i64 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_resolve_mem64_i32" (func $resolve_mem64_i32 (param i32 i64 i64 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_resolve_array_i8" (func $resolve_array_i8 (param (ref array) i32 i32 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_resolve_array_i16" (func $resolve_array_i16 (param (ref array) i32 i32 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_resolve_array_i32" (func $resolve_array_i32 (param (ref array) i32 i32 i32 i32 i32) (result i32 i32)))
  (import "facet" "dns_next" (func $next (param i32) (result i32 i64 i64 i32 i32 i32)))
  (import "facet" "handle_close" (func $close (param i32) (result i32)))

  (memory 1)
  (data (i32.const 0) "localhost")
  (data (i32.const 32) "\6c\00\6f\00\63\00\61\00\6c\00\68\00\6f\00\73\00\74\00")
  (data (i32.const 64) "\6c\00\00\00\6f\00\00\00\63\00\00\00\61\00\00\00\6c\00\00\00\68\00\00\00\6f\00\00\00\73\00\00\00\74\00\00\00")

  (func $close-resolver (param $r i32) (result i32)
    (call $close (local.get $r)))

  (func (export "run") (result i32)
    (local $r i32) (local $e i32) (local $family i32) (local $hi i64) (local $lo i64)
    (local $scope i32) (local $done i32) (local $i i32)
    (local $a8 (ref $a8)) (local $a16 (ref $a16)) (local $a32 (ref $a32))

    ;; The original UTF-8 Memory32 resolver must produce at least one address and terminate.
    (call $resolve_mem32_i8 (i32.const 0) (i32.const 0) (i32.const 9) (i32.const 0) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $r)
    (if (local.get $e) (then (return (local.get $e))))
    (block $finished
      (loop $again
        (call $next (local.get $r))
        (local.set $e) (local.set $done) (local.set $scope) (local.set $lo) (local.set $hi) (local.set $family)
        (if (local.get $e) (then (return (local.get $e))))
        (br_if $finished (local.get $done))
        (local.set $i (i32.add (local.get $i) (i32.const 1)))
        (if (i32.gt_u (local.get $i) (i32.const 32)) (then (return (i32.const 100))))
        (br $again)))
    (drop (call $close-resolver (local.get $r)))
    (if (i32.eqz (local.get $i)) (then (return (i32.const 101))))

    ;; Equivalent valid Memory32 UTF-16 and UTF-32 presentation strings.
    (call $resolve_mem32_i16 (i32.const 0) (i32.const 32) (i32.const 9) (i32.const 0) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $r)
    (if (local.get $e) (then (return (local.get $e))))
    (drop (call $close-resolver (local.get $r)))
    (call $resolve_mem32_i32 (i32.const 0) (i32.const 64) (i32.const 9) (i32.const 0) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $r)
    (if (local.get $e) (then (return (local.get $e))))
    (drop (call $close-resolver (local.get $r)))

    ;; All GC-array text widths resolve the same ASCII hostname without lowering.
    (local.set $a8 (array.new_fixed $a8 9
      (i32.const 108) (i32.const 111) (i32.const 99) (i32.const 97) (i32.const 108)
      (i32.const 104) (i32.const 111) (i32.const 115) (i32.const 116)))
    (local.set $a16 (array.new_fixed $a16 9
      (i32.const 108) (i32.const 111) (i32.const 99) (i32.const 97) (i32.const 108)
      (i32.const 104) (i32.const 111) (i32.const 115) (i32.const 116)))
    (local.set $a32 (array.new_fixed $a32 9
      (i32.const 108) (i32.const 111) (i32.const 99) (i32.const 97) (i32.const 108)
      (i32.const 104) (i32.const 111) (i32.const 115) (i32.const 116)))
    (call $resolve_array_i8 (local.get $a8) (i32.const 0) (i32.const 9) (i32.const 0) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $r)
    (if (local.get $e) (then (return (local.get $e))))
    (drop (call $close-resolver (local.get $r)))
    (call $resolve_array_i16 (local.get $a16) (i32.const 0) (i32.const 9) (i32.const 0) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $r)
    (if (local.get $e) (then (return (local.get $e))))
    (drop (call $close-resolver (local.get $r)))
    (call $resolve_array_i32 (local.get $a32) (i32.const 0) (i32.const 9) (i32.const 0) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $r)
    (if (local.get $e) (then (return (local.get $e))))
    (drop (call $close-resolver (local.get $r)))

    ;; Memory64 resolver variants still validate the explicit memory index. This module
    ;; intentionally has no Memory64 memory, so index 1 must fail atomically with ERR_FAULT.
    (call $resolve_mem64_i8 (i32.const 1) (i64.const 0) (i64.const 9) (i32.const 0) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $r)
    (if (i32.or (local.get $r) (i32.ne (local.get $e) (i32.const 24)))
      (then (return (i32.const 102))))
    (call $resolve_mem64_i16 (i32.const 1) (i64.const 0) (i64.const 9) (i32.const 0) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $r)
    (if (i32.or (local.get $r) (i32.ne (local.get $e) (i32.const 24)))
      (then (return (i32.const 103))))
    (call $resolve_mem64_i32 (i32.const 1) (i64.const 0) (i64.const 9) (i32.const 0) (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $r)
    (if (i32.or (local.get $r) (i32.ne (local.get $e) (i32.const 24)))
      (then (return (i32.const 104))))

    (i32.const 0))
)
(assert_return (invoke "run") (i32.const 0))
