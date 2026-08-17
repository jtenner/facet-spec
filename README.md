# WPSI

**WPSI** is a small, Core-WebAssembly-native system interface designed for modern WebAssembly runtimes.

WPSI keeps the system ABI intentionally simple: ordinary imported functions from the `"wpsi"` module, explicit representation-specific function names, capability-oriented resource handles, first-class multi-memory support, Memory64 support, WebAssembly GC array buffers, 8/16/32-bit text representations with optional WTF sentinel preservation, and capability-oriented filesystem preopens, including an optional conventional `~` guest-home preopen.

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
- **Text width is explicit.** Textual import names select 8-bit, 16-bit, or 32-bit code units. A single `wtf` boolean selects strict Unicode or reversible surrogate-sentinel handling; there is no encoding enum.
- **Natural host-to-guest strings.** Host-originated strings can write directly into linear memory or existing GC arrays, or allocate the caller's concrete GC array type.
- **Capability-oriented resources.** Host filesystems and networking remain explicitly granted.
- **No mandatory filesystem allocation.** Embedders may expose ordinary directory preopens as needed; `~` is the conventional optional guest-home/private-area name and has no special ABI semantics.
- **Incremental runtime support.** A runtime can implement only the representation families it actually supports.
- **Compatibility-first behavior.** Error classes, path resolution, polling, and socket state semantics intentionally track WASI where the models overlap.

## Documents

- [`SPEC.md`](SPEC.md) — normative WPSI 0.1 ABI, representations, constants, and function signatures.
- [`spec/behavior.md`](spec/behavior.md) — normative validation order, errors, text transfer, path resolution, GC rules, polling, and networking semantics.
- [`spec/imports.wat`](spec/imports.wat) — canonical Core Wasm import declarations.
- [`spec/tests/README.md`](spec/tests/README.md) — normative conformance-suite and host-manifest contract.
- [`spec/tests/catalog.json`](spec/tests/catalog.json) — machine-readable inventory of conformance tests and required profiles.
- [`docs/design.md`](docs/design.md) — design rationale and non-goals.
- [`docs/runtime-implementation.md`](docs/runtime-implementation.md) — runtime implementation guidance, including GC array borrowing.
- [`docs/open-questions.md`](docs/open-questions.md) — intentionally deferred decisions.
- [`ROADMAP.md`](ROADMAP.md) — implementation and stabilization roadmap.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contribution and specification-change process.
- [`SECURITY.md`](SECURITY.md) — security model and vulnerability reporting guidance.

## Conformance suite

The repository includes **143 focused WAST tests** covering the Core import ABI, Memory32, Memory64, multi-memory selection, GC arrays and nested arrays, strict/WTF text handling, preopen conventions, filesystem rights, links, polling, sockets, DNS, lifecycle, and adversarial bounds behavior.

The suite deliberately mirrors `WebAssembly/wasi-testsuite` host-manifest conventions—same-basename JSON, `run`, `wait`, `read`, `connect`, `send`, `recv`, `root`, fixtures, and `.cleanup` artifacts—so existing runtime adapters can be extended instead of replaced. WPSI adds only the `preopens` provisioning needed for explicit multi-directory capability tests.

Static checks validate catalog generation, manifests, fixture paths, metadata, exact WPSI import signatures, and source hygiene. CI also parses the canonical import module and every WAST script with a pinned `wasm-tools` release.

## Status

WPSI 0.1 is a draft intended for implementation experiments, conformance tests, and API review. Function signatures are expected to stabilize before a 1.0 release.

The planned first reference implementation is a **Wago plugin**, followed by a second independent runtime prototype before ABI stabilization.

## License

WPSI is licensed under the [MIT License](LICENSE).
