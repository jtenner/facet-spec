# Examples

These small WAT modules demonstrate the representation-specific WPSI ABI.

- [`memory32-write.wat`](memory32-write.wat) writes a string from linear memory through `fd_write_mem32` and explicitly selects memory index 0.
- [`gc-array-read.wat`](gc-array-read.wat) reads directly into a mutable Wasm GC `array<i8>` through `fd_read_array_i8` without a linear-memory adapter.

The examples intentionally import only the WPSI functions they use.
