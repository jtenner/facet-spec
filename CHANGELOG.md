# Changelog

All notable specification changes will be recorded here.

## Unreleased

### Added

- Initial WPSI 0.1 draft.
- Core imported-function ABI under module `wpsi`.
- Explicit Memory32 and Memory64 representation families.
- Explicit Wasm GC `array<i8>`, `array<i16>`, `array<i32>`, `array<i64>`, and `array<v128>` raw-buffer families.
- Normative logical byte view for numeric GC arrays, including partial-element byte ranges.
- Multi-memory-aware linear buffer and iovec representations.
- UTF-8, UTF-16, 32-bit code-point text, and WTF surrogate-sentinel semantics.
- Opaque resource handles and capability-oriented filesystem/network access.
- Conventional optional `~` preopen for embedders that want to expose a guest-home/private writable area using ordinary directory-capability semantics.
- Filesystem, links, sockets, DNS, clocks, randomness, and polling function families.
- Canonical WAT import declarations and runtime implementation guidance.
- Comprehensive initial conformance suite with 143 focused WAST tests, WASI-compatible host manifests, deterministic fixtures, generated catalog metadata, exact import-signature validation, and pinned `wasm-tools` parsing in CI.
- Normative `spec/behavior.md` defining validation precedence, error normalization, text transfer, path and symlink resolution, settled GC-array behavior, polling, and networking state semantics.

### Decided

- GC raw-buffer byte offsets and lengths are `i64`; runtimes bounds-check them against the actual GC array byte length.
- Validation failures use a deterministic order: scalar arguments, handles, resource state/authority, guest representation, ranges, text, namespace resolution, host operation, then host-error normalization.
- Error meanings follow WASI/POSIX categories where practical while keeping WPSI's own numeric namespace.
- Resource handle encoding is entirely runtime-private. Only `0` has a standardized numeric meaning; guests may not interpret nonzero handle bits or ranges, and stale handles may never alias unrelated live resources.
- Scratch-specific ABI functions and quota provisioning were removed. WPSI allocates no mandatory writable filesystem; `~` is only a conventional optional preopen display name and all storage semantics come from ordinary directory capabilities.
- Filesystem path resolution uses the WASI capability-beneath model: relative paths only, no temporary escape through `..`, and no absolute/rooted symlink escape.
- Wide GC arrays retain arbitrary partial-element byte ranges; GC inputs use `(ref array)` with dynamic storage validation; immutable source arrays are allowed.
- Nested GC `readv/writev` is whole-child only in WPSI 0.1. `first/count` select complete child arrays; per-child slice descriptors are intentionally omitted.
- Host-originated strings use source-specific length/copy APIs rather than string resource handles. GC callers may provide an existing array or request allocation of the concrete nullable array type declared by the import signature.
- Text APIs no longer use an `ENC_*` selector. Code-unit width is encoded in the import name (`i8`, `i16`, or `i32`) and a single `wtf` boolean selects strict Unicode versus reversible surrogate-sentinel semantics.
- Linear-memory textual imports include both memory address width and code-unit width, for example `path_open_mem32_i16` and `args_read_mem64_i8`.
- The old raw-8 string mode is removed. Non-Unicode host units are represented through WTF surrogate sentinels when lossless conversion is possible; WPSI does not silently substitute U+FFFD.
- Polling is level-triggered and snapshot-based; I/O errors/hangups are readiness events rather than poll-operation failures.
- Networking follows WASI-style socket state/error semantics adapted to synchronous WPSI calls; network authority remains embedder/instantiation policy rather than a guest-visible policy API.

### Deferred

- Async buffer ownership and cancellation semantics.
- Profile-specific version negotiation.
