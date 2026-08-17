# WPSI 0.1 Behavioral Semantics

**Status:** Draft, normative  
**Applies to:** WPSI 0.1  
**Companion to:** [`../SPEC.md`](../SPEC.md)

This document is part of the normative WPSI 0.1 specification. `SPEC.md` defines the public ABI, function signatures, constants, representations, and profiles. This document fixes behavioral details that runtimes need in order to produce compatible results.

The defaults intentionally follow established WASI behavior where it maps cleanly to WPSI. The goal is to minimize implementation novelty for runtimes that already implement WASI, while preserving the parts of WPSI that are deliberately different: direct Core Wasm imports, explicit multi-memory addressing, Memory64, and Wasm GC arrays.

## 1. Validation and error precedence

WPSI functions MUST validate guest-controlled inputs in the following order unless a function explicitly states otherwise:

1. **Scalar form.** Validate enum values, flag masks, reserved bits, mutually incompatible scalar options, numeric domains such as port ranges, and other scalar-only constraints.
2. **Resource handles.** Validate handles in parameter order. A zero, stale, closed, unknown, or wrong-resource-kind handle fails with `ERR_BAD_HANDLE`.
3. **Resource state and authority.** Validate socket/file state, descriptor rights, and embedder-granted capabilities before accessing guest buffers or host namespaces.
4. **Guest representation.** Resolve the selected linear memory or GC reference and validate the expected address width, GC array kind, dynamic element storage type, and destination mutability.
5. **Ranges.** Validate indexes, offsets, lengths, descriptor tables, and all checked arithmetic. Overflow MUST be detected before address arithmetic or host calls.
6. **Text.** Validate the requested encoding and decode or validate text where the operation requires text semantics.
7. **Namespace resolution.** Resolve filesystem paths, symbolic links, DNS names, and similar namespace-dependent inputs subject to the operation's capability boundary.
8. **Host operation.** Perform the operating-system, virtual filesystem, socket, clock, random, or other host operation.
9. **Normalization.** Translate the host result into WPSI return values and WPSI error codes.

The first failing stage determines the returned WPSI error. Within one stage, parameters are validated from left to right in the order they appear in the WPSI function signature.

An implementation MAY combine or reorder internal checks when the observable result is identical.

No guest-visible mutation or externally visible host side effect may occur before stages 1 through 7 have succeeded. Reading a guest source buffer for validation is not a guest-visible mutation, but a runtime MUST NOT perform a host write, create a file, consume a datagram, advance a file position, or modify a destination buffer before deterministic validation succeeds.

This order exists to make failures reproducible across runtimes and to prevent host behavior from accidentally deciding which of several invalid guest inputs is reported first.

## 2. Error semantics

WPSI keeps its own compact numeric error namespace. The numeric values in `SPEC.md` are normative WPSI values; they are **not** required to equal POSIX errno values or WASI enum ordinals.

The intended semantics deliberately track WASI/POSIX categories where possible:

| WPSI error | Meaning |
| --- | --- |
| `ERR_OK` | Operation completed successfully. |
| `ERR_PERMISSION` | Operation is not permitted. This corresponds to the WASI/POSIX `not-permitted` / `EPERM` class and is also used for forbidden path-resolution escape attempts. |
| `ERR_NO_ENTRY` | Named filesystem object, DNS name, or other requested entry does not exist. |
| `ERR_IO` | Host I/O failure without a more specific portable classification. |
| `ERR_BAD_HANDLE` | Handle is zero, stale, closed, unknown, or the wrong resource kind. |
| `ERR_AGAIN` | Operation would block or a temporary condition requires retry. |
| `ERR_NO_MEMORY` | Runtime or host could not allocate memory or an equivalent bounded resource needed to complete the operation. |
| `ERR_ACCESS` | The underlying host object or ACL denies access, corresponding to the WASI/POSIX `access` / `EACCES` class. |
| `ERR_BUSY` | Resource is busy or conflicts with another operation already in progress. |
| `ERR_EXISTS` | Destination or requested entry already exists. |
| `ERR_NOT_DIRECTORY` | Operation requires a directory but the resolved object is not a directory. |
| `ERR_IS_DIRECTORY` | Operation requires a non-directory object but the resolved object is a directory. |
| `ERR_INVALID` | Scalar argument, flag combination, operation state, or semantic value is invalid and no more specific WPSI error applies. |
| `ERR_FILE_TOO_LARGE` | File or requested file extent exceeds an implementation or filesystem limit. |
| `ERR_NO_SPACE` | Backing storage has insufficient free space. |
| `ERR_READ_ONLY` | Mutation was requested through a read-only filesystem or read-only directory capability. |
| `ERR_PIPE` | Broken pipe or equivalent write-side stream failure. |
| `ERR_RANGE` | A valid-kind scalar index or value lies outside the operation's semantic range. Examples include an argument index past `args_count`, a port greater than 65535, or an iterator range outside an array. |
| `ERR_NOT_EMPTY` | Directory is not empty. |
| `ERR_LOOP` | Too many symbolic-link expansions or a final symbolic link was forbidden from being followed where WPSI defines that result. |
| `ERR_NAME_TOO_LONG` | A path component or name exceeds an implementation/filesystem limit. |
| `ERR_NOT_SUPPORTED` | Operation or option is valid WPSI but unsupported by the host/runtime. |
| `ERR_OVERFLOW` | Arithmetic result or host result cannot be represented in the required WPSI value type. |
| `ERR_ILLEGAL_SEQUENCE` | Text cannot be represented or decoded losslessly in the requested encoding. |
| `ERR_FAULT` | Guest linear-memory selection or byte address range is invalid or out of bounds. |
| `ERR_TYPE` | Guest representation has the wrong physical type, such as Memory64 passed to a `_mem32` operation, wrong GC element storage, or immutable GC storage used as a destination. |
| `ERR_QUOTA` | An explicit WPSI/host quota was exceeded. |
| `ERR_CANCELED` | Operation was canceled by a supported host mechanism. WPSI 0.1 does not otherwise require cancellation support. |
| `ERR_ADDRESS_IN_USE` | Socket address or ephemeral port is already in use. |
| `ERR_ADDRESS_INVALID` | Socket address is malformed, outside the socket's address family, not bindable, or otherwise invalid for the operation. |
| `ERR_CONNECTION_REFUSED` | Remote endpoint actively refused a connection. |
| `ERR_CONNECTION_RESET` | Established or pending connection was reset or aborted. |
| `ERR_NOT_CONNECTED` | Operation requires a connected socket but the socket is not connected. |
| `ERR_TIMED_OUT` | Operation exceeded its timeout. |
| `ERR_HOST_UNREACHABLE` | Host-specific routing reports that the destination host is unreachable. |
| `ERR_NETWORK_UNREACHABLE` | Routing reports that the destination network is unreachable. |
| `ERR_PROTOCOL` | Socket/protocol operation is incompatible with the socket type or a protocol-level failure has no more specific WPSI category. |
| `ERR_CAPABILITY` | The WPSI instance lacks required authority granted by the embedder or a parent WPSI capability/rights set. |
| `ERR_END` | Reserved end-of-sequence error for extensions. WPSI 0.1 operations that expose an explicit `done` result use `done` with `ERR_OK` instead. |
| `ERR_OTHER` | Host error has no stable portable WPSI classification. |

### 2.1 Capability, permission, and access

These three errors are intentionally distinct:

- `ERR_CAPABILITY` means WPSI authority was never granted or was attenuated away.
- `ERR_PERMISSION` means the operation is categorically not permitted, including a filesystem path attempting to escape its base capability.
- `ERR_ACCESS` means WPSI authority exists but the underlying host object or host access-control system denies the operation.

A runtime SHOULD classify an embedder network-policy denial as `ERR_CAPABILITY`, an operating-system `EACCES`-like filesystem denial as `ERR_ACCESS`, and an `EPERM`-like operation denial as `ERR_PERMISSION`.

### 2.2 Unknown host errors

A host error MUST NOT be guessed into an unrelated portable category merely to avoid `ERR_OTHER`. If the runtime cannot map a host failure faithfully, it MUST return `ERR_OTHER`.

### 2.3 Validation failures are side-effect free

If a function fails during validation stages 1 through 7, all non-error results MUST be zero and the operation MUST NOT mutate guest destinations or externally visible host state.

### 2.4 Partial stream I/O

For byte-stream reads and writes, if the host successfully transfers one or more bytes and then encounters an error, WPSI returns the transferred byte count with `ERR_OK`. A later operation may report the deferred host condition.

If no bytes were transferred, the host condition is returned normally.

This follows the usual POSIX/WASI stream convention and avoids returning a nonzero transfer count together with a failing errno.

EOF remains:

```text
bytes_read = 0
errno      = ERR_OK
```

A nonblocking operation that cannot transfer data immediately returns zero bytes and `ERR_AGAIN`.

### 2.5 Datagram atomicity

A datagram send is atomic from the WPSI caller's perspective: either the whole datagram is accepted and the full byte count is returned with `ERR_OK`, or zero bytes are returned with an error.

A datagram receive may copy a prefix when the destination buffer is too small. In that case the operation succeeds and sets:

```text
MSG_TRUNCATED = 1 << 0
```

in `message_flags`. The returned byte count is the number of bytes actually copied into the guest buffer.

## 3. Filesystem path and symbolic-link resolution

WPSI path resolution follows the same capability-beneath model used by WASI filesystem APIs.

### 3.1 Relative paths only

Every WPSI path is interpreted relative to the supplied directory capability.

The logical directory separator is `/`.

A path beginning with `/` is forbidden and returns `ERR_PERMISSION`.

There is no process-global host current working directory and no path operation may use an ambient host root.

### 3.2 `.` and `..`

`.` names the current directory component.

`..` removes one resolved directory component. If resolving `..` would move above the directory represented by the base capability, resolution fails with `ERR_PERMISSION`.

A path is not allowed to temporarily leave the capability and later re-enter it.

### 3.3 Intermediate symbolic links

Intermediate symbolic links may be followed while resolving a path, but every expansion remains constrained beneath the supplied directory capability.

If a symbolic link expands to an absolute/rooted host path, or if following it would step outside the base capability, resolution fails with `ERR_PERMISSION`.

The runtime MUST preserve this invariant in the presence of concurrent host filesystem rename, unlink, and symlink changes. A check-then-open implementation that permits a race to escape the directory capability is nonconforming.

### 3.4 Final symbolic-link component

The final component follows operation-specific rules:

- `path_open_*` follows the final symbolic link unless `OPEN_NOFOLLOW` is present. If the final object is a symbolic link and `OPEN_NOFOLLOW` is present, the operation returns `ERR_LOOP`.
- `path_stat_*` follows the final symbolic link only when `PATH_FOLLOW_SYMLINK` is present. Without that flag it returns metadata for the symbolic link itself.
- `path_link_*` follows the final source symbolic link only when `PATH_FOLLOW_SYMLINK` is present. The destination final component is never followed.
- `path_readlink_*` never follows the final component and requires it to be a symbolic link.
- create, remove, rename, and symlink-destination operations act on the final directory entry rather than following it, while still resolving intermediate components beneath the base capability.

An implementation-defined symlink-expansion limit is permitted. Exceeding that limit returns `ERR_LOOP`.

### 3.5 Creating and reading symbolic links

Creating a symbolic link whose target begins with `/` returns `ERR_PERMISSION`.

A relative target containing `..` MAY be stored. The capability boundary is enforced later when the link is followed.

`path_readlink_*` returns the stored target string without resolving it. If an externally created host symlink contains an absolute/rooted target, `path_readlink_*` returns `ERR_PERMISSION`, matching WASI's sandboxing behavior.

## 4. Settled Wasm GC array rules

The following rules are fixed for WPSI 0.1:

1. Raw GC-array byte offsets and byte lengths are unsigned `i64` values.
2. `array<i16>`, `array<i32>`, `array<i64>`, and `array<v128>` raw-buffer operations MUST support byte ranges that begin or end inside an element.
3. GC-array imports use the abstract non-null `(ref array)` Core Wasm parameter. The import name determines the required dynamic storage type.
4. Source arrays used by write/send operations MAY be immutable.
5. Destination arrays used by read/receive/random-fill operations MUST be mutable.
6. Dynamic kind, storage-type, or destination-mutability mismatch returns `ERR_TYPE`.
7. These rules specify observable values only and do not require contiguous physical GC storage.

## 5. System-string semantics

A `sysstr` is an immutable snapshot of one host-originated string value.

Its contents MUST remain stable until the handle is closed, even if the host argument list, environment, directory, symlink, or preopen metadata changes later.

### 5.1 Length

`sysstr_len` returns the exact number of encoding units required by the requested encoding, excluding any terminator.

Encoding units are:

```text
UTF-8 / WTF-8 / RAW8 = bytes
UTF-16 / WTF-16      = 16-bit code units
UTF-32                = 32-bit code units
```

If the value cannot be represented losslessly in the requested encoding, `sysstr_len` returns zero and `ERR_ILLEGAL_SEQUENCE`.

### 5.2 Reads and capacity

`sysstr_read_*` writes the longest prefix that fits in the supplied capacity while remaining valid in the requested encoding.

It MUST NOT split a UTF-8 encoded scalar, a UTF-16 surrogate pair in `ENC_UTF16`, or another multi-unit encoded scalar sequence. RAW8 may stop at any byte boundary.

Insufficient capacity is not an error. The function returns the number of encoding units written and `ERR_OK`.

A capacity of zero therefore returns:

```text
units_written = 0
errno         = ERR_OK
```

No NUL terminator is appended. Destination storage after `units_written` MUST remain unchanged.

Callers requiring the entire string SHOULD call `sysstr_len` first and allocate enough capacity.

### 5.3 Encoding compatibility

An invalid encoding enum returns `ERR_INVALID`.

For GC destinations, a valid encoding that is incompatible with the representation family returns `ERR_TYPE`:

```text
array_i8  -> UTF-8, WTF-8, RAW8
array_i16 -> UTF-16, WTF-16
array_i32 -> UTF-32
```

Normal Unicode scalar strings can be represented by the corresponding UTF or WTF encodings. Host-originated values containing surrogate code units or non-Unicode native bytes may require WTF or RAW8; requesting a representation that cannot preserve the value returns `ERR_ILLEGAL_SEQUENCE`.

Embedded NUL is permitted in a `sysstr`; individual consumers such as filesystem path functions may reject it.

## 6. Polling semantics

WPSI polling is level-triggered and snapshot-based.

### 6.1 File-descriptor registrations

`poll_add_fd` accepts only `POLL_READABLE` and `POLL_WRITABLE` as requested interest bits. Unknown bits or `POLL_HANGUP`, `POLL_ERROR`, or `POLL_TIMER` as requested interests return `ERR_INVALID`.

A poll set may contain at most one registration for a given fd. Adding the same fd twice returns `ERR_EXISTS`.

Updating or removing an fd that is not registered returns `ERR_NO_ENTRY`. Updating a registration does not change any ordering guarantee because WPSI does not define event ordering.

Closing an fd automatically removes future registrations for that fd from all poll sets owned by the same WPSI instance. Already-snapshotted events remain drainable and retain their captured `source_id`, `events`, and `userdata`.

### 6.2 Timers

`poll_add_timer` creates a one-shot timer subscription and returns a nonzero subscription id unique within that poll set while the subscription exists.

A deadline less than or equal to the current monotonic time is immediately ready.

Once a timer is included in a completed `poll_wait` snapshot it is removed from the active subscription set. Its captured event remains available through `poll_next` until drained.

Removing an unknown or already-fired timer id returns `ERR_NO_ENTRY`.

### 6.3 Waiting

`poll_wait` uses an absolute monotonic deadline.

`UINT64_MAX` means no timeout.

The call blocks until one or more subscriptions are ready or until the supplied deadline expires. If the deadline is already in the past, the call returns immediately.

A finite-deadline wait on an empty poll set is valid and returns zero when the deadline is reached. An empty poll set combined with `UINT64_MAX` returns `ERR_INVALID` rather than requiring a permanently unobservable wait.

When `poll_wait` returns because subscriptions are ready, it snapshots all subscriptions known to be ready at that point. `ready_count` is the number of snapshot records available through `poll_next`.

A single source produces at most one record in a snapshot; multiple conditions are ORed into its `events` field.

Event order is unspecified. Callers MUST NOT rely on registration order, fd number, timer id, or host polling order.

A second `poll_wait` before the current snapshot is fully drained returns `ERR_BUSY`.

### 6.4 Event delivery

`poll_next` removes and returns one snapshot record.

After all records are drained it returns:

```text
source_kind = 0
source_id   = 0
events      = 0
userdata    = 0
done        = 1
errno       = ERR_OK
```

A timer record has `POLL_TIMER` set.

For fd records, `POLL_HANGUP` and `POLL_ERROR` may be reported even when the caller did not request those bits. This follows the WASI principle that an I/O error makes a source ready rather than causing the poll operation itself to fail.

Regular files and other resources on which the requested operation would complete without blocking are considered ready. EOF therefore counts as readable readiness because a read can immediately return zero bytes.

## 7. Networking semantics

WPSI networking follows the state and error categories used by WASI sockets, adapted to WPSI's synchronous flat Core Wasm functions.

### 7.1 Authority

Network policy is configured by the embedder and is not exposed through a guest-visible policy-query API in WPSI 0.1.

This matches the current WASI direction where network authority is granted by instantiation/import context rather than by a discoverable policy object.

If the WPSI network profile is unavailable, required imports fail normal Wasm instantiation. If the profile exists but a specific bind, connect, send, receive, or DNS action is outside the granted network authority, that operation returns `ERR_CAPABILITY`.

### 7.2 Valid socket combinations

`socket_open` accepts:

```text
AF_INET4 + SOCK_STREAM + (PROTO_DEFAULT or PROTO_TCP)
AF_INET6 + SOCK_STREAM + (PROTO_DEFAULT or PROTO_TCP)
AF_INET4 + SOCK_DGRAM  + (PROTO_DEFAULT or PROTO_UDP)
AF_INET6 + SOCK_DGRAM  + (PROTO_DEFAULT or PROTO_UDP)
```

`AF_UNSPEC` is valid for DNS family selection but not for `socket_open`.

Unknown families/types/protocols return `ERR_INVALID`. A known but incompatible socket/protocol combination returns `ERR_PROTOCOL`.

Ports are unsigned values in the range `0..65535`; larger values return `ERR_RANGE`.

An IPv4 socket address requires `address_hi == 0` and `scope_id == 0`. Address-family mismatch or otherwise malformed addresses return `ERR_ADDRESS_INVALID`.

### 7.3 Stream socket state machine

A stream socket begins **unbound**.

- `socket_bind` is valid only while unbound. Success transitions to **bound**.
- `socket_listen` is valid only while bound. Success transitions to **listening**.
- `socket_accept` is valid only while listening. A successful accept returns a new **connected** stream socket.
- `socket_connect` is valid while unbound or bound. An unbound connect may perform an implicit bind. Success transitions to **connected**.
- `socket_local_address` requires bound, listening, connecting, or connected state.
- `socket_peer_address` requires connected state and otherwise returns `ERR_NOT_CONNECTED`.
- `socket_shutdown` is valid only for connected stream sockets and otherwise returns `ERR_NOT_CONNECTED`.

Calling bind on an already bound socket, listen on a socket that is not bound, accept on a non-listener, or connect on an already connected/listening socket returns `ERR_INVALID` unless a more specific error above applies.

A listen backlog of zero returns `ERR_INVALID`. Other positive values MAY be clamped to a host-supported range.

### 7.4 Blocking and nonblocking stream operations

Without `SOCK_NONBLOCK`, connect and accept may block until they complete or fail.

With `SOCK_NONBLOCK`:

- `socket_accept` returns `ERR_AGAIN` when no connection is pending.
- `socket_connect` may return `ERR_AGAIN` while connection establishment is still in progress.
- after `ERR_AGAIN`, the guest may use `wpsi-poll` writable/error readiness and call `socket_connect` again with the same remote address to obtain the final result;
- calling `socket_connect` with a different remote address while a connect is pending returns `ERR_BUSY`.

A final failed connection attempt leaves the socket unusable for another connect attempt; only address inspection where meaningful and `handle_close` remain valid. This follows WASI's one-connect-attempt socket model and prevents host-specific reconnect behavior from leaking into the ABI.

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

Connected stream sockets use the ordinary `fd_read_*`, `fd_write_*`, `fd_readv_*`, and `fd_writev_*` operations.

A nonblocking stream operation that cannot make progress returns zero bytes and `ERR_AGAIN`.

A graceful peer close is ordinary EOF: zero bytes and `ERR_OK`.

A write after the peer has closed the receiving direction returns `ERR_PIPE` when the host exposes that distinction.

### 7.6 Datagram sockets

`socket_bind` is valid for datagram sockets.

`socket_listen`, `socket_accept`, `socket_shutdown`, and stream `socket_connect` semantics are not defined for datagram sockets in WPSI 0.1 and return `ERR_PROTOCOL`.

Datagram data uses only `socket_sendto_*` and `socket_recvfrom_*`.

A nonblocking datagram operation with no immediate progress returns `ERR_AGAIN`.

A datagram send is all-or-nothing as defined in section 2.5. A receive buffer smaller than the datagram receives the fitting prefix and sets `MSG_TRUNCATED`.

### 7.7 DNS

`dns_resolve_*` accepts `AF_UNSPEC`, `AF_INET4`, or `AF_INET6`.

A name with no suitable address returns `ERR_NO_ENTRY`.

A temporary resolver failure returns `ERR_AGAIN`.

A permanent resolver/protocol failure without a more specific WPSI category returns `ERR_PROTOCOL` or `ERR_OTHER` when it cannot be classified faithfully.

Network-policy denial returns `ERR_CAPABILITY`.

`dns_next` uses the explicit `done` result. Exhaustion is:

```text
family      = 0
address_hi  = 0
address_lo  = 0
scope_id    = 0
done        = 1
errno       = ERR_OK
```

## 8. Deferred decisions

This document intentionally does not settle:

- scratch filesystem persistence across embedder/runtime restarts;
- handle bit layout or reserved handle ranges;
- per-child slicing for GC nested scatter/gather;
- profile-specific version negotiation;
- asynchronous buffer ownership/lifetime semantics;
- whether path encoding should ever move from an ordinary enum parameter into representation-specific import names.

Those topics remain listed in [`../docs/open-questions.md`](../docs/open-questions.md).

## 9. Compatibility references

The behavioral choices above intentionally track established WASI semantics where possible, especially:

- WASI filesystem's capability-beneath path resolution and `not-permitted` handling for escape attempts;
- WASI filesystem's distinction between access, not-permitted, read-only, overflow, unsupported, and other portable error categories;
- WASI polling's model that I/O errors make a source ready instead of making polling itself an I/O operation;
- WASI sockets' state-oriented error model and instantiation-context network authority.

WPSI does not require a runtime to implement WASI internally. These references describe compatible observable behavior only.
