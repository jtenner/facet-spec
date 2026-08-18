# Security

Facet is a system ABI that faces untrusted guest input.

Security rules are part of the interface contract.

They are not optional implementation details.

## Security model

A conforming runtime MUST treat every guest-provided value as untrusted.

This includes:

- resource handles;
- memory indexes;
- offsets;
- lengths;
- `wtf` values;
- flags;
- GC references;
- dynamic GC types.

The runtime MUST validate resource handles before use.

The runtime MUST verify that a resource belongs to the current Facet instance.

The runtime MUST validate each memory index.

The runtime MUST validate the selected memory address width.

The runtime MUST use overflow-safe arithmetic for pointer and range checks.

The runtime MUST validate GC reference kind.

The runtime MUST validate the dynamic array element type.

The runtime MUST validate destination mutability.

The runtime MUST validate text according to the selected code-unit width and `wtf` mode.

The runtime MUST reject embedded NUL in filesystem paths.

The runtime MUST prevent a path from escaping its directory capability.

The runtime MUST apply the same boundary to symbolic-link traversal.

The runtime MUST validate requested rights against the parent capability.

The runtime MUST enforce network authority granted by the embedder.

### Optional `~` preopen

A preopen named `~` is an ordinary directory capability.

The name MUST NOT imply ambient access to the operating-system user's home directory.

It grants only the directory authority that the embedder explicitly supplied.

### Borrowed GC and linear-memory storage

A borrowed GC backing view MUST NOT outlive the synchronous call or collector scope that makes its address valid.

The same rule applies to a borrowed linear-memory view.

The runtime MUST NOT retain borrowed guest storage for deferred work after the imported function returns.

### WTF mode

WTF mode must preserve distinct external values when the specification defines a reversible mapping.

The runtime MUST NOT silently replace an unrepresentable value with U+FFFD.

The runtime MUST NOT collapse distinct external names into one guest-visible string through lossy replacement.

## Reporting vulnerabilities

Do not publish an exploitable vulnerability in a public issue before a fix or mitigation is available.

Use GitHub private vulnerability reporting for this repository when it is available.

If private reporting is not available, contact the repository owner privately before you publish exploit details.

A useful report should include:

- the affected Facet function or rule;
- the affected runtime or implementation;
- a minimal Wasm reproducer when practical;
- the boundary that the issue crosses, if any;
- expected behavior;
- observed behavior.

Relevant boundaries include:

- capability boundaries;
- memory boundaries;
- instance boundaries;
- GC-domain boundaries;
- external system boundaries.

Facet is a draft specification.

An ambiguity that causes independent runtimes to enforce different security boundaries is also a security-relevant specification bug.
