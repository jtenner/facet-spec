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
- UTF-8, UTF-16, UTF-32, WTF-8, WTF-16, and raw 8-bit system string encodings.
- Opaque resource handles and capability-oriented filesystem/network access.
- Automatic private scratch filesystem for filesystem-enabled instances.
- Filesystem, links, sockets, DNS, clocks, randomness, and polling function families.
- Canonical WAT import declarations and runtime implementation guidance.
- Comprehensive initial conformance suite with 143 focused WAST tests, WASI-compatible host manifests, deterministic fixtures, generated catalog metadata, exact import-signature validation, and pinned `wasm-tools` parsing in CI.

### Decided

- GC raw-buffer byte offsets and lengths are `i64`. The existing normative signatures remain unchanged; runtimes bounds-check these values against the actual GC array byte length.
