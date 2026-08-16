# WPSI Design Rationale

This document is informative. `SPEC.md` is normative.

## Why a flat imported-function ABI?

WPSI is deliberately smaller than a component model.

The system boundary already has a strong type system available: Core WebAssembly. For the operations WPSI targets, ordinary imports provide enough structure without introducing another interface language or canonical lowering format.

A minimal interface also makes runtime adoption easier. An embedder can implement WPSI using the same host-function machinery it already uses for other Core Wasm imports.

## Why not type-directed polymorphic imports?

Core Wasm permits repeated import names with different type descriptions, and an embedder could resolve `"wpsi"."fd_read"` based on the function type.

WPSI intentionally does not depend on that behavior.

Instead it uses names such as:

```text
fd_read_mem32
fd_read_mem64
fd_read_array_i8
fd_read_array_i16
fd_read_array_i32
fd_read_array_i64
fd_read_array_v128
```

This has a few useful properties:

- existing runtime import registries can remain keyed by module/name;
- missing representation support is visible as an ordinary missing import;
- stack traces and diagnostics show the selected ABI directly;
- runtimes can adopt GC and Memory64 support independently;
- no linker extension is required.

## Why an explicit memory index?

A pointer without a memory identity is insufficient once a module has multiple linear memories.

WPSI therefore treats:

```text
(memory_index, pointer, length)
```

as the basic linear-buffer reference.

There is no distinguished application memory and no privileged memory 0.

The same convention appears inside WPSI linear scatter/gather descriptors, allowing one `readv` or `writev` operation to span multiple memories.

## Why separate Memory32 and Memory64 imports?

The pointer width changes the Core Wasm signature. Encoding it in the import name avoids runtime flags, ambiguous integer interpretation, and accidental truncation.

A runtime can support either or both families.

## Why GC arrays?

Modern Wasm languages do not necessarily represent arrays in linear memory. Requiring every system operation to serialize a GC-native buffer through linear memory creates unnecessary copying and privileges one storage model.

WPSI therefore treats numeric Wasm GC arrays as direct I/O buffers.

The specification defines a portable **logical byte view** rather than a physical heap layout. Engines with contiguous storage can optimize this directly; engines with different layouts can implement the same observable semantics through temporary native storage.

## Why include i16, i32, i64, and v128 raw buffers?

Major Wasm GC implementations commonly represent numeric arrays as contiguous fixed-width storage. Wider arrays can therefore be useful native buffers, particularly for languages whose natural representation is not `array<i8>`.

WPSI's logical byte view also makes partial-element I/O well-defined. A byte range may begin or end inside an element; only the corresponding value bits change.

The initial raw-buffer set intentionally excludes `f32` and `f64`. They provide little systems-I/O benefit over same-width integer storage and would require additional care around floating-point representation and NaN payload expectations.

## Why UTF-16 and UTF-32?

A portable system interface should not require every language to convert its native text representation to UTF-8 merely to cross the host boundary.

WPSI supports UTF-8, UTF-16, and UTF-32 directly. WTF-8/WTF-16 and raw 8-bit system strings exist for host namespaces that cannot be losslessly modeled as Unicode scalar text.

## Why system-string handles?

Some strings originate on the host before the guest has selected a destination representation. Arguments, environment entries, directory entry names, preopen labels, and symlink targets are examples.

`sysstr` handles allow the guest to query a host-generated string and then copy it into Memory32, Memory64, `array<i8>`, `array<i16>`, or `array<i32>` without making one encoding globally privileged.

## Why a private scratch filesystem?

Capability security and useful filesystem semantics are not contradictory.

A WPSI filesystem implementation gives each instance authority over a private scratch namespace. That namespace contains no ambient authority over the host filesystem.

Real host directories remain explicit preopened capabilities.

This lets ordinary programs create temporary files without requiring the embedder to mount a real host directory simply to provide writable storage.

## Why opaque i32 resource handles?

Opaque numeric handles are simple, portable across current engines, and keep resource authority under embedder control.

WPSI does not require host objects to become `externref` or GC references. A future extension can explore reference-typed resource handles independently without changing the existing ABI.

## Why synchronous calls first?

WPSI 0.1 focuses on the smallest implementable system boundary. Synchronous calls also make scoped borrowing of moving-GC objects tractable: the runtime can root/pin or enter a no-move region for one host call and invalidate the backing view before return.

Asynchronous host operations need an explicit ownership and lifetime model and are intentionally deferred.

## Why not require zero-copy?

Zero-copy is an implementation property, not a portable semantic guarantee.

WPSI instead guarantees that a representation does not have to be translated through an unrelated guest memory. A runtime may use a direct native view, pinning, a no-GC scope, or a temporary native buffer depending on collector and operating-system constraints.

## Design rule for future additions

When adding a new operation, ask:

1. What is the semantic operation?
2. Which Core Wasm representations materially change its signature?
3. Can those representations receive explicit names?
4. Can the observable behavior be specified without depending on one runtime's private heap layout?
5. What capability does the operation consume or create?
6. Can a runtime that does not support the relevant Wasm feature simply omit the import?

If the answer to those questions stays simple, the operation likely fits WPSI.
