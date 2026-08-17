;; WPSI conformance test: imports/profile-surface
;; Purpose: Representative imports guard profile naming and Core signatures.
;; Required profiles: core, memory32, memory64, gc-array, filesystem, links, network, poll
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "abi_version" (func $abi (result i32)))
  (import "wpsi" "random_fill_mem32" (func $m32 (param i32 i32 i32) (result i64 i32)))
  (import "wpsi" "random_fill_mem64" (func $m64 (param i32 i64 i64) (result i64 i32)))
  (import "wpsi" "random_fill_array_i8" (func $gc (param (ref array) i64 i64) (result i64 i32)))
  (import "wpsi" "fs_scratch" (func $fs (result i32 i32)))
  (import "wpsi" "path_link_mem32_i8" (func $link (param i32 i32 i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "wpsi" "socket_open" (func $sock (param i32 i32 i32 i32) (result i32 i32)))
  (import "wpsi" "poll_create" (func $poll (result i32 i32)))
  (func (export "version") (result i32) (call $abi)))
(assert_return (invoke "version") (i32.const 1))
