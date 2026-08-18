# Facet 0.1 Behavioral Semantics

**Status:** Draft, normative  
**Applies to:** Facet 0.1  
**Companion to:** [`../SPEC.md`](../SPEC.md)

This document is part of the normative Facet 0.1 specification.

`SPEC.md` defines the public ABI, signatures, constants, representations, and profiles.

This document defines behavior that independent runtimes must implement consistently.

Facet follows established WASI behavior when that behavior maps cleanly to the Facet model.

Facet remains different in these areas:

- direct Core WebAssembly imports;
- explicit multi-memory addressing;
- Memory64;
- direct WebAssembly GC-array buffers.

Use [`../docs/terminology.md`](../docs/terminology.md) for the project terminology.

## 1. Validation and error precedence

A Facet function MUST validate guest-controlled input in the order below unless that function defines a different order.

### Stage 1: scalar form

Validate scalar-only constraints first.

Examples include:

- the `wtf` boolean;
- enum values;
- flag masks;
- reserved bits;
- mutually incompatible options;
- numeric domains such as port ranges.

### Stage 2: resource handles

Validate handles in parameter order.

A zero handle returns `ERR_BAD_HANDLE`.

A stale handle returns `ERR_BAD_HANDLE`.

A closed handle returns `ERR_BAD_HANDLE`.

An unknown handle returns `ERR_BAD_HANDLE`.

A handle for the wrong resource kind returns `ERR_BAD_HANDLE`.

### Stage 3: resource state and authority

Validate resource state before the runtime accesses guest buffers or external namespaces.

Validate descriptor rights at this stage.

Validate authority granted by the embedder at this stage.

### Stage 4: guest representation

Resolve the selected linear memory or GC reference.

Validate the memory address width.

Validate the GC array kind and dynamic element storage type.

For a destination GC array, validate mutability.

### Stage 5: ranges

Validate indexes, offsets, lengths, and descriptor tables.

Use checked arithmetic.

The runtime MUST detect arithmetic overflow before it computes an address or starts an external operation.

### Stage 6: text

Validate the code-unit representation selected by the import name.

Apply strict or WTF text rules when the operation uses text.

### Stage 7: namespace resolution

Resolve filesystem paths, symbolic links, DNS names, and similar namespace inputs.

The runtime MUST apply the capability boundary during this stage.

### Stage 8: external operation

Perform the operating-system, virtual-filesystem, socket, clock, random, or other external operation.

### Stage 9: normalization

Translate the external result into Facet result values and Facet error codes.

### 1.1 Which failure wins

The first failing stage determines the returned Facet error.

Within one stage, validate parameters from left to right in function-signature order.

The runtime MAY combine or reorder internal checks when the guest-visible result is identical.

The runtime MUST NOT cause a guest-visible mutation before stages 1 through 7 succeed.

The runtime MUST NOT cause an externally visible side effect before stages 1 through 7 succeed.

Reading a guest source buffer for validation is not a guest-visible mutation.

Before validation succeeds, the runtime MUST NOT:

- write to an external resource;
- create a file;
- consume a datagram;
- advance a file position;
- modify a guest destination buffer.

This validation order makes failures reproducible across runtimes.

It also prevents external behavior from deciding which invalid guest input is reported first.

### 1.2 Opaque handle values

A Facet resource handle is an opaque `i32` token that belongs to one Facet instance.

Only the value `0` has defined bit-level meaning.

The value `0` is always invalid.

No nonzero bit, range, subfield, ordering relation, or numeric pattern is portable Facet information.

A guest MUST NOT inspect a handle to infer:

- resource kind;
- table position;
- generation;
- authority;
- age;
- runtime implementation strategy.

The runtime can choose any private handle encoding that preserves the Facet rules.

A stale or closed handle MUST return `ERR_BAD_HANDLE`.

A stale or closed handle MUST NOT become authority over an unrelated live resource through internal slot reuse.

### 1.3 Synchronous call lifetime

Every Facet imported function has a bounded synchronous lifetime.

Borrowed guest storage is valid only during the call that borrowed it.

Before the runtime returns to the guest, it MUST release every borrow of guest linear memory.

Before the runtime returns to the guest, it MUST release every borrowed Wasm GC reference or backing view created for the operation.

The runtime MUST NOT arrange for later work to access borrowed guest storage.

This prohibition includes later work performed by:

- a callback;
- a worker;
- an operating-system request;
- a future completion;
- another deferred action.

The runtime MAY copy guest data into independent runtime-owned storage.

The runtime MAY retain ordinary Facet resource state when an operation requires it.

Retained state MUST NOT depend on the lifetime or location of guest storage from which it was derived.

Multiple guest execution contexts MAY run concurrently.

Each Facet call still completes or returns `ERR_AGAIN` before its guest-storage borrows end.

A scheduler can use `facet-poll` to wait for readiness and retry a nonblocking operation.

## 2. Error semantics

Facet has its own compact numeric error namespace.

The numeric values in `SPEC.md` are normative Facet values.

They do not have to equal POSIX `errno` values.

They do not have to equal WASI enum ordinals.

Facet follows WASI and POSIX error categories when practical.

| Facet error | Meaning |
| --- | --- |
| `ERR_OK` | The operation completed successfully. |
| `ERR_PERMISSION` | Facet does not permit the operation. Use this for a forbidden capability-boundary escape. |
| `ERR_NO_ENTRY` | The requested filesystem entry, DNS name, or similar named entry does not exist. |
| `ERR_IO` | An external I/O failure occurred and no more specific portable category applies. |
| `ERR_BAD_HANDLE` | The handle is zero, stale, closed, unknown, or for the wrong resource kind. |
| `ERR_AGAIN` | The operation would block, or a temporary condition requires retry. |
| `ERR_NO_MEMORY` | The runtime or external system could not allocate a required bounded resource. |
| `ERR_ACCESS` | Facet authority exists, but the external access-control system denies access. |
| `ERR_BUSY` | The resource conflicts with another active operation or state. |
| `ERR_EXISTS` | The requested destination or entry already exists. |
| `ERR_NOT_DIRECTORY` | The operation requires a directory, but the object is not a directory. |
| `ERR_IS_DIRECTORY` | The operation requires a non-directory object, but the object is a directory. |
| `ERR_INVALID` | A scalar value, flag combination, resource state, or semantic value is invalid and no more specific error applies. |
| `ERR_FILE_TOO_LARGE` | The file or requested extent exceeds an implementation or filesystem limit. |
| `ERR_NO_SPACE` | The backing storage has insufficient free space. |
| `ERR_READ_ONLY` | The operation requests mutation through a read-only filesystem or directory capability. |
| `ERR_PIPE` | A broken pipe or equivalent write-side stream failure occurred. |
| `ERR_RANGE` | A value has the correct kind but is outside the semantic range for the operation. |
| `ERR_NOT_EMPTY` | The directory is not empty. |
| `ERR_LOOP` | Symbolic-link expansion exceeded a limit, or the operation forbids following the final symbolic link. |
| `ERR_NAME_TOO_LONG` | A path component or name exceeds an implementation or filesystem limit. |
| `ERR_NOT_SUPPORTED` | The operation or option is valid Facet but is not supported by the runtime or external system. |
| `ERR_OVERFLOW` | A required value cannot be represented in the Facet result type. |
| `ERR_ILLEGAL_SEQUENCE` | Text cannot be represented or decoded losslessly in the selected representation and mode. |
| `ERR_FAULT` | A selected linear memory or byte range is invalid or out of bounds. |
| `ERR_TYPE` | The guest representation has the wrong physical type or mutability. |
| `ERR_QUOTA` | An explicit Facet or embedder policy quota was exceeded. |
| `ERR_CANCELED` | A supported external mechanism canceled the operation. Facet 0.1 does not otherwise require cancellation support. |
| `ERR_ADDRESS_IN_USE` | The requested socket address or port is already in use. |
| `ERR_ADDRESS_INVALID` | The socket address is malformed or invalid for the requested operation. |
| `ERR_CONNECTION_REFUSED` | The remote endpoint refused the connection. |
| `ERR_CONNECTION_RESET` | A connected or pending connection was reset or aborted. |
| `ERR_NOT_CONNECTED` | The operation requires a connected socket, but the socket is not connected. |
| `ERR_TIMED_OUT` | The operation exceeded its timeout. |
| `ERR_HOST_UNREACHABLE` | Routing reports that the destination host is unreachable. |
| `ERR_NETWORK_UNREACHABLE` | Routing reports that the destination network is unreachable. |
| `ERR_PROTOCOL` | The operation is incompatible with the socket protocol or a protocol failure has no more specific category. |
| `ERR_CAPABILITY` | The embedder did not grant the authority required by the operation, or that authority was attenuated away. |
| `ERR_END` | Reserved for end-of-sequence use by extensions. Facet 0.1 sequences with a `done` result use `done` with `ERR_OK`. |
| `ERR_OTHER` | An external failure has no stable portable Facet classification. |

### 2.1 Capability, permission, and access

`ERR_CAPABILITY`, `ERR_PERMISSION`, and `ERR_ACCESS` have different meanings.

Use `ERR_CAPABILITY` when the embedder never granted the required authority or when the authority was attenuated away.

Use `ERR_PERMISSION` when Facet itself prohibits the operation.

A filesystem path that tries to escape its directory capability returns `ERR_PERMISSION`.

Use `ERR_ACCESS` when Facet authority exists but the external access-control system denies the operation.

A runtime SHOULD map an embedder network-policy denial to `ERR_CAPABILITY`.

A runtime SHOULD map an operating-system `EACCES`-like filesystem denial to `ERR_ACCESS`.

A runtime SHOULD map an `EPERM`-like operation denial to `ERR_PERMISSION`.

### 2.2 Unknown external errors

The runtime MUST NOT guess an unrelated portable error category only to avoid `ERR_OTHER`.

If the runtime cannot classify an external failure faithfully, it MUST return `ERR_OTHER`.

### 2.3 Validation failures are side-effect free

If a function fails during validation stages 1 through 7, all non-error results MUST be zero.

The operation MUST NOT modify a guest destination in this case.

The operation MUST NOT modify externally visible state in this case.

### 2.4 Partial stream I/O

A byte-stream read or write can transfer some bytes before an external error occurs.

If the operation transferred one or more bytes, Facet returns the transferred byte count with `ERR_OK`.

A later operation can report the deferred external condition.

If the operation transferred zero bytes, return the external condition normally.

EOF is:

```text
bytes_read = 0
errno      = ERR_OK
```

A nonblocking operation that cannot transfer data immediately returns zero bytes and `ERR_AGAIN`.

### 2.5 Datagram atomicity

A datagram send is atomic from the Facet caller's perspective.

Either the runtime accepts the complete datagram and returns the full byte count with `ERR_OK`, or it returns zero bytes with an error.

A datagram receive MAY copy a prefix when the destination buffer is too small.

In this case, the receive succeeds and sets:

```text
MSG_TRUNCATED = 1 << 0
```

in `message_flags`.

The returned byte count is the number of bytes copied into the guest buffer.

## 3. Filesystem path and symbolic-link resolution

Facet path resolution uses a capability-beneath model.

Every path operation is constrained by its supplied directory capability.

### 3.1 Relative paths only

Every Facet path is relative to the supplied directory capability.

The logical directory separator is `/`.

A path that begins with `/` returns `ERR_PERMISSION`.

Facet has no process-global current working directory from the operating system.

A Facet path operation MUST NOT use an ambient operating-system root.

The raw Facet path grammar does not give `~` special meaning.

If the embedder provides a preopen whose display name is `~`, a higher-level binding MAY interpret `~/x` as convenience syntax.

The binding can select that preopen and pass `x` as the relative path.

Without that higher-level rule, a `~` path component is an ordinary filename component.

### 3.2 `.` and `..`

`.` names the current directory component.

`..` removes one resolved directory component.

If `..` would move above the supplied directory capability, resolution returns `ERR_PERMISSION`.

A path MUST NOT leave the capability temporarily and later re-enter it.

### 3.3 Intermediate symbolic links

The runtime MAY follow intermediate symbolic links while it resolves a path.

Every expansion MUST remain beneath the supplied directory capability.

If a symbolic link expands to an absolute or rooted external path, resolution returns `ERR_PERMISSION`.

If following a symbolic link would move outside the base capability, resolution returns `ERR_PERMISSION`.

The runtime MUST preserve this rule during concurrent filesystem rename, unlink, and symbolic-link changes.

A check-then-open implementation that permits a race to escape the capability is nonconforming.

### 3.4 Final symbolic-link component

The final path component uses operation-specific rules.

#### `path_open_*`

`path_open_*` follows the final symbolic link unless `OPEN_NOFOLLOW` is present.

If the final object is a symbolic link and `OPEN_NOFOLLOW` is present, return `ERR_LOOP`.

#### `path_stat_*`

`path_stat_*` follows the final symbolic link only when `PATH_FOLLOW_SYMLINK` is present.

Without that flag, return metadata for the symbolic link itself.

#### `path_link_*`

`path_link_*` follows the final source symbolic link only when `PATH_FOLLOW_SYMLINK` is present.

The destination final component is never followed.

#### `path_readlink_*`

`path_readlink_*` never follows the final component.

The final component MUST be a symbolic link.

#### create, remove, rename, and symlink destination

These operations act on the final directory entry instead of following it.

They still resolve intermediate components beneath the supplied directory capability.

The runtime MAY use an implementation-defined symbolic-link expansion limit.

Exceeding that limit returns `ERR_LOOP`.

### 3.5 Creating and reading symbolic links

Creating a symbolic link whose target begins with `/` returns `ERR_PERMISSION`.

A relative target that contains `..` MAY be stored.

The runtime enforces the capability boundary later if that link is followed.

`path_readlink_*` returns the stored target text without resolving it.

If an externally created symbolic link contains an absolute or rooted target, `path_readlink_*` returns `ERR_PERMISSION`.

## 4. Settled Wasm GC array rules

The following rules are fixed for Facet 0.1.

1. Raw GC-array byte offsets and byte lengths are unsigned `i64` values.
2. `array<i16>`, `array<i32>`, `array<i64>`, and `array<v128>` raw-buffer operations MUST support byte ranges that begin or end inside an element.
3. GC-array imports use the abstract non-null `(ref array)` parameter.
4. The import name determines the required dynamic storage type.
5. A source array used by a write or send MAY be immutable.
6. A destination array used by a read, receive, or random-fill MUST be mutable.
7. A dynamic kind, storage-type, or destination-mutability mismatch returns `ERR_TYPE`.
8. Nested GC `readv` and `writev` use complete selected child arrays only.
9. `first` and `count` select the children.
10. Facet 0.1 has no per-child slice descriptors.
11. The runtime MUST validate every selected nested child before I/O begins.
12. A later invalid child MUST NOT cause partial I/O through an earlier child.
13. These rules define observable values only.
14. These rules do not require contiguous physical GC storage.

## 5. Text and host-originated string transfer

Facet does not use an encoding enum.

Facet does not use resource handles only to transport strings.

### 5.1 Representation and WTF mode

The import name selects the text width:

```text
_i8  -> UTF-8 / WTF-8 code units
_i16 -> UTF-16 / WTF-16 code units
_i32 -> 32-bit code points
```

Every text operation receives `wtf: i32`:

```text
0 = strict Unicode
1 = WTF / surrogate-sentinel mode
```

Any other value returns `ERR_INVALID`.

The runtime MUST reject the invalid `wtf` value before it modifies a guest destination or resolves an external text namespace.

Strict mode rejects malformed UTF-8.

Strict mode rejects unpaired UTF-16 surrogates.

Strict mode rejects surrogate-valued `i32` code points.

Strict mode rejects values above `0x10ffff`.

Each of these cases returns `ERR_ILLEGAL_SEQUENCE`.

WTF mode permits surrogate values as reversible sentinels.

WTF mode MUST NOT silently substitute U+FFFD for an external value.

For a byte-oriented external namespace, invalid UTF-8 bytes MAY map to `U+DC80..U+DCFF` as defined by the specification.

For a UTF-16 external namespace, preserve unpaired surrogate code units directly.

### 5.2 Length queries

Each stable indexed source exposes width-specific length operations.

Examples include `args_len_i8`, `args_len_i16`, and `args_len_i32`.

The returned length is the exact number of required code units.

The length excludes a terminator.

An invalid source index returns zero and `ERR_RANGE`.

An invalid `wtf` value returns zero and `ERR_INVALID`.

A source value that cannot be represented losslessly returns zero and `ERR_ILLEGAL_SEQUENCE`.

### 5.3 Guest-owned destinations

`*_read_mem32_i*`, `*_read_mem64_i*`, and `*_read_into_array_i*` copy the complete represented string into guest-owned storage.

The destination must have enough capacity for the complete value.

If capacity is too small, return zero units and `ERR_RANGE`.

In this case, the runtime MUST NOT modify the destination.

On success, `units_written` is the complete code-unit length.

The runtime does not append a NUL terminator.

Storage after the represented value remains unchanged.

A zero-capacity destination succeeds only for an empty string.

For a GC-array destination, offset and capacity are measured in array elements.

A GC-array destination MUST be mutable.

A GC-array destination MUST match the storage class named by the import.

For linear memory, the pointer is a byte address.

For linear memory, capacity is measured in code units.

### 5.4 Allocating GC results

`*_read_array_i8`, `*_read_array_i16`, and `*_read_array_i32` allocate a fresh Wasm GC array.

The importing module selects the concrete result heap type.

The runtime validates that type during import linking.

A mismatched storage class is an import-type mismatch.

It fails instantiation instead of returning runtime `ERR_TYPE`.

On success:

```text
value = non-null reference to a fresh exact-length array
errno = ERR_OK
```

On failure:

```text
value = null
errno = specific error
```

An empty string returns a non-null zero-length array.

Allocation failure returns `ERR_NO_MEMORY`.

### 5.5 Stable and stateful sources

Arguments are immutable Facet instance inputs.

Environment entries are immutable Facet instance inputs.

Preopen display names are immutable Facet instance inputs.

These values remain stable for the lifetime of the instance.

Directory iteration is stateful.

A width-specific `dir_iter_next_len_i*` snapshots the next entry but does not consume it.

A successful read of that entry consumes it.

A successful allocating read of that entry consumes it.

A failed capacity check does not consume it.

A failed text-validation check does not consume it.

Rewind discards a pending snapshot.

A symbolic-link target is identified by the supplied path instead of a string handle.

Separate length and read calls can observe different filesystem states.

A caller that requires one atomic result SHOULD use an allocating GC readlink when available.

A caller can also provide enough guest-owned capacity for one read operation.

### 5.6 Error examples

```text
args_read_array_i16(index_out_of_range, 0)
  -> (null, ERR_RANGE)

args_read_array_i8(valid_index, 2)
  -> (null, ERR_INVALID)

args_read_mem32_i8(valid_index, 0, memory, ptr, too_small)
  -> (0, ERR_RANGE)
```

These are ordinary Facet errors.

They are not Wasm traps.

## 6. Polling semantics

Facet polling is level-triggered and snapshot-based.

### 6.1 File-descriptor registrations

`poll_add_fd` accepts `POLL_READABLE` and `POLL_WRITABLE` as requested interest bits.

Unknown interest bits return `ERR_INVALID`.

Requesting `POLL_HANGUP`, `POLL_ERROR`, or `POLL_TIMER` as an interest returns `ERR_INVALID`.

A poll set MAY contain at most one registration for one file descriptor.

Adding the same file descriptor twice returns `ERR_EXISTS`.

Updating an unregistered file descriptor returns `ERR_NO_ENTRY`.

Removing an unregistered file descriptor returns `ERR_NO_ENTRY`.

Updating a registration does not create an event-order guarantee.

Facet does not define event order.

Closing a file descriptor removes future registrations for that descriptor from all poll sets owned by the same Facet instance.

An event that is already in a readiness snapshot remains available.

That event keeps its captured `source_id`, `events`, and `userdata`.

### 6.2 Timers

`poll_add_timer` creates a one-shot timer subscription.

It returns a nonzero subscription ID.

The ID is unique inside that poll set while the subscription exists.

A deadline less than or equal to the current monotonic time is immediately ready.

When a timer appears in a completed `poll_wait` snapshot, the timer is removed from the active subscription set.

The captured timer event remains available through `poll_next` until the guest drains it.

Removing an unknown timer ID returns `ERR_NO_ENTRY`.

Removing an already-fired timer ID returns `ERR_NO_ENTRY`.

### 6.3 Waiting

`poll_wait` uses an absolute monotonic deadline.

`UINT64_MAX` means no timeout.

The call blocks until at least one subscription is ready or until the deadline expires.

If the deadline is already in the past, the call returns immediately.

A finite-deadline wait on an empty poll set is valid.

It returns zero when the deadline is reached.

An empty poll set with `UINT64_MAX` returns `ERR_INVALID`.

This avoids a wait that can never become observable.

When readiness causes `poll_wait` to return, the runtime snapshots all subscriptions known to be ready at that point.

`ready_count` is the number of snapshot records available through `poll_next`.

One source produces at most one record in a snapshot.

If more than one condition is true for that source, OR the conditions into its `events` field.

Event order is unspecified.

The guest MUST NOT depend on:

- registration order;
- file-descriptor number;
- timer ID;
- operating-system polling order.

A second `poll_wait` before the guest drains the current snapshot returns `ERR_BUSY`.

### 6.4 Event delivery

`poll_next` removes and returns one readiness-snapshot record.

After all records are drained, it returns:

```text
source_kind = 0
source_id   = 0
events      = 0
userdata    = 0
done        = 1
errno       = ERR_OK
```

A timer record has `POLL_TIMER` set.

For file-descriptor records, the runtime MAY report `POLL_HANGUP` even when the guest did not request that bit.

The runtime MAY report `POLL_ERROR` even when the guest did not request that bit.

An I/O error makes the source ready instead of making the poll operation itself fail.

A regular file is ready when the requested operation would complete without blocking.

The same rule applies to another resource whose requested operation would complete without blocking.

EOF counts as readable readiness because a read can immediately return zero bytes.

## 7. Networking semantics

Facet networking follows WASI socket state and error categories where they fit the Facet model.

The Facet API remains synchronous and uses flat Core WebAssembly functions.

### 7.1 Authority

The embedder configures network policy.

Facet 0.1 does not expose that policy through a guest-visible query API.

If the Facet network profile is unavailable, a required network import fails normal Wasm instantiation.

If the profile exists but a requested network action is outside granted authority, return `ERR_CAPABILITY`.

This rule applies to:

- bind;
- connect;
- send;
- receive;
- DNS resolution.

### 7.2 Valid socket combinations

`socket_open` accepts:

```text
AF_INET4 + SOCK_STREAM + (PROTO_DEFAULT or PROTO_TCP)
AF_INET6 + SOCK_STREAM + (PROTO_DEFAULT or PROTO_TCP)
AF_INET4 + SOCK_DGRAM  + (PROTO_DEFAULT or PROTO_UDP)
AF_INET6 + SOCK_DGRAM  + (PROTO_DEFAULT or PROTO_UDP)
```

`AF_UNSPEC` is valid for DNS family selection.

`AF_UNSPEC` is not valid for `socket_open`.

An unknown family, socket type, or protocol returns `ERR_INVALID`.

A known but incompatible socket and protocol combination returns `ERR_PROTOCOL`.

A port is an unsigned value in the range `0..65535`.

A larger value returns `ERR_RANGE`.

An IPv4 address requires `address_hi == 0`.

An IPv4 address requires `scope_id == 0`.

A family mismatch or malformed address returns `ERR_ADDRESS_INVALID`.

### 7.3 Stream socket state machine

A stream socket begins in the **unbound** state.

#### Bind

`socket_bind` is valid only in the unbound state.

Success changes the state to **bound**.

#### Listen

`socket_listen` is valid only in the bound state.

Success changes the state to **listening**.

#### Accept

`socket_accept` is valid only in the listening state.

A successful accept returns a new **connected** stream socket.

#### Connect

`socket_connect` is valid in the unbound or bound state.

An unbound connect MAY perform an implicit bind.

Success changes the state to **connected**.

#### Local address

`socket_local_address` requires a bound, listening, connecting, or connected state.

#### Peer address

`socket_peer_address` requires a connected state.

Otherwise it returns `ERR_NOT_CONNECTED`.

#### Shutdown

`socket_shutdown` is valid only for a connected stream socket.

Otherwise it returns `ERR_NOT_CONNECTED`.

Calling bind on an already bound socket returns `ERR_INVALID` unless a more specific rule applies.

Calling listen on a socket that is not bound returns `ERR_INVALID` unless a more specific rule applies.

Calling accept on a non-listener returns `ERR_INVALID` unless a more specific rule applies.

Calling connect on an already connected or listening socket returns `ERR_INVALID` unless a more specific rule applies.

A listen backlog of zero returns `ERR_INVALID`.

The runtime MAY clamp another positive backlog value to a supported external range.

### 7.4 Blocking and nonblocking stream operations

Without `SOCK_NONBLOCK`, connect and accept MAY block until they complete or fail.

With `SOCK_NONBLOCK`, `socket_accept` returns `ERR_AGAIN` when no connection is pending.

With `SOCK_NONBLOCK`, `socket_connect` MAY return `ERR_AGAIN` while connection establishment is in progress.

After `socket_connect` returns `ERR_AGAIN`, the guest can wait for writable or error readiness with `facet-poll`.

The guest can then call `socket_connect` again with the same remote address to obtain the final result.

Calling `socket_connect` with a different remote address while a connect is pending returns `ERR_BUSY`.

A final failed connection attempt makes that stream socket unusable for another connect attempt.

The guest can still close the socket.

The guest can still inspect addresses when that inspection is meaningful.

Typical final mappings include:

```text
connection refused -> ERR_CONNECTION_REFUSED
connection reset/aborted -> ERR_CONNECTION_RESET
timeout -> ERR_TIMED_OUT
host unreachable -> ERR_HOST_UNREACHABLE
network unreachable -> ERR_NETWORK_UNREACHABLE
address already used -> ERR_ADDRESS_IN_USE
```

### 7.5 Stream data

A connected stream socket uses the ordinary `fd_read_*`, `fd_write_*`, `fd_readv_*`, and `fd_writev_*` operations.

A nonblocking stream operation that cannot make progress returns zero bytes and `ERR_AGAIN`.

A graceful peer close is ordinary EOF.

EOF returns zero bytes and `ERR_OK`.

A write after the peer closes its receiving direction returns `ERR_PIPE` when the external system exposes that distinction.

### 7.6 Datagram sockets

`socket_bind` is valid for datagram sockets.

Facet 0.1 does not define `socket_listen` for datagram sockets.

Facet 0.1 does not define `socket_accept` for datagram sockets.

Facet 0.1 does not define `socket_shutdown` for datagram sockets.

Facet 0.1 does not define stream `socket_connect` semantics for datagram sockets.

Each of these operations returns `ERR_PROTOCOL` on a datagram socket.

Datagram data uses only `socket_sendto_*` and `socket_recvfrom_*`.

A nonblocking datagram operation with no immediate progress returns `ERR_AGAIN`.

A datagram send is all-or-nothing as defined in section 2.5.

If a receive buffer is smaller than the datagram, the operation copies the fitting prefix and sets `MSG_TRUNCATED`.

### 7.7 DNS

`dns_resolve_*` accepts `AF_UNSPEC`, `AF_INET4`, or `AF_INET6`.

A name with no suitable address returns `ERR_NO_ENTRY`.

A temporary resolver failure returns `ERR_AGAIN`.

A permanent resolver or protocol failure returns `ERR_PROTOCOL` when that category applies.

If no more specific portable category applies, return `ERR_OTHER`.

An embedder network-policy denial returns `ERR_CAPABILITY`.

`dns_next` uses an explicit `done` result.

Exhaustion is:

```text
family      = 0
address_hi  = 0
address_lo  = 0
scope_id    = 0
done        = 1
errno       = ERR_OK
```

## 8. Version and feature compatibility

Facet 0.1 has one global ABI version.

Profiles do not have independent versions.

Import presence and Core Wasm type matching are the authoritative feature-detection mechanism.

The runtime MUST NOT require a guest-visible profile manifest in addition to normal Core Wasm linking.

The runtime MUST NOT require profile-version negotiation in addition to normal Core Wasm linking.

The runtime MUST NOT require a scalar feature-query call in addition to normal Core Wasm linking.

Profile labels are descriptive groupings for documentation and conformance only.

## 9. Compatibility references

Facet intentionally follows established WASI behavior where practical.

Important compatibility areas include:

- filesystem capability-beneath path resolution;
- `not-permitted` handling for escape attempts;
- the distinction between access, permission, read-only, overflow, unsupported, and other portable filesystem errors;
- the polling rule that an I/O error makes a source ready instead of making polling itself fail;
- socket state-oriented errors;
- network authority supplied by the instantiation context.

A runtime does not have to implement WASI internally.

These references describe compatible observable behavior only.
