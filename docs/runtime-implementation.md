# Runtime Implementation Guidance

This document is informative.

`SPEC.md` and `spec/behavior.md` define observable behavior.

Use [`terminology.md`](terminology.md) for the project terminology.

## Import registration

Facet functions are ordinary imports from module `facet`.

A runtime does not need polymorphic import resolution.

A runtime can register only the imports for features that it supports.

For example, a runtime without Wasm GC can implement:

```text
facet-core
facet-memory32
facet-filesystem
```

A runtime with more Core WebAssembly features can also implement:

```text
facet-memory64
facet-gc-array
facet-network
facet-poll
```

Do not build a second feature-negotiation registry for Facet.

Do not build independent profile-version negotiation.

Register the imports that the runtime implements.

Let normal Core WebAssembly import and type matching determine whether a module can instantiate.

`abi_version()` is the only global ABI generation number.

Profile labels are implementation and conformance groupings only.

## Synchronous call boundary

Treat the return from every Facet imported function as a hard lifetime boundary.

After return, no deferred runtime work may retain:

- a guest linear-memory view;
- a guest GC reference borrowed for the call;
- a raw GC payload pointer;
- a pin;
- a root used only for the call;
- a no-move token;
- another borrowed guest-storage view.

If an external API requires data after the Facet call returns, copy the data into independent runtime-owned storage.

For nonblocking I/O, prefer an operation that returns `ERR_AGAIN` and is retried after polling.

Do not start background work that will later dereference a guest pointer or borrowed GC reference.

The runtime MAY retain Facet resource state and independent runtime-owned metadata.

This restriction applies to each call.

It does not prohibit concurrent WebAssembly execution.

A runtime can execute multiple instances, actors, tasks, or scheduler contexts concurrently.

Each Facet call must still obey the same lifetime boundary.

## Linear-memory access

For every `_mem32` or `_mem64` call:

1. resolve the calling instance;
2. validate `memory_index` against that instance's memory index space;
3. validate the selected memory's address width;
4. check pointer and length arithmetic for overflow;
5. bounds-check the range against the current memory size;
6. keep the memory backing stable for the synchronous operation;
7. perform the operation directly on the selected memory when this is safe.

Do not give memory 0 special treatment.

## Text representation

The import name selects text width.

Dispatch `*_i8`, `*_i16`, and `*_i32` directly to the corresponding code-unit path.

Do not decode a text-width enum on each call.

The `wtf` argument is a strict boolean.

Validate it before the runtime modifies guest storage or resolves an external text namespace.

```text
wtf = 0 -> strict Unicode scalar text
wtf = 1 -> permit surrogate sentinel values
```

For a byte-oriented external namespace, a practical reversible mapping for invalid UTF-8 bytes is `U+DC80..U+DCFF`.

For a UTF-16 external namespace, preserve unpaired surrogate code units directly.

Do not substitute U+FFFD when the specification requires lossless transfer.

Return `ERR_ILLEGAL_SEQUENCE` when the selected mode cannot represent the external value.

For linear memory, `_i16` and `_i32` code units use little-endian byte order.

The pointer is a byte address.

Lengths and capacities are code-unit counts.

## GC array access

A useful internal runtime primitive is:

```text
with_array_bytes(reference, expected_element_type, access_mode, callback)
```

A conceptual implementation should:

1. validate the array reference;
2. validate the dynamic storage type;
3. validate destination mutability when required;
4. validate the logical byte range;
5. keep the reference alive;
6. establish a pin, no-move scope, or no-GC scope when required;
7. resolve the current backing storage;
8. call the operation with a temporary byte view;
9. invalidate the temporary byte view;
10. leave the collector scope.

The callback must not retain the native address or byte view.

### Direct fast path

If the runtime stores pointer-free numeric arrays contiguously, the logical byte view can map directly to the array payload.

The runtime must still keep the object stable for the complete synchronous call.

This can let an operating-system `read` write directly into the GC array.

### Portable fallback

A runtime can use temporary native storage when its GC layout is not suitable for direct access.

For a read:

```text
external read -> temporary bytes -> logical-byte-view update
```

For a write:

```text
logical-byte-view extraction -> temporary bytes -> external write
```

This is conforming when the observable result matches the specification.

The fallback must preserve partial-element behavior.

## Runtime-allocated GC string results

Allocating string imports such as `args_read_array_i16` use the concrete nullable array result type declared by the importing module.

At import instantiation:

1. inspect the requested function result type;
2. require a concrete array heap type with the storage class named by the import;
3. retain the runtime type identity in the imported-function implementation.

At call time:

1. encode the complete source string;
2. allocate exactly the requested array type at the exact required length;
3. initialize every element;
4. return the non-null reference with `ERR_OK`.

If allocation fails, return `null` with `ERR_NO_MEMORY`.

The result array can be mutable or immutable.

This path allocates a new object.

It does not borrow an existing GC array.

Guest-owned `*_read_into_array_*` destinations still require normal validation and mutable storage.

## Current runtime layout observations

The observations in this section explain why the Facet 0.1 GC-array design can be efficient.

They are not normative requirements.

### Wago

Wago stores GC objects in byte heaps with a 16-byte object header.

Array size is computed as:

```text
header + element_size * length
```

The final object is aligned as required by the collector.

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

Numeric stores use little-endian byte encoding.

A `v128` value occupies two consecutive little-endian 64-bit words.

The collector resolves compact references through handle metadata to nursery, old, large, or tiny backing storage.

Relevant source files:

- `wago-org/wago/src/core/runtime/gc/layout.go`
- `wago-org/wago/src/core/runtime/gc/desc.go`
- `wago-org/wago/src/core/runtime/gc/storage.go`
- `wago-org/wago/src/core/runtime/gc/alloc.go`

A Wago Facet plugin can implement pointer-free array access efficiently.

It should add a scoped collector API that validates the array and prevents unsafe relocation for the duration of the call.

### Wasmtime

Wasmtime's `GcArrayLayout` describes collector-specific headers followed by contiguous naturally aligned elements.

Element offsets use this form:

```text
base_size + index * elem_size
```

The relevant numeric and SIMD storage sizes are 1, 2, 4, 8, and 16 bytes.

Wasmtime's public `ArrayRef` interface is typed.

Lower-level runtime code uses `AutoAssertNoGc`, `GcArrayLayout`, and raw GC-heap offsets.

A Facet integration could build a scoped byte-borrow primitive on those internal mechanisms.

It should not expose collector layout as public Facet API.

Relevant source files:

- `bytecodealliance/wasmtime/crates/environ/src/gc.rs`
- `bytecodealliance/wasmtime/crates/wasmtime/src/runtime/vm/gc/enabled/arrayref.rs`
- `bytecodealliance/wasmtime/crates/wasmtime/src/runtime/gc/enabled/arrayref.rs`

### V8

V8's `WasmArray` stores a length in the object.

It computes array size from a header plus `element_size * length`, rounded to object alignment.

An element address is the array payload base plus `index * element_size`.

V8 supports element widths of 1, 2, 4, 8, and 16 bytes in this representation.

Relevant source files:

- `v8/v8/src/wasm/wasm-objects.tq`
- `v8/v8/src/wasm/wasm-objects-inl.h`

A V8 implementation must still coordinate with the moving collector before it gives an element address to an external synchronous operation.

### SpiderMonkey

SpiderMonkey's `WasmArrayObject` has an internal `data_` pointer for element storage.

Array indexing scales the index by the element storage size.

Numeric values, including `V128`, use their corresponding fixed-width native representation.

SpiderMonkey also contains logic that coordinates array backing storage with generational GC and object movement.

Relevant source area:

- `mozilla/gecko-dev/js/src/wasm/WasmGcObject.cpp`

## Partial-element updates

Do not implement an unaligned byte range by casting the beginning of the range to the array element type.

If the runtime can expose the payload as bytes, update the selected byte range directly.

If the runtime can access only typed elements, use read-modify-write for partial elements.

A portable `array<i32>` update has this shape:

```text
[first partial i32]
[complete i32 elements ...]
[last partial i32]
```

Process complete elements in bulk when practical.

All integer encoding in the logical byte view is little-endian.

## Reference arrays

The raw `_array_i8`, `_array_i16`, `_array_i32`, `_array_i64`, and `_array_v128` functions are only for pointer-free numeric arrays.

Do not treat a reference-bearing array as a raw byte buffer.

A reference slot can contain runtime-private data such as:

- collector handles;
- compressed pointers;
- write-barrier state;
- other private representations.

Nested scatter/gather arrays are different.

The outer array contains references and is traversed structurally.

Each selected child is then validated as one of the allowed pointer-free numeric array types.

For Facet 0.1:

1. validate the complete `first..first+count` child range before external I/O;
2. expose each selected child's complete logical byte view in sequence;
3. do not infer a per-child slice.

A short external transfer can stop inside the final child reached.

Bytes after the transferred prefix remain unchanged.

## GC barriers

Raw writes into pointer-free arrays do not require a reference write barrier.

The runtime must still preserve collector invariants for:

- object movement;
- pinning;
- incremental collection;
- concurrent collection;
- object liveness.

## Capability table

One practical private handle encoding is an index plus a generation value:

```text
handle = generation | slot
```

The exact bit allocation is runtime-private.

Handle lookup should validate:

- a nonzero handle;
- slot bounds;
- generation match;
- resource kind when required;
- rights and capability set;
- instance ownership;
- open state.

Other private handle encodings are also conforming when they preserve the normative handle rules.

## Optional `~` preopen

Facet has no scratch-specific runtime subsystem.

If the embedder wants to provide a guest home or private directory, expose it as an ordinary preopen with display name `~`.

Do not allocate this storage when the embedding environment does not need it.

The backing storage is ordinary filesystem policy.

It can be:

- an operating-system directory;
- a memory filesystem;
- a temporary directory;
- an overlay;
- a persistent store;
- another directory-capability implementation.

The display name `~` grants no rights by itself.

It does not imply the operating-system user's home directory.

A libc or language runtime that supports `~/path` can resolve the `~` preopen once.

It can then issue normal handle-relative Facet path operations.

## Testing recommendations

Every representation family should test:

- zero-length operations;
- exact-end boundary operations;
- a range that is one byte out of bounds;
- offset-plus-length overflow;
- short reads and writes;
- EOF;
- invalid memory indexes;
- memory-address-width mismatch;
- GC element-type mismatch;
- immutable destination arrays;
- unaligned and partial-element GC byte ranges;
- forced moving collection around imported calls;
- immediate memory growth or GC after return, to detect retained guest borrows;
- stale handles;
- close races;
- capability escapes;
- symbolic-link escapes.
