# WPSI Roadmap

WPSI is currently an experimental 0.1 draft.

## Phase 0 — Specification hygiene

- [x] Define the flat `wpsi` import namespace.
- [x] Define explicit Memory32, Memory64, and GC-array representation families.
- [x] Define multi-memory addressing.
- [x] Define 8-bit, 16-bit, and 32-bit text representation families.
- [x] Define strict Unicode versus WTF surrogate-sentinel semantics with a single boolean.
- [x] Define ordinary filesystem preopens and the optional `~` guest-home convention without scratch-specific ABI functions.
- [x] Define canonical WAT import signatures.
- [x] Define deterministic validation and error precedence.
- [x] Keep resource-handle encoding entirely runtime-private while requiring stale-handle safety.
- [x] Define WASI-compatible error semantics and host-error normalization.
- [x] Define WASI-style capability-beneath path and symlink resolution.
- [x] Freeze WPSI 0.1 GC raw-buffer behavior: `i64` byte ranges, partial wide elements, abstract `(ref array)`, and immutable sources.
- [x] Freeze nested GC scatter/gather as whole-child only; `first/count` select child arrays and per-child slices are outside WPSI 0.1.
- [x] Define direct host-originated string transfer for linear memory, existing GC arrays, and caller-typed allocated GC arrays.
- [x] Define polling snapshot/readiness semantics.
- [x] Freeze WPSI 0.1 host calls as synchronous and forbid retaining borrowed guest storage across returns.
- [x] Define synchronous socket state and error semantics using WASI as the compatibility baseline.
- [x] Add a comprehensive WAST conformance suite and pinned syntax validation in CI.
- [x] Validate `spec/imports.wat` directly with pinned current Core Wasm tooling in CI.
- [ ] Add a machine-readable function/signature manifest independent of the test catalog.
- [ ] Resolve or explicitly defer the remaining questions in `docs/open-questions.md` before declaring the ABI stable.

## Phase 1 — Wago reference implementation

Implement WPSI as a Wago plugin.

Wago is the first implementation vehicle because it already has:

- Core Wasm 3.0 GC types;
- typed host-function boundaries;
- multi-memory and Memory64 support;
- explicit plugin host-import registration;
- a native GC with contiguous pointer-free numeric array storage.

Initial implementation order:

1. `wpsi-core`, including handles, errors, arguments/environment, clocks, and randomness.
2. `wpsi-memory32`.
3. `wpsi-filesystem` with ordinary preopens and handle-relative paths.
4. `wpsi-gc-array`, beginning with `array_i8` and then wider numeric/SIMD buffers.
5. `wpsi-memory64`.
6. `wpsi-poll`.
7. `wpsi-network`.
8. `wpsi-links`.

The plugin should use [`spec/behavior.md`](spec/behavior.md) as the behavioral contract and the conformance suite as the acceptance test.

A Wago implementation should add a scoped internal GC-array byte-borrow primitive rather than exposing collector backing addresses as persistent public API.

For textual imports, Wago should dispatch directly from the import-name representation (`i8`, `i16`, or `i32`) and treat `wtf` as a strict boolean semantic option rather than an encoding negotiation layer.

## Phase 2 — Conformance execution

The source conformance suite now exists. The remaining work is to execute it against real implementations.

- [x] Build portable Core Wasm/WAST fixtures for every current profile.
- [x] Add multi-memory and GC logical-byte-view tests.
- [x] Add capability-escape and stale-handle tests.
- [x] Add WASI-compatible JSON host manifests and deterministic fixtures.
- [ ] Connect the Wago plugin to the complete suite.
- [ ] Add forced moving-GC runtime tests.
- [ ] Add cross-representation differential execution against the Wago plugin.
- [ ] Publish a runtime conformance matrix.

## Phase 3 — Second-runtime prototype

Prototype the smallest useful subset in a second independent runtime, preferably Wasmtime or another runtime with mature Wasm GC support.

The goal is to discover assumptions accidentally inherited from Wago before stabilizing the ABI.

## Phase 4 — ABI stabilization

Before WPSI 1.0:

- freeze error-number semantics;
- freeze text/WTF semantics;
- freeze all core/filesystem import signatures;
- document extension/versioning rules;
- require two independent runtime implementations for stable profiles;
- require cross-runtime conformance for GC logical byte views;
- decide whether networking and links are 1.0 core profiles or remain extensions.

## Deferred / post-0.1 questions

The remaining questions in `docs/open-questions.md` are intentionally not blockers for beginning the Wago implementation. The remaining question is profile-specific version negotiation.

## Post-1.0 candidates

Potential independent extensions include:

- process spawning;
- threading/synchronization integrations;
- reference-typed host resource handles;
- HTTP/TLS profiles;
- structured GC-record operations where a clear portable use case exists.
