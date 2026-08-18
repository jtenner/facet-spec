# WPSI Conformance Test Suite

**Status:** Draft  
**Manifest version:** 1  
**Applies to:** WPSI 0.1

This directory contains the normative WPSI conformance tests.

A test is a standard WebAssembly Script (`.wast`) file.

A test can also have a same-basename JSON manifest when it needs external setup or interaction.

The manifest model follows `WebAssembly/wasi-testsuite` conventions where those conventions can express the required setup without weakening the WPSI contract.

## Authoring goal

Each test should isolate one important observable rule.

Each test should explain why that rule matters.

Do not assert behavior that the specification does not promise.

## Compatibility rule

Reuse a WASI testsuite convention when it can express the same setup or interaction.

The following fields and operations keep their WASI meanings:

- `args`, `env`, and `root` on `run`;
- `run`, `wait`, `read`, `connect`, `send`, and `recv` operations;
- relative fixture paths;
- `.cleanup` artifacts;
- an empty guest environment unless `env` supplies entries;
- external per-runtime skip and expected-failure files.

WPSI adds one host-provisioning extension:

- `preopens`, for explicit multiple directory capabilities, guest display names, and rights.

A preopen can use guest display name `~`.

The harness provisions it exactly like any other preopen.

## Discovery

For `foo.wast`, the runner looks for `foo.json` in the same directory.

If no manifest exists, use this default:

```json
{
  "version": 1,
  "operations": [
    { "type": "run" },
    { "type": "wait", "exit_code": 0 }
  ]
}
```

For every test, the runner MUST create a fresh test context.

The fresh context includes:

- a handle table;
- poll state;
- network state;
- an argument vector;
- an environment.

Each module instantiated by one WAST script receives a distinct WPSI instance context unless the manifest explicitly requests runtime-mediated sharing.

This rule prevents raw handles from crossing module-instance boundaries.

Delete `.cleanup` artifacts before execution.

Delete them again after execution.

Generated `wast2json` output MUST go to a build directory.

Source-side JSON is always WPSI harness metadata.

## `run`

Example:

```json
{
  "type": "run",
  "args": ["alpha", "beta"],
  "env": {"KEY": "value"},
  "root": "../fixtures/root"
}
```

`root` creates one preopen with display name `/`.

This matches the WASI testsuite convention.

For more than one preopen, use `preopens`:

```json
{
  "type": "run",
  "preopens": [
    {"host": "../fixtures/root", "guest": "/", "rights": ["read", "stat", "iterate"]},
    {"host": "../fixtures/write", "guest": "/work", "rights": ["read", "write", "create", "remove", "rename", "stat", "iterate"]}
  ]
}
```

Preopen order is normative for a test.

`fs_preopen_get(0)` corresponds to the first entry.

A manifest `host` path is relative to the manifest file.

The `guest` field is the display name returned by the preopen-name APIs.

The `guest` field does not create ambient path authority.

Supported right names are:

```text
read write seek tell stat set-size sync
open create remove rename link symlink readlink iterate
```

If a preopen grants mutation rights, the runner MUST give that test an isolated view of the fixture directory.

The runner MUST NOT mutate the checked-in fixture tree directly.

A fresh run starts from the committed fixture contents.

A runner can provide isolation with:

- a copy;
- an overlay filesystem;
- a temporary directory;
- an equivalent mechanism.

## Optional `~` preopen

The harness does not allocate writable guest storage automatically.

A test that needs a guest home or private writable area must provision an ordinary preopen explicitly.

Example:

```json
{
  "type": "run",
  "preopens": [
    {"host": "../fixtures/root", "guest": "~", "rights": ["read", "write", "open", "create", "remove", "stat"]}
  ]
}
```

A test with no `root` and no `preopens` receives no filesystem roots.

This matches the WPSI rule that writable storage is optional.

## WAST execution

Evaluate each WAST script in source order.

Resolve WPSI imports from module `"facet"`.

WAST assertions are the source of truth for guest-visible results.

The manifest describes only external provisioning and interactions.

A module that exports `_start` can also be launched by the `run` operation for process-style or networking-style tests.

These tests use `wait`, `read`, `connect`, `send`, and `recv` with the same meanings used by `WebAssembly/wasi-testsuite`.

## Text tests

The WPSI import name selects text width: `i8`, `i16`, or `i32`.

Text functions use the boolean `wtf` argument.

`wtf == 0` selects strict Unicode.

`wtf == 1` selects reversible surrogate-sentinel behavior.

A non-boolean `wtf` value must produce the exact `ERR_INVALID` behavior defined by the specification.

Strict mode must produce `ERR_ILLEGAL_SEQUENCE` when the source cannot be represented without loss.

WPSI 0.1 has no `ENC_*` selector.

WPSI 0.1 has no raw-string encoding mode.

## Profiles and unsupported tests

Infer required WPSI functions from the imports in the test.

A runner may report a test as `unsupported` only when the runner lacks a required WPSI representation family or Core WebAssembly feature.

`unsupported` is distinct from:

- pass;
- fail;
- expected-fail.

The catalog in [`catalog.json`](catalog.json) contains human-readable profile metadata.

The catalog does not override imports.

The conformance contract has no profile-version fields.

The conformance contract has no separate feature-query results.

Import presence and Core WebAssembly type matching are authoritative.

## Harness-driven tests

Most tests use ordinary WAST assertions.

A small number use `Test kind: harness` because they require behavior outside the standard WAST command language.

Examples include:

- process exit;
- stdout or stderr validation;
- network client interaction;
- passing a raw value between independently instantiated modules.

Harness tests still use standard WAST modules.

They also use the same operation format as `WebAssembly/wasi-testsuite`.

The catalog identifies the additional runner obligation.

The TCP and UDP echo tests use fixed loopback ports inside a fresh per-test network context.

A runner without network namespaces MUST serialize these network tests.

The runner MUST also verify that the selected ports are available before launch.

## Result classes

Reports must distinguish these result classes:

1. malformed or invalid Core WebAssembly;
2. WPSI import or link failure;
3. WPSI runtime `errno` mismatch;
4. guest trap;
5. runtime crash or timeout;
6. unsupported feature.

A crash is always a test failure.

A panic is always a test failure.

Out-of-bounds runtime memory access is always a test failure.

Leaked authority is always a test failure.

These remain failures even when the guest supplied invalid data.

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
fixtures/      external directories used by manifests
```

## Authoring requirements

A new test MUST:

- include a purpose comment;
- include a required-profile comment;
- assert one primary behavior;
- preserve sentinels around modified buffers;
- close resources that it acquires unless lifecycle is the behavior under test;
- avoid wall-clock timing assumptions when a property assertion is sufficient;
- avoid public-network dependencies;
- use exact error codes only when the WPSI specification fixes them;
- be added to `catalog.json` by the generator.

The current catalog contains **143** focused tests.

Run:

```bash
python3 spec/tests/tools/generate_suite.py --check
python3 spec/tests/tools/check_suite.py
```

When `wasm-tools` is installed, also run:

```bash
wasm-tools parse spec/imports.wat -o /tmp/facet-imports.wasm
python3 spec/tests/tools/parse_wast.py --wasm-tools wasm-tools
```
