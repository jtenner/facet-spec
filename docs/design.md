# WPSI Design Rationale

This document explains why the specification has its current shape.

This document is informative.

`SPEC.md` and `spec/behavior.md` are normative.

Use [`terminology.md`](terminology.md) for the project terminology.

## Why a flat imported-function ABI?

WPSI uses ordinary Core WebAssembly imports.

Core WebAssembly already provides a strong type system at the system boundary.

For the operations in WPSI 0.1, ordinary imports provide enough structure.

WPSI therefore does not require:

- another interface language;
- a canonical lowering format;
- a component model;
- a special linker protocol.

This keeps runtime adoption small.

An embedder can implement WPSI with the same host-function mechanism that it already uses for other Core WebAssembly imports.

The caller-typed GC allocation functions are a narrow exception to ordinary abstract `(ref array)` parameters.

For those functions, import instantiation also validates the concrete result array type selected by the guest.

## Why not type-directed polymorphic imports?

Core WebAssembly can contain repeated import names with different function types.

An embedder could inspect the type and choose an implementation for a name such as `"facet"."fd_read"`.

WPSI does not depend on that behavior.

Instead, it uses explicit names:

```text
fd_read_mem32
fd_read_mem64
fd_read_array_i8
fd_read_array_i16
fd_read_array_i32
fd_read_array_i64
fd_read_array_v128
```

This choice has several benefits:

- a runtime can use a normal module-and-name import registry;
- missing representation support appears as a normal missing import;
- stack traces show the selected representation;
- diagnostics show the selected representation;
- a runtime can add GC support independently;
- a runtime can add Memory64 support independently;
- no linker extension is required.

The duplicated names are intentional.

They are cheaper than a second dynamic import-resolution system.

## Why no profile versions or feature-query API?

Core WebAssembly linking already answers the feature question.

A module declares the imports that it requires.

Each import includes its exact function type.

Instantiation succeeds only when the runtime can provide compatible imports.

A second feature registry would duplicate this information.

It could also disagree with the imports that the program actually needs.

WPSI therefore uses one coarse `abi_version()` for the overall ABI generation.

Import presence and type compatibility are authoritative for optional support.

Profile names remain useful for:

- documentation;
- implementation planning;
- conformance reporting.

Profiles are not independently negotiated runtime objects.

An additive change can introduce a new import without changing existing modules.

An incompatible form of one operation should normally receive a new import name.

Only an incompatible change to the overall WPSI ABI generation requires an `abi_version()` increment.

## Why an explicit memory index?

A pointer is not enough when one module has more than one linear memory.

The runtime must also know which memory owns that pointer.

WPSI therefore treats this tuple as the basic linear-memory buffer reference:

```text
(memory_index, pointer, length)
```

Memory 0 has no special status.

The same rule appears inside linear scatter/gather descriptors.

One `readv` or `writev` operation can therefore use more than one linear memory.

## Why separate Memory32 and Memory64 imports?

Memory32 and Memory64 use different Core WebAssembly pointer types.

That difference changes the function signature.

WPSI puts the address width in the import name.

This avoids:

- runtime pointer-width flags;
- ambiguous integer interpretation;
- accidental truncation.

A runtime can implement either family or both families.

## Why GC arrays?

A modern WebAssembly language does not have to store every array in linear memory.

If a language uses GC-native arrays, forcing system I/O through linear memory creates extra copies.

It also gives linear memory an unnecessary privileged role.

WPSI therefore lets supported numeric GC arrays act as direct I/O buffers.

The specification defines a **logical byte view** for portability.

The logical byte view defines observable values.

It does not expose the runtime's physical GC heap layout.

A runtime with contiguous numeric-array storage can use a direct fast path.

A runtime with another layout can use temporary native storage and produce the same observable result.

## Why include `i16`, `i32`, `i64`, and `v128` raw buffers?

Major WebAssembly GC implementations commonly store numeric arrays in fixed-width storage.

A wider numeric array can therefore be a useful native buffer for a language whose natural representation is not `array<i8>`.

The logical byte view makes partial-element I/O precise.

A byte range can begin inside an element.

A byte range can end inside an element.

Only the selected value bits change.

WPSI 0.1 does not include `f32` or `f64` raw-buffer facets.

Those types provide little systems-I/O benefit over integers of the same width.

They also introduce extra questions about floating-point representation and NaN payloads.

## Why are nested GC scatter/gather buffers whole-child only?

The outer GC array already provides a simple scatter/gather list.

Each selected child is one complete buffer.

Adding an offset and length for every child would require another descriptor representation.

Possible descriptor designs include GC structs or parallel arrays.

Each option adds complexity to an operation that is mainly an optimization.

WPSI 0.1 therefore keeps nested `readv` and `writev` structural.

`first` and `count` choose the child arrays.

Each selected child contributes its complete logical byte view.

The ordinary single-array functions already provide `byte_offset` and `byte_length` when one array needs a slice.

A future extension can add sliced scatter/gather under new import names if real workloads justify the extra ABI surface.

## Why UTF-16 and UTF-32?

A portable system interface should not require every language to convert native text to UTF-8 before it crosses the system boundary.

WPSI supports 8-bit, 16-bit, and 32-bit text representations directly.

The import name selects the representation width.

The `wtf` boolean selects strict Unicode or reversible surrogate-sentinel behavior.

This keeps physical representation separate from text semantics.

## Why no system-string handles?

Arguments, environment values, preopen labels, directory-entry names, and symbolic-link targets already have a source identity.

Creating a second resource handle only to move a string would add:

- allocation;
- handle lookup;
- lifetime rules;
- close operations.

It would not add authority.

WPSI therefore transfers these strings directly from their source operation.

A linear-memory caller can query the required code-unit length and provide destination storage.

A GC caller can provide an existing mutable array.

A GC caller can also request a fresh caller-typed array from an allocating string function.

For an allocating GC result, the module's import signature contains the concrete nullable array result type.

The runtime validates the requested storage class during instantiation.

The runtime then allocates exactly that concrete GC type.

This asymmetry is intentional.

Linear memory naturally uses guest-owned addresses.

WebAssembly GC naturally supports returned references to newly allocated objects.

## Why is `~` an ordinary preopen instead of a special scratch API?

WPSI already has the required mechanism: directory capabilities and preopens.

A separate scratch-resource class would add:

- new imports;
- quota APIs;
- lifetime rules;
- implementation machinery.

It would not add a new authority model.

An embedder that wants to provide a convenient guest home can expose a normal preopen with display name `~`.

A higher-level binding can map `~/foo` to that directory handle and the relative path `foo`.

The name itself has no special authority.

The preopen can be:

- temporary;
- persistent;
- memory-backed;
- directory-backed;
- read-only;
- writable;
- quota-limited;
- absent.

The embedder decides these properties.

The name `~` does not mean the operating-system user's home directory unless the embedder explicitly grants that directory.

This design also lets constrained runtimes avoid allocating storage they do not need.

## Why opaque `i32` resource handles?

Opaque numeric handles are simple Core WebAssembly values.

They keep resource authority under runtime and embedder control.

Only `0` has a standardized numeric meaning.

WPSI does not standardize:

- resource-kind tags;
- reserved handle ranges;
- table-index fields;
- generation fields;
- ordering guarantees.

A runtime can use any private strategy that prevents a stale handle from identifying an unrelated live resource.

Examples include generation counters, monotonic IDs, randomized values, and delayed reuse.

Bindings only need to preserve the `i32` token and pass it back to WPSI.

WPSI also does not require an external resource to become an `externref` or GC reference.

A future extension can explore reference-typed resource handles independently.

## Why are WPSI calls synchronous?

WPSI makes synchronous call lifetime a core ABI rule.

This keeps guest-storage ownership local and understandable.

For one call, the runtime can:

1. validate the guest storage;
2. root or pin a GC object when necessary;
3. stabilize linear memory when necessary;
4. perform the operation;
5. invalidate the borrowed view;
6. return.

No guest pointer, GC reference, or borrowed backing address remains live in deferred runtime work after the call returns.

Nonblocking I/O still works with concurrency.

An operation can return `ERR_AGAIN`.

A scheduler can run other work while it waits with `wpsi-poll`.

The scheduler can retry the operation when the resource is ready.

This model works well with:

- actor schedulers;
- event loops;
- green threads;
- multiple WebAssembly instances.

WPSI does not standardize any of those execution models.

A future specification that adds true asynchronous imported calls would need a separate ownership model.

That would be an explicit extension to the WPSI 0.1 lifetime rule.

## Why not require zero-copy?

Zero-copy execution is an implementation property.

It is not a portable semantic guarantee.

WPSI guarantees that the guest does not have to translate data through unrelated linear memory only to cross the ABI.

A runtime can use:

- a direct native view;
- pinning;
- a no-GC scope;
- a temporary native buffer.

The runtime chooses the safe implementation for its collector and operating-system APIs.

## Design rule for future additions

Before adding an operation, answer these questions:

1. What semantic system operation does the import provide?
2. Which Core WebAssembly representations change the function signature?
3. Can those representations use explicit import names?
4. Can the specification define observable behavior without exposing a runtime's private heap layout?
5. What capability does the operation consume or create?
6. Can a runtime omit the import when it does not support the required WebAssembly feature?

If the answers remain simple, the operation probably fits WPSI.

## Why a WTF boolean instead of an encoding enum?

The code-unit width changes the physical ABI.

It therefore belongs in the import name.

Strict Unicode versus WTF semantics do not change the Core WebAssembly signature.

They therefore use one boolean parameter.

The rule is:

```text
physical representation -> import name
strict vs sentinel text  -> wtf boolean
```

`wtf = 0` requires Unicode scalar text.

`wtf = 1` permits surrogate values as reversible sentinels.

WPSI does not need an `ENC_*` namespace or a separate raw-8 string mode.
