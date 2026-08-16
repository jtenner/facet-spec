(module
  (type $bytes (array (mut i8)))

  (import "wpsi" "stdio_stdin"
    (func $stdio_stdin (result i32 i32)))

  (import "wpsi" "fd_read_array_i8"
    (func $fd_read_array_i8
      (param i32 (ref array) i64 i64)
      (result i64 i32)))

  (func (export "read") (param $capacity i32) (result i64 i32)
    (local $fd i32)
    (local $errno i32)

    call $stdio_stdin
    local.set $errno
    local.set $fd

    ;; The concrete (ref $bytes) value is a subtype of the import's
    ;; abstract (ref array) parameter. No linear-memory adapter is needed.
    local.get $fd
    local.get $capacity
    array.new_default $bytes
    i64.const 0
    local.get $capacity
    i64.extend_i32_u
    call $fd_read_array_i8
  )
)
