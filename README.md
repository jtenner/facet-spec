# WPSI

**WPSI** is a small, Core-WebAssembly-native system interface designed for modern WebAssembly runtimes.

WPSI keeps the system ABI intentionally simple: ordinary imported functions from the `"wpsi"` module, explicit representation-specific function names, capability-oriented resource handles, first-class multi-memory support, Memory64 support, WebAssembly GC array buffers, UTF-8/UTF-16/UTF-32 text, and a private writable scratch filesystem for every filesystem-enabled instance.

WPSI is an experimental specification. The current draft is **WPSI 0.1**.

## Why WPSI?

Traditional Wasm system interfaces tend to assume that structured data ultimately passes through one distinguished linear memory. That model becomes awkward when a module uses multiple memories, Memory64, or WebAssembly GC objects as its native representation.

WPSI instead follows one rule:

> A system operation has one semantic meaning, but each materially different Core WebAssembly representation receives an explicit import name.

For example:

```text
wpsi.fd_read_mem32
wpsi.fd_read_mem64
wpsi.fd_read_array_i8
wpsi.fd_read_array_i16
wpsi.fd_read_array_i32
wpsi.fd_read_array_i64
wpsi.fd_read_array_v128
```

No polymorphic import resolver, canonical ABI, component model, or implicit memory 0 is required.

## Core properties

- **Multi-memory by construction.** Every linear-memory operation takes an explicit memory index.
- **Memory32 and Memory64.** Pointer width is part of the import name and signature.
- **WebAssembly GC arrays are valid I/O buffers.** Numeric arrays expose a normative logical byte view while implementations remain free to optimize contiguous native representations.
- **UTF-8, UTF-16, and UTF-32.** Text does not have to round-trip through UTF-8.
- **Capability-oriented resources.** Host filesystems and networking remain explicitly granted.
- **Private scratch filesystem.** Filesystem-enabled instances always have writable private storage even when no host directory is mounted.
- **Incremental runtime support.** A runtime can implement only the representation families it actually supports.

## Documents

- [`SPEC.md`](SPEC.md) — normative WPSI 0.1 specification.
- [`spec/imports.wat`](spec/imports.wat) — canonical Core Wasm import declarations.
- [`docs/design.md`](docs/design.md) — design rationale and non-goals.
- [`docs/runtime-implementation.md`](docs/runtime-implementation.md) — runtime implementation guidance, including GC array borrowing.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contribution and specification-change process.
- [`SECURITY.md`](SECURITY.md) — security model and vulnerability reporting guidance.

## Status

WPSI 0.1 is a draft intended for implementation experiments, conformance tests, and API review. Function signatures are expected to stabilize before a 1.0 release.

## License

WPSI is licensed under the [MIT License](LICENSE).
