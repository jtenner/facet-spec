(module
  (import "facet" "stdio_stdout"
    (func $stdio_stdout (result i32 i32)))

  (import "facet" "fd_write_mem32"
    (func $fd_write_mem32
      (param i32 i32 i32 i32)
      (result i64 i32)))

  (memory $main 1)

  (data (i32.const 0) "hello from WPSI\n")

  (func (export "run") (result i64 i32)
    (local $fd i32)
    (local $errno i32)

    call $stdio_stdout
    local.set $errno
    local.set $fd

    ;; A real guest would handle the stdio error before continuing.
    local.get $fd
    i32.const 0      ;; memory index: $main is memory 0
    i32.const 0      ;; pointer
    i32.const 16     ;; length
    call $fd_write_mem32
  )
)
