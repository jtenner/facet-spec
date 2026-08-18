# WPSI Roadmap

WPSI is an experimental 0.1 draft.

## Phase 0 — Specification hygiene

- [x] Define the flat `facet` import namespace.
- [x] Define explicit Memory32, Memory64, and GC-array representation families.
- [x] Define multi-memory addressing.
- [x] Define 8-bit, 16-bit, and 32-bit text representation families.
- [x] Define strict Unicode and WTF surrogate-sentinel semantics with one boolean.
- [x] Define ordinary filesystem preopens and the optional `~` convention.
- [x] Remove scratch-specific ABI functions.
- [x] Define canonical WAT import signatures.
- [x] Define deterministic validation and error precedence.
- [x] Keep resource-handle encoding runtime-private.
- [x] Require stale-handle safety.
- [x] Define WASI-compatible error categories where practical.
- [x] Define capability-beneath path and symbolic-link resolution.
- [x] Freeze WPSI 0.1 GC raw-buffer behavior.
- [x] Support `i64` GC byte ranges and partial wide elements.
- [x] Use abstract `(ref array)` parameters for raw GC buffers.
- [x] Permit immutable GC source arrays.
- [x] Freeze nested GC scatter/gather as whole-child only.
- [x] Define direct string transfer for linear memory and existing GC arrays.
- [x] Define caller-typed allocated GC string results.
- [x] Define polling snapshot and readiness semantics.
- [x] Freeze WPSI 0.1 imported calls as synchronous.
- [x] Forbid retained guest-storage borrows after return.
- [x] Define one global ABI version.
- [x] Make import and type matching authoritative for feature detection.
- [x] Define synchronous socket state and error semantics.
- [x] Add a comprehensive WAST conformance suite.
- [x] Pin syntax validation in CI.
- [x] Parse `spec/imports.wat` directly in CI.
- [x] Resolve the WPSI 0.1 ABI questions tracked in `docs/open-questions.md`.
- [x] Add a controlled project glossary.
- [x] Add a simple-technical-English writing guide.
- [x] Rewrite human-facing normative and implementation documentation for accessibility without changing ABI behavior.
- [ ] Add a machine-readable function and signature manifest that is independent of the test catalog.

## Phase 1 — Wago reference implementation

Implement WPSI as a Wago plugin.

Wago is the first implementation vehicle because it already supports:

- Core Wasm 3.0 GC types;
- typed imported-function boundaries;
- multi-memory;
- Memory64;
- explicit plugin import registration;
- a native GC with contiguous pointer-free numeric array storage.

Implement profiles in this order:

1. `wpsi-core`;
2. `wpsi-memory32`;
3. `wpsi-filesystem`;
4. `wpsi-gc-array`;
5. `wpsi-memory64`;
6. `wpsi-poll`;
7. `wpsi-network`;
8. `wpsi-links`.

The Wago implementation should use [`spec/behavior.md`](spec/behavior.md) as its behavioral contract.

It should use the conformance suite as its acceptance test.

The GC implementation should add a scoped internal byte-borrow primitive for numeric GC arrays.

It should not expose persistent collector backing addresses as public API.

Text imports should dispatch from the representation named by the import.

The runtime should treat `wtf` as a strict boolean semantic option.

## Phase 2 — Conformance execution

The source conformance suite exists.

The next goal is to execute it against real runtimes.

- [x] Build portable Core Wasm and WAST fixtures for every current profile.
- [x] Add multi-memory tests.
- [x] Add GC logical-byte-view tests.
- [x] Add capability-escape tests.
- [x] Add stale-handle tests.
- [x] Add compatible JSON harness manifests and deterministic fixtures.
- [ ] Connect the Wago plugin to the complete suite.
- [ ] Add forced moving-GC runtime tests.
- [ ] Add cross-representation differential execution against the Wago plugin.
- [ ] Publish a runtime conformance matrix.

## Phase 3 — Second runtime prototype

Prototype the smallest useful subset in a second independent runtime.

Wasmtime or another runtime with mature Wasm GC support is a good candidate.

The purpose is to find assumptions that accidentally depend on Wago before ABI stabilization.

## Phase 4 — ABI stabilization

Before WPSI 1.0:

- freeze error-number semantics;
- freeze text and WTF semantics;
- freeze all core and filesystem import signatures;
- document extension and versioning rules;
- require two independent runtime implementations for stable profiles;
- require cross-runtime conformance for GC logical byte views;
- decide whether networking and links are 1.0 core profiles or extensions.

## Open ABI questions

There are currently no unresolved WPSI 0.1 ABI design questions.

Implementation work can still expose specification defects.

The second runtime prototype can also expose specification defects.

Any new incompatibility must be proposed as an explicit specification change before 1.0.

## Post-1.0 candidates

Possible independent extensions include:

- process spawning;
- threading and synchronization integrations;
- reference-typed resource handles;
- HTTP and TLS profiles;
- structured GC-record operations when a clear portable use case exists.
