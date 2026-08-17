from pathlib import Path


def read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    Path(path).write_text(text.rstrip() + "\n", encoding="utf-8")


# SPEC.md
p = "SPEC.md"
text = read(p)
old = """All WPSI resources are opaque nonzero `i32` handles.

Handle `0` is always invalid.

Handles are instance-local and unforgeable in the semantic sense: an implementation MUST validate a handle before dereferencing the resource it names.

An implementation MUST prevent a stale closed handle from accidentally gaining authority over an unrelated resource solely through unchecked slot reuse. Generation counters, monotonic IDs, delayed reuse, or equivalent mechanisms are acceptable."""
new = """All WPSI resources are opaque nonzero `i32` handles.

Handle `0` is always invalid.

Handles are instance-local and unforgeable in the semantic sense: an implementation MUST validate a handle before dereferencing the resource it names.

Except for the reserved invalid value `0`, the numeric bits of a handle have no WPSI-defined meaning. WPSI does not reserve handle ranges, expose table indexes or generation fields, encode resource kinds in handle bits, or otherwise standardize a handle layout. Guests MUST treat every nonzero handle as an opaque token and MUST NOT derive authority, resource kind, lifetime, or runtime state from its numeric value.

An implementation MUST prevent a stale closed handle from accidentally gaining authority over an unrelated resource solely through unchecked slot reuse. A previously closed handle value MUST NOT later identify an unrelated live resource in the same WPSI instance. Generation counters, monotonic IDs, randomized tokens, delayed reuse, or equivalent mechanisms are acceptable implementation strategies, and their encoding remains entirely runtime-private."""
if old not in text:
    raise SystemExit("SPEC.md handle section did not match expected text")
write(p, text.replace(old, new, 1))


# spec/behavior.md
p = "spec/behavior.md"
text = read(p)
marker = """This order exists to make failures reproducible across runtimes and to prevent host behavior from accidentally deciding which of several invalid guest inputs is reported first.

## 2. Error semantics"""
replacement = """This order exists to make failures reproducible across runtimes and to prevent host behavior from accidentally deciding which of several invalid guest inputs is reported first.

### 1.1 Opaque handle values

A WPSI resource handle is an instance-local opaque `i32` token. Only the value `0` has defined bit-level meaning: it is always invalid.

No nonzero handle bit, range, subfield, ordering relation, or numeric pattern is portable WPSI information. A guest MUST NOT inspect a handle to infer its resource kind, table position, generation, authority, age, or implementation strategy.

Runtimes are free to choose any private handle encoding that preserves the observable WPSI rules. In particular, a stale or closed handle MUST return `ERR_BAD_HANDLE` and MUST NOT become authority over an unrelated live resource through internal slot reuse.

## 2. Error semantics"""
if marker not in text:
    raise SystemExit("spec/behavior.md insertion marker not found")
text = text.replace(marker, replacement, 1)
text = text.replace("- handle bit layout or reserved handle ranges;\n", "", 1)
write(p, text)


# docs/open-questions.md
write(
    "docs/open-questions.md",
    """# WPSI 0.1 Open Questions

This file tracks decisions intentionally deferred while WPSI 0.1 is implemented and tested.

Resolved questions are removed from this file and recorded in the normative specification, [`spec/behavior.md`](../spec/behavior.md), or the design rationale.

## 1. Scratch filesystem lifetime and persistence

The draft requires private writable scratch storage and permits multiple backing strategies.

Questions:

- Must scratch always be ephemeral across process/runtime restarts?
- May an embedder deliberately persist scratch while preserving its sandbox identity?
- Should quota reporting be mandatory or optional?

Current preference: lifetime is tied to the WPSI instance unless the embedder explicitly supplies a persistent private implementation.

## 2. Scatter/gather nested GC arrays

The current GC `readv/writev` form uses an outer array of child-array references and consumes complete logical byte views for selected children.

Questions:

- Do we need per-child slices/offsets?
- If yes, should those be represented by structs, parallel arrays, or a separate descriptor array type?
- Is full-child scatter/gather enough for 0.1?

Current preference: keep 0.1 simple and benchmark real language lowering before adding descriptors.

## 3. Async extension

Asynchronous host operations are deliberately omitted because they require retained buffer ownership/lifetime semantics.

Before adding async operations, define:

- whether guest memory/GC buffers can remain borrowed across suspension;
- how memory growth and GC movement interact with retained borrows;
- cancellation;
- resource ownership on dropped futures/continuations;
- whether async operations use handles, callbacks, stack switching, or another Core Wasm mechanism.

## 4. Profile versioning

The draft uses one `abi_version()` value and import presence as feature detection.

Questions:

- Do profiles need independent versions?
- Should there be a compact scalar feature-query API?
- Is normal missing-import failure enough for most tooling?

Current preference: keep import presence authoritative and add explicit profile versioning only if real runtime negotiation requires it.
""",
)


# docs/design.md
p = "docs/design.md"
text = read(p)
old = """## Why opaque i32 resource handles?

Opaque numeric handles are simple, portable across current engines, and keep resource authority under embedder control.

WPSI does not require host objects to become `externref` or GC references. A future extension can explore reference-typed resource handles independently without changing the existing ABI."""
new = """## Why opaque i32 resource handles?

Opaque numeric handles are simple, portable across current engines, and keep resource authority under embedder control.

`Opaque` is intentional and complete: WPSI assigns no meaning to the bits of a nonzero handle. There are no standardized resource-kind tags, reserved ranges, table-index fields, generation fields, or ordering guarantees. A runtime may use generation counters, monotonically increasing IDs, randomized values, delayed reuse, or another representation as long as stale handles cannot alias unrelated live resources.

Keeping the encoding private avoids constraining runtime handle tables and prevents language bindings from accidentally depending on one implementation's bookkeeping. Bindings need only preserve the `i32` token and pass it back to WPSI.

WPSI does not require host objects to become `externref` or GC references. A future extension can explore reference-typed resource handles independently without changing the existing ABI."""
if old not in text:
    raise SystemExit("docs/design.md handle rationale did not match expected text")
write(p, text.replace(old, new, 1))


# ROADMAP.md
p = "ROADMAP.md"
text = read(p)
anchor = "- [x] Define deterministic validation and error precedence.\n"
addition = anchor + "- [x] Keep resource-handle encoding entirely runtime-private while requiring stale-handle safety.\n"
if anchor not in text:
    raise SystemExit("ROADMAP.md insertion anchor not found")
text = text.replace(anchor, addition, 1)
text = text.replace(
    "They cover handle encoding, scratch persistence, per-child GC scatter/gather slicing, async ownership, and profile-specific version negotiation.",
    "They cover scratch persistence, per-child GC scatter/gather slicing, async ownership, and profile-specific version negotiation.",
    1,
)
write(p, text)


# CHANGELOG.md
p = "CHANGELOG.md"
text = read(p)
anchor = "- Error meanings follow WASI/POSIX categories where practical while keeping WPSI's own numeric namespace.\n"
addition = anchor + "- Resource handle encoding is entirely runtime-private. Only `0` has a standardized numeric meaning; guests may not interpret nonzero handle bits or ranges, and stale handles may never alias unrelated live resources.\n"
if anchor not in text:
    raise SystemExit("CHANGELOG.md insertion anchor not found")
text = text.replace(anchor, addition, 1)
text = text.replace("- Handle bit layout and reserved ranges.\n", "", 1)
write(p, text)

print("resolved WPSI handle encoding as runtime-private")
