# WPSI 0.1 Open Questions

This file tracks decisions intentionally deferred while WPSI 0.1 is implemented and tested.

Resolved questions are removed from this file and recorded in the normative specification, [`spec/behavior.md`](../spec/behavior.md), or the design rationale.

## 1. Profile versioning

The draft uses one `abi_version()` value and import presence as feature detection.

Questions:

- Do profiles need independent versions?
- Should there be a compact scalar feature-query API?
- Is normal missing-import failure enough for most tooling?

Current preference: keep import presence authoritative and add explicit profile versioning only if real runtime negotiation requires it.
