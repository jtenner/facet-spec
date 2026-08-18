;; Facet conformance test: imports/random_fill_array_i64
;; Purpose: Exact Core signature for facet.random_fill_array_i64.
;; Required profiles: gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "random_fill_array_i64" (func $random_fill_array_i64 (param (ref array) i64 i64) (result i64 i32))))
