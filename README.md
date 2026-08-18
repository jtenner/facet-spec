# WPSI

WPSI is a small system interface for Core WebAssembly.

It lets a WebAssembly guest use system resources such as files, clocks, random data, sockets, and polling.

WPSI uses ordinary Core WebAssembly imports. It does not require a component model, a canonical ABI, or a special linker.

## The main idea

One system operation can use more than one guest representation.

For example, a file read can write into:

- Memory32;
- Memory64;
- a WebAssembly GC array.

Each representation has an explicit import name:

```text
wpsi.fd_read_mem32
wpsi.fd_read_mem64
wpsi.fd_read_array_i8
wpsi.fd_read_array_i16
wpsi.fd_read_array_i32
wpsi.fd_read_array_i64
wpsi.fd_read_array_v128
```

The guest chooses the representation by choosing the import.

There is no runtime polymorphic dispatch between these forms.

## Core properties

### Explicit memory selection

Every linear-memory operation identifies the memory that it uses.

Memory 0 has no special status.

### Memory32 and Memory64

The import name and Core WebAssembly signature identify the address width.

A `_mem32` facet uses an `i32` address.

A `_mem64` facet uses an `i64` address.

### WebAssembly GC arrays

A guest can use supported numeric GC arrays directly as I/O buffers.

The specification defines a portable **logical byte view** for these arrays.

The runtime does not have to expose its physical GC heap layout.

### Explicit text width

Text import names select one of these representations:

```text
_i8  = 8-bit code units
_i16 = 16-bit code units
_i32 = 32-bit code points
```

The `wtf` argument selects strict Unicode or reversible surrogate-sentinel behavior.

WPSI does not use an encoding enum.

### Capability-oriented resources

The embedder grants filesystem and network authority explicitly.

A resource cannot gain more authority than the capability from which it was derived.

### Synchronous call lifetime

Every WPSI imported function is synchronous.

The runtime MUST NOT retain a guest pointer, GC reference, or other borrowed guest storage after the function returns.

Nonblocking operations can return `ERR_AGAIN`.

A scheduler can then use `wpsi-poll` and retry the operation later.

Concurrency belongs outside the WPSI call boundary.

### No mandatory filesystem allocation

A filesystem implementation can expose zero preopens.

An embedder can provide a normal preopen named `~` when it wants to provide a guest home or private writable area.

The name `~` does not grant special authority and does not automatically refer to the host user's home directory.

### Import-driven feature detection

WPSI has one global ABI version.

Profiles do not have independent versions.

A module declares the imports that it needs.

Normal Core WebAssembly import and type matching determine whether the runtime can instantiate that module.

## Start here

Read these documents in this order if you are new to the project:

1. [`docs/terminology.md`](docs/terminology.md) — the terms used by the specification.
2. [`SPEC.md`](SPEC.md) — the normative ABI, constants, representations, and function signatures.
3. [`spec/behavior.md`](spec/behavior.md) — normative behavior, validation order, errors, path rules, polling, and networking.
4. [`docs/design.md`](docs/design.md) — why the ABI has this shape.
5. [`docs/runtime-implementation.md`](docs/runtime-implementation.md) — guidance for runtime implementers.

## Other documents

- [`spec/imports.wat`](spec/imports.wat) — canonical Core WebAssembly import declarations.
- [`spec/tests/README.md`](spec/tests/README.md) — conformance-suite and host-manifest contract.
- [`spec/tests/catalog.json`](spec/tests/catalog.json) — machine-readable conformance-test inventory.
- [`docs/writing-style.md`](docs/writing-style.md) — project rules for simple technical English.
- [`docs/open-questions.md`](docs/open-questions.md) — current ABI question status.
- [`ROADMAP.md`](ROADMAP.md) — implementation and stabilization roadmap.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contribution rules.
- [`SECURITY.md`](SECURITY.md) — security model and vulnerability reporting guidance.

## Conformance suite

The repository contains 143 focused WAST tests.

The suite covers:

- the Core import ABI;
- Memory32 and Memory64;
- multi-memory selection;
- GC arrays and nested GC arrays;
- strict and WTF text behavior;
- filesystem preopens, paths, and rights;
- hard links and symbolic links;
- polling;
- sockets and DNS;
- resource lifetime;
- adversarial bounds and capability cases.

The host-manifest format follows `WebAssembly/wasi-testsuite` conventions where those conventions fit the WPSI contract.

WPSI adds `preopens` provisioning for tests that need more than one explicit directory capability.

Static checks validate the catalog, manifests, fixtures, metadata, import signatures, and source hygiene.

CI also parses the canonical imports and every WAST source with a pinned `wasm-tools` release.

## Status

WPSI 0.1 is an experimental draft.

The first reference implementation is planned as a Wago plugin.

A second independent runtime prototype is planned before ABI stabilization.

## License

WPSI is licensed under the [MIT License](LICENSE).
