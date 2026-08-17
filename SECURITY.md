# Security

WPSI is a specification for a sandbox-facing system ABI. Security properties are therefore part of the interface contract rather than optional implementation details.

## Security model

A conforming implementation must treat all guest-provided values as untrusted, including handles, memory indexes, offsets, lengths, `wtf` booleans, flags, GC references, and dynamic GC types.

Implementations must validate:

- resource handles and resource ownership;
- memory index existence and address width;
- pointer-range arithmetic using overflow-safe checks;
- GC reference kind, dynamic array element type, and mutability;
- text well-formedness under the import's code-unit width and strict/WTF mode;
- path restrictions, including embedded NUL and capability-boundary traversal;
- requested rights against the parent capability;
- filesystem traversal, including traversal through symbolic links;
- network actions against host-granted network authority.

A preopen named `~` must not imply ambient access to the host user's home directory. Like every filesystem root, it grants only the directory authority explicitly supplied by the embedder. Host filesystem paths and network access remain explicit capabilities.

A borrowed GC backing view must never outlive the synchronous call or collector scope that makes its address stable.

WTF mode must be reversible where it is used to preserve non-Unicode host units. Implementations must not silently replace unrepresentable values with U+FFFD or otherwise collapse distinct host names into the same guest-visible string.

## Reporting vulnerabilities

Please do not publish exploitable vulnerabilities in a public issue before a fix or mitigation is available.

Use GitHub's private vulnerability-reporting mechanism for this repository when available. If private reporting is not available, contact the repository owner privately before publishing details.

Useful reports should include:

- the affected WPSI function or rule;
- the relevant runtime or implementation;
- a minimal Wasm reproducer when possible;
- whether the issue crosses a capability, memory, instance, GC-domain, or host boundary;
- expected and observed behavior.

Because WPSI is currently a draft specification, ambiguities that could cause independent runtimes to enforce different security boundaries should also be treated as security-relevant specification bugs.
