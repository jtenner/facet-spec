# WPSI Conformance Test Suite

**Status:** Draft  
**Manifest version:** 1  
**Applies to:** WPSI 0.1

This directory contains the normative WPSI conformance tests. Tests are standard
WebAssembly Script (`.wast`) files and optional same-basename JSON manifests.
The host-manifest model intentionally mirrors the operation-based format from
`WebAssembly/wasi-testsuite` so an existing WASI adapter can be extended rather
than replaced.

Contributions are welcome. Every contributed test should isolate one important
contract, document why it matters, and avoid asserting behavior the WPSI
specification does not promise.

## Compatibility rule

> Reuse a WASI testsuite convention whenever it can express the same host setup
> or interaction without weakening the WPSI contract.

The following fields and operations retain their WASI meanings:

- `args`, `env`, and `root` on `run`;
- `run`, `wait`, `read`, `connect`, `send`, and `recv` operations;
- relative fixture paths;
- `.cleanup` artifacts;
- an empty guest environment unless `env` supplies entries;
- external per-runtime skip and expected-failure files.

WPSI adds one host-provisioning extension:

- `preopens`, for more than one directory capability, explicit guest display names, or explicit rights.

A preopen may use the guest display name `~`; this is provisioned exactly like any other preopen.

## Discovery

For each `foo.wast`, a runner looks for `foo.json` in the same directory. If no
manifest exists, the default is:

```json
{
  "version": 1,
  "operations": [
    { "type": "run" },
    { "type": "wait", "exit_code": 0 }
  ]
}
```

A runner must create a fresh test context, handle table, poll state, network namespace,
argument vector, and environment for every test.
Each module instantiated by one WAST script receives a distinct WPSI instance
context unless the test manifest explicitly requests host-mediated sharing.
This prevents raw handles from crossing module-instance boundaries.
Files ending in `.cleanup` are deleted before and after execution.

Generated `wast2json` output must go to a build directory; source-side JSON is
always WPSI host metadata.

## `run`

```json
{
  "type": "run",
  "args": ["alpha", "beta"],
  "env": {"KEY": "value"},
  "root": "../fixtures/root"
}
```

`root` creates one preopen whose display name is `/`. This is deliberately the
same convention used by the WASI testsuite.

For multiple preopens:

```json
{
  "type": "run",
  "preopens": [
    {"host": "../fixtures/root", "guest": "/", "rights": ["read", "stat", "iterate"]},
    {"host": "../fixtures/write", "guest": "/work", "rights": ["read", "write", "create", "remove", "rename", "stat", "iterate"]}
  ]
}
```

Preopen order is normative for a test: `fs_preopen_get(0)` corresponds to the
first entry. `host` paths are relative to the manifest. `guest` is the value
returned by the preopen-name APIs; it is not ambient path authority.

Supported manifest right names are:

```text
read write seek tell stat set-size sync
open create remove rename link symlink readlink iterate
```

A preopen that grants mutation rights MUST be backed by an isolated per-test view
of its fixture directory. Runners MUST NOT mutate the checked-in fixture tree in
place. A fresh run starts from the committed fixture contents; copying, overlay
filesystems, temporary directories, or equivalent isolation are all acceptable.

## Optional `~` preopen

The conformance harness does not allocate scratch storage implicitly. Tests that need a private/writable guest home provision an ordinary preopen explicitly:

```json
{
  "type": "run",
  "preopens": [
    {"host": "../fixtures/root", "guest": "~", "rights": ["read", "write", "open", "create", "remove", "stat"]}
  ]
}
```

A test with no `root` and no `preopens` receives no filesystem roots. This keeps the harness aligned with WPSI's rule that writable storage is optional rather than automatically allocated.

## WAST execution

The runner evaluates the script in source order and resolves imports from the
`"wpsi"` module. WAST assertions remain the source of truth for guest-visible
results. The manifest describes only host provisioning and interactions.

A module exporting `_start` may also be launched by the `run` operation for
process- and networking-style tests. Such tests use `wait`, `read`, `connect`,
`send`, and `recv` exactly as the WASI testsuite does.

## Text tests

Text representation is selected by the WPSI import name: `i8`, `i16`, or `i32`.
Textual calls use a boolean `wtf` argument where `0` means strict Unicode and
`1` enables reversible surrogate-sentinel semantics. Tests should use exact
`ERR_INVALID` behavior for non-boolean `wtf` values and `ERR_ILLEGAL_SEQUENCE`
when strict mode cannot represent the source without loss.

There is no `ENC_*` selector or raw-string encoding mode in WPSI 0.1.

## Profiles and unsupported tests

Required WPSI functions are inferred from imports. A runner may report a test as
`unsupported` only when it lacks a required WPSI representation family or Core
Wasm feature. Unsupported is distinct from pass, fail, and expected-fail.

The catalog in [`catalog.json`](catalog.json) provides human-readable profile
metadata but does not override the imports.

## Harness-driven tests

Most tests contain ordinary WAST assertions. A small number are marked
`Test kind: harness` because they require behavior outside the standard WAST
command language, such as process exit, stdout/stderr validation, network
client interactions, or passing a raw value between independently instantiated
modules. Harness tests still use standard WAST modules and the same operation
format as `WebAssembly/wasi-testsuite`; the catalog identifies the additional
runner obligation.

The TCP and UDP echo tests bind fixed loopback ports inside the fresh per-test
network context. Runners without network namespaces MUST serialize harness
network tests and ensure the selected ports are unavailable before launch.

## Result classes

Reports must distinguish:

1. malformed or invalid Core Wasm;
2. WPSI import/link failure;
3. WPSI runtime errno mismatch;
4. guest trap;
5. host crash or timeout;
6. unsupported feature.

A crash, panic, out-of-bounds host access, or leaked authority is always a test
failure, even if the guest supplied invalid data.

## Structure

```text
core/          version, stdio, process, handle lifecycle
args-env/      arguments, environment, text widths, and WTF behavior
clocks/        system and monotonic clocks
random/        bounds and mutation rules
memory32/      Memory32 and multi-memory I/O
memory64/      Memory64 I/O and overflow handling
gc-array/      typed arrays, byte views, mutability, nested arrays
filesystem/    descriptors, paths, rights, preopens, and the optional `~` convention
links/         hard links and symbolic links
network/       sockets and DNS
poll/          poll sets, timers, and readiness
adversarial/   overflow, atomicity, stale handles, and isolation
imports/       signature and feature-surface guards
tools/         deterministic generation and static validation
fixtures/      host directories used by manifests
```

## Authoring requirements

A new test must:

- include a purpose comment and required-profile comment;
- assert one primary behavior;
- preserve sentinels around modified buffers;
- close resources it acquires unless lifecycle is the subject;
- avoid wall-clock timing assumptions when a property assertion is enough;
- avoid public-network dependencies;
- use exact error codes only where the WPSI specification fixes them;
- be added to `catalog.json` by the generator.

The current catalog contains **143** focused tests.

Run:

```bash
python3 spec/tests/tools/generate_suite.py --check
python3 spec/tests/tools/check_suite.py
```

When `wasm-tools` is installed, also run:

```bash
wasm-tools parse spec/imports.wat -o /tmp/wpsi-imports.wasm
python3 spec/tests/tools/parse_wast.py --wasm-tools wasm-tools
```
