#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text.rstrip() + "\n", encoding="utf-8")


def replace_section(text: str, start: str, end: str, replacement: str) -> str:
    a = text.index(start)
    b = text.index(end, a)
    return text[:a] + replacement.rstrip() + "\n\n" + text[b:]


def replace_block(text: str, start: str, end: str, replacement: str) -> str:
    a = text.index(start)
    b = text.index(end, a)
    return text[:a] + replacement.rstrip() + "\n\n" + text[b:]


# ---------------------------------------------------------------------------
# SPEC.md
# ---------------------------------------------------------------------------

spec = read("SPEC.md")

spec = spec.replace(
    "At instantiation the runtime MUST validate that the requested concrete result type is an array with the storage class named by the import. The element may be mutable or immutable.\n\nOn success the host allocates exactly that concrete Wasm GC type and returns a non-null reference. On failure it returns `ref.null` and a nonzero `errno`.",
    "At instantiation the runtime MUST validate that the requested concrete result type is an array with the storage class named by the import. The element may be mutable or immutable. An incompatible concrete result type is an import-type mismatch and MUST fail instantiation; it is not a runtime `errno`.\n\nOn success the host allocates exactly that concrete Wasm GC type and returns a non-null reference. On call failure it returns `ref.null` and a nonzero `errno`.",
)

spec = replace_section(
    spec,
    "## 8. Text encodings",
    "## 10. Capabilities and scratch storage",
    r'''## 8. Text representations and WTF mode

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

For caller-owned destinations, insufficient capacity returns `ERR_RANGE`, writes nothing, and leaves the source position unchanged when the source is stateful. A wrong GC destination storage class returns `ERR_TYPE`. No WPSI string-copy function appends a NUL terminator.'''
)

spec = replace_section(
    spec,
    "## 13. Arguments and environment",
    "## 14. Clocks",
    r'''## 13. Arguments and environment

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

An unknown environment field selector returns `ERR_INVALID`.'''
)

spec = replace_section(
    spec,
    "## 16. Filesystem roots",
    "## 17. Descriptor metadata",
    r'''## 16. Filesystem roots

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

Preopen ordering and display names MUST remain stable for the lifetime of the instance.'''
)

spec = replace_section(
    spec,
    "## 23. Path representations",
    "## 32. Networking constants",
    r'''## 23. Path representations

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

The returned target is the stored symbolic-link text and is not recursively resolved.'''
)

spec = replace_section(
    spec,
    "## 36. DNS",
    "## 37. Polling",
    r'''## 36. DNS

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

Resolver handles are released with `handle_close`.'''
)

write("SPEC.md", spec)


# ---------------------------------------------------------------------------
# spec/behavior.md
# ---------------------------------------------------------------------------

behavior = read("spec/behavior.md")
behavior = behavior.replace(
    "Validate enum values, flag masks, reserved bits, mutually incompatible scalar options, numeric domains such as port ranges, and other scalar-only constraints.",
    "Validate booleans such as `wtf`, enum values, flag masks, reserved bits, mutually incompatible scalar options, numeric domains such as port ranges, and other scalar-only constraints.",
)
behavior = behavior.replace(
    "Validate the requested encoding and decode or validate text where the operation requires text semantics.",
    "Validate the code-unit representation selected by the import name and apply strict or WTF text semantics where the operation requires text.",
)
behavior = behavior.replace(
    "Text cannot be represented or decoded losslessly in the requested encoding.",
    "Text cannot be represented or decoded losslessly in the selected code-unit representation and WTF mode.",
)
behavior = behavior.replace(
    "or an incompatible concrete GC allocation result type.",
    ".",
)

behavior = replace_section(
    behavior,
    "## 5. Host-originated string transfer",
    "## 6. Polling semantics",
    r'''## 5. Text and host-originated string transfer

WPSI does not use an encoding enum and does not use resource handles merely to transport strings.

### 5.1 Representation and WTF mode

The text width is selected by the import name:

```text
_i8  -> UTF-8 / WTF-8 code units
_i16 -> UTF-16 / WTF-16 code units
_i32 -> 32-bit code points
```

Every textual operation receives `wtf: i32`:

```text
0 = strict Unicode
1 = WTF / surrogate-sentinel mode
```

Other values return `ERR_INVALID` before any guest destination or host namespace is touched.

Strict mode rejects malformed UTF-8, unpaired UTF-16 surrogates, surrogate-valued i32 code points, and values above `0x10ffff` with `ERR_ILLEGAL_SEQUENCE`.

WTF mode permits surrogate values as reversible sentinels. It never silently substitutes U+FFFD. For host-originated byte namespaces, invalid UTF-8 bytes may be represented with `U+DC80..U+DCFF`; UTF-16 host namespaces preserve unpaired surrogates directly.

### 5.2 Length queries

Every stable indexed source exposes width-specific length operations such as `args_len_i8`, `args_len_i16`, and `args_len_i32`. Length is the exact number of code units required, excluding any terminator.

An invalid source index returns zero and `ERR_RANGE`. An invalid `wtf` value returns zero and `ERR_INVALID`. A source value that cannot be represented losslessly under the selected mode returns zero and `ERR_ILLEGAL_SEQUENCE`.

### 5.3 Caller-owned destinations

`*_read_mem32_i*`, `*_read_mem64_i*`, and `*_read_into_array_i*` copy the complete represented string into caller-owned storage.

The operation succeeds only when the supplied capacity can hold the entire value. If capacity is too small, it returns zero units and `ERR_RANGE` and MUST NOT modify the destination.

On success, `units_written` is the complete code-unit length. No NUL terminator is appended and storage after the represented value is unchanged.

A zero-capacity destination succeeds only for an empty string.

Array destination offsets and capacities are measured in array elements. Array destinations must be mutable and must match the storage class named by the import. Linear-memory pointers are byte addresses while capacity is measured in code units.

### 5.4 Allocating GC results

`*_read_array_i8`, `*_read_array_i16`, and `*_read_array_i32` allocate a fresh Wasm GC array using the concrete result heap type declared by the importing module.

The runtime validates the concrete result type during import linking. A mismatched storage class is an import-type mismatch and fails instantiation rather than becoming a runtime `ERR_TYPE`.

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

An empty string still returns a non-null zero-length array. Allocation failure returns `ERR_NO_MEMORY`.

### 5.5 Stable and stateful sources

Arguments, environment entries, and preopen display names are immutable WPSI instance inputs and therefore remain stable for the lifetime of the instance.

Directory iteration is stateful. A width-specific `dir_iter_next_len_i*` snapshots but does not consume the next entry. A successful read/allocating next call consumes it; a failed capacity or text validation check does not. Rewind discards any pending snapshot.

A symbolic-link target is identified by the supplied path rather than a string handle. Separate length and read calls may observe different host filesystem states. Callers requiring one atomic result SHOULD use an allocating GC readlink when available or provide sufficient caller-owned capacity in one read operation.

### 5.6 Error examples

```text
args_read_array_i16(index_out_of_range, 0)
  -> (null, ERR_RANGE)

args_read_array_i8(valid_index, 2)
  -> (null, ERR_INVALID)

args_read_mem32_i8(valid_index, 0, memory, ptr, too_small)
  -> (0, ERR_RANGE)
```

These are ordinary WPSI errors, not Wasm traps.'''
)

write("spec/behavior.md", behavior)


# ---------------------------------------------------------------------------
# docs
# ---------------------------------------------------------------------------

design = read("docs/design.md")
design = design.replace(
    "WPSI supports UTF-8, UTF-16, and UTF-32 directly. WTF-8/WTF-16 and raw 8-bit system strings exist for host namespaces that cannot be losslessly modeled as Unicode scalar text.",
    "WPSI supports 8-bit, 16-bit, and 32-bit text representations directly. The representation width is part of the import name rather than an encoding enum. A single `wtf` boolean selects strict Unicode or surrogate-sentinel mode, so host namespaces with non-Unicode units can be preserved without a separate raw-string encoding value.",
)
design = design.replace(
    "Linear-memory callers query the encoded length when necessary and provide `(memory, pointer, capacity)` storage.",
    "Linear-memory callers query the width-specific code-unit length when necessary and provide `(memory, pointer, capacity)` storage.",
)
design += r'''

## Why a WTF boolean instead of an encoding enum?

The code-unit width changes the physical ABI and therefore belongs in the import name. UTF versus WTF semantics do not change the Core Wasm signature, so they are represented by one boolean.

This keeps the rule simple:

```text
physical representation -> import name
strict vs sentinel text  -> wtf boolean
```

`wtf = 0` requires Unicode scalar text. `wtf = 1` permits surrogate values as reversible sentinels. WPSI does not need an `ENC_*` namespace or a separate raw-8 string mode.
'''
write("docs/design.md", design)

runtime = read("docs/runtime-implementation.md")
insert_at = "## GC array access"
text_guidance = r'''## Text representation

Text width is part of the WPSI import name. A runtime should dispatch `*_i8`, `*_i16`, and `*_i32` directly to the corresponding code-unit reader/writer rather than decoding an encoding enum on every call.

The `wtf` argument is a strict boolean. Validate it before touching guest buffers or host namespaces.

```text
wtf = 0 -> strict Unicode scalar text
wtf = 1 -> permit surrogate sentinel values
```

On byte-oriented host namespaces, a practical reversible mapping for invalid UTF-8 bytes is the surrogate-escape range `U+DC80..U+DCFF`. On UTF-16 hosts, preserve unpaired surrogate code units directly. Never substitute U+FFFD when WPSI requires lossless transfer; return `ERR_ILLEGAL_SEQUENCE` if the selected mode cannot represent the host value.

For linear memory, `_i16` and `_i32` code units are little-endian. The pointer remains a byte address while lengths/capacities are code-unit counts.

'''
runtime = runtime.replace(insert_at, text_guidance + insert_at)
write("docs/runtime-implementation.md", runtime)

openq = read("docs/open-questions.md")
openq = re.sub(
    r"\n## 2\. Path encoding parameter\n.*?Current preference: yes; the Core Wasm signature is unchanged by the encoding enum\.\n",
    "\n",
    openq,
    flags=re.S,
)
for old, new in [("## 3.", "## 2."), ("## 4.", "## 3."), ("## 5.", "## 4."), ("## 6.", "## 5.")]:
    openq = openq.replace(old, new)
write("docs/open-questions.md", openq)

readme = read("README.md")
readme = readme.replace(
    "UTF-8, UTF-16, and UTF-32. Text does not have to round-trip through UTF-8.",
    "UTF-8, UTF-16, and 32-bit code-point text. Code-unit width is explicit in the import name, while one `wtf` boolean enables reversible surrogate-sentinel handling when strict Unicode is insufficient.",
)
readme = readme.replace(
    "UTF-8, UTF-16, UTF-32 text",
    "UTF-8, UTF-16, 32-bit code-point text",
)
write("README.md", readme)

changelog = read("CHANGELOG.md")
needle = "### Decided\n"
addition = "\n- Text APIs no longer use an `ENC_*` selector. Code-unit width is encoded in the import name (`i8`, `i16`, or `i32`) and a single `wtf` boolean selects strict Unicode versus reversible surrogate-sentinel semantics. The old `RAW8` mode is removed; non-Unicode host units are represented through WTF sentinels when lossless conversion is possible.\n- Linear-memory textual imports now include both memory width and code-unit width, for example `path_open_mem32_i16` and `args_read_mem64_i8`.\n"
if addition.strip() not in changelog:
    changelog = changelog.replace(needle, needle + addition)
changelog = changelog.replace("UTF-8, UTF-16, UTF-32, WTF-8, WTF-16, and raw 8-bit system string encodings.", "UTF-8, UTF-16, 32-bit code-point text, and WTF surrogate-sentinel semantics.")
write("CHANGELOG.md", changelog)


# ---------------------------------------------------------------------------
# spec/imports.wat
# ---------------------------------------------------------------------------

imports = read("spec/imports.wat")

args_env_block = r'''  ;; Arguments and environment
  (import "wpsi" "args_count" (func $args_count (result i32 i32)))
  (import "wpsi" "args_len_i8" (func $args_len_i8 (param i32 i32) (result i64 i32)))
  (import "wpsi" "args_len_i16" (func $args_len_i16 (param i32 i32) (result i64 i32)))
  (import "wpsi" "args_len_i32" (func $args_len_i32 (param i32 i32) (result i64 i32)))
  (import "wpsi" "args_read_mem32_i8" (func $args_read_mem32_i8 (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "args_read_mem32_i16" (func $args_read_mem32_i16 (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "args_read_mem32_i32" (func $args_read_mem32_i32 (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "args_read_mem64_i8" (func $args_read_mem64_i8 (param i32 i32 i32 i64 i64) (result i64 i32)))
  (import "wpsi" "args_read_mem64_i16" (func $args_read_mem64_i16 (param i32 i32 i32 i64 i64) (result i64 i32)))
  (import "wpsi" "args_read_mem64_i32" (func $args_read_mem64_i32 (param i32 i32 i32 i64 i64) (result i64 i32)))
  (import "wpsi" "args_read_into_array_i8" (func $args_read_into_array_i8 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "args_read_into_array_i16" (func $args_read_into_array_i16 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "args_read_into_array_i32" (func $args_read_into_array_i32 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "args_read_array_i8" (func $args_read_array_i8 (param i32 i32) (result (ref null $wpsi_string_i8) i32)))
  (import "wpsi" "args_read_array_i16" (func $args_read_array_i16 (param i32 i32) (result (ref null $wpsi_string_i16) i32)))
  (import "wpsi" "args_read_array_i32" (func $args_read_array_i32 (param i32 i32) (result (ref null $wpsi_string_i32) i32)))

  (import "wpsi" "env_count" (func $env_count (result i32 i32)))
  (import "wpsi" "env_len_i8" (func $env_len_i8 (param i32 i32 i32) (result i64 i32)))
  (import "wpsi" "env_len_i16" (func $env_len_i16 (param i32 i32 i32) (result i64 i32)))
  (import "wpsi" "env_len_i32" (func $env_len_i32 (param i32 i32 i32) (result i64 i32)))
  (import "wpsi" "env_read_mem32_i8" (func $env_read_mem32_i8 (param i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "env_read_mem32_i16" (func $env_read_mem32_i16 (param i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "env_read_mem32_i32" (func $env_read_mem32_i32 (param i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "env_read_mem64_i8" (func $env_read_mem64_i8 (param i32 i32 i32 i32 i64 i64) (result i64 i32)))
  (import "wpsi" "env_read_mem64_i16" (func $env_read_mem64_i16 (param i32 i32 i32 i32 i64 i64) (result i64 i32)))
  (import "wpsi" "env_read_mem64_i32" (func $env_read_mem64_i32 (param i32 i32 i32 i32 i64 i64) (result i64 i32)))
  (import "wpsi" "env_read_into_array_i8" (func $env_read_into_array_i8 (param i32 i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "env_read_into_array_i16" (func $env_read_into_array_i16 (param i32 i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "env_read_into_array_i32" (func $env_read_into_array_i32 (param i32 i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "env_read_array_i8" (func $env_read_array_i8 (param i32 i32 i32) (result (ref null $wpsi_string_i8) i32)))
  (import "wpsi" "env_read_array_i16" (func $env_read_array_i16 (param i32 i32 i32) (result (ref null $wpsi_string_i16) i32)))
  (import "wpsi" "env_read_array_i32" (func $env_read_array_i32 (param i32 i32 i32) (result (ref null $wpsi_string_i32) i32)))'''
imports = replace_block(imports, "  ;; Arguments and environment", "  ;; Clocks", args_env_block)

preopen_block = r'''  ;; Filesystem roots
  (import "wpsi" "fs_scratch" (func $fs_scratch (result i32 i32)))
  (import "wpsi" "fs_scratch_limits" (func $fs_scratch_limits (result i64 i64 i32)))
  (import "wpsi" "fs_scratch_usage" (func $fs_scratch_usage (result i64 i64 i32)))
  (import "wpsi" "fs_preopen_count" (func $fs_preopen_count (result i32 i32)))
  (import "wpsi" "fs_preopen_get" (func $fs_preopen_get (param i32) (result i32 i32)))
  (import "wpsi" "fs_preopen_name_len_i8" (func $fs_preopen_name_len_i8 (param i32 i32) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_len_i16" (func $fs_preopen_name_len_i16 (param i32 i32) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_len_i32" (func $fs_preopen_name_len_i32 (param i32 i32) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_mem32_i8" (func $fs_preopen_name_read_mem32_i8 (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_mem32_i16" (func $fs_preopen_name_read_mem32_i16 (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_mem32_i32" (func $fs_preopen_name_read_mem32_i32 (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_mem64_i8" (func $fs_preopen_name_read_mem64_i8 (param i32 i32 i32 i64 i64) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_mem64_i16" (func $fs_preopen_name_read_mem64_i16 (param i32 i32 i32 i64 i64) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_mem64_i32" (func $fs_preopen_name_read_mem64_i32 (param i32 i32 i32 i64 i64) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_into_array_i8" (func $fs_preopen_name_read_into_array_i8 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_into_array_i16" (func $fs_preopen_name_read_into_array_i16 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_into_array_i32" (func $fs_preopen_name_read_into_array_i32 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_array_i8" (func $fs_preopen_name_read_array_i8 (param i32 i32) (result (ref null $wpsi_string_i8) i32)))
  (import "wpsi" "fs_preopen_name_read_array_i16" (func $fs_preopen_name_read_array_i16 (param i32 i32) (result (ref null $wpsi_string_i16) i32)))
  (import "wpsi" "fs_preopen_name_read_array_i32" (func $fs_preopen_name_read_array_i32 (param i32 i32) (result (ref null $wpsi_string_i32) i32)))'''
imports = replace_block(imports, "  ;; Filesystem roots", "  ;; Descriptor metadata", preopen_block)


def emit_path_imports() -> str:
    out: list[str] = ["  ;; Textual filesystem paths"]
    stat_result = "(result i32 i32 i64 i64 i32 i64 i32 i64 i32 i32)"
    for t in ("i8", "i16", "i32"):
        out += [
            f'  (import "wpsi" "path_open_mem32_{t}" (func $path_open_mem32_{t} (param i32 i32 i32 i32 i32 i32 i64) (result i32 i32)))',
            f'  (import "wpsi" "path_open_mem64_{t}" (func $path_open_mem64_{t} (param i32 i32 i64 i64 i32 i32 i64) (result i32 i32)))',
            f'  (import "wpsi" "path_open_array_{t}" (func $path_open_array_{t} (param i32 (ref array) i32 i32 i32 i32 i64) (result i32 i32)))',
            f'  (import "wpsi" "path_stat_mem32_{t}" (func $path_stat_mem32_{t} (param i32 i32 i32 i32 i32 i32) {stat_result}))',
            f'  (import "wpsi" "path_stat_mem64_{t}" (func $path_stat_mem64_{t} (param i32 i32 i64 i64 i32 i32) {stat_result}))',
            f'  (import "wpsi" "path_stat_array_{t}" (func $path_stat_array_{t} (param i32 (ref array) i32 i32 i32 i32) {stat_result}))',
            f'  (import "wpsi" "path_create_dir_mem32_{t}" (func $path_create_dir_mem32_{t} (param i32 i32 i32 i32 i32) (result i32)))',
            f'  (import "wpsi" "path_create_dir_mem64_{t}" (func $path_create_dir_mem64_{t} (param i32 i32 i64 i64 i32) (result i32)))',
            f'  (import "wpsi" "path_create_dir_array_{t}" (func $path_create_dir_array_{t} (param i32 (ref array) i32 i32 i32) (result i32)))',
            f'  (import "wpsi" "path_remove_mem32_{t}" (func $path_remove_mem32_{t} (param i32 i32 i32 i32 i32 i32) (result i32)))',
            f'  (import "wpsi" "path_remove_mem64_{t}" (func $path_remove_mem64_{t} (param i32 i32 i64 i64 i32 i32) (result i32)))',
            f'  (import "wpsi" "path_remove_array_{t}" (func $path_remove_array_{t} (param i32 (ref array) i32 i32 i32 i32) (result i32)))',
            f'  (import "wpsi" "path_rename_mem32_{t}" (func $path_rename_mem32_{t} (param i32 i32 i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))',
            f'  (import "wpsi" "path_rename_mem64_{t}" (func $path_rename_mem64_{t} (param i32 i32 i64 i64 i32 i32 i32 i64 i64 i32 i32) (result i32)))',
            f'  (import "wpsi" "path_rename_array_{t}" (func $path_rename_array_{t} (param i32 (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32 i32) (result i32)))',
        ]
    out += [
        '',
        '  ;; Directory iteration',
        '  (import "wpsi" "dir_iter_open" (func $dir_iter_open (param i32) (result i32 i32)))',
    ]
    for t in ("i8", "i16", "i32"):
        result = "(result i64 i32 i64 i32 i32)"
        out += [
            f'  (import "wpsi" "dir_iter_next_len_{t}" (func $dir_iter_next_len_{t} (param i32 i32) {result}))',
            f'  (import "wpsi" "dir_iter_next_mem32_{t}" (func $dir_iter_next_mem32_{t} (param i32 i32 i32 i32 i32) {result}))',
            f'  (import "wpsi" "dir_iter_next_mem64_{t}" (func $dir_iter_next_mem64_{t} (param i32 i32 i32 i64 i64) {result}))',
            f'  (import "wpsi" "dir_iter_next_into_array_{t}" (func $dir_iter_next_into_array_{t} (param i32 i32 (ref array) i32 i32) {result}))',
            f'  (import "wpsi" "dir_iter_next_array_{t}" (func $dir_iter_next_array_{t} (param i32 i32) (result (ref null $wpsi_string_{t}) i32 i64 i32 i32)))',
        ]
    out.append('  (import "wpsi" "dir_iter_rewind" (func $dir_iter_rewind (param i32) (result i32)))')
    out += ['', '  ;; Links and symbolic links']
    for t in ("i8", "i16", "i32"):
        out += [
            f'  (import "wpsi" "path_link_mem32_{t}" (func $path_link_mem32_{t} (param i32 i32 i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))',
            f'  (import "wpsi" "path_link_mem64_{t}" (func $path_link_mem64_{t} (param i32 i32 i64 i64 i32 i32 i32 i64 i64 i32 i32) (result i32)))',
            f'  (import "wpsi" "path_link_array_{t}" (func $path_link_array_{t} (param i32 (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32 i32) (result i32)))',
            f'  (import "wpsi" "path_symlink_mem32_{t}" (func $path_symlink_mem32_{t} (param i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))',
            f'  (import "wpsi" "path_symlink_mem64_{t}" (func $path_symlink_mem64_{t} (param i32 i64 i64 i32 i32 i32 i64 i64 i32) (result i32)))',
            f'  (import "wpsi" "path_symlink_array_{t}" (func $path_symlink_array_{t} (param (ref array) i32 i32 i32 i32 (ref array) i32 i32 i32) (result i32)))',
            f'  (import "wpsi" "path_readlink_len_mem32_{t}" (func $path_readlink_len_mem32_{t} (param i32 i32 i32 i32 i32 i32) (result i64 i32)))',
            f'  (import "wpsi" "path_readlink_mem32_{t}" (func $path_readlink_mem32_{t} (param i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i64 i32)))',
            f'  (import "wpsi" "path_readlink_len_mem64_{t}" (func $path_readlink_len_mem64_{t} (param i32 i32 i64 i64 i32 i32) (result i64 i32)))',
            f'  (import "wpsi" "path_readlink_mem64_{t}" (func $path_readlink_mem64_{t} (param i32 i32 i64 i64 i32 i32 i64 i64 i32) (result i64 i32)))',
            f'  (import "wpsi" "path_readlink_len_array_{t}" (func $path_readlink_len_array_{t} (param i32 (ref array) i32 i32 i32 i32) (result i64 i32)))',
            f'  (import "wpsi" "path_readlink_into_array_{t}" (func $path_readlink_into_array_{t} (param i32 (ref array) i32 i32 i32 (ref array) i32 i32 i32) (result i64 i32)))',
            f'  (import "wpsi" "path_readlink_array_{t}" (func $path_readlink_array_{t} (param i32 (ref array) i32 i32 i32 i32) (result (ref null $wpsi_string_{t}) i32)))',
        ]
    return "\n".join(out)

imports = replace_block(imports, "  ;; Path open", "  ;; Socket lifecycle", emit_path_imports())

dns_lines = ["  ;; DNS"]
for t in ("i8", "i16", "i32"):
    dns_lines += [
        f'  (import "wpsi" "dns_resolve_mem32_{t}" (func $dns_resolve_mem32_{t} (param i32 i32 i32 i32 i32 i32) (result i32 i32)))',
        f'  (import "wpsi" "dns_resolve_mem64_{t}" (func $dns_resolve_mem64_{t} (param i32 i64 i64 i32 i32 i32) (result i32 i32)))',
        f'  (import "wpsi" "dns_resolve_array_{t}" (func $dns_resolve_array_{t} (param (ref array) i32 i32 i32 i32 i32) (result i32 i32)))',
    ]
dns_lines += [
    '  (import "wpsi" "dns_next"',
    '    (func $dns_next (param i32) (result i32 i64 i64 i32 i32 i32)))',
]
imports = replace_block(imports, "  ;; DNS", "  ;; Polling", "\n".join(dns_lines))
write("spec/imports.wat", imports)


# ---------------------------------------------------------------------------
# WAST migration
# ---------------------------------------------------------------------------

ENC_POSITIONS: dict[str, tuple[int, ...]] = {
    "args_len": (1,),
    "args_read_mem32": (1,), "args_read_mem64": (1,),
    "args_read_into_array_i8": (1,), "args_read_into_array_i16": (1,), "args_read_into_array_i32": (1,),
    "args_read_array_i8": (1,), "args_read_array_i16": (1,), "args_read_array_i32": (1,),
    "env_len": (2,),
    "env_read_mem32": (2,), "env_read_mem64": (2,),
    "env_read_into_array_i8": (2,), "env_read_into_array_i16": (2,), "env_read_into_array_i32": (2,),
    "env_read_array_i8": (2,), "env_read_array_i16": (2,), "env_read_array_i32": (2,),
    "fs_preopen_name_len": (1,),
    "fs_preopen_name_read_mem32": (1,), "fs_preopen_name_read_mem64": (1,),
    "fs_preopen_name_read_into_array_i8": (1,), "fs_preopen_name_read_into_array_i16": (1,), "fs_preopen_name_read_into_array_i32": (1,),
    "fs_preopen_name_read_array_i8": (1,), "fs_preopen_name_read_array_i16": (1,), "fs_preopen_name_read_array_i32": (1,),
    "dir_iter_next_len": (1,), "dir_iter_next_mem32": (1,), "dir_iter_next_mem64": (1,),
    "dir_iter_next_into_array_i8": (1,), "dir_iter_next_into_array_i16": (1,), "dir_iter_next_into_array_i32": (1,),
    "dir_iter_next_array_i8": (1,), "dir_iter_next_array_i16": (1,), "dir_iter_next_array_i32": (1,),
    "path_open_mem32": (4,), "path_open_mem64": (4,),
    "path_open_array_i8": (4,), "path_open_array_i16": (4,), "path_open_array_i32": (4,),
    "path_stat_mem32": (4,), "path_stat_mem64": (4,),
    "path_stat_array_i8": (4,), "path_stat_array_i16": (4,), "path_stat_array_i32": (4,),
    "path_create_dir_mem32": (4,), "path_create_dir_mem64": (4,),
    "path_create_dir_array_i8": (4,), "path_create_dir_array_i16": (4,), "path_create_dir_array_i32": (4,),
    "path_remove_mem32": (4,), "path_remove_mem64": (4,),
    "path_remove_array_i8": (4,), "path_remove_array_i16": (4,), "path_remove_array_i32": (4,),
    "path_rename_mem32": (4, 9), "path_rename_mem64": (4, 9),
    "path_rename_array_i8": (4, 9), "path_rename_array_i16": (4, 9), "path_rename_array_i32": (4, 9),
    "path_link_mem32": (4, 9), "path_link_mem64": (4, 9),
    "path_link_array_i8": (4, 9), "path_link_array_i16": (4, 9), "path_link_array_i32": (4, 9),
    "path_symlink_mem32": (3, 8), "path_symlink_mem64": (3, 8),
    "path_symlink_array_i8": (3, 8), "path_symlink_array_i16": (3, 8), "path_symlink_array_i32": (3, 8),
    "path_readlink_len_mem32": (4, 5), "path_readlink_len_mem64": (4, 5),
    "path_readlink_mem32": (4, 8), "path_readlink_mem64": (4, 8),
    "path_readlink_len_array_i8": (4, 5), "path_readlink_len_array_i16": (4, 5), "path_readlink_len_array_i32": (4, 5),
    "path_readlink_into_array_i8": (4, 8), "path_readlink_into_array_i16": (4, 8), "path_readlink_into_array_i32": (4, 8),
    "path_readlink_array_i8": (4, 5), "path_readlink_array_i16": (4, 5), "path_readlink_array_i32": (4, 5),
    "dns_resolve_mem32": (3,), "dns_resolve_mem64": (3,),
    "dns_resolve_array_i8": (3,), "dns_resolve_array_i16": (3,), "dns_resolve_array_i32": (3,),
}

GENERIC_SUFFIX = {
    "args_len", "args_read_mem32", "args_read_mem64",
    "env_len", "env_read_mem32", "env_read_mem64",
    "fs_preopen_name_len", "fs_preopen_name_read_mem32", "fs_preopen_name_read_mem64",
    "dir_iter_next_len", "dir_iter_next_mem32", "dir_iter_next_mem64",
    "path_open_mem32", "path_open_mem64", "path_stat_mem32", "path_stat_mem64",
    "path_create_dir_mem32", "path_create_dir_mem64", "path_remove_mem32", "path_remove_mem64",
    "path_rename_mem32", "path_rename_mem64", "path_link_mem32", "path_link_mem64",
    "path_symlink_mem32", "path_symlink_mem64",
    "path_readlink_len_mem32", "path_readlink_len_mem64", "path_readlink_mem32", "path_readlink_mem64",
    "dns_resolve_mem32", "dns_resolve_mem64",
}

ENC_TO_MODE = {
    1: ("i8", 0),
    2: ("i16", 0),
    3: ("i32", 0),
    4: ("i8", 1),
    5: ("i8", 1),
    6: ("i16", 1),
}

IMPORT_START = re.compile(r'\(import\s+"wpsi"\s+"([^"]+)"\s+\(func\s+(\$[^\s()]+)')


def matching_paren(text: str, start: int) -> int:
    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(text)):
        c = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == '"':
                in_string = False
            continue
        if c == '"':
            in_string = True
        elif c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("unbalanced expression")


def arg_spans(call_text: str) -> list[tuple[int, int]]:
    # call_text begins with (call $name ...)
    m = re.match(r'\(call\s+\$[^\s()]+', call_text)
    if not m:
        return []
    i = m.end()
    end = len(call_text) - 1
    spans: list[tuple[int, int]] = []
    while i < end:
        while i < end and call_text[i].isspace():
            i += 1
        if i >= end:
            break
        start = i
        if call_text[i] == '(':
            close = matching_paren(call_text, i)
            i = close + 1
        else:
            while i < end and not call_text[i].isspace() and call_text[i] != ')':
                i += 1
        spans.append((start, i))
    return spans


def infer_width_from_path(path: Path) -> str:
    name = path.name.lower()
    if "utf16" in name or "i16" in name:
        return "i16"
    if "utf32" in name or "i32" in name:
        return "i32"
    return "i8"


def migrate_wast(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    imports_found = [(m.group(1), m.group(2)) for m in IMPORT_START.finditer(text)]
    replacements: list[tuple[int, int, str]] = []
    renames: list[tuple[str, str, str]] = []

    for old_name, local in imports_found:
        positions = ENC_POSITIONS.get(old_name)
        if not positions:
            continue
        values: list[int] = []
        needle = f"(call {local}"
        cursor = 0
        while True:
            start = text.find(needle, cursor)
            if start < 0:
                break
            close = matching_paren(text, start)
            call = text[start:close + 1]
            spans = arg_spans(call)
            for pos in positions:
                if pos >= len(spans):
                    raise SystemExit(f"missing text-mode arg {pos} in {path}: {call}")
                a, b = spans[pos]
                expr = call[a:b]
                cm = re.fullmatch(r'\(i32\.const\s+(-?\d+)\)', expr.strip())
                if not cm:
                    raise SystemExit(f"non-constant legacy encoding arg in {path}: {expr}")
                old_value = int(cm.group(1))
                if old_value not in ENC_TO_MODE:
                    raise SystemExit(f"unknown legacy encoding {old_value} in {path}")
                width, mode = ENC_TO_MODE[old_value]
                values.append(old_value)
                replacements.append((start + a, start + b, f"(i32.const {mode})"))
            cursor = close + 1

        widths = {ENC_TO_MODE[v][0] for v in values}
        width = next(iter(widths)) if widths else infer_width_from_path(path)
        if len(widths) > 1:
            raise SystemExit(f"mixed code-unit widths need explicit split in {path}: {old_name} {sorted(widths)}")

        new_name = old_name
        if old_name in GENERIC_SUFFIX:
            new_name = f"{old_name}_{width}"
        renames.append((old_name, new_name, local))

    for a, b, replacement in sorted(replacements, reverse=True):
        text = text[:a] + replacement + text[b:]
    for old_name, new_name, local in renames:
        if old_name != new_name:
            text = text.replace(f'(import "wpsi" "{old_name}" (func {local}', f'(import "wpsi" "{new_name}" (func {local}')

    path.write_text(text, encoding="utf-8")


for wast in sorted((ROOT / "spec/tests").rglob("*.wast")):
    migrate_wast(wast)


# Replace the one test whose old purpose was specifically encoding-family mismatch.
old = ROOT / "spec/tests/args-env/args-read-array-encoding-mismatch.wast"
if old.exists():
    new = old.with_name("args-read-array-invalid-wtf.wast")
    new.write_text(r''';; WPSI conformance test: args-env/args-read-array-invalid-wtf
;; Purpose: Allocating string reads reject non-boolean WTF selectors with null and ERR_INVALID.
;; Required profiles: core, gc-array, args-env
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array (mut i8)))
  (import "wpsi" "args_read_array_i8"
    (func $read (param i32 i32) (result (ref null $a) i32)))
  (func (export "run") (result i32 i32)
    (local $v (ref null $a)) (local $e i32)
    (call $read (i32.const 0) (i32.const 2)) (local.set $e) (local.set $v)
    (ref.is_null (local.get $v))
    (local.get $e)))
(assert_return (invoke "run") (i32.const 1) (i32.const 12))
'''.rstrip() + "\n", encoding="utf-8")
    old.unlink()
    old_json = old.with_suffix(".json")
    if old_json.exists():
        old_json.rename(new.with_suffix(".json"))

# RAW8 is gone; retain the coverage as an explicit WTF-mode test.
old = ROOT / "spec/tests/filesystem/path-raw8.wast"
if old.exists():
    new = old.with_name("path-wtf8.wast")
    text = old.read_text(encoding="utf-8")
    text = text.replace("filesystem/path-raw8", "filesystem/path-wtf8")
    text = text.replace("ENC_RAW8 accepts an uninterpreted ASCII path without Unicode conversion.", "WTF mode is a boolean text mode and accepts ordinary UTF-8 as a valid subset.")
    text = text.replace('"path_open_mem32"', '"path_open_mem32_i8"')
    # Generic migration converted legacy ENC_RAW8=4 to wtf=1.
    new.write_text(text, encoding="utf-8")
    old.unlink()
    old_json = old.with_suffix(".json")
    if old_json.exists():
        old_json.rename(new.with_suffix(".json"))


# ---------------------------------------------------------------------------
# General textual cleanup and invariants
# ---------------------------------------------------------------------------

for rel in ["SPEC.md", "spec/behavior.md", "docs/design.md", "docs/runtime-implementation.md", "README.md", "CHANGELOG.md", "spec/tests/README.md"]:
    p = ROOT / rel
    if not p.exists():
        continue
    text = p.read_text(encoding="utf-8")
    text = text.replace("UTF-8, UTF-16, UTF-32", "UTF-8, UTF-16, and 32-bit code-point")
    p.write_text(text, encoding="utf-8")

# Any remaining legacy tokens indicate the migration missed something normative or test-visible.
legacy_patterns = [
    re.compile(r"\bENC_(?:UTF8|UTF16|UTF32|RAW8|WTF8|WTF16)\b"),
    re.compile(r"\bRAW8\b"),
]
legacy_hits: list[str] = []
check_files = [ROOT / "SPEC.md", ROOT / "spec/behavior.md", ROOT / "spec/imports.wat", ROOT / "docs/design.md", ROOT / "docs/runtime-implementation.md", ROOT / "README.md"]
check_files += list((ROOT / "spec/tests").rglob("*.wast"))
for p in check_files:
    text = p.read_text(encoding="utf-8")
    for pattern in legacy_patterns:
        if pattern.search(text):
            legacy_hits.append(str(p.relative_to(ROOT)))
            break
if legacy_hits:
    raise SystemExit("legacy encoding-selector text remains:\n" + "\n".join(sorted(set(legacy_hits))))

legacy_imports = [
    '"args_len"', '"args_read_mem32"', '"args_read_mem64"',
    '"env_len"', '"env_read_mem32"', '"env_read_mem64"',
    '"fs_preopen_name_len"', '"fs_preopen_name_read_mem32"', '"fs_preopen_name_read_mem64"',
    '"dir_iter_next_len"', '"dir_iter_next_mem32"', '"dir_iter_next_mem64"',
    '"path_open_mem32"', '"path_open_mem64"', '"path_stat_mem32"', '"path_stat_mem64"',
    '"path_create_dir_mem32"', '"path_create_dir_mem64"', '"path_remove_mem32"', '"path_remove_mem64"',
    '"path_rename_mem32"', '"path_rename_mem64"', '"path_link_mem32"', '"path_link_mem64"',
    '"path_symlink_mem32"', '"path_symlink_mem64"',
    '"path_readlink_len_mem32"', '"path_readlink_len_mem64"', '"path_readlink_mem32"', '"path_readlink_mem64"',
    '"dns_resolve_mem32"', '"dns_resolve_mem64"',
]
legacy_import_hits: list[str] = []
for p in [ROOT / "spec/imports.wat", *list((ROOT / "spec/tests").rglob("*.wast"))]:
    text = p.read_text(encoding="utf-8")
    if any(token in text for token in legacy_imports):
        legacy_import_hits.append(str(p.relative_to(ROOT)))
if legacy_import_hits:
    raise SystemExit("legacy unsuffixed text imports remain:\n" + "\n".join(sorted(set(legacy_import_hits))))

print("migrated WPSI text APIs to width-specific imports plus WTF boolean")
