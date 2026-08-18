;; WPSI conformance test: imports/random_fill_array_i8
;; Purpose: Exact Core signature for facet.random_fill_array_i8.
;; Required profiles: gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "random_fill_array_i8" (func $random_fill_array_i8 (param (ref array) i64 i64) (result i64 i32))))
