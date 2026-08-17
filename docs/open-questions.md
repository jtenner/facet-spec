# WPSI 0.1 Open Questions

This file tracks decisions intentionally deferred while WPSI 0.1 is implemented and tested.

Resolved questions are removed from this file and recorded in the normative specification, [`spec/behavior.md`](../spec/behavior.md), or the design rationale.

## 1. Async extension

Asynchronous host operations are deliberately omitted because they require retained buffer ownership/lifetime semantics.

Before adding async operations, define:

- whether guest memory/GC buffers can remain borrowed across suspension;
- how memory growth and GC movement interact with retained borrows;
- cancellation;
- resource ownership on dropped futures/continuations;
- whether async operations use handles, callbacks, stack switching, or another Core Wasm mechanism.

## 2. Profile versioning

The draft uses one `abi_version()` value and import presence as feature detection.

Questions:

- Do profiles need independent versions?
- Should there be a compact scalar feature-query API?
- Is normal missing-import failure enough for most tooling?

Current preference: keep import presence authoritative and add explicit profile versioning only if real runtime negotiation requires it.
