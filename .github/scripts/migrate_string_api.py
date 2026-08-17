#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_section(text: str, start: str, end: str, replacement: str) -> str:
    pattern = re.compile(rf"(?ms)^{re.escape(start)}\n.*?(?=^{re.escape(end)}\n)")
    updated, count = pattern.subn(replacement.rstrip() + "\n\n", text, count=1)
    if count != 1:
        raise SystemExit(f"failed to replace section {start!r}")
    return updated


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.rstrip() + "\n", encoding="utf-8")


def migrate_spec() -> None:
    path = ROOT / "SPEC.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace("sysstr      = i32\n", "")

    text = replace_section(
        text,
        "### 3.5 Incremental implementation is allowed",
        "## 4. Conformance profiles",
        """### 3.5 Caller-typed GC allocation results

Most GC-array parameters use the abstract `(ref array)` type and are dynamically validated by the runtime.

A small set of host-originated string functions instead allocate and return a new GC array. For those functions, the importing module declares a **concrete nullable array result type** such as:

```wat
(type $string16 (array (mut i16)))
(import "wpsi" "args_read_array_i16"
  (func (param i32 i32) (result (ref null $string16) i32)))
```

The function name fixes the required element storage class (`i8`, `i16`, or `i32`). The concrete array type is selected by the importing module. At instantiation the runtime MUST validate that the requested concrete result type is an array with the storage class named by the import. The element may be mutable or immutable.

On success the host allocates exactly that concrete Wasm GC type and returns a non-null reference. On failure it returns `ref.null` and a nonzero `errno`.

This is a narrow type-specialization rule for host allocation, not semantic overload resolution: the operation and storage class remain determined by the import name.

### 3.6 Incremental implementation is allowed

A runtime MAY implement only the WPSI profiles for WebAssembly features it supports. Missing imports fail through normal WebAssembly instantiation.""",
    )

    text = replace_section(
        text,
        "## 9. System strings",
        "## 10. Capabilities and scratch storage",
        """## 9. Host-originated strings

WPSI does not define a string resource handle. A host-originated string is identified by the operation that owns it: an argument index, environment-entry index, preopen index, directory iterator position, or symbolic-link path.

For stable indexed sources, WPSI exposes three forms:

1. `*_len` returns the number of encoding units required;
2. `*_read_mem32`, `*_read_mem64`, and `*_read_into_array_*` copy into caller-owned storage;
3. `*_read_array_*` allocates and returns a caller-typed concrete GC array.

Linear-memory forms necessarily receive an explicit memory index, pointer, and capacity. GC `read_into` forms receive an existing `(ref array)`, element offset, and capacity. Allocating GC forms return `(ref null $caller_type, errno)` as described in section 3.5.

Encoding-unit sizes are:

```text
UTF-8 / WTF-8 / RAW8 = 1 byte
UTF-16 / WTF-16      = 2 bytes
UTF-32                = 4 bytes
```

A successful allocating function returns an array whose length exactly equals the encoded string length. Empty strings return a non-null zero-length array.

For all allocating string functions:

- an invalid source index returns `(null, ERR_RANGE)`;
- an invalid encoding enum returns `(null, ERR_INVALID)`;
- a valid encoding incompatible with the named array storage family returns `(null, ERR_TYPE)`;
- a source value that cannot be represented losslessly returns `(null, ERR_ILLEGAL_SEQUENCE)`;
- allocation failure returns `(null, ERR_NO_MEMORY)`.

For caller-owned destinations, insufficient capacity returns `ERR_RANGE`, writes nothing, and leaves the source position unchanged when the source is stateful. No WPSI string-copy function appends a NUL terminator.

Array encoding compatibility is:

```text
array_i8  -> UTF-8, WTF-8, RAW8
array_i16 -> UTF-16, WTF-16
array_i32 -> UTF-32
```""",
    )

    text = replace_section(
        text,
        "## 13. Arguments and environment",
        "## 14. Clocks",
        """## 13. Arguments and environment

Argument and environment ordering MUST remain stable for the lifetime of the instance.

```text
args_count() -> (count: i32, errno: i32)
args_len(index: i32, encoding: i32)
  -> (units: i64, errno: i32)

args_read_mem32(index: i32, encoding: i32,
                memory: i32, pointer: i32, capacity_units: i32)
  -> (units_written: i64, errno: i32)
args_read_mem64(index: i32, encoding: i32,
                memory: i32, pointer: i64, capacity_units: i64)
  -> (units_written: i64, errno: i32)

args_read_into_array_i8(index: i32, encoding: i32,
                        destination: ref array, offset: i32, capacity_units: i32)
  -> (units_written: i64, errno: i32)
args_read_into_array_i16(...) -> (units_written: i64, errno: i32)
args_read_into_array_i32(...) -> (units_written: i64, errno: i32)

args_read_array_i8(index: i32, encoding: i32)
  -> (value: ref null $caller_i8_array, errno: i32)
args_read_array_i16(index: i32, encoding: i32)
  -> (value: ref null $caller_i16_array, errno: i32)
args_read_array_i32(index: i32, encoding: i32)
  -> (value: ref null $caller_i32_array, errno: i32)
```

Environment entries use a scalar field selector:

```text
ENV_NAME  = 0
ENV_VALUE = 1
```

```text
env_count() -> (count: i32, errno: i32)
env_len(index: i32, field: i32, encoding: i32)
  -> (units: i64, errno: i32)

env_read_mem32(index: i32, field: i32, encoding: i32,
               memory: i32, pointer: i32, capacity_units: i32)
  -> (units_written: i64, errno: i32)
env_read_mem64(index: i32, field: i32, encoding: i32,
               memory: i32, pointer: i64, capacity_units: i64)
  -> (units_written: i64, errno: i32)

env_read_into_array_i8(index: i32, field: i32, encoding: i32,
                       destination: ref array, offset: i32, capacity_units: i32)
  -> (units_written: i64, errno: i32)
env_read_into_array_i16(...) -> (units_written: i64, errno: i32)
env_read_into_array_i32(...) -> (units_written: i64, errno: i32)

env_read_array_i8(index: i32, field: i32, encoding: i32)
  -> (value: ref null $caller_i8_array, errno: i32)
env_read_array_i16(index: i32, field: i32, encoding: i32)
  -> (value: ref null $caller_i16_array, errno: i32)
env_read_array_i32(index: i32, field: i32, encoding: i32)
  -> (value: ref null $caller_i32_array, errno: i32)
```

An unknown environment field selector returns `ERR_INVALID`.""",
    )

    text = replace_section(
        text,
        "## 16. Filesystem roots",
        "## 17. Descriptor metadata",
        """## 16. Filesystem roots

```text
fs_scratch() -> (directory: i32, errno: i32)

fs_scratch_limits()
  -> (byte_quota: i64, object_quota: i64, errno: i32)

fs_scratch_usage()
  -> (bytes_used: i64, object_count: i64, errno: i32)

fs_preopen_count() -> (count: i32, errno: i32)
fs_preopen_get(index: i32) -> (directory: i32, errno: i32)

fs_preopen_name_len(index: i32, encoding: i32)
  -> (units: i64, errno: i32)
fs_preopen_name_read_mem32(index: i32, encoding: i32,
                           memory: i32, pointer: i32, capacity_units: i32)
  -> (units_written: i64, errno: i32)
fs_preopen_name_read_mem64(index: i32, encoding: i32,
                           memory: i32, pointer: i64, capacity_units: i64)
  -> (units_written: i64, errno: i32)
fs_preopen_name_read_into_array_i8(index: i32, encoding: i32,
                                   destination: ref array, offset: i32, capacity_units: i32)
  -> (units_written: i64, errno: i32)
fs_preopen_name_read_into_array_i16(...) -> (units_written: i64, errno: i32)
fs_preopen_name_read_into_array_i32(...) -> (units_written: i64, errno: i32)
fs_preopen_name_read_array_i8(index: i32, encoding: i32)
  -> (value: ref null $caller_i8_array, errno: i32)
fs_preopen_name_read_array_i16(index: i32, encoding: i32)
  -> (value: ref null $caller_i16_array, errno: i32)
fs_preopen_name_read_array_i32(index: i32, encoding: i32)
  -> (value: ref null $caller_i32_array, errno: i32)
```

`UINT64_MAX` means a quota dimension is not declared.

Preopen ordering and display names MUST remain stable for the lifetime of the instance.""",
    )

    text = replace_section(
        text,
        "## 28. Directory iteration",
        "## 29. Hard links",
        """## 28. Directory iteration

```text
dir_iter_open(directory: i32)
  -> (iterator: i32, errno: i32)

dir_iter_next_len(iterator: i32, encoding: i32)
  -> (units: i64, file_type: i32, inode: i64, done: i32, errno: i32)

dir_iter_next_mem32(iterator: i32, encoding: i32,
                    memory: i32, pointer: i32, capacity_units: i32)
  -> (units_written: i64, file_type: i32, inode: i64, done: i32, errno: i32)
dir_iter_next_mem64(iterator: i32, encoding: i32,
                    memory: i32, pointer: i64, capacity_units: i64)
  -> (units_written: i64, file_type: i32, inode: i64, done: i32, errno: i32)

dir_iter_next_into_array_i8(iterator: i32, encoding: i32,
                            destination: ref array, offset: i32, capacity_units: i32)
  -> (units_written: i64, file_type: i32, inode: i64, done: i32, errno: i32)
dir_iter_next_into_array_i16(...) -> same-dir-result
dir_iter_next_into_array_i32(...) -> same-dir-result

dir_iter_next_array_i8(iterator: i32, encoding: i32)
  -> (name: ref null $caller_i8_array,
      file_type: i32, inode: i64, done: i32, errno: i32)
dir_iter_next_array_i16(iterator: i32, encoding: i32) -> same-allocated-dir-result
dir_iter_next_array_i32(iterator: i32, encoding: i32) -> same-allocated-dir-result

dir_iter_rewind(iterator: i32) -> (errno: i32)
```

The iterator itself identifies the pending directory entry; WPSI does not allocate a separate name resource.

`dir_iter_next_len` peeks and snapshots the next entry without consuming it. Repeated length queries observe the same pending entry. Any successful `dir_iter_next_mem*`, `dir_iter_next_into_array_*`, or `dir_iter_next_array_*` call consumes that entry and advances the iterator.

If caller-owned capacity is insufficient, the operation returns `ERR_RANGE`, performs no write, and does not advance. The caller may query `dir_iter_next_len` and retry.

At end of iteration, `done == 1`, scalar metadata is zero, and allocating forms return `ref.null` with `ERR_OK`.

`dir_iter_rewind` discards any pending snapshot and resets the iterator. The iterator is released with `handle_close`.""",
    )

    text = replace_section(
        text,
        "## 31. Read symbolic link",
        "## 32. Networking constants",
        """## 31. Read symbolic link

`path_readlink_*` never creates an intermediate string resource.

Linear-memory forms accept both the input path and output destination:

```text
path_readlink_len_mem32(directory: i32,
                        path_memory: i32, path_pointer: i32,
                        path_length: i32, path_encoding: i32,
                        target_encoding: i32)
  -> (units: i64, errno: i32)

path_readlink_mem32(directory: i32,
                    path_memory: i32, path_pointer: i32,
                    path_length: i32, path_encoding: i32,
                    target_memory: i32, target_pointer: i32,
                    target_capacity_units: i32, target_encoding: i32)
  -> (units_written: i64, errno: i32)

path_readlink_len_mem64(directory: i32,
                        path_memory: i32, path_pointer: i64,
                        path_length: i64, path_encoding: i32,
                        target_encoding: i32)
  -> (units: i64, errno: i32)

path_readlink_mem64(directory: i32,
                    path_memory: i32, path_pointer: i64,
                    path_length: i64, path_encoding: i32,
                    target_memory: i32, target_pointer: i64,
                    target_capacity_units: i64, target_encoding: i32)
  -> (units_written: i64, errno: i32)
```

GC forms use the same element-storage family for the input path and output target. This avoids an input/output representation cross-product:

```text
path_readlink_len_array_i8(directory: i32, path: ref array,
                           offset: i32, length: i32, path_encoding: i32,
                           target_encoding: i32)
  -> (units: i64, errno: i32)

path_readlink_into_array_i8(directory: i32, path: ref array,
                            path_offset: i32, path_length: i32, path_encoding: i32,
                            destination: ref array, destination_offset: i32,
                            target_capacity_units: i32, target_encoding: i32)
  -> (units_written: i64, errno: i32)

path_readlink_array_i8(directory: i32, path: ref array,
                       offset: i32, length: i32, path_encoding: i32,
                       target_encoding: i32)
  -> (target: ref null $caller_i8_array, errno: i32)
```

Equivalent `array_i16` and `array_i32` functions are defined.

For an allocating GC readlink, `target_encoding` MUST be compatible with the named array storage family. Caller-owned reads require enough capacity for the complete target; insufficient capacity returns `ERR_RANGE` without modifying the destination.

The returned target is the stored symbolic-link text and is not recursively resolved.""",
    )

    text = text.replace(
        "4. validate GC array kind, dynamic element type, and destination mutability;\n",
        "4. validate GC array kind, dynamic element type, destination mutability, and caller-selected concrete allocation result types;\n",
    )
    text = text.replace(
        "UTF-16 and UTF-32 strings SHOULD remain in their native representation when the corresponding WPSI function exists; conversion through UTF-8 is not required.\n",
        "UTF-16 and UTF-32 strings SHOULD remain in their native representation when the corresponding WPSI function exists; conversion through UTF-8 is not required. GC-oriented languages SHOULD prefer allocating `*_read_array_*` functions when they want a fresh string and `*_read_into_array_*` when they already own reusable storage.\n",
    )
    path.write_text(text, encoding="utf-8")


def migrate_behavior() -> None:
    path = ROOT / "spec" / "behavior.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "4. **Guest representation.** Resolve the selected linear memory or GC reference and validate the expected address width, GC array kind, dynamic element storage type, and destination mutability.\n",
        "4. **Guest representation.** Resolve the selected linear memory or GC reference and validate the expected address width, GC array kind, dynamic element storage type, destination mutability, and any caller-selected concrete GC allocation result type.\n",
    )
    text = text.replace(
        "| `ERR_TYPE` | Guest representation has the wrong physical type, such as Memory64 passed to a `_mem32` operation, wrong GC element storage, or immutable GC storage used as a destination. |",
        "| `ERR_TYPE` | Guest representation has the wrong physical type, such as Memory64 passed to a `_mem32` operation, wrong GC element storage, immutable GC storage used as a destination, or an incompatible concrete GC allocation result type. |",
    )
    text = replace_section(
        text,
        "## 5. System-string semantics",
        "## 6. Polling semantics",
        """## 5. Host-originated string transfer

WPSI does not use resource handles merely to transport strings.

The string source is identified directly by its owning operation: argument index, environment index plus field selector, preopen index, iterator state, or symlink path. This removes handle allocation, lookup, and close operations from ordinary string access.

### 5.1 Length queries

Every stable indexed source exposes a `*_len` operation. Length is the exact number of encoding units required, excluding any terminator.

```text
UTF-8 / WTF-8 / RAW8 = bytes
UTF-16 / WTF-16      = 16-bit code units
UTF-32                = 32-bit code units
```

An invalid source index returns zero and `ERR_RANGE`. An invalid encoding enum returns zero and `ERR_INVALID`. A source value that cannot be represented losslessly in the requested encoding returns zero and `ERR_ILLEGAL_SEQUENCE`.

### 5.2 Caller-owned destinations

`*_read_mem32`, `*_read_mem64`, and `*_read_into_array_*` copy the complete encoded string into caller-owned storage.

The operation succeeds only when the supplied capacity can hold the entire encoded value. If capacity is too small, it returns zero units and `ERR_RANGE` and MUST NOT modify the destination.

On success, `units_written` is the complete encoded length. No NUL terminator is appended and storage after the encoded value is unchanged.

A zero-capacity destination succeeds only for an empty string.

Array destination offsets and capacities are measured in array elements. Array destinations must be mutable and must match the storage class named by the import. Linear-memory pointers are byte addresses while capacity is measured in encoding units.

### 5.3 Allocating GC results

`*_read_array_i8`, `*_read_array_i16`, and `*_read_array_i32` allocate a fresh Wasm GC array using the **concrete result heap type declared by the importing module**.

The runtime validates that the result type is a concrete array whose element storage matches the import suffix. The returned array may have mutable or immutable elements because the runtime initializes the complete object before exposing it to the guest.

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

A valid encoding incompatible with the result family returns `ERR_TYPE`:

```text
array_i8  -> UTF-8, WTF-8, RAW8
array_i16 -> UTF-16, WTF-16
array_i32 -> UTF-32
```

### 5.4 Stable sources

Arguments, environment entries, and preopen display names are immutable WPSI instance inputs and therefore remain stable for the lifetime of the instance.

Directory iteration is stateful. `dir_iter_next_len` snapshots but does not consume the next entry. A successful read/allocating next call consumes it; a failed capacity or encoding check does not. Rewind discards any pending snapshot.

A symbolic-link target is identified by the supplied path rather than a string handle. As with ordinary filesystem operations, concurrent host changes may cause separate length and read calls to observe different filesystem states. Callers requiring one atomic result SHOULD use an allocating GC readlink when available or provide sufficient caller-owned capacity in one read operation.

### 5.5 Error examples

```text
args_read_array_i16(index_out_of_range, ENC_UTF16)
  -> (null, ERR_RANGE)

args_read_array_i8(valid_index, ENC_UTF16)
  -> (null, ERR_TYPE)

args_read_mem32(valid_index, ENC_UTF8, memory, ptr, too_small)
  -> (0, ERR_RANGE)
```

These are ordinary WPSI errors, not Wasm traps.""",
    )
    path.write_text(text, encoding="utf-8")


def migrate_design() -> None:
    path = ROOT / "docs" / "design.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "For the operations WPSI targets, ordinary imports provide enough structure without introducing another interface language or canonical lowering format.\n",
        "For the operations WPSI targets, ordinary imports provide enough structure without introducing another interface language or canonical lowering format. Host-allocated GC string results are a narrow exception where import instantiation also validates the caller-selected concrete array result type.\n",
    )
    text = replace_section(
        text,
        "## Why system-string handles?",
        "## Why a private scratch filesystem?",
        """## Why no system-string handles?

Strings such as arguments, environment values, preopen labels, directory-entry names, and symbolic-link targets already have a natural source identity. Creating another resource handle solely to move those strings adds allocation, lookup, lifetime, and close operations without adding authority.

WPSI therefore lets the source operation expose the string directly.

Linear-memory callers query the encoded length when necessary and provide `(memory, pointer, capacity)` storage. GC callers may either provide an existing mutable array with `*_read_into_array_*` or use `*_read_array_*` to ask the runtime to allocate a fresh result.

For allocating GC results, the concrete nullable array result type appears in the module's import signature. The runtime validates the requested storage class and allocates exactly that Wasm GC type. This lets a language receive its native `array<i8>`, `array<i16>`, or `array<i32>` representation without a temporary string resource or linear-memory lowering.

This asymmetry is intentional: linear memory naturally uses caller-owned addresses, while Wasm GC can naturally return newly allocated references.""",
    )
    path.write_text(text, encoding="utf-8")


def migrate_runtime_guide() -> None:
    path = ROOT / "docs" / "runtime-implementation.md"
    text = path.read_text(encoding="utf-8")
    marker = "## Current runtime layout observations\n"
    addition = """## Host-allocated GC string results

Allocating string imports such as `args_read_array_i16` are specialized to the concrete nullable array result type requested by the importing module.

At import instantiation a runtime should:

1. inspect the requested function result type;
2. require a concrete array heap type with the storage class named by the import;
3. retain the runtime type identity in the host-function instance;
4. encode the selected source string completely;
5. allocate exactly that array type at the exact required length;
6. initialize every element before returning the reference;
7. return `null` plus `ERR_NO_MEMORY` if allocation fails.

The result array may be mutable or immutable. This path does not borrow an existing object and therefore does not use the scoped raw-array byte-borrow primitive.

Caller-owned `*_read_into_array_*` functions still use normal destination validation and require mutable arrays.

"""
    if addition not in text:
        text = text.replace(marker, addition + marker)
    path.write_text(text, encoding="utf-8")


def migrate_imports() -> None:
    path = ROOT / "spec" / "imports.wat"
    text = path.read_text(encoding="utf-8")
    if "$wpsi_string_i8" not in text:
        text = text.replace(
            "(module\n",
            """(module
  ;; Representative concrete result types for host-allocated strings.
  ;; Allocating string imports are templates: an importing module supplies its
  ;; own concrete array type with the matching element storage class.
  (type $wpsi_string_i8 (array (mut i8)))
  (type $wpsi_string_i16 (array (mut i16)))
  (type $wpsi_string_i32 (array (mut i32)))

""",
            1,
        )

    text = re.sub(
        r"(?ms)^  ;; Arguments and environment\n.*?(?=^  ;; Clocks\n)",
        """  ;; Arguments and environment
  (import "wpsi" "args_count" (func $args_count (result i32 i32)))
  (import "wpsi" "args_len" (func $args_len (param i32 i32) (result i64 i32)))
  (import "wpsi" "args_read_mem32" (func $args_read_mem32 (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "args_read_mem64" (func $args_read_mem64 (param i32 i32 i32 i64 i64) (result i64 i32)))
  (import "wpsi" "args_read_into_array_i8" (func $args_read_into_array_i8 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "args_read_into_array_i16" (func $args_read_into_array_i16 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "args_read_into_array_i32" (func $args_read_into_array_i32 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "args_read_array_i8" (func $args_read_array_i8 (param i32 i32) (result (ref null $wpsi_string_i8) i32)))
  (import "wpsi" "args_read_array_i16" (func $args_read_array_i16 (param i32 i32) (result (ref null $wpsi_string_i16) i32)))
  (import "wpsi" "args_read_array_i32" (func $args_read_array_i32 (param i32 i32) (result (ref null $wpsi_string_i32) i32)))

  (import "wpsi" "env_count" (func $env_count (result i32 i32)))
  (import "wpsi" "env_len" (func $env_len (param i32 i32 i32) (result i64 i32)))
  (import "wpsi" "env_read_mem32" (func $env_read_mem32 (param i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "env_read_mem64" (func $env_read_mem64 (param i32 i32 i32 i32 i64 i64) (result i64 i32)))
  (import "wpsi" "env_read_into_array_i8" (func $env_read_into_array_i8 (param i32 i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "env_read_into_array_i16" (func $env_read_into_array_i16 (param i32 i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "env_read_into_array_i32" (func $env_read_into_array_i32 (param i32 i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "env_read_array_i8" (func $env_read_array_i8 (param i32 i32 i32) (result (ref null $wpsi_string_i8) i32)))
  (import "wpsi" "env_read_array_i16" (func $env_read_array_i16 (param i32 i32 i32) (result (ref null $wpsi_string_i16) i32)))
  (import "wpsi" "env_read_array_i32" (func $env_read_array_i32 (param i32 i32 i32) (result (ref null $wpsi_string_i32) i32)))

""",
        text,
        count=1,
    )

    text = re.sub(
        r"(?ms)^  ;; Filesystem roots\n.*?(?=^  ;; Descriptor metadata\n)",
        """  ;; Filesystem roots
  (import "wpsi" "fs_scratch" (func $fs_scratch (result i32 i32)))
  (import "wpsi" "fs_scratch_limits" (func $fs_scratch_limits (result i64 i64 i32)))
  (import "wpsi" "fs_scratch_usage" (func $fs_scratch_usage (result i64 i64 i32)))
  (import "wpsi" "fs_preopen_count" (func $fs_preopen_count (result i32 i32)))
  (import "wpsi" "fs_preopen_get" (func $fs_preopen_get (param i32) (result i32 i32)))
  (import "wpsi" "fs_preopen_name_len" (func $fs_preopen_name_len (param i32 i32) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_mem32" (func $fs_preopen_name_read_mem32 (param i32 i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_mem64" (func $fs_preopen_name_read_mem64 (param i32 i32 i32 i64 i64) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_into_array_i8" (func $fs_preopen_name_read_into_array_i8 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_into_array_i16" (func $fs_preopen_name_read_into_array_i16 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_into_array_i32" (func $fs_preopen_name_read_into_array_i32 (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (import "wpsi" "fs_preopen_name_read_array_i8" (func $fs_preopen_name_read_array_i8 (param i32 i32) (result (ref null $wpsi_string_i8) i32)))
  (import "wpsi" "fs_preopen_name_read_array_i16" (func $fs_preopen_name_read_array_i16 (param i32 i32) (result (ref null $wpsi_string_i16) i32)))
  (import "wpsi" "fs_preopen_name_read_array_i32" (func $fs_preopen_name_read_array_i32 (param i32 i32) (result (ref null $wpsi_string_i32) i32)))

""",
        text,
        count=1,
    )

    text = re.sub(
        r"(?ms)^  ;; Directory iteration\n.*?(?=^  ;; Hard links\n)",
        """  ;; Directory iteration
  (import "wpsi" "dir_iter_open" (func $dir_iter_open (param i32) (result i32 i32)))
  (import "wpsi" "dir_iter_next_len" (func $dir_iter_next_len (param i32 i32) (result i64 i32 i64 i32 i32)))
  (import "wpsi" "dir_iter_next_mem32" (func $dir_iter_next_mem32 (param i32 i32 i32 i32 i32) (result i64 i32 i64 i32 i32)))
  (import "wpsi" "dir_iter_next_mem64" (func $dir_iter_next_mem64 (param i32 i32 i32 i64 i64) (result i64 i32 i64 i32 i32)))
  (import "wpsi" "dir_iter_next_into_array_i8" (func $dir_iter_next_into_array_i8 (param i32 i32 (ref array) i32 i32) (result i64 i32 i64 i32 i32)))
  (import "wpsi" "dir_iter_next_into_array_i16" (func $dir_iter_next_into_array_i16 (param i32 i32 (ref array) i32 i32) (result i64 i32 i64 i32 i32)))
  (import "wpsi" "dir_iter_next_into_array_i32" (func $dir_iter_next_into_array_i32 (param i32 i32 (ref array) i32 i32) (result i64 i32 i64 i32 i32)))
  (import "wpsi" "dir_iter_next_array_i8" (func $dir_iter_next_array_i8 (param i32 i32) (result (ref null $wpsi_string_i8) i32 i64 i32 i32)))
  (import "wpsi" "dir_iter_next_array_i16" (func $dir_iter_next_array_i16 (param i32 i32) (result (ref null $wpsi_string_i16) i32 i64 i32 i32)))
  (import "wpsi" "dir_iter_next_array_i32" (func $dir_iter_next_array_i32 (param i32 i32) (result (ref null $wpsi_string_i32) i32 i64 i32 i32)))
  (import "wpsi" "dir_iter_rewind" (func $dir_iter_rewind (param i32) (result i32)))

""",
        text,
        count=1,
    )

    text = re.sub(
        r"(?ms)^  ;; Read symbolic link\n.*?(?=^  ;; Socket lifecycle\n)",
        """  ;; Read symbolic link
  (import "wpsi" "path_readlink_len_mem32" (func $path_readlink_len_mem32 (param i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "path_readlink_mem32" (func $path_readlink_mem32 (param i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "path_readlink_len_mem64" (func $path_readlink_len_mem64 (param i32 i32 i64 i64 i32 i32) (result i64 i32)))
  (import "wpsi" "path_readlink_mem64" (func $path_readlink_mem64 (param i32 i32 i64 i64 i32 i32 i64 i64 i32) (result i64 i32)))
  (import "wpsi" "path_readlink_len_array_i8" (func $path_readlink_len_array_i8 (param i32 (ref array) i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "path_readlink_len_array_i16" (func $path_readlink_len_array_i16 (param i32 (ref array) i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "path_readlink_len_array_i32" (func $path_readlink_len_array_i32 (param i32 (ref array) i32 i32 i32 i32) (result i64 i32)))
  (import "wpsi" "path_readlink_into_array_i8" (func $path_readlink_into_array_i8 (param i32 (ref array) i32 i32 i32 (ref array) i32 i32 i32) (result i64 i32)))
  (import "wpsi" "path_readlink_into_array_i16" (func $path_readlink_into_array_i16 (param i32 (ref array) i32 i32 i32 (ref array) i32 i32 i32) (result i64 i32)))
  (import "wpsi" "path_readlink_into_array_i32" (func $path_readlink_into_array_i32 (param i32 (ref array) i32 i32 i32 (ref array) i32 i32 i32) (result i64 i32)))
  (import "wpsi" "path_readlink_array_i8" (func $path_readlink_array_i8 (param i32 (ref array) i32 i32 i32 i32) (result (ref null $wpsi_string_i8) i32)))
  (import "wpsi" "path_readlink_array_i16" (func $path_readlink_array_i16 (param i32 (ref array) i32 i32 i32 i32) (result (ref null $wpsi_string_i16) i32)))
  (import "wpsi" "path_readlink_array_i32" (func $path_readlink_array_i32 (param i32 (ref array) i32 i32 i32 i32) (result (ref null $wpsi_string_i32) i32)))

""",
        text,
        count=1,
    )
    if "sysstr" in text:
        raise SystemExit("spec/imports.wat still contains sysstr")
    path.write_text(text, encoding="utf-8")


def update_existing_tests() -> None:
    tests = ROOT / "spec" / "tests"

    # Remove the obsolete sysstr-specific corpus and its manifests.
    for path in (tests / "args-env").glob("sysstr-*"):
        path.unlink()

    # fs_preopen_get no longer allocates a name handle. Most filesystem tests
    # used the name only to close it, so this mechanical rewrite preserves them.
    for path in tests.rglob("*.wast"):
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            '(import "wpsi" "fs_preopen_get" (func $get (param i32) (result i32 i32 i32)))',
            '(import "wpsi" "fs_preopen_get" (func $get (param i32) (result i32 i32)))',
        )
        text = text.replace(
            '(call $get (i32.const 0)) (local.set $e) (local.set $name) (local.set $dir)',
            '(call $get (i32.const 0)) (local.set $e) (local.set $dir)',
        )
        text = text.replace('(drop (call $close (local.get $name)))\n', '')
        path.write_text(text, encoding="utf-8")

    write(
        "spec/tests/args-env/out-of-range-zeroes.wast",
        """;; WPSI conformance test: args-env/out-of-range-zeroes
;; Purpose: Out-of-range argument and environment indexes return zero lengths and ERR_RANGE.
;; Required profiles: core, args-env
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "args_len" (func $arg (param i32 i32) (result i64 i32)))
  (import "wpsi" "env_len" (func $env (param i32 i32 i32) (result i64 i32)))
  (func (export "arg") (result i64 i32) (call $arg (i32.const -1) (i32.const 1)))
  (func (export "env") (result i64 i32) (call $env (i32.const -1) (i32.const 0) (i32.const 1))))
(assert_return (invoke "arg") (i64.const 0) (i32.const 17))
(assert_return (invoke "env") (i64.const 0) (i32.const 17))""",
    )

    # Replace the old readlink-via-sysstr test with direct output storage.
    write(
        "spec/tests/links/symlink-readlink.wast",
        """;; WPSI conformance test: links/symlink-readlink
;; Purpose: A symbolic-link target round-trips directly into caller-owned linear memory.
;; Required profiles: core, memory32, filesystem, links
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "fs_scratch" (func $scratch (result i32 i32)))
  (import "wpsi" "path_symlink_mem32" (func $symlink (param i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i32)))
  (import "wpsi" "path_readlink_mem32" (func $readlink (param i32 i32 i32 i32 i32 i32 i32 i32 i32) (result i64 i32)))
  (memory 1)
  (data (i32.const 0) "target.txt") (data (i32.const 32) "link.txt")
  (func (export "run") (result i32)
    (local $dir i32) (local $e i32) (local $n i64)
    (call $scratch) (local.set $e) (local.set $dir)
    (local.set $e (call $symlink (i32.const 0) (i32.const 0) (i32.const 10) (i32.const 1) (local.get $dir) (i32.const 0) (i32.const 32) (i32.const 8) (i32.const 1)))
    (call $readlink (local.get $dir)
      (i32.const 0) (i32.const 32) (i32.const 8) (i32.const 1)
      (i32.const 0) (i32.const 64) (i32.const 10) (i32.const 1))
    (local.set $e) (local.set $n)
    (i32.or (local.get $e)
      (i32.or (i64.ne (local.get $n) (i64.const 10))
        (i32.or (i32.ne (i32.load (i32.const 64)) (i32.const 1735549300))
                (i32.ne (i32.load16_u (i32.const 72)) (i32.const 29752))))))
)
(assert_return (invoke "run") (i32.const 0))""",
    )

    # Directory iteration tests that consumed sysstr names are replaced below.
    for name in ["dir-iterate-rewind.wast"]:
        candidate = tests / "filesystem" / name
        if candidate.exists():
            candidate.unlink()
        manifest = candidate.with_suffix(".json")
        if manifest.exists():
            manifest.unlink()


def add_string_tests() -> None:
    manifest = {
        "version": 1,
        "operations": [
            {"type": "run", "args": ["alpha", "βeta", "𐐷"], "env": {"WPSI_TEST": "café"}},
            {"type": "wait", "exit_code": 0},
        ],
    }
    manifest_text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"

    cases: dict[str, str] = {
        "args-read-mem32-utf8.wast": """;; WPSI conformance test: args-env/args-read-mem32-utf8
;; Purpose: Arguments copy directly into caller-owned Memory32 without an intermediate string handle.
;; Required profiles: core, memory32, args-env, text
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "args_read_mem32" (func $read (param i32 i32 i32 i32 i32) (result i64 i32)))
  (memory 1)
  (func (export "run") (result i32)
    (local $n i64) (local $e i32)
    (call $read (i32.const 0) (i32.const 1) (i32.const 0) (i32.const 16) (i32.const 5))
    (local.set $e) (local.set $n)
    (i32.or (local.get $e)
      (i32.or (i64.ne (local.get $n) (i64.const 5))
              (i32.ne (i32.load8_u (i32.const 16)) (i32.const 97)))))
)
(assert_return (invoke "run") (i32.const 0))""",
        "args-read-insufficient-capacity.wast": """;; WPSI conformance test: args-env/args-read-insufficient-capacity
;; Purpose: A too-small string destination returns ERR_RANGE and remains unmodified.
;; Required profiles: core, memory32, args-env, text, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (import "wpsi" "args_read_mem32" (func $read (param i32 i32 i32 i32 i32) (result i64 i32)))
  (memory 1)
  (data (i32.const 16) "Z")
  (func (export "run") (result i32)
    (local $n i64) (local $e i32)
    (call $read (i32.const 0) (i32.const 1) (i32.const 0) (i32.const 16) (i32.const 4))
    (local.set $e) (local.set $n)
    (i32.and
      (i32.and (i64.eqz (local.get $n)) (i32.eq (local.get $e) (i32.const 17)))
      (i32.eq (i32.load8_u (i32.const 16)) (i32.const 90))))
)
(assert_return (invoke "run") (i32.const 1))""",
        "args-read-into-array-i16.wast": """;; WPSI conformance test: args-env/args-read-into-array-i16
;; Purpose: UTF-16 arguments can be copied directly into an existing mutable array<i16>.
;; Required profiles: core, gc-array, args-env, text
;;
;; SPDX-License-Identifier: MIT

(module
  (type $a (array (mut i16)))
  (import "wpsi" "args_read_into_array_i16" (func $read (param i32 i32 (ref array) i32 i32) (result i64 i32)))
  (func (export "run") (result i32)
    (local $a (ref $a)) (local $n i64) (local $e i32)
    (local.set $a (array.new_default $a (i32.const 5)))
    (call $read (i32.const 0) (i32.const 2) (local.get $a) (i32.const 0) (i32.const 5))
    (local.set $e) (local.set $n)
    (i32.or (local.get $e)
      (i32.or (i64.ne (local.get $n) (i64.const 5))
              (i32.ne (array.get_u $a (local.get $a) (i32.const 0)) (i32.const 97)))))
)
(assert_return (invoke "run") (i32.const 0))""",
        "args-read-array-i8.wast": """;; WPSI conformance test: args-env/args-read-array-i8
;; Purpose: The host can allocate the caller's concrete array<i8> result type for an argument.
;; Required profiles: core, gc-array, args-env, text
;;
;; SPDX-License-Identifier: MIT

(module
  (type $s (array (mut i8)))
  (import "wpsi" "args_read_array_i8" (func $read (param i32 i32) (result (ref null $s) i32)))
  (func (export "run") (result i32)
    (local $s (ref null $s)) (local $e i32)
    (call $read (i32.const 0) (i32.const 1)) (local.set $e) (local.set $s)
    (if (result i32) (ref.is_null (local.get $s))
      (then (i32.const 1))
      (else
        (i32.or (local.get $e)
          (i32.or (i32.ne (array.len (local.get $s)) (i32.const 5))
                  (i32.ne (array.get_u $s (ref.as_non_null (local.get $s)) (i32.const 0)) (i32.const 97)))))))
)
(assert_return (invoke "run") (i32.const 0))""",
        "args-read-array-i16.wast": """;; WPSI conformance test: args-env/args-read-array-i16
;; Purpose: The host can allocate the caller's concrete array<i16> result type.
;; Required profiles: core, gc-array, args-env, text
;;
;; SPDX-License-Identifier: MIT

(module
  (type $s (array i16))
  (import "wpsi" "args_read_array_i16" (func $read (param i32 i32) (result (ref null $s) i32)))
  (func (export "run") (result i32)
    (local $s (ref null $s)) (local $e i32)
    (call $read (i32.const 1) (i32.const 2)) (local.set $e) (local.set $s)
    (i32.or (local.get $e) (ref.is_null (local.get $s))))
)
(assert_return (invoke "run") (i32.const 0))""",
        "args-read-array-oob-null.wast": """;; WPSI conformance test: args-env/args-read-array-oob-null
;; Purpose: An out-of-range allocating argument read returns null and ERR_RANGE.
;; Required profiles: core, gc-array, args-env, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (type $s (array (mut i8)))
  (import "wpsi" "args_read_array_i8" (func $read (param i32 i32) (result (ref null $s) i32)))
  (func (export "run") (result i32)
    (local $s (ref null $s)) (local $e i32)
    (call $read (i32.const -1) (i32.const 1)) (local.set $e) (local.set $s)
    (i32.and (ref.is_null (local.get $s)) (i32.eq (local.get $e) (i32.const 17))))
)
(assert_return (invoke "run") (i32.const 1))""",
        "args-read-array-encoding-mismatch.wast": """;; WPSI conformance test: args-env/args-read-array-encoding-mismatch
;; Purpose: A valid encoding incompatible with the allocated array storage family returns null and ERR_TYPE.
;; Required profiles: core, gc-array, args-env, text, adversarial
;;
;; SPDX-License-Identifier: MIT

(module
  (type $s (array (mut i8)))
  (import "wpsi" "args_read_array_i8" (func $read (param i32 i32) (result (ref null $s) i32)))
  (func (export "run") (result i32)
    (local $s (ref null $s)) (local $e i32)
    (call $read (i32.const 0) (i32.const 2)) (local.set $e) (local.set $s)
    (i32.and (ref.is_null (local.get $s)) (i32.eq (local.get $e) (i32.const 25))))
)
(assert_return (invoke "run") (i32.const 1))""",
        "env-read-array-name.wast": """;; WPSI conformance test: args-env/env-read-array-name
;; Purpose: Environment names are selected directly by index and field without string handles.
;; Required profiles: core, gc-array, args-env, text
;;
;; SPDX-License-Identifier: MIT

(module
  (type $s (array (mut i8)))
  (import "wpsi" "env_read_array_i8" (func $read (param i32 i32 i32) (result (ref null $s) i32)))
  (func (export "run") (result i32)
    (local $s (ref null $s)) (local $e i32)
    (call $read (i32.const 0) (i32.const 0) (i32.const 1)) (local.set $e) (local.set $s)
    (i32.or (local.get $e) (ref.is_null (local.get $s))))
)
(assert_return (invoke "run") (i32.const 0))""",
        "env-read-array-value.wast": """;; WPSI conformance test: args-env/env-read-array-value
;; Purpose: Environment values can be allocated directly as caller-typed GC arrays.
;; Required profiles: core, gc-array, args-env, text
;;
;; SPDX-License-Identifier: MIT

(module
  (type $s (array (mut i16)))
  (import "wpsi" "env_read_array_i16" (func $read (param i32 i32 i32) (result (ref null $s) i32)))
  (func (export "run") (result i32)
    (local $s (ref null $s)) (local $e i32)
    (call $read (i32.const 0) (i32.const 1) (i32.const 2)) (local.set $e) (local.set $s)
    (i32.or (local.get $e) (ref.is_null (local.get $s))))
)
(assert_return (invoke "run") (i32.const 0))""",
    }

    for filename, body in cases.items():
        write(f"spec/tests/args-env/{filename}", body)
        write(f"spec/tests/args-env/{Path(filename).with_suffix('.json').name}", manifest_text)

    write(
        "spec/tests/filesystem/dir-iterate-rewind.wast",
        """;; WPSI conformance test: filesystem/dir-iterate-rewind
;; Purpose: Directory iteration uses the iterator as the stable name source and rewind resets pending state.
;; Required profiles: core, gc-array, filesystem, text
;;
;; SPDX-License-Identifier: MIT

(module
  (type $s (array (mut i8)))
  (import "wpsi" "fs_preopen_get" (func $get (param i32) (result i32 i32)))
  (import "wpsi" "dir_iter_open" (func $open (param i32) (result i32 i32)))
  (import "wpsi" "dir_iter_next_array_i8" (func $next (param i32 i32) (result (ref null $s) i32 i64 i32 i32)))
  (import "wpsi" "dir_iter_rewind" (func $rewind (param i32) (result i32)))
  (func (export "run") (result i32)
    (local $dir i32) (local $iter i32) (local $e i32)
    (local $name (ref null $s)) (local $type i32) (local $inode i64) (local $done i32)
    (call $get (i32.const 0)) (local.set $e) (local.set $dir)
    (call $open (local.get $dir)) (local.set $e) (local.set $iter)
    (call $next (local.get $iter) (i32.const 1))
      (local.set $e) (local.set $done) (local.set $inode) (local.set $type) (local.set $name)
    (if (i32.eqz (local.get $e)) (then (local.set $e (call $rewind (local.get $iter)))))
    (local.get $e))
)
(assert_return (invoke "run") (i32.const 0))""",
    )


def update_changelog_and_readme() -> None:
    path = ROOT / "CHANGELOG.md"
    text = path.read_text(encoding="utf-8")
    decision = "- Removed `sysstr` string resources in favor of source-specific length/copy APIs, caller-owned GC `read_into` APIs, and caller-typed allocating GC string results.\n"
    if decision not in text:
        text = text.rstrip() + "\n" + decision
    path.write_text(text, encoding="utf-8")

    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = text.replace(
        "- **UTF-8, UTF-16, and UTF-32.** Text does not have to round-trip through UTF-8.\n",
        "- **UTF-8, UTF-16, and UTF-32.** Text does not have to round-trip through UTF-8; host-originated strings can write directly into linear memory or GC arrays, or allocate caller-typed GC arrays.\n",
    )
    readme.write_text(text, encoding="utf-8")


def final_checks() -> None:
    # The term may remain in changelog history only after this migration.
    forbidden: list[str] = []
    for path in [ROOT / "SPEC.md", ROOT / "spec" / "behavior.md", ROOT / "spec" / "imports.wat", ROOT / "docs" / "design.md"]:
        if "sysstr" in path.read_text(encoding="utf-8"):
            forbidden.append(str(path.relative_to(ROOT)))
    for path in (ROOT / "spec" / "tests").rglob("*.wast"):
        if "sysstr" in path.read_text(encoding="utf-8"):
            forbidden.append(str(path.relative_to(ROOT)))
    if forbidden:
        raise SystemExit("legacy sysstr references remain:\n" + "\n".join(forbidden))


def main() -> None:
    migrate_spec()
    migrate_behavior()
    migrate_design()
    migrate_runtime_guide()
    migrate_imports()
    update_existing_tests()
    add_string_tests()
    update_changelog_and_readme()
    final_checks()
    print("migrated WPSI host strings away from sysstr resources")


if __name__ == "__main__":
    main()
