# WPSI Conformance Tests

This directory is reserved for portable WPSI conformance fixtures.

The initial test suite should be runtime-neutral: small Core Wasm modules import a narrow WPSI surface and a harness supplies controlled host resources.

## Test groups

### Core

- ABI version.
- invalid and double-closed handles.
- argument/environment ordering and `sysstr` lifetime.
- clock invariants.
- random-fill range checking.

### Multi-memory

- read/write using nonzero memory indexes.
- imported and locally defined memories in one memory index space.
- one `readv` spanning several memories.
- invalid memory indexes.
- Memory32/Memory64 mismatch.

### Memory safety

- exact-end ranges.
- one-byte out-of-bounds ranges.
- overflowing pointer-plus-length arithmetic.
- zero-length ranges at end-of-memory.
- short reads and writes.

### GC arrays

Run each raw-buffer test for:

```text
i8
i16
i32
i64
v128
```

Cover:

- exact element ranges;
- partial first element;
- partial last element;
- range spanning partial/full/partial elements;
- little-endian logical byte interpretation;
- wrong dynamic element type;
- immutable destination array;
- forced GC before and after the host boundary;
- forced moving collection where the runtime supports it;
- outer-array and child-array validation for scatter/gather.

### Text

- UTF-8 round trip.
- UTF-16 BMP and surrogate-pair round trip.
- UTF-32 scalar-value round trip.
- malformed UTF-8/UTF-16/UTF-32 rejection.
- WTF-8/WTF-16 surrogate preservation.
- raw 8-bit system-string preservation.
- embedded NUL rejection for paths where required.

### Filesystem capabilities

- scratch starts empty.
- scratch is writable without a host preopen.
- two instances do not see each other's scratch files by default.
- `..` traversal cannot escape a directory capability.
- symlink traversal cannot escape a capability.
- requested child rights cannot exceed parent rights.
- host preopens expose only explicitly granted directories.

### Networking

- capability-denied socket creation/connect.
- IPv4 and IPv6 scalar address round trips.
- stream short reads/writes.
- datagram send/receive representation parity across linear memory and GC arrays.
- DNS iterator lifecycle.

### Polling

- descriptor readiness.
- monotonic timer readiness.
- userdata preservation.
- event draining before the next `poll_wait`.
- close races.

## Cross-representation oracle

Where practical, tests should perform the same operation through several representations and compare the resulting byte stream:

```text
mem32
mem64
array_i8
array_i16
array_i32
array_i64
array_v128
```

This is especially valuable for validating partial-element GC semantics.

## File naming

Suggested layout:

```text
tests/
  core/
  memory32/
  memory64/
  gc-array/
  filesystem/
  network/
  poll/
  fixtures/
```

Each test module should import only the functions required for that case so that a runtime can run the subset corresponding to the WPSI profiles it supports.
