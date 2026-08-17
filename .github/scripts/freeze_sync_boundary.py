#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text.rstrip() + "\n", encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    if old not in text:
        raise SystemExit(f"expected text not found in {path}: {old[:120]!r}")
    write(path, text.replace(old, new, 1))


# ---------------------------------------------------------------------------
# SPEC.md: make synchronous host-call lifetime a core normative invariant.
# ---------------------------------------------------------------------------
replace_once(
    "SPEC.md",
    """### 3.6 Incremental implementation is allowed

A runtime MAY implement only the WPSI profiles for WebAssembly features it supports. Missing imports fail through normal WebAssembly instantiation.

## 4. Conformance profiles""",
    """### 3.6 Incremental implementation is allowed

A runtime MAY implement only the WPSI profiles for WebAssembly features it supports. Missing imports fail through normal WebAssembly instantiation.

### 3.7 Synchronous host-call boundary

Every WPSI host call is synchronous at the Core Wasm ABI boundary.

An implementation MUST NOT retain a guest linear-memory pointer or slice, a Wasm GC reference, a raw GC backing pointer, or any other borrowed guest storage after the imported function returns. Any rooting, pinning, no-move region, no-GC region, or equivalent borrow scope established to service the call MUST end before return.

The host MAY retain independent host-owned state or data copied from the guest, but that state MUST NOT depend on continued validity of borrowed guest storage.

WPSI 0.1 defines no asynchronous host functions, futures, callbacks, actor primitives, or retained-buffer operations. Nonblocking resources report `ERR_AGAIN`, and `wpsi-poll` provides the portable readiness mechanism for schedulers that do not want to block an execution context.

This rule does not prohibit concurrency outside the WPSI call boundary. A runtime or guest language MAY schedule multiple tasks, actors, instances, or execution contexts concurrently while each individual WPSI call remains synchronous.

## 4. Conformance profiles""",
)

# Strengthen the existing GC-specific lifetime wording so it explicitly nests
# under the general call-boundary rule.
replace_once(
    "SPEC.md",
    """A runtime MUST keep the referenced object alive for the complete synchronous host call.

A raw backing pointer or slice MUST NOT escape the collector scope in which its address is valid.

Moving collectors MUST pin, enter an appropriate no-move/no-GC region, re-resolve addresses safely, or copy through implementation-private native storage as required.""",
    """A runtime MUST keep the referenced object alive for the complete synchronous host call.

A raw backing pointer, slice, or GC reference MUST NOT escape the dynamic extent of the WPSI call. The collector scope in which a backing address is valid MUST end before the imported function returns.

Moving collectors MUST pin, enter an appropriate no-move/no-GC region, re-resolve addresses safely, or copy through implementation-private native storage as required.""",
)


# ---------------------------------------------------------------------------
# spec/behavior.md: normative observable lifetime rule and close deferred async.
# ---------------------------------------------------------------------------
replace_once(
    "spec/behavior.md",
    """Runtimes are free to choose any private handle encoding that preserves the observable WPSI rules. In particular, a stale or closed handle MUST return `ERR_BAD_HANDLE` and MUST NOT become authority over an unrelated live resource through internal slot reuse.

## 2. Error semantics""",
    """Runtimes are free to choose any private handle encoding that preserves the observable WPSI rules. In particular, a stale or closed handle MUST return `ERR_BAD_HANDLE` and MUST NOT become authority over an unrelated live resource through internal slot reuse.

### 1.2 Synchronous call lifetime

Every WPSI imported function has a bounded synchronous lifetime. Guest storage borrowed by a call is valid only during that call.

Before returning to the guest, the runtime MUST release every borrow of guest linear memory and every borrowed Wasm GC reference or backing view established for the operation. The runtime MUST NOT arrange for a callback, worker, kernel operation, future completion, or other later action to read from or write to borrowed guest storage after return.

A runtime MAY copy guest data into host-owned storage or retain ordinary WPSI resource state when an operation requires it. Such retained state MUST be independent of the lifetime or location of the guest storage from which it was derived.

Concurrency is outside this lifetime rule: multiple guest execution contexts may run concurrently, but each WPSI call still completes or returns `ERR_AGAIN` before its guest-storage borrows end. A scheduler can use `wpsi-poll` to wait for readiness and retry a nonblocking operation.

## 2. Error semantics""",
)

behavior = read("spec/behavior.md")
for stale in [
    "- asynchronous buffer ownership/lifetime semantics;\n",
    "- async buffer ownership and cancellation semantics;\n",
]:
    behavior = behavior.replace(stale, "")
write("spec/behavior.md", behavior)


# ---------------------------------------------------------------------------
# docs/design.md: make the choice permanent for 0.1 and explain actor affinity.
# ---------------------------------------------------------------------------
replace_once(
    "docs/design.md",
    """## Why synchronous calls first?

WPSI 0.1 focuses on the smallest implementable system boundary. Synchronous calls also make scoped borrowing of moving-GC objects tractable: the runtime can root/pin or enter a no-move region for one host call and invalidate the backing view before return.

Asynchronous host operations need an explicit ownership and lifetime model and are intentionally deferred.""",
    """## Why are WPSI calls synchronous?

WPSI deliberately makes synchronous call lifetime a core ABI invariant rather than defining futures or retained-buffer asynchronous host operations.

This keeps guest-storage ownership local and tractable. A runtime can root or pin a Wasm GC object, stabilize linear memory, perform one host operation, invalidate the borrowed view, and return. No guest pointer, GC reference, or borrowed backing address remains live in host code after the call boundary.

Nonblocking I/O still composes with concurrency: an operation can return `ERR_AGAIN`, a scheduler can wait through `wpsi-poll`, run other work, and retry when the resource becomes ready.

This model is intentionally friendly to actor-style, event-loop, green-thread, and multi-instance scheduling without standardizing any of those execution models. WPSI defines neither actors nor a scheduler; it only guarantees that each system call has a bounded synchronous dynamic extent.

A future specification that introduces true asynchronous host calls would need a separate ownership model and would be an explicit extension to this invariant, not an implied part of WPSI 0.1.""",
)


# ---------------------------------------------------------------------------
# docs/runtime-implementation.md: implementation contract and tests.
# ---------------------------------------------------------------------------
runtime = read("docs/runtime-implementation.md")
marker = """while a Core Wasm 3.0 runtime may additionally implement:

```text
wpsi-memory64
wpsi-gc-array
wpsi-network
wpsi-poll
```

## Linear-memory access"""
addition = """while a Core Wasm 3.0 runtime may additionally implement:

```text
wpsi-memory64
wpsi-gc-array
wpsi-network
wpsi-poll
```

## Synchronous call boundary

Treat the return from every WPSI host function as a hard lifetime boundary.

No guest linear-memory view, GC reference, raw GC payload pointer, pin, root, no-move token, or other borrowed guest-storage state may remain owned by host work after the function returns. If an operating-system or runtime API requires an operation to outlive the call, copy the relevant guest data into host-owned storage or use a nonblocking operation that returns `ERR_AGAIN` and is retried after polling.

Do not implement a WPSI import by starting background work that will later dereference a guest pointer or GC reference. The host may retain WPSI resource handles and host-owned metadata, but not borrowed guest storage.

This restriction is per call, not per runtime. A runtime is free to execute multiple Wasm instances, actors, tasks, or scheduler contexts concurrently as long as each WPSI call obeys the same lifetime boundary.

## Linear-memory access"""
if marker not in runtime:
    raise SystemExit("runtime implementation insertion marker missing")
runtime = runtime.replace(marker, addition, 1)

# Add a test recommendation for borrow lifetime.
marker = "- forced moving collection around host calls;\n"
if marker not in runtime:
    raise SystemExit("runtime testing marker missing")
runtime = runtime.replace(
    marker,
    marker + "- immediate memory growth/GC after return to catch retained guest borrows;\n",
    1,
)
write("docs/runtime-implementation.md", runtime)


# ---------------------------------------------------------------------------
# docs/open-questions.md: async is settled; profile versioning is the sole item.
# ---------------------------------------------------------------------------
write(
    "docs/open-questions.md",
    """# WPSI 0.1 Open Questions

This file tracks decisions intentionally deferred while WPSI 0.1 is implemented and tested.

Resolved questions are removed from this file and recorded in the normative specification, [`spec/behavior.md`](../spec/behavior.md), or the design rationale.

## 1. Profile versioning

The draft uses one `abi_version()` value and import presence as feature detection.

Questions:

- Do profiles need independent versions?
- Should there be a compact scalar feature-query API?
- Is normal missing-import failure enough for most tooling?

Current preference: keep import presence authoritative and add explicit profile versioning only if real runtime negotiation requires it.
""",
)


# ---------------------------------------------------------------------------
# ROADMAP.md + CHANGELOG.md + README.md
# ---------------------------------------------------------------------------
roadmap = read("ROADMAP.md")
anchor = "- [x] Define polling snapshot/readiness semantics.\n"
if anchor not in roadmap:
    raise SystemExit("roadmap async decision anchor missing")
roadmap = roadmap.replace(
    anchor,
    anchor + "- [x] Freeze WPSI 0.1 host calls as synchronous and forbid retaining borrowed guest storage across returns.\n",
    1,
)
roadmap = roadmap.replace(
    "They cover async ownership and profile-specific version negotiation.",
    "The remaining question is profile-specific version negotiation.",
)
roadmap = roadmap.replace("- asynchronous operations with explicit buffer ownership;\n", "")
write("ROADMAP.md", roadmap)

changelog = read("CHANGELOG.md")
anchor = "- Nested GC `readv/writev` is whole-child only in WPSI 0.1. `first/count` select complete child arrays; per-child slice descriptors are intentionally omitted.\n"
if anchor not in changelog:
    raise SystemExit("changelog async decision anchor missing")
changelog = changelog.replace(
    anchor,
    anchor + "- WPSI 0.1 host calls are synchronously bounded: implementations may not retain guest linear-memory views, GC references, or other borrowed guest storage after return. Nonblocking I/O uses `ERR_AGAIN` plus `wpsi-poll`; concurrency and actor/task scheduling remain outside the ABI.\n",
    1,
)
changelog = changelog.replace("- Async buffer ownership and cancellation semantics.\n", "")
write("CHANGELOG.md", changelog)

readme = read("README.md")
anchor = "- **Capability-oriented resources.** Host filesystems and networking remain explicitly granted.\n"
if anchor not in readme:
    raise SystemExit("README property anchor missing")
readme = readme.replace(
    anchor,
    anchor + "- **Synchronous call lifetime.** WPSI never retains borrowed guest pointers or GC references after a host call returns; nonblocking I/O composes with `wpsi-poll` and external actor/task schedulers.\n",
    1,
)
write("README.md", readme)


# ---------------------------------------------------------------------------
# Hygiene assertions.
# ---------------------------------------------------------------------------
if "## 1. Async extension" in read("docs/open-questions.md"):
    raise SystemExit("async remains an open question")
if "Async buffer ownership and cancellation semantics" in read("CHANGELOG.md"):
    raise SystemExit("async remains deferred in changelog")
if "They cover async ownership" in read("ROADMAP.md"):
    raise SystemExit("async remains deferred in roadmap")
if "Asynchronous host operations need an explicit ownership" in read("docs/design.md"):
    raise SystemExit("old async-deferred design wording remains")
if "### 3.7 Synchronous host-call boundary" not in read("SPEC.md"):
    raise SystemExit("normative synchronous boundary missing from SPEC.md")
if "### 1.2 Synchronous call lifetime" not in read("spec/behavior.md"):
    raise SystemExit("normative synchronous lifetime missing from behavior.md")

print("froze WPSI 0.1 as synchronous and removed async from deferred decisions")
