# WPSI 0.1 Open Questions

This file tracks decisions intentionally deferred while WPSI 0.1 is implemented and tested.

Resolved questions are removed from this file and recorded in the normative specification, [`spec/behavior.md`](../spec/behavior.md), or the design rationale.

## 1. Scatter/gather nested GC arrays

The current GC `readv/writev` form uses an outer array of child-array references and consumes complete logical byte views for selected children.

Questions:

- Do we need per-child slices/offsets?
- If yes, should those be represented by structs, parallel arrays, or a separate descriptor array type?
- Is full-child scatter/gather enough for 0.1?

Current preference: keep 0.1 simple and benchmark real language lowering before adding descriptors.

## 2. Async extension

Asynchronous host operations are deliberately omitted because they require retained buffer ownership/lifetime semantics.

Before adding async operations, define:

- whether guest memory/GC buffers can remain borrowed across suspension;
- how memory growth and GC movement interact with retained borrows;
- cancellation;
- resource ownership on dropped futures/continuations;
- whether async operations use handles, callbacks, stack switching, or another Core Wasm mechanism.

## 3. Profile versioning

The draft uses one `abi_version()` value and import presence as feature detection.

Questions:

- Do profiles need independent versions?
- Should there be a compact scalar feature-query API?
- Is normal missing-import failure enough for most tooling?

Current preference: keep import presence authoritative and add explicit profile versioning only if real runtime negotiation requires it.
