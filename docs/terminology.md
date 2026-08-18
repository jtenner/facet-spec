# Technical Terminology

This glossary defines the preferred terms for human-facing documentation in this repository.

Use these terms consistently. Do not create a second term for the same concept unless the distinction is necessary.

## Actors

### guest

The WebAssembly module that calls imported system functions.

Use **guest** when the text means code or storage owned by that module.

Examples:

- guest memory;
- guest storage;
- guest input.

### runtime

The software that implements the imported system functions.

The runtime validates guest values, manages resource handles, and performs system operations.

### embedder

The software that creates a guest instance and grants authority to it.

The embedder decides which filesystem roots, network capabilities, arguments, environment values, and other external resources are available to the guest.

### operating system

The external operating system used by a runtime implementation.

Use this term only when the behavior specifically depends on an operating-system service or error.

### host

Avoid **host** when **runtime**, **embedder**, or **operating system** is more precise.

The word can remain in established external terms, code identifiers, quoted material, and phrases where no more precise actor exists.

## Interface concepts

### operation

One semantic system action.

Examples include reading a file, opening a path, resolving a DNS name, and waiting for readiness.

### representation

The physical guest form used to pass data through the Core WebAssembly ABI.

Examples include Memory32, Memory64, and a WebAssembly GC array.

### facet

One explicit Core WebAssembly representation of an operation.

For example, `fd_read_mem32`, `fd_read_mem64`, and `fd_read_array_i8` are different representation forms of the same file-read operation.

A facet has a fixed import name and a fixed Core WebAssembly type.

### profile

A documentation and conformance grouping for related imports.

A profile is not an independently versioned runtime object.

Import presence and Core WebAssembly type matching determine support.

### capability

A resource that gives the guest specified authority.

A capability limits what the guest can do with an external resource.

### authority

The operations that a capability permits.

A derived resource MUST NOT have more authority than the resource from which it was derived.

### handle

An opaque nonzero `i32` value that identifies a resource inside one interface instance.

The guest MUST NOT interpret the numeric bits of a handle.

### preopen

A directory capability that the embedder provides when the instance starts.

A preopen has a guest-visible display name and an explicit set of rights.

## Memory and GC terms

### linear memory

A normal Core WebAssembly memory.

A linear-memory operation identifies the memory explicitly. Memory 0 has no special authority.

### Memory32

A linear memory whose address type is `i32`.

### Memory64

A linear memory whose address type is `i64`.

### GC array

A WebAssembly GC array used directly as a system-operation buffer.

Raw GC-array buffer facets support only the numeric storage classes defined by the specification.

### logical byte view

The portable sequence of bytes that the specification defines for a supported numeric GC array.

The logical byte view defines observable values. It does not define the physical layout of the runtime GC heap.

### borrowed guest storage

Guest storage that the runtime can access only during one synchronous imported call.

Examples include:

- a linear-memory pointer or slice;
- a GC reference;
- a raw GC backing pointer;
- a temporary byte view of a GC array.

The runtime MUST NOT retain borrowed guest storage after the call returns.

### caller-owned destination

A destination buffer that the guest supplies to an operation.

The operation writes into this storage only after validation succeeds.

### runtime-owned storage

Storage that the runtime allocates and owns independently of a guest borrow.

The runtime can retain this storage after an imported function returns if the ABI permits the related resource state.

## Text terms

### strict Unicode mode

Text mode selected by `wtf == 0`.

The text must contain valid Unicode scalar text for its representation.

### WTF mode

Text mode selected by `wtf == 1`.

This mode permits surrogate values that preserve external non-Unicode units when the specification defines a reversible mapping.

### code unit

One element of a text representation.

The width depends on the selected facet:

- `_i8`: 8 bits;
- `_i16`: 16 bits;
- `_i32`: 32 bits.

## Filesystem terms

### directory capability

A directory handle that defines the root of authority for relative path operations.

A path operation MUST NOT escape above this directory.

### display name

The guest-visible name associated with a preopen.

The display name does not grant authority by itself.

### symbolic link

A filesystem entry that stores a path target.

Path resolution can follow a symbolic link only when the operation and capability rules permit it.

## Networking terms

### socket

A network resource identified by a file-descriptor handle.

Connected stream sockets use the ordinary file-descriptor read and write facets.

### poll set

A resource that stores readiness registrations and timers for `poll_wait`.

### readiness snapshot

The set of ready events captured by one successful `poll_wait` call.

The guest drains this snapshot with `poll_next` before it calls `poll_wait` again.

## Normative terms

### MUST / MUST NOT

An absolute requirement or prohibition.

### SHOULD / SHOULD NOT

A recommendation. An implementation can deviate only when it has a valid reason and still preserves required behavior.

### MAY

A permitted choice.
