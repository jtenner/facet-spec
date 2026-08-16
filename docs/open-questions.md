# WPSI 0.1 Open Questions

This file tracks decisions that should be resolved before declaring the 0.1 ABI stable.

## 1. Canonical error namespace

The current draft defines its own compact errno namespace.

Questions:

- Should errors deliberately resemble POSIX/WASI values or remain WPSI-specific?
- Which errors are stable enough to expose portably across Windows, Unix, and virtual filesystems?
- Should unsupported host distinctions collapse to `ERR_OTHER` or a more specific portable category?

## 2. Handle encoding guarantees

The spec requires stale-handle safety but leaves encoding private.

Questions:

- Is that enough for interoperable language bindings?
- Should WPSI reserve any handle ranges or bits?
- Should duplicated/shared handles be added before 1.0?

Current preference: keep handle encoding entirely runtime-private.

## 3. GC raw-buffer range width

Raw GC array functions currently use `i64` byte offsets and lengths even though Core Wasm GC array lengths are currently bounded by `i32` indexing semantics.

Advantages:

- one uniform raw-buffer signature family;
- future-proof arithmetic;
- totals such as scatter/gather byte counts already use `i64`.

Cost:

- runtimes perform range checks that usually reduce to a smaller object bound.

Question: keep `i64`, or use `i32` offsets/counts for GC arrays?

Current preference: keep `i64` for raw byte ranges.

## 4. Partial wide-array elements

The current logical-byte-view rule permits a read or write to begin and end inside `i16`, `i32`, `i64`, or `v128` elements.

This is expressive and maps efficiently to runtimes with contiguous payload storage, but fallback implementations may need read-modify-write at the edges.

Questions:

- Should partial elements remain mandatory?
- Would aligned-only ranges materially improve portability?

Current preference: keep arbitrary byte ranges unless a second-runtime prototype exposes a serious implementation problem.

## 5. Abstract `(ref array)` import parameters

GC imports use `(ref array)` and validate the dynamic element storage type based on the import name.

Questions:

- Does every target runtime's host-function API make abstract arrayref parameters practical?
- Should a future optional typed-import mechanism allow concrete imported array types for stronger static validation?

Current preference: keep `(ref array)` as the portable base ABI.

## 6. Immutable source arrays

Write/send operations may accept immutable arrays because the host only reads them. Read/receive/random-fill operations require mutable arrays.

Question: should this remain dynamic validation or should source/destination import families somehow encode mutability?

Current preference: dynamic validation is sufficient and avoids another naming dimension.

## 7. System strings

`sysstr` exists so host-originated text is not forced into one guest encoding.

Questions:

- Should `sysstr` be retained in 1.0?
- Should there be direct bulk argument/environment fill operations for high-throughput startup?
- How should hosts with non-Unicode path namespaces expose conversion failures?

## 8. Path encoding parameter

Path representation families carry an encoding parameter rather than multiplying import names by UTF encoding.

Question: is this the right dividing line between representation naming and semantic options?

Current preference: yes; the Core Wasm signature is unchanged by the encoding enum.

## 9. Scratch filesystem lifetime and persistence

The draft requires private writable scratch storage and permits multiple backing strategies.

Questions:

- Must scratch always be ephemeral across process/runtime restarts?
- May an embedder deliberately persist scratch while preserving its sandbox identity?
- Should quota reporting be mandatory or optional?

Current preference: lifetime is tied to the WPSI instance unless the embedder explicitly supplies a persistent private implementation.

## 10. Directory capability traversal

The spec requires preventing path/symlink escape.

Question: should WPSI standardize detailed symlink-follow behavior for every path function before 1.0 rather than relying on flags plus the capability invariant?

This needs adversarial filesystem tests.

## 11. Scatter/gather nested GC arrays

The current GC `readv/writev` form uses an outer array of child-array references and consumes complete logical byte views for selected children.

Questions:

- Do we need per-child slices/offsets?
- If yes, should those be represented by structs, parallel arrays, or a separate descriptor array type?
- Is full-child scatter/gather enough for 0.1?

Current preference: keep 0.1 simple and benchmark real language lowering before adding descriptors.

## 12. Polling model

Polling uses a resource handle instead of memory-resident event structures.

Questions:

- Is iterator-style `poll_next` sufficiently efficient?
- Should a future bulk event read have Memory32/Memory64/GC variants?
- How should cancellation interact with blocking host calls?

## 13. Network capability vocabulary

WPSI states that networking is capability-controlled but does not standardize the embedder-side capability configuration format.

Question: should the ABI specify discoverable guest-visible network policy, or leave policy entirely to the embedder?

Current preference: leave policy configuration outside the guest ABI; failed authority checks return `ERR_CAPABILITY`.

## 14. Async extension

Asynchronous host operations are deliberately omitted because they require retained buffer ownership/lifetime semantics.

Before adding async operations, define:

- whether guest memory/GC buffers can remain borrowed across suspension;
- how memory growth and GC movement interact with retained borrows;
- cancellation;
- resource ownership on dropped futures/continuations;
- whether async operations use handles, callbacks, stack switching, or another Core Wasm mechanism.

## 15. Profile versioning

The draft uses one `abi_version()` value and import presence as feature detection.

Questions:

- Do profiles need independent versions?
- Should there be a compact scalar feature-query API?
- Is normal missing-import failure enough for most tooling?

Current preference: keep import presence authoritative and add explicit profile versioning only if real runtime negotiation requires it.
