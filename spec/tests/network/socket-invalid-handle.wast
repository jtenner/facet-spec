;; WPSI conformance test: network/socket-invalid-handle
;; Purpose: Socket operations validate handles before host access.
;; Required profiles: core, network
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "socket_shutdown" (func $shutdown (param i32 i32) (result i32)))
  (func (export "run") (result i32) (call $shutdown (i32.const 0) (i32.const 3))))
(assert_return (invoke "run") (i32.const 4))
