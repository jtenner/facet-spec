# WPSI Roadmap

WPSI is currently an experimental 0.1 draft.

## Phase 0 — Specification hygiene

- [x] Define the flat `wpsi` import namespace.
- [x] Define explicit Memory32, Memory64, and GC-array representation families.
- [x] Define multi-memory addressing.
- [x] Define UTF-8, UTF-16, and UTF-32 text representations.
- [x] Define private scratch filesystem semantics.
- [x] Define canonical WAT import signatures.
- [ ] Validate every WAT declaration with current Core Wasm tooling.
- [ ] Add a machine-readable function/signature manifest.
- [ ] Resolve the open questions in `docs/open-questions.md`.

## Phase 1 — Wago reference implementation

Use Wago as the first implementation vehicle because it already has:

- Core Wasm 3.0 GC types;
- typed host-function boundaries;
- multi-memory and Memory64 support;
- explicit plugin host-import registration;
- a native GC with contiguous pointer-free numeric array storage.

Initial implementation order:

1. `wpsi-core`.
2. `wpsi-memory32`.
3. `wpsi-filesystem` with private scratch storage.
4. `wpsi-gc-array`, beginning with `array_i8` and then wider numeric/SIMD buffers.
5. `wpsi-memory64`.
6. `wpsi-poll`.
7. `wpsi-network`.
8. `wpsi-links`.

A Wago implementation should add a scoped internal GC-array byte-borrow primitive rather than exposing collector backing addresses as persistent public API.

## Phase 2 — Conformance suite

- Build portable Core Wasm fixtures for every profile.
- Add cross-representation byte-oracle tests.
- Add multi-memory differential tests.
- Add forced moving-GC tests.
- Add capability-escape tests.
- Publish a runtime conformance matrix.

## Phase 3 — Second-runtime prototype

Prototype the smallest useful subset in a second independent runtime, preferably Wasmtime or another runtime with mature Wasm GC support.

The goal is to discover assumptions accidentally inherited from Wago before stabilizing the ABI.

## Phase 4 — ABI stabilization

Before WPSI 1.0:

- freeze error-number semantics;
- freeze encoding semantics;
- freeze all core/filesystem import signatures;
- document extension/versioning rules;
- require two independent runtime implementations for stable profiles;
- require cross-runtime conformance for GC logical byte views;
- decide whether networking and links are 1.0 core profiles or remain extensions.

## Post-1.0 candidates

Potential independent extensions include:

- process spawning;
- asynchronous operations with explicit buffer ownership;
- threading/synchronization integrations;
- reference-typed host resource handles;
- HTTP/TLS profiles;
- structured GC-record operations where a clear portable use case exists.
