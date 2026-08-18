# Examples

These small WAT modules show the main Facet representation forms.

## Memory32 write

[`memory32-write.wat`](memory32-write.wat) writes a string from linear memory with `fd_write_mem32`.

The call explicitly selects memory index 0.

The index is explicit even though this example uses only one memory.

## GC-array read

[`gc-array-read.wat`](gc-array-read.wat) reads directly into a mutable Wasm GC `array<i8>` with `fd_read_array_i8`.

The guest does not need a linear-memory adapter for this operation.

Each example imports only the Facet functions that it uses.
