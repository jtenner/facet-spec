# WPSI 0.1 — WebAssembly Portable System Interface

**Status:** Draft  
**Version:** 0.1  
**Import module:** `wpsi`

## 1. Overview

WPSI is a low-level system interface for Core WebAssembly modules.

WPSI deliberately avoids an interface-definition language, canonical lowering layer, component model, or linker-specific polymorphic import resolution. A WPSI operation is represented directly as a Core WebAssembly imported function.

Representation differences that change the Core WebAssembly calling convention are encoded in the imported function name.

For example:

```text
fd_read_mem32
fd_read_mem64
fd_read_array_i8
fd_read_array_i16
fd_read_array_i32
fd_read_array_i64
fd_read_array_v128
```

These functions perform the same semantic operation with different physical guest representations.

WPSI has four primary design goals:

1. work naturally with WebAssembly multi-memory and Memory64;
2. treat WebAssembly GC arrays as legitimate system-call buffers;
3. support UTF-8, UTF-16, and UTF-32 without mandatory conversion through UTF-8;
4. preserve capability-oriented sandboxing while giving filesystem-enabled instances private writable scratch storage by default.

## 2. Normative language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative requirements.

## 3. Core design rules

### 3.1 Core WebAssembly is the ABI

WPSI function signatures use Core WebAssembly types directly. There is no canonical ABI between a guest and WPSI.

### 3.2 Representation-specific names

If two guest representations require materially different Core Wasm signatures, they receive different import names.

Semantic options that do not change the Core Wasm representation SHOULD remain ordinary parameters.

### 3.3 Memory 0 is not privileged

Every operation that accesses linear memory receives an explicit `memory_index`.

No WPSI function implicitly selects memory 0.

### 3.4 GC arrays are first-class buffers

A guest MAY pass a WebAssembly GC array directly to a WPSI function. The implementation MUST NOT require the guest to copy that array through unrelated linear memory.

### 3.5 Caller-typed GC allocation results

Most GC-array parameters use the abstract `(ref array)` type and are dynamically validated by the runtime.

A small set of host-originated string functions instead allocate and return a new GC array. For those functions, the importing module declares a **concrete nullable array result type** such as:

```wat
(type $string16 (array (mut i16)))
(import "wpsi" "args_read_array_i16"
  (func (param i32 i32) (result (ref null $string16) i32)))
```

The function name fixes the required element storage class (`i8`, `i16`, or `i32`). The concrete array type is selected by the importing module. At instantiation the runtime MUST validate that the requested concrete result type is an array with the storage class named by the import. The element may be mutable or immutable. An incompatible concrete result type is an import-type mismatch and MUST fail instantiation; it is not a runtime `errno`.

On success the host allocates exactly that concrete Wasm GC type and returns a non-null reference. On call failure it returns `ref.null` and a nonzero `errno`.

This is a narrow type-specialization rule for host allocation, not semantic overload resolution: the operation and storage class remain determined by the import name.

### 3.6 Incremental implementation is allowed

A runtime MAY implement only the WPSI profiles for WebAssembly features it supports. Missing imports fail through normal WebAssembly instantiation.

## 4. Conformance profiles

The initial profiles are:

```text
wpsi-core
wpsi-memory32
wpsi-memory64
wpsi-gc-array
wpsi-filesystem
wpsi-links
wpsi-network
wpsi-poll
```

`wpsi-core` defines scalar operations, handles, process information, clocks, arguments, environment strings, and random scalar values.

`wpsi-memory32` defines `_mem32` buffer operations.

`wpsi-memory64` defines `_mem64` buffer operations.

`wpsi-gc-array` defines `_array_*` operations.

`wpsi-filesystem` defines private scratch storage, preopens, descriptors, directory iteration, and path operations.

`wpsi-links` defines hard-link and symbolic-link operations.

`wpsi-network` defines sockets and DNS.

`wpsi-poll` defines multi-resource polling.

## 5. Fundamental ABI conventions

Conceptual aliases used by this specification are:

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

All WPSI resources are opaque nonzero `i32` handles.

Handle `0` is always invalid.

Handles are instance-local and unforgeable in the semantic sense: an implementation MUST validate a handle before dereferencing the resource it names.

An implementation MUST prevent a stale closed handle from accidentally gaining authority over an unrelated resource solely through unchecked slot reuse. Generation counters, monotonic IDs, delayed reuse, or equivalent mechanisms are acceptable.

### 5.2 Error convention

`errno` is always the final result value when present.

```text
ERR_OK = 0
```

On failure, non-error results MUST be zero unless a function explicitly states otherwise.

Guest-controlled invalid input SHOULD return an error instead of trapping. Traps are reserved for runtime invariants, explicit termination, or unrecoverable implementation failure.

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

Unless otherwise specified, sizes, indexes, offsets, and counts carried in `i32` are interpreted as unsigned 32-bit values and those carried in `i64` as unsigned 64-bit values.

`fd_seek.signed_offset` is interpreted as signed `i64`.

All bounds arithmetic MUST be overflow-safe.

## 6. Linear memory representations

### 6.1 Memory32

A `_mem32` operation receives:

```text
memory_index: i32
pointer:      i32
length:       i32
```

The selected memory MUST have an `i32` address type. Selecting a Memory64 memory returns `ERR_TYPE`.

### 6.2 Memory64

A `_mem64` operation receives:

```text
memory_index: i32
pointer:      i64
length:       i64
```

The selected memory MUST have an `i64` address type. Selecting a Memory32 memory returns `ERR_TYPE`.

### 6.3 Memory index space

`memory_index` is an index into the calling module instance's normal WebAssembly memory index space. Imported and locally defined memories participate normally.

Invalid indexes or out-of-bounds ranges return `ERR_FAULT`.

## 7. WebAssembly GC array representations

GC-array functions accept an abstract non-null array reference:

```wat
(ref array)
```

The imported function name defines the required dynamic element storage type.

Supported raw buffer variants are:

```text
array_i8
array_i16
array_i32
array_i64
array_v128
```

For destination operations the dynamic array element must be mutable.

Type or mutability mismatch returns `ERR_TYPE`.

### 7.1 Normative logical byte view

WPSI defines a logical byte view for supported numeric arrays. This rule defines observable behavior and does **not** require any particular physical GC heap layout.

Element widths are:

```text
i8    = 1 byte
i16   = 2 bytes
i32   = 4 bytes
i64   = 8 bytes
v128  = 16 bytes
```

Integer elements are represented little-endian in the logical byte view.

A `v128` element exposes the same sequence of 16 bytes that the value would have when stored by WebAssembly's ordinary `v128.store` semantics.

For example, an `array<i32>` element whose value is `0x12345678` contributes:

```text
78 56 34 12
```

### 7.2 Byte offsets and partial elements

Raw array I/O takes `byte_offset: i64` and `byte_length: i64`.

An operation MAY begin or end inside an element. Bytes outside the selected logical byte range MUST remain unchanged.

Consequently, reading one byte into the first byte of an `i32` element changes only the corresponding eight value bits.

All bit patterns are valid for the supported integer and `v128` buffer types.

### 7.3 Lifetime and moving collectors

A runtime MUST keep the referenced object alive for the complete synchronous host call.

A raw backing pointer or slice MUST NOT escape the collector scope in which its address is valid.

Moving collectors MUST pin, enter an appropriate no-move/no-GC region, re-resolve addresses safely, or copy through implementation-private native storage as required.

### 7.4 Nested arrays

Scatter/gather GC operations accept an outer `(ref array)` whose selected children MUST be non-null references to arrays of the element type named by the function.

Read operations require mutable child arrays.

## 8. Text representations and WTF mode

WPSI does not use a text-encoding enum.

The import name identifies the physical text representation:

```text
_i8  = 8-bit code units
_i16 = 16-bit code units
_i32 = 32-bit code points
```

Linear-memory text imports combine the memory address width and text width in the name, for example:

```text
args_read_mem32_i8
args_read_mem64_i16
path_open_mem32_i32
```

GC-array text imports use the existing `array_i8`, `array_i16`, and `array_i32` families.

Every textual operation receives:

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

- `_i8` is well-formed UTF-8;
- `_i16` is well-formed UTF-16;
- `_i32` contains Unicode scalar values only.

With `wtf == 1`, surrogate code points in `0xd800..0xdfff` are permitted as reversible sentinel values:

- `_i8` uses WTF-8;
- `_i16` uses WTF-16 code units;
- `_i32` stores the code-point values directly, including surrogate sentinels.

WPSI MUST NOT silently replace an unrepresentable host unit with U+FFFD. Strict mode returns `ERR_ILLEGAL_SEQUENCE`; WTF mode preserves such values through surrogate sentinels when the host namespace can be represented that way.

On byte-string host namespaces, invalid UTF-8 bytes `0x80..0xff` SHOULD be mapped reversibly to `U+DC80..U+DCFF`. On UTF-16 host namespaces, unpaired surrogate code units are preserved directly. A host that still cannot represent a requested WTF sequence returns `ERR_ILLEGAL_SEQUENCE`.

Linear-memory `_i16` and `_i32` values are little-endian. WPSI strings are length-delimited and are never implicitly NUL-terminated.

## 9. Host-originated strings

WPSI does not define a string resource handle. A host-originated string is identified by the operation that owns it: an argument index, environment-entry index, preopen index, directory iterator position, or symbolic-link path.

For stable indexed sources, WPSI exposes three forms:

1. `*_len_i8`, `*_len_i16`, and `*_len_i32` return the required code-unit count;
2. `*_read_mem32_i*`, `*_read_mem64_i*`, and `*_read_into_array_i*` copy into caller-owned storage;
3. `*_read_array_i*` allocates and returns a caller-typed concrete GC array.

The representation suffix selects the code-unit width. `wtf` selects strict Unicode or surrogate-sentinel semantics. There is no second encoding selector.

Linear-memory forms necessarily receive an explicit memory index, pointer, and capacity. GC `read_into` forms receive an existing `(ref array)`, element offset, and capacity. Allocating GC forms return `(ref null $caller_type, errno)` as described in section 3.5.

A successful allocating function returns an array whose length exactly equals the represented string length. Empty strings return a non-null zero-length array.

For all allocating string functions:

- an invalid source index returns `(null, ERR_RANGE)`;
- an invalid `wtf` value returns `(null, ERR_INVALID)`;
- a source value that cannot be represented losslessly under the requested mode returns `(null, ERR_ILLEGAL_SEQUENCE)`;
- allocation failure returns `(null, ERR_NO_MEMORY)`.

For caller-owned destinations, insufficient capacity returns `ERR_RANGE`, writes nothing, and leaves the source position unchanged when the source is stateful. A wrong GC destination storage class returns `ERR_TYPE`. No WPSI string-copy function appends a NUL terminator.

## 10. Capabilities and scratch storage

WPSI resource handles represent authority.

Host filesystem and networking authority MUST be explicitly granted by the embedder.

A child resource MUST NOT gain greater authority than the capability from which it was derived.

A filesystem-enabled instance MUST have a private writable scratch filesystem even when no host directory has been granted.

The scratch filesystem:

- begins logically empty;
- is private unless explicitly shared by the embedder;
- grants no authority over unrelated host paths;
- MUST prevent escape into the host filesystem;
- MAY be memory-backed, temp-directory-backed, overlay-backed, or otherwise virtualized;
- MAY enforce host-configured quotas;
- is destroyed or made unreachable when the instance is destroyed.

A libc compatibility layer SHOULD normally map this capability to `/tmp`, but `/tmp` is not part of the WPSI ABI.

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

All functions are imported from module `"wpsi"`.

```text
abi_version() -> (version: i32)

handle_close(handle: i32) -> (errno: i32)

proc_exit(exit_code: i32) -> ()

proc_yield() -> (errno: i32)

stdio_stdin()  -> (fd: i32, errno: i32)
stdio_stdout() -> (fd: i32, errno: i32)
stdio_stderr() -> (fd: i32, errno: i32)
```

WPSI 0.1 reports `abi_version() == 1`.

## 13. Arguments and environment

Argument and environment ordering MUST remain stable for the lifetime of the instance.

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

Environment entries use a scalar field selector:

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

## 16. Filesystem roots

```text
fs_scratch() -> (directory: i32, errno: i32)

fs_scratch_limits()
  -> (byte_quota: i64, object_quota: i64, errno: i32)

fs_scratch_usage()
  -> (bytes_used: i64, object_count: i64, errno: i32)

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

`UINT64_MAX` means a quota dimension is not declared.

Preopen ordering and display names MUST remain stable for the lifetime of the instance.

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

`pread` and `pwrite` MUST NOT change the descriptor's sequential file position.

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

All path operations are relative to a directory capability. WPSI has no implicit process-wide host current working directory.

Path import names identify both the storage representation and code-unit width.

Linear-memory path families are:

```text
*_mem32_i8   *_mem32_i16   *_mem32_i32
*_mem64_i8   *_mem64_i16   *_mem64_i32
```

GC path families are:

```text
*_array_i8   *_array_i16   *_array_i32
```

Every path representation receives a `wtf: i32` boolean as defined in section 8. There is no path encoding enum.

For linear memory, `pointer` is a byte address while `length` and capacities are measured in code units. `_i16` and `_i32` values are little-endian. For GC arrays, offsets and lengths are measured in array elements/code units.

The logical directory separator is `/`. Embedded NUL is invalid in every WPSI filesystem path and returns `ERR_INVALID`.

An implementation MUST prevent path or symlink traversal from escaping the authority represented by the directory handle.

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

`T` is part of the actual import name; for example `path_open_mem32_i16`.

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

Rename uses the same code-unit width for both paths to avoid a width cross-product. The source and destination may independently choose strict or WTF mode.

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

The iterator itself identifies the pending directory entry; WPSI does not allocate a separate name resource.

`dir_iter_next_len_T` peeks and snapshots the next entry without consuming it. Repeated length queries observe the same pending entry. Any successful read or allocating next call consumes that entry and advances the iterator.

If caller-owned capacity is insufficient, the operation returns `ERR_RANGE`, performs no write, and does not advance. The caller may query the matching length function and retry.

At end of iteration, `done == 1`, scalar metadata is zero, and allocating forms return `ref.null` with `ERR_OK`.

`dir_iter_rewind` discards any pending snapshot and resets the iterator. The iterator is released with `handle_close`.

## 29. Hard links

Hard links use the same code-unit width for source and destination. For each `T` in `i8`, `i16`, and `i32`, `path_link_mem32_T`, `path_link_mem64_T`, and `path_link_array_T` use the same argument shapes as the corresponding `path_rename_*_T` functions.

## 30. Symbolic links

The symlink target and destination use the same code-unit width but independent `wtf` flags.

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

`path_readlink_*` never creates an intermediate string resource. The input path and output target use the same code-unit width to avoid a representation cross-product, but may independently choose strict or WTF mode.

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

Caller-owned reads require enough capacity for the complete target; insufficient capacity returns `ERR_RANGE` without modifying the destination.

The returned target is the stored symbolic-link text and is not recursively resolved.

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

IP addresses are represented as:

```text
family:      i32
address_hi:  i64
address_lo:  i64
port:        i32
scope_id:    i32
```

For IPv4, `address_hi == 0`, the low 32 bits of `address_lo` contain the address in network bit order, and `scope_id == 0`.

For IPv6, `address_hi` is the most-significant 64 bits and `address_lo` the least-significant 64 bits.

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

Connected stream sockets use ordinary `fd_read_*`, `fd_write_*`, `fd_readv_*`, and `fd_writev_*` data transfer.

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

DNS hostnames use the same text representation rule as other WPSI text: the import suffix chooses `i8`, `i16`, or `i32`, and `wtf` selects strict Unicode or surrogate-sentinel mode.

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

Resolver handles are released with `handle_close`.

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

`UINT64_MAX` as the `poll_wait` deadline means no deadline.

All ready events from one `poll_wait` MUST be consumed before another `poll_wait`; otherwise `ERR_BUSY` is returned.

## 38. GC implementation contract

A runtime implementing a raw GC-array destination SHOULD conceptually perform:

```text
1. validate the reference is an array;
2. validate its dynamic element storage type;
3. validate mutability for destination operations;
4. validate byte_offset + byte_length with overflow-safe arithmetic;
5. root the object;
6. establish any pin/no-move/no-GC scope required by the collector;
7. resolve the current backing representation;
8. perform the synchronous operation;
9. preserve bytes outside the requested logical range;
10. invalidate any temporary native view before leaving the collector scope.
```

An implementation MAY directly expose contiguous pointer-free payload storage to the host operation where its collector permits this.

An implementation MAY instead use temporary native storage and encode/decode the logical byte view.

Both implementations are conforming if observable results are identical.

## 39. Zero-copy guidance

WPSI does not guarantee zero-copy execution.

WPSI does guarantee that ABI conversion through unrelated guest linear memory is unnecessary.

Implementations SHOULD avoid intermediate copies when their memory or GC representation and host API make direct access safe.

## 40. Concurrency

WPSI 0.1 functions are synchronous.

A runtime MAY invoke them concurrently from multiple Wasm threads.

A close racing with an operation MAY either allow the already-admitted operation to complete or cause it to return `ERR_BAD_HANDLE`. It MUST NOT cause use-after-free.

## 41. Security requirements

A conforming implementation MUST:

1. validate all guest handles before use;
2. validate memory indexes and address widths;
3. bounds-check ranges with overflow-safe arithmetic;
4. validate GC array kind, dynamic element type, destination mutability, and caller-selected concrete allocation result types;
5. validate text according to the declared encoding;
6. prevent filesystem escape beyond directory capability authority;
7. keep private scratch storage isolated from unrelated host files;
8. enforce host-granted filesystem and network capabilities;
9. prevent synchronous GC borrows from outliving their safe collector scope;
10. clean up instance-owned resources when the instance is destroyed.

## 42. Language implementation guidance

Languages SHOULD expose semantic operations rather than WPSI representation details.

A compiler may lower:

```text
Memory32 slice -> *_mem32
Memory64 slice -> *_mem64
GC array<i8>   -> *_array_i8
GC array<i16>  -> *_array_i16
GC array<i32>  -> *_array_i32
GC array<i64>  -> *_array_i64
GC array<v128> -> *_array_v128
```

UTF-16 and UTF-32 strings SHOULD remain in their native representation when the corresponding WPSI function exists; conversion through UTF-8 is not required. GC-oriented languages SHOULD prefer allocating `*_read_array_*` functions when they want a fresh string and `*_read_into_array_*` when they already own reusable storage.

## 43. Explicit omissions from 0.1

The initial specification intentionally does not define:

- process spawning;
- signals;
- threads or synchronization primitives;
- asynchronous host functions;
- HTTP or TLS;
- GPU or GUI access;
- arbitrary GC struct ABI records;
- retained host ownership of guest GC references;
- automatic WASI compatibility.

These may be added as independent extensions.

## 44. Compatibility policy

Published stable WPSI function signatures are immutable.

If semantics or a Core WebAssembly signature must change incompatibly, a new import name MUST be introduced.

New representation variants MAY be added without modifying existing variants.

## 45. Rationale for explicit names

WPSI does not overload the same import name by function type.

Explicit representation names are preferred because they:

- use ordinary import resolution;
- work with runtimes that index host functions by module and field name;
- make missing feature support obvious;
- make traces and debugging clearer;
- allow incremental GC and Memory64 support;
- avoid special linker semantics.

The deliberate naming duplication is considered less costly than introducing another ABI-description layer.
