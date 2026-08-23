# Facet 0.1 release semantics

This document is normative for Facet 0.1.

It resolves behavior that was left ambiguous by `SPEC.md` and `spec/behavior.md` during implementation of the Wago reference runtime. For the cases listed here, this document takes precedence over older Facet 0.1 text that is incomplete or permits multiple observable interpretations.

## Filesystem final components

`path_open_*` and `path_stat_*` operate on a resolved target.

For these operations, a final `.` names the resolved current directory. A final `..` is resolved normally and returns `ERR_PERMISSION` if resolution would move above the supplied directory capability.

For these operations, a trailing `/` requires the resolved target to be a directory. If the target exists and is not a directory, return `ERR_NOT_DIRECTORY`.

Entry operations require a concrete final directory-entry name. The following operations return `ERR_INVALID` when the final component is `.`, `..`, or empty because the path ends in `/`:

- `path_create_dir_*`;
- `path_remove_*`;
- both source and destination of `path_rename_*`;
- both source and destination entry positions of `path_link_*`;
- the destination of `path_symlink_*`;
- `path_readlink_*`.

Intermediate `.` and `..` components continue to use the capability-beneath rules in `spec/behavior.md`.

## Filesystem flag combinations

Facet 0.1 defines these combinations exactly:

- `OPEN_EXCLUSIVE` without `OPEN_CREATE` returns `ERR_INVALID`;
- `OPEN_TRUNCATE` without requested `RIGHT_WRITE` returns `ERR_CAPABILITY`;
- `OPEN_APPEND` without requested `RIGHT_WRITE` returns `ERR_CAPABILITY`;
- `OPEN_DIRECTORY` combined with `OPEN_CREATE` or `OPEN_TRUNCATE` returns `ERR_INVALID`;
- `path_remove_*` requires exactly one of `REMOVE_FILE` or `REMOVE_DIRECTORY`; zero or both bits returns `ERR_INVALID`;
- rename flags `0` and `RENAME_REPLACE` both request ordinary replacement semantics;
- `RENAME_NO_REPLACE` and `RENAME_EXCHANGE` are mutually exclusive with every other rename mode; any combined rename mode returns `ERR_INVALID`;
- `fd_set_flags(fd, 0)` is a valid no-op for a preopen or directory descriptor;
- setting `FD_APPEND` or `FD_NONBLOCK` on a preopen or directory descriptor returns `ERR_INVALID`.

These are scalar, descriptor, or authority validation rules. Validation completes before the external filesystem is mutated.

## Directory-entry inode semantics

The `inode` field returned by directory iteration is an opaque filesystem identity hint.

`inode == 0` means that a stable inode-like value is unavailable. A guest MUST NOT treat zero as a real object identity.

When a runtime returns a nonzero inode for an entry, the value MUST identify the object named by that entry at the time the entry snapshot is created. For an unchanged entry that continues to name the same object, a runtime MUST return the same nonzero inode after `dir_iter_rewind` during the lifetime of that directory resource.

The runtime MUST obtain entry metadata from the directory enumeration itself or relative to the directory capability. It MUST NOT resolve an entry through a process-global current working directory or another ambient namespace.

If enumeration succeeds but an optional descriptor-relative metadata query cannot produce a stable inode, the runtime MAY return inode zero instead of failing iteration.

## Preopen authority identity

A configured preopen selects one directory authority.

The runtime MUST materialize or otherwise pin that authority before guest code can observe the preopen. After the authority is selected, later changes to an ambient host pathname MUST NOT cause that Facet preopen to resolve to a different directory.

Two guest instances created from one activated configuration MUST NOT receive different underlying directory authority merely because the host pathname used to configure the preopen was renamed, replaced, or retargeted between guest calls.

## Manifest preopen rights

The Facet conformance manifest distinguishes an omitted `rights` member from an explicit empty array.

- omitted `rights` means the harness MAY apply its documented default preopen rights;
- `rights: []` means exactly zero Facet rights are granted.

A harness or runtime adapter MUST preserve this distinction. It MUST NOT translate an explicit empty rights array into a default grant.

The same authority rule applies to embedding APIs: a representable zero-rights preopen MUST remain zero authority after normalization.

## Canonical structural import signatures

`spec/imports.wat` is the canonical Core WebAssembly import contract for Facet 0.1. An implementation MUST reject an importing module whose Facet function signature is not structurally compatible with the canonical declaration, even when the runtime's native host-function registry represents reference values only through a coarser ABI category.

In particular, a canonical `(ref array)` parameter is a non-null abstract array reference. It MUST NOT be silently accepted as `(ref null array)`, `(ref any)`, an exact reference, or an arbitrary caller-defined heap type merely because those representations share one host ABI slot category.

The allocating string and readlink imports are deliberate templates. For those imports, the importing module selects the concrete nullable result array type. The selected type MUST have the storage class required by the import suffix (`i8`, `i16`, or `i32`). A mismatched concrete result type is a module-linking or instantiation failure, not a guest-visible runtime `ERR_TYPE` fallback.

A runtime MAY enforce these rules when it binds host imports, when it validates the importing module, or immediately before instantiation, provided no guest code executes with an incompatible Facet signature.

## DNS names

Facet 0.1 DNS names are ASCII DNS presentation strings.

After decoding the selected `_i8`, `_i16`, or `_i32` representation, every code point in a DNS name MUST be in `U+0001..U+007F`. An embedded U+0000 or any non-ASCII code point returns `ERR_INVALID`.

Facet 0.1 performs no implicit IDNA, UTS #46, locale, or Unicode-hostname conversion. A guest that needs an internationalized domain name MUST convert it to an ASCII IDNA form before calling Facet.

The runtime supplies the resulting ASCII name to its resolver without adding a NUL byte. Embedder resolver search-domain policy MAY still apply when that authority is granted.

## DNS resolution lifetime

A DNS operation MUST NOT create an indefinitely unbounded host wait. The runtime MUST impose a finite implementation-defined resolver deadline or an equivalent finite cancellation policy.

If the host runtime exposes cancellation of the active guest invocation to the resolver integration, cancellation of that invocation SHOULD cancel the outstanding resolver operation. A cancellation that terminates resolution maps to `ERR_CANCELED`. Resolver deadline expiry maps to `ERR_TIMED_OUT`.

Runtime or plugin shutdown MUST be able to cancel outstanding resolver work that it owns. An implementation whose host-callback API does not expose the active invocation cancellation context MUST still use a finite resolver deadline; lack of such an API does not permit an unbounded background resolver call.

The precise finite deadline is implementation-defined in Facet 0.1 and SHOULD be documented by the runtime adapter.

## Nonblocking stream connection completion

After a nonblocking `socket_connect` returns `ERR_AGAIN`, a later retry MUST NOT report success merely because `SO_ERROR` is currently zero.

The runtime first observes writable, error, or hangup readiness for the socket. If none is ready, the retry returns `ERR_AGAIN`. After readiness, the runtime reads the platform connection error state. Zero means connected; a nonzero platform error maps to the corresponding Facet error.

This is the same readiness sequence exposed to a guest through `facet-poll`.

## Cross-device filesystem errors

An `EXDEV`-equivalent error produced specifically by capability-beneath path resolution maps to `ERR_PERMISSION` because it indicates an attempted escape from the supplied directory authority.

An `EXDEV`-equivalent error from an otherwise-authorized filesystem operation, such as rename or hard-link creation across mount points, does not indicate a Facet capability failure. If no more specific portable Facet category applies, return `ERR_OTHER`.

## Descriptor state after partial I/O

If an implementation temporarily changes host descriptor flags to implement Facet semantics, it MUST NOT continue using a descriptor whose host flags can no longer be synchronized with the runtime's logical descriptor state.

If an externally visible partial write has already occurred, the operation may report the transferred byte count according to Facet partial-I/O rules, but the descriptor MUST then be poisoned, closed, or retain a terminal deferred error before any later operation.

## Resource exhaustion

A Facet runtime MUST impose finite implementation limits on guest-controlled host allocations that are not already bounded by guest memory itself. This includes at least:

- iovec counts;
- aggregate vectored-I/O bytes staged in host memory;
- decoded text units copied into host allocations;
- active poll registrations and timers.

Exceeding an implementation resource budget returns `ERR_QUOTA` before the unbounded host allocation is attempted.

Directory iteration SHOULD stream entries instead of materializing an entire directory into host memory.

## Portable errno mappings

When the host reports an error with a direct Facet category, implementations use that category rather than `ERR_OTHER`. Facet 0.1 includes these stable mappings:

- I/O failure -> `ERR_IO`;
- allocation failure -> `ERR_NO_MEMORY`;
- numeric/platform overflow -> `ERR_OVERFLOW`;
- cancellation -> `ERR_CANCELED`;
- deadline/timeout expiry -> `ERR_TIMED_OUT`;
- storage quota exhaustion -> `ERR_QUOTA`.

Unknown or platform-specific errors continue to use `ERR_OTHER` when no accurate portable category exists.
