;; WPSI conformance test: args-env/args-read-array-oob-null
;; Purpose: An out-of-range allocating argument read returns null and ERR_RANGE.
;; Required profiles: core, gc-array, args-env, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (type $s (array (mut i8)))
  (import "wpsi" "args_read_array_i8" (func $read (param i32 i32) (result (ref null $s) i32)))
  (func (export "run") (result i32)
    (local $s (ref null $s)) (local $e i32)
    (call $read (i32.const -1) (i32.const 0)) (local.set $e) (local.set $s)
    (i32.and (ref.is_null (local.get $s)) (i32.eq (local.get $e) (i32.const 17))))
)
(assert_return (invoke "run") (i32.const 1))
