;; WPSI conformance test: args-env/args-read-array-i16
;; Purpose: The host can allocate the caller's concrete array<i16> result type.
;; Required profiles: core, gc-array, args-env, text
;;
;; SPDX-License-Identifier: MIT

(module
  (type $s (array i16))
  (import "facet" "args_read_array_i16" (func $read (param i32 i32) (result (ref null $s) i32)))
  (func (export "run") (result i32)
    (local $s (ref null $s)) (local $e i32)
    (call $read (i32.const 1) (i32.const 0)) (local.set $e) (local.set $s)
    (i32.or (local.get $e) (ref.is_null (local.get $s))))
)
(assert_return (invoke "run") (i32.const 0))
