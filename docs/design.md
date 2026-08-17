# WPSI Design Rationale

This document is informative. `SPEC.md` is normative.

## Why a flat imported-function ABI?

WPSI is deliberately smaller than a component model.

The system boundary already has a strong type system available: Core WebAssembly. For the operations WPSI targets, ordinary imports provide enough structure without introducing another interface language or canonical lowering format. Host-allocated GC string results are a narrow exception where import instantiation also validates the caller-selected concrete array result type.

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

## Why no profile versions or feature-query API?

Core Wasm linking already answers the feature question precisely: a module declares the imports it requires, including their exact function types, and instantiation succeeds only when the runtime can provide them.

Adding `filesystem_version()`, `gc_array_version()`, profile manifests, or a scalar feature-query API would duplicate that mechanism and create a second source of truth that could disagree with the imports actually needed by the program.

WPSI therefore keeps one coarse `abi_version()` for the overall ABI generation and treats import presence plus type compatibility as authoritative for optional capability support. Profile names remain useful for documentation, implementation planning, and conformance reporting, but they are not independently negotiated runtime entities.

Additive evolution can introduce new imports without disturbing existing modules. A genuinely incompatible form of one operation should normally receive a new import name; only an incompatible change to the overall WPSI ABI generation requires incrementing `abi_version()`.

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

## Why are nested GC scatter/gather buffers whole-child only?

The outer GC array already provides a simple scatter/gather list: each selected child is one complete buffer. Adding an offset and length for every child would require another portable descriptor representation, such as GC structs or parallel arrays, and would substantially complicate an operation that is primarily an optimization.

WPSI 0.1 therefore keeps nested `readv/writev` structural: `first` and `count` choose child arrays, and each child contributes its entire logical byte view. The ordinary single-array I/O functions already provide `byte_offset` and `byte_length` when a caller needs a slice of one array.

A future extension may add sliced scatter/gather under new import names if real compiler/runtime workloads demonstrate that the additional ABI surface is worthwhile.

## Why UTF-16 and UTF-32?

A portable system interface should not require every language to convert its native text representation to UTF-8 merely to cross the host boundary.

WPSI supports 8-bit, 16-bit, and 32-bit text representations directly. The representation width is part of the import name rather than an encoding enum. A single `wtf` boolean selects strict Unicode or surrogate-sentinel mode, so host namespaces with non-Unicode units can be preserved without a separate raw-string encoding value.

## Why no system-string handles?

Strings such as arguments, environment values, preopen labels, directory-entry names, and symbolic-link targets already have a natural source identity. Creating another resource handle solely to move those strings adds allocation, lookup, lifetime, and close operations without adding authority.

WPSI therefore lets the source operation expose the string directly.

Linear-memory callers query the width-specific code-unit length when necessary and provide `(memory, pointer, capacity)` storage. GC callers may either provide an existing mutable array with `*_read_into_array_*` or use `*_read_array_*` to ask the runtime to allocate a fresh result.

For allocating GC results, the concrete nullable array result type appears in the module's import signature. The runtime validates the requested storage class and allocates exactly that Wasm GC type. This lets a language receive its native `array<i8>`, `array<i16>`, or `array<i32>` representation without a temporary string resource or linear-memory lowering.

This asymmetry is intentional: linear memory naturally uses caller-owned addresses, while Wasm GC can naturally return newly allocated references.

## Why is `~` an ordinary preopen instead of a special scratch API?

WPSI already has the primitive it needs: directory capabilities and preopens. A second resource class for temporary or private storage would add imports, quota APIs, lifetime rules, and implementation machinery without adding new authority semantics.

An embedder that wants to give a guest a convenient writable home can therefore expose a normal preopen with the display name `~`. Higher-level bindings may map `~/foo` to that directory handle plus the relative path `foo`.

Nothing about the name is magical. The preopen may be temporary, persistent, memory-backed, host-directory-backed, read-only, writable, quota-limited, or absent, according to the authority and policy the embedder explicitly supplies. In particular, `~` never means the host user's home directory unless the embedder deliberately grants that directory as a capability.

This keeps constrained runtimes free from allocating storage they do not need and keeps all filesystem authority on one mechanism.

## Why opaque i32 resource handles?

Opaque numeric handles are simple, portable across current engines, and keep resource authority under embedder control.

`Opaque` is intentional and complete: WPSI assigns no meaning to the bits of a nonzero handle. There are no standardized resource-kind tags, reserved ranges, table-index fields, generation fields, or ordering guarantees. A runtime may use generation counters, monotonically increasing IDs, randomized values, delayed reuse, or another representation as long as stale handles cannot alias unrelated live resources.

Keeping the encoding private avoids constraining runtime handle tables and prevents language bindings from accidentally depending on one implementation's bookkeeping. Bindings need only preserve the `i32` token and pass it back to WPSI.

WPSI does not require host objects to become `externref` or GC references. A future extension can explore reference-typed resource handles independently without changing the existing ABI.

## Why are WPSI calls synchronous?

WPSI deliberately makes synchronous call lifetime a core ABI invariant rather than defining futures or retained-buffer asynchronous host operations.

This keeps guest-storage ownership local and tractable. A runtime can root or pin a Wasm GC object, stabilize linear memory, perform one host operation, invalidate the borrowed view, and return. No guest pointer, GC reference, or borrowed backing address remains live in host code after the call boundary.

Nonblocking I/O still composes with concurrency: an operation can return `ERR_AGAIN`, a scheduler can wait through `wpsi-poll`, run other work, and retry when the resource becomes ready.

This model is intentionally friendly to actor-style, event-loop, green-thread, and multi-instance scheduling without standardizing any of those execution models. WPSI defines neither actors nor a scheduler; it only guarantees that each system call has a bounded synchronous dynamic extent.

A future specification that introduces true asynchronous host calls would need a separate ownership model and would be an explicit extension to this invariant, not an implied part of WPSI 0.1.

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

## Why a WTF boolean instead of an encoding enum?

The code-unit width changes the physical ABI and therefore belongs in the import name. UTF versus WTF semantics do not change the Core Wasm signature, so they are represented by one boolean.

This keeps the rule simple:

```text
physical representation -> import name
strict vs sentinel text  -> wtf boolean
```

`wtf = 0` requires Unicode scalar text. `wtf = 1` permits surrogate values as reversible sentinels. WPSI does not need an `ENC_*` namespace or a separate raw-8 string mode.
