# Changelog

This file records notable specification changes.

## Unreleased

### Added

- Initial WPSI 0.1 draft.
- Core imported-function ABI under module `facet`.
- Explicit Memory32 and Memory64 representation families.
- Explicit Wasm GC raw-buffer families for `array<i8>`, `array<i16>`, `array<i32>`, `array<i64>`, and `array<v128>`.
- Normative logical byte view for numeric GC arrays.
- Partial-element byte-range behavior for wide GC arrays.
- Multi-memory-aware linear buffers and iovecs.
- UTF-8, UTF-16, and 32-bit code-point text representations.
- WTF surrogate-sentinel semantics.
- Opaque resource handles.
- Capability-oriented filesystem and network access.
- Optional `~` preopen convention for embedders that want to provide a guest home or private writable area.
- Filesystem, links, sockets, DNS, clocks, randomness, and polling function families.
- Canonical WAT import declarations.
- Runtime implementation guidance.
- Initial conformance suite with 143 focused WAST tests.
- Compatible JSON harness manifests and deterministic fixtures.
- Generated catalog metadata.
- Exact import-signature validation.
- Pinned `wasm-tools` parsing in CI.
- Normative `spec/behavior.md` for validation order, error normalization, text transfer, path resolution, GC rules, polling, and networking.
- `docs/terminology.md` for controlled project terminology.
- `docs/writing-style.md` for simple technical English and accessibility rules.

### Decided

- The Core WebAssembly import module is `facet`. The previous import-module namespace is not retained as a compatibility alias.
- GC raw-buffer byte offsets and lengths are `i64`.
- The runtime bounds-checks each GC range against the actual array byte length.
- Validation uses a deterministic stage order.
- Error meanings follow WASI and POSIX categories where practical while keeping WPSI numeric values.
- Resource-handle encoding is runtime-private.
- Only handle value `0` has a standardized numeric meaning.
- The guest must not interpret nonzero handle bits or ranges.
- A stale handle must not alias an unrelated live resource.
- Scratch-specific ABI functions and quota provisioning were removed.
- WPSI allocates no mandatory writable filesystem.
- `~` is only an optional preopen display-name convention.
- Filesystem path resolution uses a capability-beneath model.
- Paths cannot escape through `..` or rooted symbolic links.
- Wide GC arrays support arbitrary partial-element byte ranges.
- Raw GC inputs use `(ref array)` with dynamic storage validation.
- Source arrays can be immutable.
- Nested GC `readv` and `writev` use complete selected child arrays.
- WPSI 0.1 has no per-child slice descriptor for nested GC scatter/gather.
- WPSI imported calls are synchronous.
- The runtime cannot retain borrowed guest linear-memory or GC storage after return.
- Nonblocking I/O uses `ERR_AGAIN` and `wpsi-poll`.
- Concurrency and scheduler policy remain outside the ABI.
- WPSI uses one global `abi_version()`.
- Profiles do not have independent versions.
- WPSI has no separate feature-query API.
- Import presence and exact Core WebAssembly type matching are authoritative for optional support.
- Host-originated strings use source-specific length and copy APIs instead of string resource handles.
- A GC caller can provide an existing destination array or request allocation of its concrete result array type.
- Text APIs do not use an `ENC_*` selector.
- Import names identify code-unit width.
- The `wtf` boolean selects strict Unicode or reversible surrogate-sentinel semantics.
- The old raw-8 string mode was removed.
- WPSI does not silently substitute U+FFFD for unrepresentable external text.
- Polling is level-triggered and snapshot-based.
- I/O errors and hangups are readiness events instead of `poll_wait` failures.
- Networking uses WASI-style socket state and error categories adapted to synchronous WPSI calls.
- Network authority is embedder policy, not a guest-visible policy object.
- Human-facing documentation follows a simple-technical-English style inspired by controlled technical English.
- Documentation rewrites must preserve normative ABI meaning.
- Project prose uses `guest`, `runtime`, `embedder`, and `operating system` instead of using `host` for several different actors when a more precise term exists.
