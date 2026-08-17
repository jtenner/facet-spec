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
- Automatic private scratch filesystem for filesystem-enabled instances.
- Filesystem, links, sockets, DNS, clocks, randomness, and polling function families.
- Canonical WAT import declarations and runtime implementation guidance.
- Comprehensive initial conformance suite with 143 focused WAST tests, WASI-compatible host manifests, deterministic fixtures, generated catalog metadata, exact import-signature validation, and pinned `wasm-tools` parsing in CI.
- Normative `spec/behavior.md` defining validation precedence, error normalization, path and symlink resolution, settled GC-array behavior, `sysstr` conversion, polling, and networking state semantics.

### Decided

- Text APIs no longer use an `ENC_*` selector. Code-unit width is encoded in the import name (`i8`, `i16`, or `i32`) and a single `wtf` boolean selects strict Unicode versus reversible surrogate-sentinel semantics. The old `RAW8` mode is removed; non-Unicode host units are represented through WTF sentinels when lossless conversion is possible.
- Linear-memory textual imports now include both memory width and code-unit width, for example `path_open_mem32_i16` and `args_read_mem64_i8`.

- GC raw-buffer byte offsets and lengths are `i64`. The existing normative signatures remain unchanged; runtimes bounds-check these values against the actual GC array byte length.
- Validation failures use a deterministic order: scalar arguments, handles, resource state/authority, guest representation, ranges, text, namespace resolution, host operation, then host-error normalization.
- Error meanings follow WASI/POSIX categories where practical while keeping WPSI's existing numeric namespace.
- Filesystem path resolution uses the WASI capability-beneath model: relative paths only, no temporary escape through `..`, and no absolute/rooted symlink escape.
- Wide GC arrays retain arbitrary partial-element byte ranges; GC imports use `(ref array)` with dynamic storage validation; immutable source arrays are allowed.
- `sysstr` values are immutable snapshots and short destination buffers receive the longest valid encoded prefix without implicit NUL termination.
- Polling is level-triggered and snapshot-based; I/O errors/hangups are readiness events rather than poll-operation failures.
- Networking follows WASI-style socket state/error semantics adapted to synchronous WPSI calls; network authority remains embedder/instantiation policy rather than a guest-visible policy API.

### Deferred

- Scratch persistence across runtime/embedder restarts.
- Handle bit layout and reserved ranges.
- Per-child slicing for nested GC scatter/gather.
- Async buffer ownership and cancellation semantics.
- Profile-specific version negotiation.
- Reconsideration of the path encoding parameter shape.
- Removed `sysstr` string resources in favor of source-specific length/copy APIs, caller-owned GC `read_into` APIs, and caller-typed allocating GC string results.
