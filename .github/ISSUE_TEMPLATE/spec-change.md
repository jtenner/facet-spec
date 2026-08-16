---
name: Specification change
about: Propose a normative WPSI addition or change
title: "spec: "
labels: specification
---

## Problem

What system-interface or portability problem needs to be solved?

## Proposed semantics

Describe the operation and its observable behavior.

## Core Wasm signatures

List every new or changed import signature.

```wat
;; imports here
```

## Representations

Which representation families are affected?

- [ ] Memory32
- [ ] Memory64
- [ ] GC array
- [ ] Scalar/resource only

## Multi-memory behavior

Explain how the operation selects or interacts with memories.

## Capability/security impact

What authority does the operation consume or create? What untrusted values must be validated?

## Runtime implementation notes

Can existing runtimes implement this with ordinary host imports? Are pinning, no-GC scopes, barriers, or layout-independent fallbacks required?

## Conformance tests

List tests that distinguish conforming and non-conforming implementations.

## Compatibility

Does this modify an existing published signature or can it be introduced under a new import name?
