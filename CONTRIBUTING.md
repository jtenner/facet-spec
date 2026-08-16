# Contributing to WPSI

WPSI is an experimental systems-interface specification. Contributions should favor small, explicit Core WebAssembly mechanisms over new abstraction layers.

## Specification changes

A normative change should explain:

1. the system operation or portability problem being solved;
2. the exact Core WebAssembly signature or representation involved;
3. behavior for Memory32, Memory64, multi-memory, and Wasm GC where applicable;
4. capability and sandboxing implications;
5. failure and bounds-checking behavior;
6. whether existing runtimes can implement the change without special linker semantics;
7. conformance tests that distinguish correct and incorrect implementations.

Changes to published function signatures require especially strong justification. Once a signature is declared stable, incompatible changes should use a new import name rather than silently changing the old ABI.

## Design constraints

Prefer:

- ordinary Core Wasm imports;
- explicit representation suffixes;
- deterministic validation;
- zero-copy or single-copy implementation opportunities;
- no distinguished linear memory;
- runtime-independent observable semantics;
- opt-in extensions for functionality not universally implementable.

Avoid:

- hidden dependence on memory 0;
- canonical serialization through an unrelated scratch memory;
- linker-specific import overloading;
- ABI behavior that depends on one runtime's private object layout;
- host ambient authority that bypasses resource capabilities.

## Pull requests

Keep specification changes focused. Update `SPEC.md`, `spec/imports.wat`, and relevant conformance documentation together when an ABI function changes.

Where possible, include examples or tests that exercise boundary conditions such as:

- invalid memory indexes;
- Memory32/Memory64 mismatches;
- arithmetic overflow;
- short reads and writes;
- partial GC-array element updates;
- GC movement during host interaction;
- immutable GC destination arrays;
- malformed text;
- path traversal and symlink escapes;
- stale or cross-instance handles.

## Formatting

Markdown should use normative **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** language consistently.

WAT examples should be valid Core WebAssembly text for the feature set they demonstrate.

## License

By contributing, you agree that your contributions are licensed under the repository's MIT License.
