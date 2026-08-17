# WPSI conformance tests

The normative WPSI 0.1 test suite lives in [`spec/tests`](../spec/tests).
It currently contains **143** standard WAST tests plus compatibility-oriented
host manifests, deterministic fixtures, a machine-readable catalog, signature
validation against [`spec/imports.wat`](../spec/imports.wat), and pinned
`wasm-tools` syntax checks.

Coverage includes Core resource semantics, arguments and environment, clocks,
randomness, Memory32, Memory64, multi-memory I/O, GC arrays and nested arrays,
UTF-8/UTF-16/UTF-32, scratch storage, preopens and rights, links, sockets, DNS,
polling, stale handles, and cross-instance isolation.

Contributions are welcome. See [`spec/tests/README.md`](../spec/tests/README.md)
for the runner contract and authoring requirements.
