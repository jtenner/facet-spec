;; Facet conformance test: imports/random_fill_array_i16
;; Purpose: Exact Core signature for facet.random_fill_array_i16.
;; Required profiles: gc-array
;;
;; SPDX-License-Identifier: MIT

(module
  (import "facet" "random_fill_array_i16" (func $random_fill_array_i16 (param (ref array) i64 i64) (result i64 i32))))
