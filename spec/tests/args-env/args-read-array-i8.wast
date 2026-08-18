;; Facet conformance test: args-env/args-read-array-i8
;; Purpose: The host can allocate the caller's concrete array<i8> result type for an argument.
;; Required profiles: core, gc-array, args-env, text
;;
;; SPDX-License-Identifier: MIT

(module
  (type $s (array (mut i8)))
  (import "facet" "args_read_array_i8" (func $read (param i32 i32) (result (ref null $s) i32)))
  (func (export "run") (result i32)
    (local $s (ref null $s)) (local $e i32)
    (call $read (i32.const 0) (i32.const 0)) (local.set $e) (local.set $s)
    (if (result i32) (ref.is_null (local.get $s))
      (then (i32.const 1))
      (else
        (i32.or (local.get $e)
          (i32.or (i32.ne (array.len (local.get $s)) (i32.const 5))
                  (i32.ne (array.get_u $s (ref.as_non_null (local.get $s)) (i32.const 0)) (i32.const 97)))))))
)
(assert_return (invoke "run") (i32.const 0))
