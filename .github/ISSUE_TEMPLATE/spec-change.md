---
name: Specification change
about: Propose a normative Facet addition or change
title: "spec: "
labels: specification
---

## Problem

Describe the system-interface or portability problem.

Use short sentences.

## Proposed behavior

Describe the guest-visible behavior.

State one normative rule per sentence when practical.

## Core Wasm signatures

List each new or changed import signature.

```wat
;; imports here
```

## Representations

Select each affected representation family.

- [ ] Memory32
- [ ] Memory64
- [ ] GC array
- [ ] Scalar or resource only

## Multi-memory behavior

Explain how the operation selects memory.

Explain whether one call can use more than one memory.

## Capability and security impact

State the authority that the operation consumes or creates.

List the untrusted values that the runtime must validate.

## Runtime implementation notes

Explain whether a runtime can implement this with ordinary imported functions.

List special implementation requirements when applicable, such as:

- pinning;
- no-GC scopes;
- barriers;
- layout-independent fallbacks.

## Conformance tests

List tests that distinguish a conforming implementation from a nonconforming implementation.

## Compatibility

State whether the proposal changes an existing published signature.

If it is incompatible, explain why a new import name is or is not sufficient.

## Documentation accessibility

- [ ] Uses the terms in `docs/terminology.md`.
- [ ] Follows `docs/writing-style.md`.
- [ ] Uses one normative requirement per sentence where practical.
- [ ] Keeps the actor clear.
- [ ] Does not change normative meaning only to simplify wording.
