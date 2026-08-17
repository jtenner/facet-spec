#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text.rstrip() + "\n", encoding="utf-8")


# SPEC.md — make the version/feature model normative.
spec = read("SPEC.md")
old = "WPSI 0.1 reports `abi_version() == 1`.\n\n## 13. Arguments and environment"
new = """WPSI 0.1 reports `abi_version() == 1`.

### 12.1 Versioning and feature detection

`abi_version()` versions the overall WPSI ABI generation. WPSI profiles do not have independent version numbers, and WPSI 0.1 defines no scalar feature-query or profile-query API.

Support for a WPSI operation is determined by normal Core WebAssembly linking. The presence of the requested import together with exact Core Wasm type compatibility is authoritative. A module SHOULD import the operations and representation families it actually requires; a runtime MAY expose any conforming subset.

Profile names such as `wpsi-filesystem`, `wpsi-gc-array`, and `wpsi-network` are documentation and conformance groupings only. They are not a second runtime negotiation namespace.

An additive capability introduced under the same ABI generation SHOULD use a new import and does not by itself require an `abi_version()` increment. An incompatible replacement for one operation SHOULD normally use a new import name so old and new operations can coexist. A change that makes the overall WPSI ABI generation incompatibly different MUST increment `abi_version()`.

## 13. Arguments and environment"""
if old not in spec:
    raise SystemExit("SPEC.md abi_version anchor not found")
spec = spec.replace(old, new, 1)
write("SPEC.md", spec)


# spec/behavior.md — there are no remaining deferred 0.1 decisions.
behavior = read("spec/behavior.md")
old = """## 8. Deferred decisions

This document intentionally does not settle:

- profile-specific version negotiation;

Those topics remain listed in [`../docs/open-questions.md`](../docs/open-questions.md).

## 9. Compatibility references"""
new = """## 8. Version and feature compatibility

WPSI 0.1 has one global ABI version and no independently versioned profiles. Import presence and Core Wasm type matching are the authoritative feature-detection mechanism.

A runtime MUST NOT require a guest-visible profile manifest, profile-version negotiation step, or scalar feature-query call in addition to normal Core Wasm linking. Profile labels are descriptive groupings for documentation and conformance only.

## 9. Compatibility references"""
if old not in behavior:
    raise SystemExit("spec/behavior.md deferred section not found")
behavior = behavior.replace(old, new, 1)
write("spec/behavior.md", behavior)


# docs/open-questions.md — close the tracker.
write("docs/open-questions.md", """# WPSI 0.1 Open Questions

There are currently **no unresolved WPSI 0.1 ABI design questions** tracked by this document.

The decisions that were previously deferred have been resolved in the normative specification, [`spec/behavior.md`](../spec/behavior.md), or [`docs/design.md`](design.md). New implementation experience may still motivate future specification changes, but those should be proposed as explicit extensions or revisions rather than treated as implicit 0.1 negotiation points.
""")


# docs/design.md — explain why imports are enough.
design = read("docs/design.md")
anchor = "## Why an explicit memory index?"
section = """## Why no profile versions or feature-query API?

Core Wasm linking already answers the feature question precisely: a module declares the imports it requires, including their exact function types, and instantiation succeeds only when the runtime can provide them.

Adding `filesystem_version()`, `gc_array_version()`, profile manifests, or a scalar feature-query API would duplicate that mechanism and create a second source of truth that could disagree with the imports actually needed by the program.

WPSI therefore keeps one coarse `abi_version()` for the overall ABI generation and treats import presence plus type compatibility as authoritative for optional capability support. Profile names remain useful for documentation, implementation planning, and conformance reporting, but they are not independently negotiated runtime entities.

Additive evolution can introduce new imports without disturbing existing modules. A genuinely incompatible form of one operation should normally receive a new import name; only an incompatible change to the overall WPSI ABI generation requires incrementing `abi_version()`.

"""
if anchor not in design:
    raise SystemExit("docs/design.md insertion anchor not found")
design = design.replace(anchor, section + anchor, 1)
write("docs/design.md", design)


# Runtime implementation guidance.
runtime = read("docs/runtime-implementation.md")
anchor = """wpsi-poll
```

## Synchronous call boundary"""
replacement = """wpsi-poll
```

Do not build a second profile-version or feature-negotiation registry for WPSI. Register the imports the runtime implements and let ordinary Core Wasm import/type matching decide whether a module can instantiate. `abi_version()` is the only global ABI generation number; profile labels are implementation/conformance groupings, not independently versioned runtime objects.

## Synchronous call boundary"""
if anchor not in runtime:
    raise SystemExit("docs/runtime-implementation.md host-import anchor not found")
runtime = runtime.replace(anchor, replacement, 1)
write("docs/runtime-implementation.md", runtime)


# Conformance harness guidance.
tests = read("spec/tests/README.md")
old = """The catalog in [`catalog.json`](catalog.json) provides human-readable profile
metadata but does not override the imports.

## Harness-driven tests"""
new = """The catalog in [`catalog.json`](catalog.json) provides human-readable profile
metadata but does not override the imports. There are no profile-version fields
or separate feature-query results in the conformance contract: import presence
and Core Wasm type matching are authoritative.

## Harness-driven tests"""
if old not in tests:
    raise SystemExit("spec/tests/README.md profile anchor not found")
tests = tests.replace(old, new, 1)
write("spec/tests/README.md", tests)


# README summary.
readme = read("README.md")
old = "- **Incremental runtime support.** A runtime can implement only the representation families it actually supports.\n"
new = old + "- **Import-driven feature detection.** WPSI has one global ABI version; optional support is determined by ordinary import presence and Core Wasm type matching, not profile-version or feature-query APIs.\n"
if old not in readme:
    raise SystemExit("README incremental-support bullet not found")
readme = readme.replace(old, new, 1)
readme = readme.replace(
    "- [`docs/open-questions.md`](docs/open-questions.md) — intentionally deferred decisions.",
    "- [`docs/open-questions.md`](docs/open-questions.md) — WPSI 0.1 open-question status; currently no unresolved ABI design questions.",
    1,
)
write("README.md", readme)


# Roadmap — mark the question set closed.
roadmap = read("ROADMAP.md")
old = "- [x] Freeze WPSI 0.1 host calls as synchronous and forbid retaining borrowed guest storage across returns.\n"
new = old + "- [x] Define one global ABI version and make import/type matching authoritative for feature detection; profiles are not independently versioned.\n"
if old not in roadmap:
    raise SystemExit("ROADMAP sync bullet not found")
roadmap = roadmap.replace(old, new, 1)
roadmap = roadmap.replace(
    "- [ ] Resolve or explicitly defer the remaining questions in `docs/open-questions.md` before declaring the ABI stable.",
    "- [x] Resolve the WPSI 0.1 ABI questions tracked in `docs/open-questions.md`.",
    1,
)
old = """## Deferred / post-0.1 questions

The remaining questions in `docs/open-questions.md` are intentionally not blockers for beginning the Wago implementation. The remaining question is profile-specific version negotiation.

## Post-1.0 candidates"""
new = """## Open ABI questions

There are currently no unresolved WPSI 0.1 ABI design questions. Implementation work and the second-runtime prototype may still expose issues that require explicit specification changes before 1.0.

## Post-1.0 candidates"""
if old not in roadmap:
    raise SystemExit("ROADMAP deferred section not found")
roadmap = roadmap.replace(old, new, 1)
write("ROADMAP.md", roadmap)


# Changelog — resolve final deferred item.
changelog = read("CHANGELOG.md")
anchor = "- WPSI 0.1 host calls are synchronously bounded: implementations may not retain guest linear-memory views, GC references, or other borrowed guest storage after return. Nonblocking I/O uses `ERR_AGAIN` plus `wpsi-poll`; concurrency and actor/task scheduling remain outside the ABI.\n"
addition = anchor + "- WPSI uses one global `abi_version()` and no independently versioned profiles or feature-query API. Import presence and exact Core Wasm type matching are authoritative for optional feature support.\n"
if anchor not in changelog:
    raise SystemExit("CHANGELOG decision anchor not found")
changelog = changelog.replace(anchor, addition, 1)
old = """\n### Deferred

- Profile-specific version negotiation.
"""
if old not in changelog:
    raise SystemExit("CHANGELOG deferred section not found")
changelog = changelog.replace(old, "", 1)
write("CHANGELOG.md", changelog)


# Hygiene: no stale profile-version deferral or feature-query proposal should remain.
for rel in [
    "SPEC.md", "spec/behavior.md", "docs/open-questions.md", "docs/design.md",
    "docs/runtime-implementation.md", "spec/tests/README.md", "README.md",
    "ROADMAP.md", "CHANGELOG.md",
]:
    text = read(rel)
    stale = [
        "profile-specific version negotiation",
        "Do profiles need independent versions?",
        "Should there be a compact scalar feature-query API?",
    ]
    for needle in stale:
        if needle in text:
            raise SystemExit(f"stale versioning question remains in {rel}: {needle}")

print("closed WPSI 0.1 profile versioning and feature-detection question")
