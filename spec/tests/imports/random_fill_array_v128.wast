;; WPSI conformance test: imports/random_fill_array_v128
;; Purpose: Exact Core signature for facet.random_fill_array_v128.
;; Required profiles: gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "random_fill_array_v128" (func $random_fill_array_v128 (param (ref array) i64 i64) (result i64 i32))))
