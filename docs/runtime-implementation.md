# Runtime Implementation Guidance

This document is informative. `SPEC.md` defines observable behavior.

## Host-import structure

A runtime does not need polymorphic import resolution. WPSI functions are ordinary imports from module `wpsi`.

A minimal implementation can register only the functions corresponding to features it supports.

For example, a runtime without Wasm GC may implement:

```text
wpsi-core
wpsi-memory32
wpsi-filesystem
```

while a Core Wasm 3.0 runtime may additionally implement:

```text
wpsi-memory64
wpsi-gc-array
wpsi-network
wpsi-poll
```

Do not build a second profile-version or feature-negotiation registry for WPSI. Register the imports the runtime implements and let ordinary Core Wasm import/type matching decide whether a module can instantiate. `abi_version()` is the only global ABI generation number; profile labels are implementation/conformance groupings, not independently versioned runtime objects.

## Synchronous call boundary

Treat the return from every WPSI host function as a hard lifetime boundary.

No guest linear-memory view, GC reference, raw GC payload pointer, pin, root, no-move token, or other borrowed guest-storage state may remain owned by host work after the function returns. If an operating-system or runtime API requires an operation to outlive the call, copy the relevant guest data into host-owned storage or use a nonblocking operation that returns `ERR_AGAIN` and is retried after polling.

Do not implement a WPSI import by starting background work that will later dereference a guest pointer or GC reference. The host may retain WPSI resource handles and host-owned metadata, but not borrowed guest storage.

This restriction is per call, not per runtime. A runtime is free to execute multiple Wasm instances, actors, tasks, or scheduler contexts concurrently as long as each WPSI call obeys the same lifetime boundary.

## Linear-memory access

For every `_mem32` or `_mem64` call:

1. resolve the calling instance;
2. validate `memory_index` against the instance's memory index space;
3. validate the selected memory's address width;
4. check pointer/length arithmetic for overflow;
5. bounds-check against the memory's current size;
6. keep the memory backing stable for the synchronous host operation;
7. perform the host operation directly on the selected memory when safe.

Memory 0 must not receive special treatment.

## Text representation

Text width is part of the WPSI import name. A runtime should dispatch `*_i8`, `*_i16`, and `*_i32` directly to the corresponding code-unit reader/writer rather than decoding an encoding enum on every call.

The `wtf` argument is a strict boolean. Validate it before touching guest buffers or host namespaces.

```text
wtf = 0 -> strict Unicode scalar text
wtf = 1 -> permit surrogate sentinel values
```

On byte-oriented host namespaces, a practical reversible mapping for invalid UTF-8 bytes is the surrogate-escape range `U+DC80..U+DCFF`. On UTF-16 hosts, preserve unpaired surrogate code units directly. Never substitute U+FFFD when WPSI requires lossless transfer; return `ERR_ILLEGAL_SEQUENCE` if the selected mode cannot represent the host value.

For linear memory, `_i16` and `_i32` code units are little-endian. The pointer remains a byte address while lengths/capacities are code-unit counts.

## GC array access

A useful internal runtime primitive is:

```text
with_array_bytes(reference, expected_element_type, access_mode, callback)
```

with semantics equivalent to:

```text
validate array reference
validate dynamic storage type
validate destination mutability when required
validate logical byte range
root reference
establish pin/no-move/no-GC scope if needed
resolve current backing storage
invoke callback over a temporary byte view
invalidate the byte view
leave collector scope
```

The callback must not retain the native address or slice.

### Fast path

If a runtime stores pointer-free numeric arrays contiguously and can safely stabilize the object for a synchronous call, the logical byte view can map directly onto the array payload.

This permits operations such as an OS `read` to write directly into the GC array.

### Portable fallback

A runtime whose array layout is non-contiguous, encoded, compressed, or otherwise unsuitable for direct native access may use a temporary native byte buffer.

For reads:

```text
host read -> temporary bytes -> logical-byte-view update
```

For writes:

```text
logical-byte-view extraction -> temporary bytes -> host write
```

This is conforming as long as partial-element behavior and all observable values match the specification.

## Host-allocated GC string results

Allocating string imports such as `args_read_array_i16` are specialized to the concrete nullable array result type requested by the importing module.

At import instantiation a runtime should:

1. inspect the requested function result type;
2. require a concrete array heap type with the storage class named by the import;
3. retain the runtime type identity in the host-function instance;
4. encode the selected source string completely;
5. allocate exactly that array type at the exact required length;
6. initialize every element before returning the reference;
7. return `null` plus `ERR_NO_MEMORY` if allocation fails.

The result array may be mutable or immutable. This path does not borrow an existing object and therefore does not use the scoped raw-array byte-borrow primitive.

Caller-owned `*_read_into_array_*` functions still use normal destination validation and require mutable arrays.

## Current runtime layout observations

These observations motivated the WPSI 0.1 array design. They are not normative requirements.

### Wago

Wago's collector stores objects in byte heaps with a 16-byte object header. Array size is computed as:

```text
header + element_size * length
```

with final object alignment.

Current numeric storage sizes are:

```text
i8      1
 i16     2
 i32     4
 i64     8
 f32     4
 f64     8
 v128   16
```

Numeric stores use little-endian byte encoding, and `v128` occupies two consecutive little-endian 64-bit words. The collector resolves compact references through handle metadata to nursery/old/large/tiny backing storage.

Relevant source files:

- `wago-org/wago/src/core/runtime/gc/layout.go`
- `wago-org/wago/src/core/runtime/gc/desc.go`
- `wago-org/wago/src/core/runtime/gc/storage.go`
- `wago-org/wago/src/core/runtime/gc/alloc.go`

A Wago WPSI plugin can therefore implement pointer-free array access efficiently if it adds a scoped collector API that validates the array and prevents backing relocation for the duration of the host call.

### Wasmtime

Wasmtime's `GcArrayLayout` explicitly describes arrays as collector-specific headers followed by contiguous naturally aligned elements. Element offsets are computed from:

```text
base_size + index * elem_size
```

and storage sizes are 1, 2, 4, 8, and 16 bytes for the corresponding numeric/SIMD types.

Wasmtime's public `ArrayRef` interface is intentionally typed, while lower-level runtime code operates with `AutoAssertNoGc`, `GcArrayLayout`, and raw GC-heap offsets. A WPSI integration could build a scoped bulk-borrow primitive on those mechanisms without making layout public API.

Relevant source files:

- `bytecodealliance/wasmtime/crates/environ/src/gc.rs`
- `bytecodealliance/wasmtime/crates/wasmtime/src/runtime/vm/gc/enabled/arrayref.rs`
- `bytecodealliance/wasmtime/crates/wasmtime/src/runtime/gc/enabled/arrayref.rs`

### V8

V8's `WasmArray` stores a length in the object and computes array size as a header plus `element_size * length`, rounded to object alignment. Element addresses are computed as the array header offset plus `index * element_size`.

V8 supports element widths 1, 2, 4, 8, and 16 bytes in this representation.

Relevant source files:

- `v8/v8/src/wasm/wasm-objects.tq`
- `v8/v8/src/wasm/wasm-objects-inl.h`

A V8 implementation must still coordinate with the moving collector before handing an element address to an external synchronous operation.

### SpiderMonkey

SpiderMonkey's `WasmArrayObject` exposes an internal `data_` pointer to its element storage. Array indexing scales the index by the element storage size and addresses `data_ + offset`.

Numeric values, including `V128`, are written through the corresponding fixed-width native representation. SpiderMonkey also has explicit logic for keeping array backing/trailer storage coordinated with generational GC and object movement.

Relevant source area:

- `mozilla/gecko-dev/js/src/wasm/WasmGcObject.cpp`

## Partial element updates

For wide arrays, do not implement an unaligned byte range by blindly casting the beginning of the range to the element type.

If the runtime can expose the payload as bytes, the operation is naturally a byte-range update.

If it only exposes typed element operations, handle the first and last partial elements with read-modify-write and bulk-process complete elements in between.

Example for a portable `array<i32>` update:

```text
[first partial i32]
[complete i32 elements ...]
[last partial i32]
```

All integer encoding in the logical view is little-endian.

## Reference arrays

The raw `_array_i8/i16/i32/i64/v128` functions are only for pointer-free numeric arrays.

Do not treat reference-bearing arrays as raw byte buffers. Their slots may contain collector handles, compressed pointers, barriers, or other runtime-private representations.

Nested scatter/gather arrays are different: the outer array contains references and is traversed structurally, while each child is validated as one of the allowed pointer-free numeric array types.

For WPSI 0.1, validate the entire `first..first+count` child range before beginning host I/O, then expose each selected child's complete logical byte view in sequence. Do not invent or infer per-child slices. A short host transfer may finish inside the final child reached; bytes outside the transferred prefix remain untouched.

## GC barriers

Raw writes into pointer-free arrays require no reference write barrier.

The runtime must still satisfy collector invariants for object movement, pinning, incremental/concurrent collection, and object liveness.

## Capability table

A practical resource handle can be encoded as an index plus generation:

```text
handle = generation | slot
```

The exact bit allocation is runtime-private.

Lookup must validate:

- nonzero handle;
- slot bounds;
- generation match;
- resource kind when required;
- rights/capability set;
- instance ownership;
- open state.

## Optional `~` preopen

There is no scratch-specific runtime subsystem in WPSI.

If an embedder wants to provide a private or convenient guest home directory, expose it through the ordinary preopen table with the display name `~`. Do not allocate such storage when the embedding environment does not need it.

The backing implementation is ordinary filesystem policy: it may be a host directory, memory filesystem, temporary directory, overlay, persistent store, or another directory-capability implementation. The `~` name itself grants no rights and does not imply the host user's real home directory.

A libc or language runtime that supports `~/path` should resolve the `~` preopen once and then issue normal handle-relative WPSI path operations.

## Testing recommendations

Every representation family should test:

- zero-length operations;
- exact-end boundary operations;
- one-byte-out-of-bounds ranges;
- overflowing offset-plus-length;
- short reads/writes;
- EOF;
- invalid memory indexes;
- memory-address-width mismatch;
- GC element-type mismatch;
- immutable destination arrays;
- unaligned and partial-element GC byte ranges;
- forced moving collection around host calls;
- immediate memory growth/GC after return to catch retained guest borrows;
- stale handles and close races;
- capability and symlink escapes.
