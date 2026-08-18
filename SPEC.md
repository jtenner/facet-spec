# Facet 0.1 — Portable System Interface for Core WebAssembly

**Status:** Draft  
**Version:** 0.1  
**Import module:** `facet`

## 1. Overview

Facet is a low-level system interface for Core WebAssembly modules.

The WebAssembly module that calls Facet is the **guest**.

The software that implements Facet imports is the **runtime**.

The software that creates the guest instance and grants authority is the **embedder**.

See [`docs/terminology.md`](docs/terminology.md) for the full project glossary.

Facet uses ordinary Core WebAssembly imported functions.

Facet does not require:

- an interface-definition language;
- a canonical lowering layer;
- the Component Model;
- linker-specific polymorphic import resolution.

A system operation can have more than one guest representation.

A representation difference that changes the Core WebAssembly signature receives a different import name.

For example, the file-read operation has these forms:

```text
fd_read_mem32
fd_read_mem64
fd_read_array_i8
fd_read_array_i16
fd_read_array_i32
fd_read_array_i64
fd_read_array_v128
```

Each form has one fixed Core WebAssembly signature.

The guest chooses a form by importing its name.

Facet does not choose a representation dynamically at call time.

Facet has four primary design goals:

1. support WebAssembly multi-memory and Memory64 directly;
2. let supported WebAssembly GC arrays act as system-operation buffers;
3. support UTF-8, UTF-16, and UTF-32 without mandatory conversion through UTF-8;
4. preserve capability-oriented sandboxing through explicit resources and directory capabilities.

## 2. Normative language

The words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative.

An editorial change MUST NOT weaken or strengthen a normative rule.

## 3. Core design rules

### 3.1 Core WebAssembly is the ABI

Facet function signatures use Core WebAssembly types directly.

There is no canonical ABI between the guest and Facet.

### 3.2 Representation-specific names

If two guest representations require different Core WebAssembly signatures, they receive different import names.

If a semantic option does not change the Core WebAssembly representation, it SHOULD remain an ordinary parameter.

### 3.3 Memory 0 is not privileged

Every operation that accesses linear memory receives an explicit `memory_index`.

No Facet function implicitly selects memory 0.

### 3.4 GC arrays are first-class buffers

A guest MAY pass a supported WebAssembly GC array directly to a Facet function.

The runtime MUST NOT require the guest to copy that array through unrelated linear memory.

### 3.5 Caller-typed GC allocation results

Most GC-array parameters use the abstract `(ref array)` type.

The runtime validates the dynamic array type when the guest calls the function.

A small set of string functions allocate and return a new GC array.

For these functions, the importing module declares a concrete nullable array result type.

Example:

```wat
(type $string16 (array (mut i16)))
(import "facet" "args_read_array_i16"
  (func (param i32 i32) (result (ref null $string16) i32)))
```

The import name fixes the required element storage class.

The supported classes for these string results are `i8`, `i16`, and `i32`.

The importing module selects the concrete array type.

At instantiation, the runtime MUST validate that the result type is an array with the storage class named by the import.

The array element MAY be mutable or immutable.

An incompatible result type MUST fail WebAssembly instantiation.

An incompatible result type is not a runtime `errno`.

On success, the runtime allocates exactly the concrete GC array type requested by the import signature.

The runtime returns a non-null reference on success.

On call failure, the runtime returns `ref.null` and a nonzero `errno`.

This rule applies only to the host-originated allocation functions defined by this specification.

It does not create general type-directed import overload resolution.

### 3.6 Incremental implementation is allowed

A runtime MAY implement only the Facet profiles for WebAssembly features that it supports.

A missing required import causes normal WebAssembly instantiation failure.

### 3.7 Synchronous call boundary

Every Facet imported function is synchronous at the Core WebAssembly ABI boundary.

The runtime MUST NOT retain borrowed guest storage after the imported function returns.

Borrowed guest storage includes:

- a linear-memory pointer;
- a linear-memory slice;
- a Wasm GC reference;
- a raw GC backing pointer;
- another temporary view whose validity depends on guest storage remaining in place.

The runtime MAY root or pin a GC object for the duration of a call.

The runtime MAY enter a no-move region or a no-GC region for the duration of a call.

The runtime MUST end each such borrow or collector scope before it returns to the guest.

The runtime MAY retain independent runtime-owned state.

The runtime MAY also retain data that it copied from the guest into independent runtime-owned storage.

Retained state MUST NOT depend on the continued validity or location of borrowed guest storage.

Facet 0.1 defines no asynchronous host functions, futures, callbacks, actor primitives, or retained-buffer operations.

A nonblocking resource reports `ERR_AGAIN` when it cannot make progress immediately.

`facet-poll` provides the readiness mechanism for a scheduler that does not want to block an execution context.

Facet does not prohibit concurrency outside one imported call.

A runtime or guest language MAY schedule multiple tasks, actors, instances, or execution contexts concurrently.

Each individual Facet call remains synchronous.

## 4. Conformance profiles

The initial profiles are:

```text
facet-core
facet-memory32
facet-memory64
facet-gc-array
facet-filesystem
facet-links
facet-network
facet-poll
```

`facet-core` defines scalar operations, handles, process information, clocks, arguments, environment strings, and random scalar values.

`facet-memory32` defines `_mem32` buffer operations.

`facet-memory64` defines `_mem64` buffer operations.

`facet-gc-array` defines `_array_*` operations.

`facet-filesystem` defines preopens, descriptors, directory iteration, and path operations.

`facet-links` defines hard-link and symbolic-link operations.

`facet-network` defines sockets and DNS.

`facet-poll` defines multi-resource polling.

Profile names are documentation and conformance groupings.

They are not independently versioned runtime objects.

## 5. Fundamental ABI conventions

The specification uses these conceptual aliases:

```text
errno       = i32
handle      = i32
fd          = i32
dir         = i32
poll_handle = i32
flags32     = i32
flags64     = i64
```

These aliases are documentation only.

### 5.1 Handles

All Facet resources use opaque nonzero `i32` handles.

Handle `0` is always invalid.

A handle belongs to one Facet instance.

The runtime MUST validate a handle before it uses the resource identified by that handle.

Only the value `0` has a Facet-defined numeric meaning.

Facet does not define:

- handle ranges;
- table indexes inside handle bits;
- generation fields inside handle bits;
- resource-kind tags inside handle bits;
- ordering guarantees for handle values.

The guest MUST treat every nonzero handle as an opaque token.

The guest MUST NOT derive authority, resource kind, lifetime, or runtime state from a handle value.

A closed handle MUST NOT later identify an unrelated live resource in the same Facet instance.

The runtime MUST therefore protect against unchecked slot reuse.

The runtime can use any private strategy that preserves this rule.

Examples include:

- generation counters;
- monotonic identifiers;
- randomized tokens;
- delayed reuse.

The handle encoding remains runtime-private.

### 5.2 Error convention

`errno` is always the final result value when a function returns an error code.

```text
ERR_OK = 0
```

On failure, all non-error results MUST be zero unless a function explicitly states another rule.

Guest-controlled invalid input SHOULD return an error instead of trapping.

A trap is reserved for:

- a runtime invariant failure;
- explicit guest termination;
- an unrecoverable implementation failure.

### 5.3 Error codes

```text
ERR_OK                  = 0
ERR_PERMISSION          = 1
ERR_NO_ENTRY            = 2
ERR_IO                  = 3
ERR_BAD_HANDLE          = 4
ERR_AGAIN               = 5
ERR_NO_MEMORY           = 6
ERR_ACCESS              = 7
ERR_BUSY                = 8
ERR_EXISTS              = 9
ERR_NOT_DIRECTORY       = 10
ERR_IS_DIRECTORY        = 11
ERR_INVALID             = 12
ERR_FILE_TOO_LARGE      = 13
ERR_NO_SPACE            = 14
ERR_READ_ONLY           = 15
ERR_PIPE                = 16
ERR_RANGE               = 17
ERR_NOT_EMPTY           = 18
ERR_LOOP                = 19
ERR_NAME_TOO_LONG       = 20
ERR_NOT_SUPPORTED       = 21
ERR_OVERFLOW            = 22
ERR_ILLEGAL_SEQUENCE    = 23
ERR_FAULT               = 24
ERR_TYPE                = 25
ERR_QUOTA               = 26
ERR_CANCELED            = 27
ERR_ADDRESS_IN_USE      = 28
ERR_ADDRESS_INVALID     = 29
ERR_CONNECTION_REFUSED  = 30
ERR_CONNECTION_RESET    = 31
ERR_NOT_CONNECTED       = 32
ERR_TIMED_OUT            = 33
ERR_HOST_UNREACHABLE    = 34
ERR_NETWORK_UNREACHABLE = 35
ERR_PROTOCOL            = 36
ERR_CAPABILITY          = 37
ERR_END                 = 38
ERR_OTHER               = 255
```

### 5.4 Integer interpretation

Unless a rule states otherwise, an `i32` size, index, offset, or count is an unsigned 32-bit value.

Unless a rule states otherwise, an `i64` size, index, offset, or count is an unsigned 64-bit value.

`fd_seek.signed_offset` is a signed `i64` value.

The runtime MUST use overflow-safe arithmetic for bounds calculations.

## 6. Linear memory representations

### 6.1 Memory32

A `_mem32` operation receives:

```text
memory_index: i32
pointer:      i32
length:       i32
```

The selected memory MUST have an `i32` address type.

Selecting a Memory64 memory returns `ERR_TYPE`.

### 6.2 Memory64

A `_mem64` operation receives:

```text
memory_index: i32
pointer:      i64
length:       i64
```

The selected memory MUST have an `i64` address type.

Selecting a Memory32 memory returns `ERR_TYPE`.

### 6.3 Memory index space

`memory_index` is an index into the normal WebAssembly memory index space of the calling module instance.

Imported memories and locally defined memories use the same index space.

An invalid memory index returns `ERR_FAULT`.

An out-of-bounds linear-memory range returns `ERR_FAULT`.

## 7. WebAssembly GC array representations

GC-array functions accept an abstract non-null array reference:

```wat
(ref array)
```

The imported function name identifies the required dynamic element storage type.

Supported raw buffer variants are:

```text
array_i8
array_i16
array_i32
array_i64
array_v128
```

A destination array MUST have mutable elements.

A storage-type mismatch returns `ERR_TYPE`.

A destination-mutability mismatch returns `ERR_TYPE`.

### 7.1 Normative logical byte view

Facet defines a logical byte view for supported numeric arrays.

The logical byte view defines observable behavior.

It does not define the physical GC heap layout.

Element widths are:

```text
i8    = 1 byte
i16   = 2 bytes
i32   = 4 bytes
i64   = 8 bytes
v128  = 16 bytes
```

Integer elements use little-endian byte order in the logical byte view.

A `v128` element exposes the same 16-byte sequence that WebAssembly `v128.store` would store.

Example:

An `array<i32>` element with value `0x12345678` contributes these bytes:

```text
78 56 34 12
```

### 7.2 Byte offsets and partial elements

Raw array I/O takes `byte_offset: i64` and `byte_length: i64`.

An operation MAY begin inside an element.

An operation MAY end inside an element.

Bytes outside the selected logical byte range MUST remain unchanged.

Example:

If the runtime reads one byte into the first byte of an `i32` element, it changes only the corresponding eight value bits.

All bit patterns are valid for the supported integer and `v128` buffer types.

### 7.3 Lifetime and moving collectors

The runtime MUST keep a referenced GC object alive for the complete synchronous call.

A raw backing pointer, byte slice, or borrowed GC reference MUST NOT outlive the call.

If a collector can move the object, the runtime MUST preserve the logical byte-view rules while the operation runs.

The runtime can do this by using one or more of these strategies:

- pin the object;
- enter a no-move region;
- enter a no-GC region;
- re-resolve the address safely;
- copy through runtime-owned native storage.

### 7.4 Nested arrays

Scatter/gather GC operations accept an outer `(ref array)`.

Each selected child MUST be a non-null reference to an array with the element type named by the function.

For a read operation, each selected child MUST be mutable.

Facet 0.1 uses whole-child scatter/gather.

`first` and `count` select a contiguous range of child arrays.

Each selected child contributes its complete logical byte view.

The selected view starts at byte offset zero and ends at the full logical byte length of that child.

Facet 0.1 does not define a per-child offset, length, slice, or descriptor.

Use an ordinary single-array function when one array requires a byte slice.

Those single-array functions already take `byte_offset` and `byte_length`.

## 8. Text representations and WTF mode

Facet does not use a text-encoding enum.

The import name identifies the physical text representation:

```text
_i8  = 8-bit code units
_i16 = 16-bit code units
_i32 = 32-bit code points
```

A linear-memory text import includes the memory address width and text width in its name.

Examples:

```text
args_read_mem32_i8
args_read_mem64_i16
path_open_mem32_i32
```

GC-array text imports use the `array_i8`, `array_i16`, and `array_i32` families.

Every text operation receives:

```text
wtf: i32
```

`wtf` is a boolean:

```text
0 = strict Unicode
1 = WTF / surrogate-sentinel mode
```

Any other value returns `ERR_INVALID`.

With `wtf == 0`:

- `_i8` contains well-formed UTF-8;
- `_i16` contains well-formed UTF-16;
- `_i32` contains Unicode scalar values only.

With `wtf == 1`, surrogate code points in `0xd800..0xdfff` are permitted as reversible sentinel values.

In WTF mode:

- `_i8` uses WTF-8;
- `_i16` uses WTF-16 code units;
- `_i32` stores code-point values directly, including surrogate sentinels.

Facet MUST NOT silently replace an unrepresentable external unit with U+FFFD.

Strict mode returns `ERR_ILLEGAL_SEQUENCE` when lossless representation is impossible.

WTF mode preserves non-Unicode values through surrogate sentinels when the external namespace can be represented by the defined mapping.

On a byte-string namespace, invalid UTF-8 bytes `0x80..0xff` SHOULD map reversibly to `U+DC80..U+DCFF`.

On a UTF-16 namespace, unpaired surrogate code units are preserved directly.

If the selected WTF representation still cannot represent the external value, the runtime returns `ERR_ILLEGAL_SEQUENCE`.

Linear-memory `_i16` and `_i32` values use little-endian byte order.

Facet strings are length-delimited.

Facet strings are not implicitly NUL-terminated.

## 9. Host-originated strings

Facet does not define a string resource handle.

A string is identified by the operation that owns the source.

Examples of stable source identities include:

- an argument index;
- an environment-entry index;
- a preopen index.

Directory iteration uses iterator state instead of a string resource.

A symbolic-link target is identified by a path operation instead of a string resource.

For stable indexed sources, Facet exposes three forms:

1. `*_len_i8`, `*_len_i16`, and `*_len_i32` return the required code-unit count;
2. `*_read_mem32_i*`, `*_read_mem64_i*`, and `*_read_into_array_i*` copy into guest-owned storage;
3. `*_read_array_i*` allocates and returns a caller-typed concrete GC array.

The representation suffix selects the code-unit width.

`wtf` selects strict Unicode or surrogate-sentinel semantics.

There is no second encoding selector.

A linear-memory form receives an explicit memory index, pointer, and capacity.

A GC `read_into` form receives an existing `(ref array)`, an element offset, and a capacity.

An allocating GC form returns `(ref null $caller_type, errno)` as defined in section 3.5.

A successful allocating function returns an array whose length exactly equals the represented string length.

An empty string returns a non-null zero-length array.

For all allocating string functions:

- an invalid source index returns `(null, ERR_RANGE)`;
- an invalid `wtf` value returns `(null, ERR_INVALID)`;
- a source value that cannot be represented losslessly returns `(null, ERR_ILLEGAL_SEQUENCE)`;
- allocation failure returns `(null, ERR_NO_MEMORY)`.

For a guest-owned destination, insufficient capacity returns `ERR_RANGE`.

The function MUST NOT modify the destination when capacity is insufficient.

If the source is stateful, the function MUST NOT advance the source when capacity is insufficient.

A wrong GC destination storage class returns `ERR_TYPE`.

No Facet string-copy function appends a NUL terminator.

## 10. Capabilities and filesystem preopens

Facet resource handles represent authority.

The embedder MUST grant filesystem authority explicitly.

The embedder MUST grant network authority explicitly.

A derived resource MUST NOT have more authority than the capability from which it was derived.

Facet does not define a mandatory scratch filesystem.

Facet does not define a mandatory home filesystem.

Facet does not allocate any other writable storage automatically.

A conforming filesystem implementation MAY expose no preopens.

Each filesystem root supplied by the embedder is an ordinary directory capability.

The guest enumerates these directory capabilities through the preopen APIs.

A guest-visible display name does not grant authority by itself.

The authority comes from the directory handle and its rights.

The embedder MAY provide an ordinary preopen whose display name is exactly `~`.

The name `~` is a convention for a guest home or private writable area when an environment wants to provide one.

The name has no special ABI behavior.

In particular:

- `~` does not automatically refer to the operating-system user's home directory;
- `~` does not imply particular rights;
- `~` does not imply a quota;
- `~` does not imply persistence;
- `~` does not imply a backing-storage type;
- `~` does not imply a lifetime;
- an embedder MAY omit `~`.

If the embedder maps `~` to external storage, the directory has only the authority that the embedder explicitly granted.

The Core Facet path ABI remains directory-handle-relative.

Raw Facet path operands do not parse or expand `~`.

A higher-level binding, libc implementation, or language runtime MAY interpret `~/x` as a convenience syntax.

Such a layer can locate the preopen whose display name is `~`.

It can then issue the ordinary Facet path operation relative to that directory handle with `x` as the relative path.

## 11. Rights and flags

### 11.1 Rights

```text
RIGHT_READ          = 1 << 0
RIGHT_WRITE         = 1 << 1
RIGHT_SEEK          = 1 << 2
RIGHT_TELL          = 1 << 3
RIGHT_STAT          = 1 << 4
RIGHT_SET_SIZE      = 1 << 5
RIGHT_SYNC          = 1 << 6
RIGHT_PATH_OPEN     = 1 << 16
RIGHT_PATH_CREATE   = 1 << 17
RIGHT_PATH_REMOVE   = 1 << 18
RIGHT_PATH_RENAME   = 1 << 19
RIGHT_PATH_LINK     = 1 << 20
RIGHT_PATH_SYMLINK  = 1 << 21
RIGHT_PATH_READLINK = 1 << 22
RIGHT_DIR_ITERATE   = 1 << 23
```

### 11.2 File types

```text
FILE_TYPE_UNKNOWN   = 0
FILE_TYPE_REGULAR   = 1
FILE_TYPE_DIRECTORY = 2
FILE_TYPE_SYMLINK   = 3
FILE_TYPE_CHAR      = 4
FILE_TYPE_BLOCK     = 5
FILE_TYPE_SOCKET    = 6
FILE_TYPE_FIFO      = 7
```

### 11.3 Descriptor flags

```text
FD_APPEND   = 1 << 0
FD_NONBLOCK = 1 << 1
```

### 11.4 Open flags

```text
OPEN_CREATE    = 1 << 0
OPEN_EXCLUSIVE = 1 << 1
OPEN_TRUNCATE  = 1 << 2
OPEN_DIRECTORY = 1 << 3
OPEN_NOFOLLOW  = 1 << 4
OPEN_APPEND    = 1 << 5
OPEN_NONBLOCK  = 1 << 6
```

### 11.5 Seek modes

```text
SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2
```

### 11.6 Path flags

```text
PATH_FOLLOW_SYMLINK = 1 << 0

REMOVE_FILE      = 1 << 0
REMOVE_DIRECTORY = 1 << 1

RENAME_REPLACE    = 1 << 0
RENAME_NO_REPLACE = 1 << 1
RENAME_EXCHANGE   = 1 << 2
```

## 12. Core functions

All functions are imported from module `"facet"`.

```text
abi_version() -> (version: i32)

handle_close(handle: i32) -> (errno: i32)

proc_exit(exit_code: i32) -> ()

proc_yield() -> (errno: i32)

stdio_stdin()  -> (fd: i32, errno: i32)
stdio_stdout() -> (fd: i32, errno: i32)
stdio_stderr() -> (fd: i32, errno: i32)
```

Facet 0.1 reports `abi_version() == 1`.

### 12.1 Versioning and feature detection

`abi_version()` identifies the overall Facet ABI generation.

Facet profiles do not have independent version numbers.

Facet 0.1 defines no scalar feature-query API.

Facet 0.1 defines no profile-query API.

Normal Core WebAssembly linking determines whether an operation is available.

The runtime must provide the requested import name with an exact compatible Core WebAssembly type.

Import presence and type compatibility are authoritative.

A module SHOULD import the operations and representation families that it requires.

A runtime MAY expose any conforming subset of Facet imports.

Profile names such as `facet-filesystem`, `facet-gc-array`, and `facet-network` are documentation and conformance groupings only.

They are not a second runtime negotiation namespace.

An additive capability under the same ABI generation SHOULD use a new import.

An additive import does not by itself require an `abi_version()` increment.

An incompatible replacement for one operation SHOULD normally use a new import name.

This lets old and new operations coexist.

A change that makes the overall Facet ABI generation incompatible MUST increment `abi_version()`.

## 13. Arguments and environment

Argument ordering MUST remain stable for the lifetime of the instance.

Environment-entry ordering MUST remain stable for the lifetime of the instance.

```text
args_count() -> (count: i32, errno: i32)

args_len_i8(index: i32, wtf: i32)  -> (units: i64, errno: i32)
args_len_i16(index: i32, wtf: i32) -> (units: i64, errno: i32)
args_len_i32(index: i32, wtf: i32) -> (units: i64, errno: i32)

args_read_mem32_i8(index: i32, wtf: i32,
                   memory: i32, pointer: i32, capacity_units: i32)
  -> (units_written: i64, errno: i32)
args_read_mem32_i16(...) -> (units_written: i64, errno: i32)
args_read_mem32_i32(...) -> (units_written: i64, errno: i32)

args_read_mem64_i8(index: i32, wtf: i32,
                   memory: i32, pointer: i64, capacity_units: i64)
  -> (units_written: i64, errno: i32)
args_read_mem64_i16(...) -> (units_written: i64, errno: i32)
args_read_mem64_i32(...) -> (units_written: i64, errno: i32)

args_read_into_array_i8(index: i32, wtf: i32,
                        destination: ref array, offset: i32, capacity_units: i32)
  -> (units_written: i64, errno: i32)
args_read_into_array_i16(...) -> (units_written: i64, errno: i32)
args_read_into_array_i32(...) -> (units_written: i64, errno: i32)

args_read_array_i8(index: i32, wtf: i32)
  -> (value: ref null $caller_i8_array, errno: i32)
args_read_array_i16(index: i32, wtf: i32)
  -> (value: ref null $caller_i16_array, errno: i32)
args_read_array_i32(index: i32, wtf: i32)
  -> (value: ref null $caller_i32_array, errno: i32)
```

Environment entries use this scalar field selector:

```text
ENV_NAME  = 0
ENV_VALUE = 1
```

```text
env_count() -> (count: i32, errno: i32)

env_len_i8(index: i32, field: i32, wtf: i32)  -> (units: i64, errno: i32)
env_len_i16(index: i32, field: i32, wtf: i32) -> (units: i64, errno: i32)
env_len_i32(index: i32, field: i32, wtf: i32) -> (units: i64, errno: i32)

env_read_mem32_i8(index: i32, field: i32, wtf: i32,
                  memory: i32, pointer: i32, capacity_units: i32)
  -> (units_written: i64, errno: i32)
env_read_mem32_i16(...) -> (units_written: i64, errno: i32)
env_read_mem32_i32(...) -> (units_written: i64, errno: i32)

env_read_mem64_i8(index: i32, field: i32, wtf: i32,
                  memory: i32, pointer: i64, capacity_units: i64)
  -> (units_written: i64, errno: i32)
env_read_mem64_i16(...) -> (units_written: i64, errno: i32)
env_read_mem64_i32(...) -> (units_written: i64, errno: i32)

env_read_into_array_i8(index: i32, field: i32, wtf: i32,
                       destination: ref array, offset: i32, capacity_units: i32)
  -> (units_written: i64, errno: i32)
env_read_into_array_i16(...) -> (units_written: i64, errno: i32)
env_read_into_array_i32(...) -> (units_written: i64, errno: i32)

env_read_array_i8(index: i32, field: i32, wtf: i32)
  -> (value: ref null $caller_i8_array, errno: i32)
env_read_array_i16(index: i32, field: i32, wtf: i32)
  -> (value: ref null $caller_i16_array, errno: i32)
env_read_array_i32(index: i32, field: i32, wtf: i32)
  -> (value: ref null $caller_i32_array, errno: i32)
```

An unknown environment field selector returns `ERR_INVALID`.

## 14. Clocks

```text
clock_system_now()
  -> (seconds_since_unix_epoch: i64,
      nanoseconds: i32,
      errno: i32)

clock_monotonic_now()
  -> (nanoseconds: i64, errno: i32)

clock_monotonic_resolution()
  -> (nanoseconds: i64, errno: i32)

sleep_for(nanoseconds: i64)
  -> (errno: i32)

sleep_until(monotonic_deadline_ns: i64)
  -> (errno: i32)
```

System-clock nanoseconds MUST be in `[0, 1_000_000_000)`.

## 15. Randomness

```text
random_u64() -> (value: i64, errno: i32)

random_fill_mem32(memory: i32, pointer: i32, length: i32)
  -> (bytes_written: i64, errno: i32)

random_fill_mem64(memory: i32, pointer: i64, length: i64)
  -> (bytes_written: i64, errno: i32)

random_fill_array_i8(destination: ref array, byte_offset: i64, byte_length: i64)
  -> (bytes_written: i64, errno: i32)
random_fill_array_i16(destination: ref array, byte_offset: i64, byte_length: i64)
  -> (bytes_written: i64, errno: i32)
random_fill_array_i32(destination: ref array, byte_offset: i64, byte_length: i64)
  -> (bytes_written: i64, errno: i32)
random_fill_array_i64(destination: ref array, byte_offset: i64, byte_length: i64)
  -> (bytes_written: i64, errno: i32)
random_fill_array_v128(destination: ref array, byte_offset: i64, byte_length: i64)
  -> (bytes_written: i64, errno: i32)
```

## 16. Filesystem preopens

```text
fs_preopen_count() -> (count: i32, errno: i32)
fs_preopen_get(index: i32) -> (directory: i32, errno: i32)

fs_preopen_name_len_i8(index: i32, wtf: i32)  -> (units: i64, errno: i32)
fs_preopen_name_len_i16(index: i32, wtf: i32) -> (units: i64, errno: i32)
fs_preopen_name_len_i32(index: i32, wtf: i32) -> (units: i64, errno: i32)

fs_preopen_name_read_mem32_i8(index: i32, wtf: i32,
                              memory: i32, pointer: i32, capacity_units: i32)
  -> (units_written: i64, errno: i32)
fs_preopen_name_read_mem32_i16(...) -> (units_written: i64, errno: i32)
fs_preopen_name_read_mem32_i32(...) -> (units_written: i64, errno: i32)

fs_preopen_name_read_mem64_i8(index: i32, wtf: i32,
                              memory: i32, pointer: i64, capacity_units: i64)
  -> (units_written: i64, errno: i32)
fs_preopen_name_read_mem64_i16(...) -> (units_written: i64, errno: i32)
fs_preopen_name_read_mem64_i32(...) -> (units_written: i64, errno: i32)

fs_preopen_name_read_into_array_i8(index: i32, wtf: i32,
                                   destination: ref array, offset: i32, capacity_units: i32)
  -> (units_written: i64, errno: i32)
fs_preopen_name_read_into_array_i16(...) -> (units_written: i64, errno: i32)
fs_preopen_name_read_into_array_i32(...) -> (units_written: i64, errno: i32)

fs_preopen_name_read_array_i8(index: i32, wtf: i32)
  -> (value: ref null $caller_i8_array, errno: i32)
fs_preopen_name_read_array_i16(index: i32, wtf: i32)
  -> (value: ref null $caller_i16_array, errno: i32)
fs_preopen_name_read_array_i32(index: i32, wtf: i32)
  -> (value: ref null $caller_i32_array, errno: i32)
```

Preopen ordering MUST remain stable for the lifetime of the instance.

Preopen display names MUST remain stable for the lifetime of the instance.

A preopen named `~` is optional.

A `~` preopen is otherwise an ordinary preopen.

The absence of `~` does not make a filesystem implementation nonconforming.

## 17. Descriptor metadata

```text
fd_rights(fd: i32) -> (rights: i64, errno: i32)

fd_get_flags(fd: i32) -> (flags: i32, errno: i32)

fd_set_flags(fd: i32, flags: i32) -> (errno: i32)

fd_stat(fd: i32)
  -> (file_type: i32,
      stat_flags: i32,
      size: i64,
      atime_seconds: i64,
      atime_nanoseconds: i32,
      mtime_seconds: i64,
      mtime_nanoseconds: i32,
      ctime_seconds: i64,
      ctime_nanoseconds: i32,
      errno: i32)
```

`stat_flags` uses:

```text
STAT_HAS_ATIME = 1 << 0
STAT_HAS_MTIME = 1 << 1
STAT_HAS_CTIME = 1 << 2
```

## 18. Sequential file reads

```text
fd_read_mem32(fd: i32, memory: i32, pointer: i32, length: i32)
  -> (bytes_read: i64, errno: i32)

fd_read_mem64(fd: i32, memory: i32, pointer: i64, length: i64)
  -> (bytes_read: i64, errno: i32)

fd_read_array_i8(fd: i32, destination: ref array,
                 byte_offset: i64, byte_length: i64)
  -> (bytes_read: i64, errno: i32)
fd_read_array_i16(fd: i32, destination: ref array,
                  byte_offset: i64, byte_length: i64)
  -> (bytes_read: i64, errno: i32)
fd_read_array_i32(fd: i32, destination: ref array,
                  byte_offset: i64, byte_length: i64)
  -> (bytes_read: i64, errno: i32)
fd_read_array_i64(fd: i32, destination: ref array,
                  byte_offset: i64, byte_length: i64)
  -> (bytes_read: i64, errno: i32)
fd_read_array_v128(fd: i32, destination: ref array,
                   byte_offset: i64, byte_length: i64)
  -> (bytes_read: i64, errno: i32)
```

EOF is `(bytes_read = 0, errno = ERR_OK)`.

Short reads are permitted.

## 19. Sequential file writes

```text
fd_write_mem32(fd: i32, memory: i32, pointer: i32, length: i32)
  -> (bytes_written: i64, errno: i32)

fd_write_mem64(fd: i32, memory: i32, pointer: i64, length: i64)
  -> (bytes_written: i64, errno: i32)

fd_write_array_i8(fd: i32, source: ref array,
                  byte_offset: i64, byte_length: i64)
  -> (bytes_written: i64, errno: i32)
fd_write_array_i16(fd: i32, source: ref array,
                   byte_offset: i64, byte_length: i64)
  -> (bytes_written: i64, errno: i32)
fd_write_array_i32(fd: i32, source: ref array,
                   byte_offset: i64, byte_length: i64)
  -> (bytes_written: i64, errno: i32)
fd_write_array_i64(fd: i32, source: ref array,
                   byte_offset: i64, byte_length: i64)
  -> (bytes_written: i64, errno: i32)
fd_write_array_v128(fd: i32, source: ref array,
                    byte_offset: i64, byte_length: i64)
  -> (bytes_written: i64, errno: i32)
```

Short writes are permitted.

## 20. Positional I/O

```text
fd_pread_mem32(fd: i32, file_offset: i64,
               memory: i32, pointer: i32, length: i32)
  -> (bytes_read: i64, errno: i32)

fd_pread_mem64(fd: i32, file_offset: i64,
               memory: i32, pointer: i64, length: i64)
  -> (bytes_read: i64, errno: i32)

fd_pread_array_i8(fd: i32, file_offset: i64, destination: ref array,
                  byte_offset: i64, byte_length: i64)
  -> (bytes_read: i64, errno: i32)
fd_pread_array_i16(fd: i32, file_offset: i64, destination: ref array,
                   byte_offset: i64, byte_length: i64)
  -> (bytes_read: i64, errno: i32)
fd_pread_array_i32(fd: i32, file_offset: i64, destination: ref array,
                   byte_offset: i64, byte_length: i64)
  -> (bytes_read: i64, errno: i32)
fd_pread_array_i64(fd: i32, file_offset: i64, destination: ref array,
                   byte_offset: i64, byte_length: i64)
  -> (bytes_read: i64, errno: i32)
fd_pread_array_v128(fd: i32, file_offset: i64, destination: ref array,
                    byte_offset: i64, byte_length: i64)
  -> (bytes_read: i64, errno: i32)

fd_pwrite_mem32(fd: i32, file_offset: i64,
                memory: i32, pointer: i32, length: i32)
  -> (bytes_written: i64, errno: i32)

fd_pwrite_mem64(fd: i32, file_offset: i64,
                memory: i32, pointer: i64, length: i64)
  -> (bytes_written: i64, errno: i32)

fd_pwrite_array_i8(fd: i32, file_offset: i64, source: ref array,
                   byte_offset: i64, byte_length: i64)
  -> (bytes_written: i64, errno: i32)
fd_pwrite_array_i16(fd: i32, file_offset: i64, source: ref array,
                    byte_offset: i64, byte_length: i64)
  -> (bytes_written: i64, errno: i32)
fd_pwrite_array_i32(fd: i32, file_offset: i64, source: ref array,
                    byte_offset: i64, byte_length: i64)
  -> (bytes_written: i64, errno: i32)
fd_pwrite_array_i64(fd: i32, file_offset: i64, source: ref array,
                    byte_offset: i64, byte_length: i64)
  -> (bytes_written: i64, errno: i32)
fd_pwrite_array_v128(fd: i32, file_offset: i64, source: ref array,
                     byte_offset: i64, byte_length: i64)
  -> (bytes_written: i64, errno: i32)
```

`pread` MUST NOT change the descriptor's sequential file position.

`pwrite` MUST NOT change the descriptor's sequential file position.

## 21. Scatter/gather I/O

### 21.1 Memory32 iovec

A Memory32 iovec is 16 bytes:

```text
offset  size  field
0       4     memory_index: u32
4       4     pointer: u32
8       4     length: u32
12      4     reserved = 0
```

Each entry MAY select a different Memory32 memory.

```text
fd_readv_mem32(fd: i32, iovec_memory: i32,
               iovec_pointer: i32, iovec_count: i32)
  -> (bytes_read: i64, errno: i32)

fd_writev_mem32(fd: i32, iovec_memory: i32,
                iovec_pointer: i32, iovec_count: i32)
  -> (bytes_written: i64, errno: i32)
```

### 21.2 Memory64 iovec

A Memory64 iovec is 24 bytes:

```text
offset  size  field
0       4     memory_index: u32
4       4     reserved = 0
8       8     pointer: u64
16      8     length: u64
```

```text
fd_readv_mem64(fd: i32, iovec_memory: i32,
               iovec_pointer: i64, iovec_count: i32)
  -> (bytes_read: i64, errno: i32)

fd_writev_mem64(fd: i32, iovec_memory: i32,
                iovec_pointer: i64, iovec_count: i32)
  -> (bytes_written: i64, errno: i32)
```

### 21.3 GC nested arrays

```text
fd_readv_array_i8(fd: i32, buffers: ref array, first: i32, count: i32)
  -> (bytes_read: i64, errno: i32)
fd_readv_array_i16(fd: i32, buffers: ref array, first: i32, count: i32)
  -> (bytes_read: i64, errno: i32)
fd_readv_array_i32(fd: i32, buffers: ref array, first: i32, count: i32)
  -> (bytes_read: i64, errno: i32)
fd_readv_array_i64(fd: i32, buffers: ref array, first: i32, count: i32)
  -> (bytes_read: i64, errno: i32)
fd_readv_array_v128(fd: i32, buffers: ref array, first: i32, count: i32)
  -> (bytes_read: i64, errno: i32)

fd_writev_array_i8(fd: i32, buffers: ref array, first: i32, count: i32)
  -> (bytes_written: i64, errno: i32)
fd_writev_array_i16(fd: i32, buffers: ref array, first: i32, count: i32)
  -> (bytes_written: i64, errno: i32)
fd_writev_array_i32(fd: i32, buffers: ref array, first: i32, count: i32)
  -> (bytes_written: i64, errno: i32)
fd_writev_array_i64(fd: i32, buffers: ref array, first: i32, count: i32)
  -> (bytes_written: i64, errno: i32)
fd_writev_array_v128(fd: i32, buffers: ref array, first: i32, count: i32)
  -> (bytes_written: i64, errno: i32)
```

`first` and `count` are unsigned child indexes and counts.

The selected child range MUST fit entirely inside the outer array.

If it does not fit, the operation returns `ERR_RANGE`.

The runtime MUST NOT perform I/O in this error case.

Each selected child participates with its complete logical byte view.

Facet 0.1 does not define per-child slices for nested GC scatter/gather.

The runtime MUST validate the complete selected child range before it performs I/O.

Validation includes:

- non-null child references;
- dynamic element storage type;
- destination mutability for reads.

If validation fails, the operation MUST NOT partially consume the stream.

If validation fails, the operation MUST NOT modify an earlier child.

Normal stream short-transfer rules still apply after validation succeeds.

A successful short read or write MAY stop inside the logical byte view of the final child reached by the transfer.

Later children remain untouched.

## 22. Positioning and persistence

```text
fd_seek(fd: i32, signed_offset: i64, whence: i32)
  -> (new_offset: i64, errno: i32)

fd_tell(fd: i32)
  -> (offset: i64, errno: i32)

fd_set_size(fd: i32, size: i64)
  -> (errno: i32)

fd_sync(fd: i32)
  -> (errno: i32)

fd_datasync(fd: i32)
  -> (errno: i32)
```

## 23. Path representations

All path operations are relative to a directory capability.

Facet has no implicit process-wide current working directory from the operating system.

A path import name identifies the storage representation and code-unit width.

Linear-memory path families are:

```text
*_mem32_i8   *_mem32_i16   *_mem32_i32
*_mem64_i8   *_mem64_i16   *_mem64_i32
```

GC path families are:

```text
*_array_i8   *_array_i16   *_array_i32
```

Every path representation receives the `wtf: i32` boolean defined in section 8.

Facet does not use a path-encoding enum.

For linear memory, `pointer` is a byte address.

For linear memory, `length` and capacity values are code-unit counts.

Linear-memory `_i16` and `_i32` values use little-endian byte order.

For GC arrays, offsets and lengths are array-element counts.

For text arrays, one array element is one code unit.

The logical directory separator is `/`.

An embedded NUL is invalid in every Facet filesystem path.

An embedded NUL returns `ERR_INVALID`.

The runtime MUST prevent path traversal from escaping the authority represented by the supplied directory handle.

The runtime MUST apply the same rule to symbolic-link traversal.

## 24. Path open

For each `T` in `i8`, `i16`, and `i32`:

```text
path_open_mem32_T(directory: i32,
                  memory: i32, pointer: i32, length: i32, wtf: i32,
                  open_flags: i32, requested_rights: i64)
  -> (fd: i32, errno: i32)

path_open_mem64_T(directory: i32,
                  memory: i32, pointer: i64, length: i64, wtf: i32,
                  open_flags: i32, requested_rights: i64)
  -> (fd: i32, errno: i32)

path_open_array_T(directory: i32, path: ref array,
                  offset: i32, length: i32, wtf: i32,
                  open_flags: i32, requested_rights: i64)
  -> (fd: i32, errno: i32)
```

`T` is part of the actual import name.

Example: `path_open_mem32_i16`.

## 25. Path stat

Each `path_stat_*` function returns the same stat tuple as `fd_stat`.

For each `T` in `i8`, `i16`, and `i32`:

```text
path_stat_mem32_T(directory: i32,
                  memory: i32, pointer: i32, length: i32,
                  wtf: i32, flags: i32)
  -> stat-result

path_stat_mem64_T(directory: i32,
                  memory: i32, pointer: i64, length: i64,
                  wtf: i32, flags: i32)
  -> stat-result

path_stat_array_T(directory: i32, path: ref array,
                  offset: i32, length: i32,
                  wtf: i32, flags: i32)
  -> stat-result
```

`stat-result` is:

```text
(file_type: i32,
 stat_flags: i32,
 size: i64,
 atime_seconds: i64,
 atime_nanoseconds: i32,
 mtime_seconds: i64,
 mtime_nanoseconds: i32,
 ctime_seconds: i64,
 ctime_nanoseconds: i32,
 errno: i32)
```

## 26. Create and remove paths

For each `T` in `i8`, `i16`, and `i32`:

```text
path_create_dir_mem32_T(directory: i32,
                        memory: i32, pointer: i32, length: i32, wtf: i32)
  -> (errno: i32)
path_create_dir_mem64_T(directory: i32,
                        memory: i32, pointer: i64, length: i64, wtf: i32)
  -> (errno: i32)
path_create_dir_array_T(directory: i32, path: ref array,
                        offset: i32, length: i32, wtf: i32)
  -> (errno: i32)

path_remove_mem32_T(directory: i32,
                    memory: i32, pointer: i32, length: i32, wtf: i32,
                    remove_flags: i32)
  -> (errno: i32)
path_remove_mem64_T(directory: i32,
                    memory: i32, pointer: i64, length: i64, wtf: i32,
                    remove_flags: i32)
  -> (errno: i32)
path_remove_array_T(directory: i32, path: ref array,
                    offset: i32, length: i32, wtf: i32,
                    remove_flags: i32)
  -> (errno: i32)
```

## 27. Rename

Rename uses the same code-unit width for the source path and destination path.

This rule avoids a width cross-product of import names.

The source and destination MAY independently select strict or WTF mode.

For each `T` in `i8`, `i16`, and `i32`:

```text
path_rename_mem32_T(source_directory: i32,
                    source_memory: i32, source_pointer: i32,
                    source_length: i32, source_wtf: i32,
                    destination_directory: i32,
                    destination_memory: i32, destination_pointer: i32,
                    destination_length: i32, destination_wtf: i32,
                    flags: i32)
  -> (errno: i32)

path_rename_mem64_T(source_directory: i32,
                    source_memory: i32, source_pointer: i64,
                    source_length: i64, source_wtf: i32,
                    destination_directory: i32,
                    destination_memory: i32, destination_pointer: i64,
                    destination_length: i64, destination_wtf: i32,
                    flags: i32)
  -> (errno: i32)

path_rename_array_T(source_directory: i32,
                    source: ref array, source_offset: i32,
                    source_length: i32, source_wtf: i32,
                    destination_directory: i32,
                    destination: ref array, destination_offset: i32,
                    destination_length: i32, destination_wtf: i32,
                    flags: i32)
  -> (errno: i32)
```

## 28. Directory iteration

```text
dir_iter_open(directory: i32)
  -> (iterator: i32, errno: i32)
```

For each `T` in `i8`, `i16`, and `i32`:

```text
dir_iter_next_len_T(iterator: i32, wtf: i32)
  -> (units: i64, file_type: i32, inode: i64, done: i32, errno: i32)

dir_iter_next_mem32_T(iterator: i32, wtf: i32,
                      memory: i32, pointer: i32, capacity_units: i32)
  -> (units_written: i64, file_type: i32, inode: i64, done: i32, errno: i32)

dir_iter_next_mem64_T(iterator: i32, wtf: i32,
                      memory: i32, pointer: i64, capacity_units: i64)
  -> (units_written: i64, file_type: i32, inode: i64, done: i32, errno: i32)

dir_iter_next_into_array_T(iterator: i32, wtf: i32,
                           destination: ref array, offset: i32, capacity_units: i32)
  -> (units_written: i64, file_type: i32, inode: i64, done: i32, errno: i32)

dir_iter_next_array_T(iterator: i32, wtf: i32)
  -> (name: ref null $caller_T_array,
      file_type: i32, inode: i64, done: i32, errno: i32)
```

```text
dir_iter_rewind(iterator: i32) -> (errno: i32)
```

The iterator identifies the pending directory entry.

Facet does not allocate a separate name resource.

`dir_iter_next_len_T` snapshots the next entry without consuming it.

Repeated length queries observe the same pending entry.

A successful read form consumes the pending entry.

A successful allocating form also consumes the pending entry.

After consumption, the iterator advances.

If guest-owned capacity is insufficient, the operation returns `ERR_RANGE`.

In this case, the operation MUST NOT write to the destination.

In this case, the iterator MUST NOT advance.

The guest can query the matching length function and retry.

At end of iteration, `done == 1`.

At end of iteration, scalar metadata is zero.

At end of iteration, allocating forms return `ref.null` with `ERR_OK`.

`dir_iter_rewind` discards a pending snapshot.

`dir_iter_rewind` resets the iterator.

Release the iterator with `handle_close`.

## 29. Hard links

Hard links use the same code-unit width for source and destination.

For each `T` in `i8`, `i16`, and `i32`, `path_link_mem32_T`, `path_link_mem64_T`, and `path_link_array_T` use the same argument shapes as the corresponding `path_rename_*_T` functions.

## 30. Symbolic links

The symbolic-link target and destination use the same code-unit width.

The target and destination MAY use independent `wtf` values.

For each `T` in `i8`, `i16`, and `i32`:

```text
path_symlink_mem32_T(target_memory: i32, target_pointer: i32,
                     target_length: i32, target_wtf: i32,
                     destination_directory: i32,
                     destination_memory: i32, destination_pointer: i32,
                     destination_length: i32, destination_wtf: i32)
  -> (errno: i32)

path_symlink_mem64_T(target_memory: i32, target_pointer: i64,
                     target_length: i64, target_wtf: i32,
                     destination_directory: i32,
                     destination_memory: i32, destination_pointer: i64,
                     destination_length: i64, destination_wtf: i32)
  -> (errno: i32)

path_symlink_array_T(target: ref array, target_offset: i32,
                     target_length: i32, target_wtf: i32,
                     destination_directory: i32,
                     destination: ref array, destination_offset: i32,
                     destination_length: i32, destination_wtf: i32)
  -> (errno: i32)
```

## 31. Read symbolic link

`path_readlink_*` does not create an intermediate string resource.

The input path and output target use the same code-unit width.

This rule avoids a representation cross-product of import names.

The path and target MAY independently select strict or WTF mode.

For each `T` in `i8`, `i16`, and `i32`:

```text
path_readlink_len_mem32_T(directory: i32,
                          path_memory: i32, path_pointer: i32,
                          path_length: i32, path_wtf: i32,
                          target_wtf: i32)
  -> (units: i64, errno: i32)

path_readlink_mem32_T(directory: i32,
                      path_memory: i32, path_pointer: i32,
                      path_length: i32, path_wtf: i32,
                      target_memory: i32, target_pointer: i32,
                      target_capacity_units: i32, target_wtf: i32)
  -> (units_written: i64, errno: i32)

path_readlink_len_mem64_T(directory: i32,
                          path_memory: i32, path_pointer: i64,
                          path_length: i64, path_wtf: i32,
                          target_wtf: i32)
  -> (units: i64, errno: i32)

path_readlink_mem64_T(directory: i32,
                      path_memory: i32, path_pointer: i64,
                      path_length: i64, path_wtf: i32,
                      target_memory: i32, target_pointer: i64,
                      target_capacity_units: i64, target_wtf: i32)
  -> (units_written: i64, errno: i32)

path_readlink_len_array_T(directory: i32, path: ref array,
                          offset: i32, length: i32, path_wtf: i32,
                          target_wtf: i32)
  -> (units: i64, errno: i32)

path_readlink_into_array_T(directory: i32, path: ref array,
                           path_offset: i32, path_length: i32, path_wtf: i32,
                           destination: ref array, destination_offset: i32,
                           target_capacity_units: i32, target_wtf: i32)
  -> (units_written: i64, errno: i32)

path_readlink_array_T(directory: i32, path: ref array,
                      offset: i32, length: i32, path_wtf: i32,
                      target_wtf: i32)
  -> (target: ref null $caller_T_array, errno: i32)
```

A guest-owned target buffer MUST have enough capacity for the complete stored target.

Insufficient capacity returns `ERR_RANGE`.

In this case, the runtime MUST NOT modify the destination.

The returned text is the stored symbolic-link target.

The runtime does not recursively resolve the returned target.

## 32. Networking constants

```text
AF_UNSPEC = 0
AF_INET4  = 1
AF_INET6  = 2

SOCK_STREAM = 1
SOCK_DGRAM  = 2

PROTO_DEFAULT = 0
PROTO_TCP     = 1
PROTO_UDP     = 2

SOCK_NONBLOCK = 1 << 0

SHUT_RD   = 1
SHUT_WR   = 2
SHUT_RDWR = 3
```

IP addresses use these fields:

```text
family:      i32
address_hi:  i64
address_lo:  i64
port:        i32
scope_id:    i32
```

For IPv4, `address_hi == 0`.

For IPv4, the low 32 bits of `address_lo` contain the address in network bit order.

For IPv4, `scope_id == 0`.

For IPv6, `address_hi` contains the most-significant 64 bits.

For IPv6, `address_lo` contains the least-significant 64 bits.

## 33. Socket lifecycle

```text
socket_open(family: i32, socket_type: i32, protocol: i32, flags: i32)
  -> (fd: i32, errno: i32)

socket_bind(fd: i32, family: i32,
            address_hi: i64, address_lo: i64,
            port: i32, scope_id: i32)
  -> (errno: i32)

socket_connect(fd: i32, family: i32,
               address_hi: i64, address_lo: i64,
               port: i32, scope_id: i32)
  -> (errno: i32)

socket_listen(fd: i32, backlog: i32)
  -> (errno: i32)

socket_accept(fd: i32, flags: i32)
  -> (client_fd: i32,
      family: i32,
      address_hi: i64,
      address_lo: i64,
      port: i32,
      scope_id: i32,
      errno: i32)

socket_local_address(fd: i32)
  -> (family: i32, address_hi: i64, address_lo: i64,
      port: i32, scope_id: i32, errno: i32)

socket_peer_address(fd: i32)
  -> (family: i32, address_hi: i64, address_lo: i64,
      port: i32, scope_id: i32, errno: i32)

socket_shutdown(fd: i32, how: i32)
  -> (errno: i32)
```

Connected stream sockets use the ordinary `fd_read_*`, `fd_write_*`, `fd_readv_*`, and `fd_writev_*` operations for data transfer.

## 34. Datagram receive

```text
socket_recvfrom_mem32(fd: i32,
                      memory: i32, pointer: i32, length: i32,
                      flags: i32)
  -> (bytes_read: i64,
      family: i32, address_hi: i64, address_lo: i64,
      port: i32, scope_id: i32,
      message_flags: i32,
      errno: i32)

socket_recvfrom_mem64(fd: i32,
                      memory: i32, pointer: i64, length: i64,
                      flags: i32)
  -> same-recv-result

socket_recvfrom_array_i8(fd: i32, destination: ref array,
                         byte_offset: i64, byte_length: i64, flags: i32)
  -> same-recv-result
socket_recvfrom_array_i16(...)  -> same-recv-result
socket_recvfrom_array_i32(...)  -> same-recv-result
socket_recvfrom_array_i64(...)  -> same-recv-result
socket_recvfrom_array_v128(...) -> same-recv-result
```

## 35. Datagram send

```text
socket_sendto_mem32(fd: i32,
                    memory: i32, pointer: i32, length: i32,
                    family: i32, address_hi: i64, address_lo: i64,
                    port: i32, scope_id: i32, flags: i32)
  -> (bytes_written: i64, errno: i32)

socket_sendto_mem64(fd: i32,
                    memory: i32, pointer: i64, length: i64,
                    family: i32, address_hi: i64, address_lo: i64,
                    port: i32, scope_id: i32, flags: i32)
  -> (bytes_written: i64, errno: i32)

socket_sendto_array_i8(fd: i32, source: ref array,
                       byte_offset: i64, byte_length: i64,
                       family: i32, address_hi: i64, address_lo: i64,
                       port: i32, scope_id: i32, flags: i32)
  -> (bytes_written: i64, errno: i32)
socket_sendto_array_i16(...)  -> (bytes_written: i64, errno: i32)
socket_sendto_array_i32(...)  -> (bytes_written: i64, errno: i32)
socket_sendto_array_i64(...)  -> (bytes_written: i64, errno: i32)
socket_sendto_array_v128(...) -> (bytes_written: i64, errno: i32)
```

## 36. DNS

DNS hostnames use the same text rules as other Facet text.

The import suffix selects `i8`, `i16`, or `i32`.

`wtf` selects strict Unicode or surrogate-sentinel mode.

For each `T` in `i8`, `i16`, and `i32`:

```text
dns_resolve_mem32_T(memory: i32, pointer: i32, length: i32,
                    wtf: i32, family: i32, flags: i32)
  -> (resolver: i32, errno: i32)

dns_resolve_mem64_T(memory: i32, pointer: i64, length: i64,
                    wtf: i32, family: i32, flags: i32)
  -> (resolver: i32, errno: i32)

dns_resolve_array_T(hostname: ref array, offset: i32, length: i32,
                    wtf: i32, family: i32, flags: i32)
  -> (resolver: i32, errno: i32)
```

```text
dns_next(resolver: i32)
  -> (family: i32,
      address_hi: i64,
      address_lo: i64,
      scope_id: i32,
      done: i32,
      errno: i32)
```

Release a resolver handle with `handle_close`.

## 37. Polling

```text
POLL_READABLE = 1 << 0
POLL_WRITABLE = 1 << 1
POLL_HANGUP   = 1 << 2
POLL_ERROR    = 1 << 3
POLL_TIMER    = 1 << 4

POLL_SOURCE_FD    = 1
POLL_SOURCE_TIMER = 2
```

```text
poll_create() -> (poll: i32, errno: i32)

poll_add_fd(poll: i32, fd: i32, interests: i32, userdata: i64)
  -> (errno: i32)

poll_update_fd(poll: i32, fd: i32, interests: i32, userdata: i64)
  -> (errno: i32)

poll_remove_fd(poll: i32, fd: i32)
  -> (errno: i32)

poll_add_timer(poll: i32, monotonic_deadline_ns: i64, userdata: i64)
  -> (subscription_id: i32, errno: i32)

poll_remove_timer(poll: i32, subscription_id: i32)
  -> (errno: i32)

poll_wait(poll: i32, monotonic_deadline_ns: i64)
  -> (ready_count: i32, errno: i32)

poll_next(poll: i32)
  -> (source_kind: i32,
      source_id: i32,
      events: i32,
      userdata: i64,
      done: i32,
      errno: i32)
```

`UINT64_MAX` as the `poll_wait` deadline means that the call has no deadline.

The guest MUST consume all ready events from one `poll_wait` before it calls `poll_wait` again on the same poll set.

If it does not, `poll_wait` returns `ERR_BUSY`.

## 38. GC implementation contract

A runtime that implements a raw GC-array destination SHOULD conceptually perform these steps:

1. validate that the reference is an array;
2. validate the dynamic element storage type;
3. validate mutability for a destination operation;
4. validate `byte_offset + byte_length` with overflow-safe arithmetic;
5. keep the object alive;
6. establish a pin, no-move scope, no-GC scope, or equivalent mechanism if required;
7. resolve the current backing representation;
8. perform the synchronous operation;
9. preserve bytes outside the requested logical range;
10. invalidate any temporary native view before the collector scope ends.

A runtime MAY directly expose contiguous pointer-free payload storage to the operating-system or runtime I/O operation when its collector makes this safe.

A runtime MAY instead use temporary runtime-owned native storage.

If it uses temporary storage, the runtime encodes or decodes the logical byte view as required.

Both strategies conform when they produce the same observable result.

## 39. Zero-copy guidance

Facet does not guarantee zero-copy execution.

Facet does guarantee that an ABI conversion through unrelated guest linear memory is unnecessary.

A runtime SHOULD avoid intermediate copies when direct access is safe for its memory representation, GC representation, and operating-system API.

## 40. Concurrency

Facet 0.1 functions are synchronous.

A runtime MAY invoke Facet functions concurrently from multiple Wasm threads or execution contexts.

A close can race with another operation on the same handle.

The runtime MAY allow an already-admitted operation to complete.

The runtime MAY instead cause that operation to return `ERR_BAD_HANDLE`.

The race MUST NOT cause use-after-free.

## 41. Security requirements

A conforming runtime MUST:

1. validate every guest handle before use;
2. validate memory indexes and address widths;
3. bounds-check ranges with overflow-safe arithmetic;
4. validate GC array kind, dynamic element type, destination mutability, and caller-selected concrete allocation result types;
5. validate text according to the selected representation and `wtf` mode;
6. prevent filesystem escape beyond the supplied directory capability;
7. enforce filesystem authority granted by the embedder;
8. enforce network authority granted by the embedder;
9. prevent a borrowed GC or linear-memory view from outliving its safe synchronous scope;
10. clean up instance-owned resources when the instance is destroyed.

## 42. Language implementation guidance

Languages SHOULD expose semantic system operations instead of exposing Facet representation details directly when a higher-level API is appropriate.

A compiler can lower a source-language buffer to these Facet forms:

```text
Memory32 slice -> *_mem32
Memory64 slice -> *_mem64
GC array<i8>   -> *_array_i8
GC array<i16>  -> *_array_i16
GC array<i32>  -> *_array_i32
GC array<i64>  -> *_array_i64
GC array<v128> -> *_array_v128
```

A UTF-16 or UTF-32 string SHOULD remain in its native representation when the corresponding Facet function exists.

Conversion through UTF-8 is not required.

A GC-oriented language SHOULD prefer an allocating `*_read_array_*` function when it wants a fresh string.

A GC-oriented language SHOULD prefer `*_read_into_array_*` when it already owns reusable destination storage.

## 43. Explicit omissions from 0.1

Facet 0.1 does not define:

- process spawning;
- signals;
- threads or synchronization primitives;
- asynchronous host functions;
- HTTP or TLS;
- GPU or GUI access;
- arbitrary GC struct ABI records;
- retained runtime ownership of guest GC references;
- automatic WASI compatibility.

A future specification can add independent extensions for these areas.

## 44. Compatibility policy

A published stable Facet function signature is immutable.

If a semantic rule or Core WebAssembly signature must change incompatibly, the specification MUST introduce a new import name.

The specification MAY add new representation variants without modifying existing variants.

## 45. Rationale for explicit names

Facet does not overload one import name by function type.

Explicit representation names have these benefits:

- they use ordinary Core WebAssembly import resolution;
- they work with runtimes that index functions by module and field name;
- they make missing feature support visible;
- they make traces and debugging clearer;
- they allow incremental GC and Memory64 support;
- they avoid special linker semantics.

The duplicated names are intentional.

Facet accepts this naming cost to avoid another ABI-description and runtime-negotiation layer.
