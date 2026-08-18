;; Facet conformance test: imports/random_fill_array_i32
;; Purpose: Exact Core signature for facet.random_fill_array_i32.
;; Required profiles: gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "random_fill_array_i32" (func $random_fill_array_i32 (param (ref array) i64 i64) (result i64 i32))))
