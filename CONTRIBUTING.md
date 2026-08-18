# Contributing to WPSI

WPSI is an experimental system-interface specification.

Contributions should prefer small and explicit Core WebAssembly mechanisms.

Avoid adding abstraction layers when ordinary Core WebAssembly imports can express the same behavior.

Read these documents before you make a normative change:

- [`docs/terminology.md`](docs/terminology.md);
- [`docs/writing-style.md`](docs/writing-style.md);
- [`SPEC.md`](SPEC.md);
- [`spec/behavior.md`](spec/behavior.md).

## Specification changes

A normative proposal should answer these questions:

1. What system operation or portability problem does the change solve?
2. What exact Core WebAssembly signature or representation does it use?
3. What does it mean for Memory32, Memory64, multi-memory, and Wasm GC when those features apply?
4. What capability or security rules apply?
5. What errors and bounds rules apply?
6. Can existing runtimes implement the change with ordinary imported functions?
7. What conformance tests distinguish a correct implementation from an incorrect implementation?

A published stable function signature requires strong compatibility protection.

Do not silently change a stable incompatible signature.

Use a new import name for an incompatible replacement.

## Design constraints

Prefer:

- ordinary Core WebAssembly imports;
- explicit representation suffixes;
- deterministic validation;
- direct-access or single-copy implementation opportunities;
- no distinguished linear memory;
- runtime-independent observable behavior;
- opt-in extensions for features that are not universally implementable.

Avoid:

- hidden dependence on memory 0;
- serialization through unrelated scratch memory;
- linker-specific import overloading;
- ABI behavior that depends on one runtime's private object layout;
- ambient external authority that bypasses resource capabilities.

## Documentation style

Human-facing documentation should follow [`docs/writing-style.md`](docs/writing-style.md).

Use the terms in [`docs/terminology.md`](docs/terminology.md).

In particular:

- use one requirement per sentence;
- use short sentences where practical;
- name the actor when it is known;
- prefer active voice;
- use one term for one concept;
- keep exact normative keywords;
- do not simplify away technical meaning.

A documentation-only rewrite MUST NOT change ABI behavior.

## Conformance tests

Contributions to the test suite are welcome.

Add normative tests under [`spec/tests`](spec/tests).

Follow the runner contract in [`spec/tests/README.md`](spec/tests/README.md).

A test should isolate one important observable behavior.

Preserve sentinels around writable ranges.

Avoid public-network dependencies.

Distinguish invalid guest input from an engine trap or runtime crash.

Do not add a manifest field or operation when an existing `WebAssembly/wasi-testsuite` convention can express the same setup.

Tests that need only guest-visible assertions should remain pure WAST.

Use same-basename JSON only when the test needs external setup or interaction, such as:

- arguments;
- environment values;
- preopens;
- process output;
- deterministic network interaction.

After you add or change tests, run:

```bash
python3 spec/tests/tools/generate_suite.py
python3 spec/tests/tools/check_suite.py
python3 spec/tests/tools/parse_wast.py --wasm-tools wasm-tools
```

Reduce each implementation bug, security finding, or fuzzing regression to the smallest permanent conformance test that reproduces it when practical.

## Pull requests

Keep each specification change focused.

When an ABI function changes, update these files together as applicable:

- `SPEC.md`;
- `spec/imports.wat`;
- `spec/behavior.md`;
- conformance tests;
- conformance documentation;
- `CHANGELOG.md`.

Include boundary cases when they are relevant.

Examples include:

- invalid memory indexes;
- Memory32 and Memory64 mismatches;
- arithmetic overflow;
- short reads and writes;
- partial GC-array element updates;
- GC movement during an imported call;
- immutable GC destination arrays;
- malformed text;
- path traversal and symbolic-link escape attempts;
- stale handles;
- cross-instance handles.

## Formatting

Use normative **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** consistently.

WAT examples must be valid Core WebAssembly text for the feature set that they demonstrate.

Use backticks for function names, constants, fields, and Core WebAssembly types in prose.

## License

By contributing, you agree that your contribution is licensed under the repository's MIT License.
