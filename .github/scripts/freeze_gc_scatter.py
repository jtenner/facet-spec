#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text.rstrip() + "\n", encoding="utf-8")


def replace_once(text: str, old: str, new: str, path: str) -> str:
    if old not in text:
        raise SystemExit(f"expected text not found in {path}: {old[:80]!r}")
    return text.replace(old, new, 1)


# SPEC.md: freeze nested-array representation and the readv/writev semantics.
spec = read("SPEC.md")
old = """### 7.4 Nested arrays

Scatter/gather GC operations accept an outer `(ref array)` whose selected children MUST be non-null references to arrays of the element type named by the function.

Read operations require mutable child arrays."""
new = """### 7.4 Nested arrays

Scatter/gather GC operations accept an outer `(ref array)` whose selected children MUST be non-null references to arrays of the element type named by the function.

Read operations require mutable child arrays.

For WPSI 0.1, nested GC scatter/gather is deliberately **whole-child only**. `first` and `count` select a contiguous range of child arrays in the outer array. Every selected child contributes its complete logical byte view, from byte offset zero through the child's full logical byte length.

There are no per-child offset, length, slice, or descriptor values in the WPSI 0.1 nested-array ABI. Partial access to one GC array uses the ordinary single-array functions that already take `byte_offset` and `byte_length`."""
spec = replace_once(spec, old, new, "SPEC.md")

old = """fd_writev_array_v128(fd: i32, buffers: ref array, first: i32, count: i32)
  -> (bytes_written: i64, errno: i32)
```

## 22. Positioning and persistence"""
new = """fd_writev_array_v128(fd: i32, buffers: ref array, first: i32, count: i32)
  -> (bytes_written: i64, errno: i32)
```

`first` and `count` are unsigned child indexes/counts. The selected range MUST fit entirely within the outer array or the operation returns `ERR_RANGE` without performing I/O.

Each selected child participates using its complete logical byte view. WPSI 0.1 does not define per-child slices for nested GC scatter/gather.

Before performing host I/O, the runtime MUST validate the complete selected child range, including non-null child references, dynamic element storage type, and destination mutability for reads. A validation failure MUST NOT partially consume the stream or modify an earlier child.

Normal stream short-transfer rules still apply. A successful short read or write MAY stop partway through the logical byte view of the final child reached by the transfer; later children are untouched.

## 22. Positioning and persistence"""
spec = replace_once(spec, old, new, "SPEC.md")
write("SPEC.md", spec)


# behavior.md: make whole-child scatter/gather part of the frozen GC rules and remove it from deferred work.
behavior = read("spec/behavior.md")
old = """6. Dynamic kind, storage-type, or destination-mutability mismatch returns `ERR_TYPE`.
7. These rules specify observable values only and do not require contiguous physical GC storage."""
new = """6. Dynamic kind, storage-type, or destination-mutability mismatch returns `ERR_TYPE`.
7. Nested GC `readv/writev` uses complete selected child arrays only. `first` and `count` select children; WPSI 0.1 has no per-child slice descriptors.
8. Every selected nested child MUST be validated before host I/O begins, so a later invalid child cannot cause partial I/O through earlier children.
9. These rules specify observable values only and do not require contiguous physical GC storage."""
behavior = replace_once(behavior, old, new, "spec/behavior.md")
behavior = behavior.replace("- per-child slicing for GC nested scatter/gather;\n", "", 1)
write("spec/behavior.md", behavior)


# Remove the resolved open question and renumber what remains.
write("docs/open-questions.md", """# WPSI 0.1 Open Questions

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
""")


# Design rationale.
design = read("docs/design.md")
anchor = """The initial raw-buffer set intentionally excludes `f32` and `f64`. They provide little systems-I/O benefit over same-width integer storage and would require additional care around floating-point representation and NaN payload expectations.

## Why UTF-16 and UTF-32?"""
addition = """The initial raw-buffer set intentionally excludes `f32` and `f64`. They provide little systems-I/O benefit over same-width integer storage and would require additional care around floating-point representation and NaN payload expectations.

## Why are nested GC scatter/gather buffers whole-child only?

The outer GC array already provides a simple scatter/gather list: each selected child is one complete buffer. Adding an offset and length for every child would require another portable descriptor representation, such as GC structs or parallel arrays, and would substantially complicate an operation that is primarily an optimization.

WPSI 0.1 therefore keeps nested `readv/writev` structural: `first` and `count` choose child arrays, and each child contributes its entire logical byte view. The ordinary single-array I/O functions already provide `byte_offset` and `byte_length` when a caller needs a slice of one array.

A future extension may add sliced scatter/gather under new import names if real compiler/runtime workloads demonstrate that the additional ABI surface is worthwhile.

## Why UTF-16 and UTF-32?"""
design = replace_once(design, anchor, addition, "docs/design.md")
write("docs/design.md", design)


# Runtime guidance.
runtime = read("docs/runtime-implementation.md")
old = """Nested scatter/gather arrays are different: the outer array contains references and is traversed structurally, while each child is validated as one of the allowed pointer-free numeric array types.

## GC barriers"""
new = """Nested scatter/gather arrays are different: the outer array contains references and is traversed structurally, while each child is validated as one of the allowed pointer-free numeric array types.

For WPSI 0.1, validate the entire `first..first+count` child range before beginning host I/O, then expose each selected child's complete logical byte view in sequence. Do not invent or infer per-child slices. A short host transfer may finish inside the final child reached; bytes outside the transferred prefix remain untouched.

## GC barriers"""
runtime = replace_once(runtime, old, new, "docs/runtime-implementation.md")
write("docs/runtime-implementation.md", runtime)


# Roadmap.
roadmap = read("ROADMAP.md")
anchor = "- [x] Freeze WPSI 0.1 GC raw-buffer behavior: `i64` byte ranges, partial wide elements, abstract `(ref array)`, and immutable sources.\n"
addition = anchor + "- [x] Freeze nested GC scatter/gather as whole-child only; `first/count` select child arrays and per-child slices are outside WPSI 0.1.\n"
roadmap = replace_once(roadmap, anchor, addition, "ROADMAP.md")
roadmap = roadmap.replace(
    "They cover per-child GC scatter/gather slicing, async ownership, and profile-specific version negotiation.",
    "They cover async ownership and profile-specific version negotiation.",
    1,
)
write("ROADMAP.md", roadmap)


# Changelog.
changelog = read("CHANGELOG.md")
anchor = "- Wide GC arrays retain arbitrary partial-element byte ranges; GC inputs use `(ref array)` with dynamic storage validation; immutable source arrays are allowed.\n"
addition = anchor + "- Nested GC `readv/writev` is whole-child only in WPSI 0.1. `first/count` select complete child arrays; per-child slice descriptors are intentionally omitted.\n"
changelog = replace_once(changelog, anchor, addition, "CHANGELOG.md")
changelog = changelog.replace("- Per-child slicing for nested GC scatter/gather.\n", "", 1)
write("CHANGELOG.md", changelog)

print("froze WPSI 0.1 nested GC scatter/gather as whole-child only")
