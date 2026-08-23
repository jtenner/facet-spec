;; Facet conformance test: args-env/args-read-into-array-i16
;; Purpose: UTF-16 arguments can be copied directly into an existing mutable array<i16>.
;; Required profiles: core, gc-array, args-env, text
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a8 (array (mut i8)))
  (type $a16 (array (mut i16)))
  (type $a32 (array (mut i32)))

  (import "facet" "args_len_i16" (func $len16 (param i32 i32) (result i64 i32)))
  (import "facet" "args_len_i32" (func $len32 (param i32 i32) (result i64 i32)))
  (import "facet" "args_read_mem32_i16" (func $read_mem32_i16 (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "args_read_mem32_i32" (func $read_mem32_i32 (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "facet" "args_read_mem64_i8" (func $read_mem64_i8 (param i32 i32 i32 i64 i64) (result i64 i32)))
  (import "facet" "args_read_mem64_i16" (func $read_mem64_i16 (param i32 i32 i32 i64 i64) (result i64 i32)))
  (import "facet" "args_read_mem64_i32" (func $read_mem64_i32 (param i32 i32 i32 i64 i64) (result i64 i32)))
  (import "facet" "args_read_into_array_i8" (func $read_into_i8 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "args_read_into_array_i16" (func $read_into_i16 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "args_read_into_array_i32" (func $read_into_i32 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "facet" "args_read_array_i32" (func $read_array_i32 (param i32 i32) (result (ref null $a32) i32)))

  (memory 1)
  (memory i64 1)

  (func (export "run") (result i32)
    (local $a8 (ref $a8))
    (local $a16 (ref $a16))
    (local $a32 (ref $a32))
    (local $allocated32 (ref null $a32))
    (local $n i64)
    (local $e i32)

    ;; "alpha" has five code units in every Facet text width.
    (call $len16 (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 5)))
      (then (return (i32.const 1))))
    (call $len32 (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 5)))
      (then (return (i32.const 2))))

    ;; Exercise the remaining linear-memory representations.
    (call $read_mem32_i16 (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 5))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 5)))
      (then (return (i32.const 3))))
    (call $read_mem32_i32 (i32.const 0) (i32.const 0) (i32.const 0) (i32.const 16) (i32.const 5))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 5)))
      (then (return (i32.const 4))))
    (call $read_mem64_i8 (i32.const 0) (i32.const 0) (i32.const 1) (i64.const 0) (i64.const 5))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 5)))
      (then (return (i32.const 5))))
    (call $read_mem64_i16 (i32.const 0) (i32.const 0) (i32.const 1) (i64.const 16) (i64.const 5))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 5)))
      (then (return (i32.const 6))))
    (call $read_mem64_i32 (i32.const 0) (i32.const 0) (i32.const 1) (i64.const 32) (i64.const 5))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e) (i64.ne (local.get $n) (i64.const 5)))
      (then (return (i32.const 7))))

    ;; Exercise caller-owned GC arrays in every textual storage width.
    (local.set $a8 (array.new_default $a8 (i32.const 5)))
    (local.set $a16 (array.new_default $a16 (i32.const 5)))
    (local.set $a32 (array.new_default $a32 (i32.const 5)))
    (call $read_into_i8 (i32.const 0) (i32.const 0) (local.get $a8) (i32.const 0) (i32.const 5))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e)
          (i32.or (i64.ne (local.get $n) (i64.const 5))
                  (i32.ne (array.get_u $a8 (local.get $a8) (i32.const 0)) (i32.const 97))))
      (then (return (i32.const 8))))
    (call $read_into_i16 (i32.const 0) (i32.const 0) (local.get $a16) (i32.const 0) (i32.const 5))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e)
          (i32.or (i64.ne (local.get $n) (i64.const 5))
                  (i32.ne (array.get_u $a16 (local.get $a16) (i32.const 0)) (i32.const 97))))
      (then (return (i32.const 9))))
    (call $read_into_i32 (i32.const 0) (i32.const 0) (local.get $a32) (i32.const 0) (i32.const 5))
    (local.set $e) (local.set $n)
    (if (i32.or (local.get $e)
          (i32.or (i64.ne (local.get $n) (i64.const 5))
                  (i32.ne (array.get $a32 (local.get $a32) (i32.const 0)) (i32.const 97))))
      (then (return (i32.const 10))))

    ;; Exercise host allocation of the remaining concrete text array family.
    (call $read_array_i32 (i32.const 0) (i32.const 0))
    (local.set $e) (local.set $allocated32)
    (if (i32.or (local.get $e) (ref.is_null (local.get $allocated32)))
      (then (return (i32.const 11))))

    (i32.const 0))
)
(assert_return (invoke "run") (i32.const 0))
