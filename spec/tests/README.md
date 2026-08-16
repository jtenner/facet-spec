# WPSI Test Suite Specification

**Status:** Draft  
**Manifest version:** 1  
**Applies to:** WPSI 0.1 conformance tests

This document defines the portable test-harness contract for the WPSI conformance suite.

The format is intentionally modeled after the existing [`WebAssembly/wasi-testsuite`](https://github.com/WebAssembly/wasi-testsuite) JSON test specification. WPSI should reuse established WASI test-runner conventions wherever they fit. A runtime that already has a WASI testsuite adapter should need as little new harness code as practical to run WPSI tests.

Contributions to the WPSI test suite are welcome. Tests should be small, deterministic, narrowly scoped, and written so that failures identify one violated contract whenever possible.

## Compatibility principle

WPSI test infrastructure follows this rule:

> Do not invent a WPSI-specific mechanism when an existing WASI testsuite convention expresses the same requirement adequately.

In particular, WPSI reuses the following WASI conventions:

- same-basename JSON test metadata;
- `args`, `env`, and `root` execution configuration;
- operation-based manifests;
- `run`, `wait`, `read`, `connect`, `send`, and `recv` operations;
- relative fixture paths;
- `.cleanup` filesystem artifacts;
- empty-by-default guest environments;
- adapter-controlled runtime invocation;
- proposal/feature declarations;
- external per-runtime skip/expected-failure policy rather than encoding runtime-specific exceptions in normative tests.

WPSI adds fields only where WPSI exposes capabilities that the WASI test manifest does not model directly, primarily multiple filesystem preopens and scratch-filesystem quotas.

## Test source format

Normative WPSI conformance tests SHOULD be authored as standard WebAssembly script files:

```text
foo.wast
```

A test MAY have a same-basename JSON manifest:

```text
foo.json
```

If no `foo.json` exists, the default manifest is used.

The `.wast` file contains WebAssembly modules and WebAssembly script assertions such as `assert_return`, `assert_trap`, `assert_invalid`, and `assert_unlinkable`. The JSON file describes only the host environment and host/test-runner interactions needed to execute the script.

Assertions that can be expressed in WAST SHOULD remain in WAST rather than being duplicated in JSON.

### Generated WAST artifacts

Tools such as `wast2json` also generate JSON. Runners that use such tools MUST place generated command JSON and generated `.wasm` modules in a build/output directory rather than beside the source test.

For example:

```text
spec/tests/gc-array/read-i32-partial.wast
spec/tests/gc-array/read-i32-partial.json

build/spec-tests/gc-array/read-i32-partial.json
build/spec-tests/gc-array/read-i32-partial.0.wasm
```

The source-side `foo.json` is always the WPSI host manifest. Generated JSON is an implementation detail of a particular WAST runner.

## Test discovery

A test executor is expected to:

1. Find all `*.wast` files beneath the requested test directory.
2. For each `foo.wast`, look for `foo.json` in the same directory.
3. Use the default manifest when no JSON file exists.
4. Remove test artifacts whose names end in `.cleanup` before the test begins.
5. Establish a fresh WPSI test-host context for the test.
6. Execute the WAST script with the configured `"wpsi"` imports.
7. Perform the manifest operations in their declared order.
8. Remove `.cleanup` artifacts after the test completes, including after failure where practical.
9. Dispose all WPSI resources and the test instance/context before beginning the next test.

Tests MUST NOT depend on state left by another test.

## Default manifest

The preferred operation-based manifest has this shape:

```json
{
  "proposals": [],
  "operations": [
    { "type": "run" },
    { "type": "wait" }
  ]
}
```

If `operations` is absent or empty, the executor MUST behave as though the two operations above were specified.

For compatibility with existing WASI test tooling, executors MAY also accept the legacy WASI-style form:

```json
{
  "args": [],
  "root": null,
  "env": {},
  "exit_code": 0,
  "stderr": "",
  "stdout": ""
}
```

New WPSI tests SHOULD use the operation-based form.

## Top-level fields

### `proposals`

```json
{
  "proposals": ["gc", "memory64", "multi-memory"]
}
```

`proposals` is an optional array of WebAssembly features that must be enabled to parse, validate, instantiate, or execute the test.

Common values include:

```text
gc
memory64
multi-memory
simd
threads
exception-handling
```

The exact feature strings accepted by an adapter are adapter-defined until a common registry is standardized. Adapters SHOULD accept the conventional WebAssembly proposal names used by their existing WASI/Core test infrastructure.

WPSI API requirements SHOULD normally be inferred from the imports used by the test rather than repeated as manifest metadata. For example, importing `wpsi.fd_read_array_i8` already establishes that the test requires WPSI GC-array support.

### `operations`

`operations` is an ordered array of host/test-runner actions.

The operation vocabulary intentionally mirrors the WASI testsuite:

```text
run
wait
read
connect
send
recv
```

WPSI-specific host configuration is carried by optional fields on `run` rather than by introducing new operations when possible.

## `run`

`run` establishes the WPSI host environment and starts execution of the test script.

```json
{
  "type": "run",
  "args": [],
  "env": {},
  "root": null
}
```

All fields are optional.

### `args`

```json
{
  "args": ["alpha", "beta"]
}
```

The values are exposed through WPSI `args_count` and `args_get` in the declared order.

Unless an adapter's existing WASI behavior requires otherwise, the runner SHOULD NOT implicitly prepend a module filename or executable name. Tests that care about a particular argument zero MUST provide it explicitly.

### `env`

```json
{
  "env": {
    "LANG": "C",
    "WPSI_TEST": "hello"
  }
}
```

The WPSI environment MUST contain exactly the specified entries and otherwise be empty.

The runner MUST NOT implicitly inherit the shell/process environment into the guest.

Environment ordering must remain stable for the lifetime of a WPSI instance as required by the WPSI specification. Tests SHOULD NOT assume a particular ordering unless the fixture itself is explicitly testing ordering behavior.

### `root`

`root` is retained with the same basic purpose as the WASI testsuite field: provision one filesystem fixture directory using a minimal manifest.

```json
{
  "type": "run",
  "root": "fixtures/basic-filesystem"
}
```

The path is relative to the directory containing the test.

For WPSI, `root` creates exactly one host-granted preopen:

- the host directory is the resolved `root` fixture directory;
- its WPSI preopen display name is `/`;
- it is returned through `fs_preopen_count` / `fs_preopen_get`;
- the adapter SHOULD grant the ordinary filesystem rights required by the test fixture unless its runtime interface requires rights to be declared explicitly.

A test needing only one ordinary preopen SHOULD prefer `root` over WPSI's extended `preopens` field. This keeps simple tests directly compatible with existing WASI testsuite concepts and minimizes adapter work.

`root: null` means no host filesystem preopen is granted.

This does **not** disable the WPSI scratch filesystem. A filesystem-enabled WPSI instance receives its private scratch filesystem independently of host preopens.

### `preopens`

`preopens` is the principal WPSI extension to WASI's `run` manifest.

It is used only when a test requires multiple preopens, distinct display names, or explicit rights.

```json
{
  "type": "run",
  "preopens": [
    {
      "host": "fixtures/input",
      "guest": "/input"
    },
    {
      "host": "fixtures/output",
      "guest": "/output",
      "rights": ["read", "write", "path-open", "path-create"]
    }
  ]
}
```

Each `host` path is relative to the test directory.

Fields:

- `host` — required fixture directory path.
- `guest` — optional WPSI preopen display name. If omitted, an adapter MAY derive a stable display name from the fixture path.
- `rights` — optional list of WPSI rights to grant.

`root` and `preopens` MUST NOT both be present in the same `run` operation.

When `rights` is omitted, the adapter SHOULD use the same default grant policy it uses for `root`.

Recommended right names correspond directly to WPSI rights:

```text
read
write
seek
tell
stat
set-size
sync
path-open
path-create
path-remove
path-rename
path-link
path-symlink
path-readlink
dir-iterate
```

Adapters MAY internally translate these strings to runtime-specific capability or preopen configuration.

### `scratch`

Every filesystem-enabled WPSI instance has a private writable scratch filesystem even when `root` and `preopens` are absent.

Most tests require no scratch manifest configuration.

Tests specifically exercising quota behavior MAY request deterministic limits:

```json
{
  "type": "run",
  "scratch": {
    "byte_quota": 1048576,
    "object_quota": 1024
  }
}
```

Both fields are optional.

An absent quota dimension means that the test does not constrain that dimension.

The scratch filesystem MUST begin logically empty for each test and MUST NOT expose files from another test, another instance, the host filesystem, or a previous execution of the same test.

### Combined example

```json
{
  "proposals": ["gc", "multi-memory"],
  "operations": [
    {
      "type": "run",
      "args": ["wpsi-test", "alpha"],
      "env": {
        "TEST_MODE": "conformance"
      },
      "root": "fixtures/files"
    },
    {
      "type": "wait",
      "exit_code": 0
    }
  ]
}
```

## `wait`

`wait` waits for the test execution to complete and validates its process-level result.

```json
{
  "type": "wait",
  "exit_code": 0
}
```

`exit_code` defaults to `0`.

A WAST script whose assertions all succeed and which does not call `proc_exit` is considered to have exit code `0` for manifest purposes.

If the guest invokes WPSI `proc_exit`, that exit code is used.

A failed WAST assertion, validation error, unexpected link error, unexpected trap, runner error, or host-adapter error fails the test independently of `exit_code`.

## `read`

`read` validates output emitted by the test.

```json
{
  "type": "read",
  "id": "stdout",
  "payload": "hello\n"
}
```

Fields:

- `id` — `stdout` or `stderr`; defaults to `stdout`.
- `payload` — expected output; defaults to the empty string.

Tests SHOULD use WAST assertions for values visible inside WebAssembly and `read` only for observable stream behavior.

## `connect`

`connect` establishes a runner-side connection to a server created by the WPSI guest.

```json
{
  "type": "connect",
  "id": "server",
  "protocol_type": "tcp"
}
```

This operation intentionally mirrors the WASI testsuite convention.

Fields:

- `id` — optional connection identifier; defaults to `server`.
- `protocol_type` — `tcp`, `udp`, or another protocol explicitly supported by the adapter.

For compatibility with the WASI testsuite, a server test MAY communicate its bound address to the runner through stdout using the conventional `<host>:<port>` form.

Tests MUST NOT require connectivity to the public Internet.

## `send`

```json
{
  "type": "send",
  "id": "server",
  "payload": "ping"
}
```

`id` must refer to a connection created by an earlier `connect` operation.

`payload` defaults to the empty string.

## `recv`

```json
{
  "type": "recv",
  "id": "server",
  "payload": "pong"
}
```

`id` must refer to a connection created by an earlier `connect` operation.

`payload` is the expected received content and defaults to the empty string.

## Operation validation

A test executor MUST validate at least the following rules before or during execution:

1. A `run` operation occurs before `read`, `connect`, `send`, or `recv`.
2. A test contains at most one active `run` execution unless a future manifest version explicitly defines multi-run semantics.
3. A `run` operation is paired with a `wait` operation.
4. `root` and `preopens` are mutually exclusive.
5. Connection IDs introduced by `connect` are unique.
6. `send` and `recv` reference a previously created connection ID.
7. Fixture paths resolve beneath the test directory; path traversal outside the test tree is rejected.
8. Unknown operation types cause a manifest validation error rather than being silently ignored.
9. Unknown WPSI-specific fields SHOULD cause a manifest validation error unless the implementation explicitly supports forward-compatible extension handling.

## Filesystem fixture rules

Fixture paths are resolved relative to the test's directory.

The runner MUST NOT mutate committed fixture files unless the test explicitly requires mutation. An implementation MAY satisfy this by copying fixtures to a temporary working directory before execution.

Tests that intentionally create temporary filesystem artifacts SHOULD name them with a `.cleanup` suffix where practical.

Runners SHOULD remove `.cleanup` artifacts before and after each test.

For tests where exact filesystem metadata matters, the test itself MUST establish the metadata it relies upon or the test manifest/specification must define it. Tests SHOULD NOT assume host-specific inode numbers, timestamp precision, ownership, permissions beyond WPSI rights, filesystem ordering, or case sensitivity unless those properties are explicitly under test.

## WPSI preopen semantics in tests

WPSI explicitly supports host-granted preopens through:

```text
fs_preopen_count()
fs_preopen_get(index)
```

The manifest provisions those preopens.

A test configured with:

```json
{
  "type": "run",
  "root": "fixtures/basic"
}
```

should observe:

```text
fs_preopen_count() == 1
fs_preopen_get(0).display_name == "/"
```

subject to successful calls and the normal `sysstr` encoding rules.

A test configured with no `root` and no `preopens` should observe zero host preopens while still being able to obtain its private scratch directory with `fs_scratch()`.

The order of `preopens` in the manifest is the order exposed by `fs_preopen_get(index)` for conformance tests.

## Scratch filesystem semantics in tests

Scratch storage is not a preopen and MUST NOT be included in `fs_preopen_count`.

The test harness MUST create a fresh scratch filesystem for each fresh WPSI instance/context.

Tests MAY rely on the following properties:

- scratch begins empty;
- scratch is writable;
- scratch is isolated from host preopens;
- scratch cannot escape to unrelated host paths;
- scratch is not shared between independent test contexts;
- configured quotas are reflected by `fs_scratch_limits` when the adapter supports deterministic quota configuration.

Tests SHOULD obtain scratch through `fs_scratch()` rather than assuming a guest path such as `/tmp`. `/tmp` is a libc compatibility convention, not part of the WPSI ABI.

## WAST assertions and host configuration

The JSON manifest provisions the environment. The WAST script defines the normative semantic assertions.

For example:

```lisp
(module
  (import "wpsi" "fs_preopen_count"
    (func $fs_preopen_count (result i32 i32)))

  (func (export "count") (result i32)
    call $fs_preopen_count
    drop)
)

(assert_return
  (invoke "count")
  (i32.const 1))
```

paired with:

```json
{
  "operations": [
    {
      "type": "run",
      "root": "fixtures/basic"
    },
    {
      "type": "wait"
    }
  ]
}
```

The same WAST script with the default manifest should expect zero preopens instead.

## Unsupported features

Unsupported features must be distinguished from conformance failures.

A runtime adapter SHOULD declare which WebAssembly proposals and WPSI import families it supports.

If a test requires a proposal or WPSI import family that an adapter explicitly declares unsupported, the runner MAY report the test as **skipped**.

If an adapter declares the feature supported and the test fails to validate, link, instantiate, or execute correctly, the result is a **failure**.

Tests MUST NOT contain runtime-name checks or runtime-specific expected behavior.

Known runtime failures and temporary skips SHOULD be maintained outside the normative test manifests, preferably using the same style of per-runtime expectation file already used by `wasi-testsuite`.

## Determinism

Normative tests MUST avoid unnecessary dependence on nondeterministic host behavior.

Tests SHOULD NOT assert:

- exact wall-clock values;
- exact random values;
- public DNS results;
- public Internet availability;
- filesystem inode values unless provided by a controlled fixture;
- host directory iteration order unless WPSI specifies the ordering;
- scheduler timing;
- platform-specific error strings.

Randomness tests should assert bounds, mutation ranges, error behavior, or other deterministic properties rather than byte values.

Clock tests should assert properties such as valid nanosecond ranges or monotonic non-regression rather than exact timestamps unless a deterministic-clock extension is explicitly configured.

Networking tests should use runner-controlled loopback peers.

## Isolation

Each test MUST execute in an isolated WPSI host context.

At minimum, independent test contexts MUST NOT accidentally share:

- WPSI handles;
- scratch filesystem contents;
- `sysstr` resources;
- directory iterators;
- poll sets;
- DNS resolver handles;
- sockets;
- runtime-private GC roots associated with WPSI calls.

A runner MAY reuse a runtime process or engine instance between tests, but it MUST preserve the observable isolation above.

## Error classification

Test runners SHOULD preserve the distinction between:

1. WebAssembly parse/validation failure;
2. WebAssembly/WPSI import linking or instantiation failure;
3. WPSI runtime `errno` results;
4. WebAssembly traps;
5. `proc_exit` termination;
6. test-runner or adapter failure.

A WPSI API misuse that the WPSI specification defines as an `errno` MUST NOT be accepted merely because the runtime trapped.

Similarly, a missing WPSI import is a link/instantiation problem, not a runtime `errno`.

## Contributor guidance

Contributions are welcome.

When adding a test:

- prefer one semantic rule per WAST file;
- use ordinary WAST assertions whenever possible;
- omit the JSON manifest when the default environment is sufficient;
- prefer `root` when one preopen is enough;
- use `preopens` only when the test genuinely needs multiple capabilities or explicit rights;
- avoid runtime-specific behavior;
- avoid public network dependencies;
- keep fixture files small;
- preserve failure atomicity checks where relevant;
- include boundary cases, zero lengths, invalid handles, stale handles, wrong GC array types, and out-of-bounds ranges when applicable;
- add regressions for every confirmed runtime bug that can be expressed portably.

Generated test matrices are welcome when they produce readable, narrowly named WAST cases and make their generation deterministic and reproducible.

## Example directory layout

```text
spec/tests/
├── README.md
├── core/
│   └── abi-version.wast
├── filesystem/
│   ├── preopen-root.wast
│   ├── preopen-root.json
│   └── fixtures/
│       └── basic/
│           └── hello.txt
├── multimemory/
│   └── read-memory-1.wast
├── gc-array/
│   ├── read-i8-basic.wast
│   ├── read-i16-partial.wast
│   ├── read-i32-partial.wast
│   └── read-v128-partial.wast
├── text/
│   ├── utf8.wast
│   ├── utf16.wast
│   └── utf32.wast
└── network/
    ├── tcp-echo.wast
    └── tcp-echo.json
```

## Relationship to the WASI testsuite

The WPSI manifest is deliberately a small compatibility-oriented extension of the WASI testsuite's operation-based JSON specification.

A WASI-oriented test runner should be able to reuse substantial infrastructure for:

- test discovery;
- manifest parsing;
- arguments;
- environment variables;
- single-root preopens;
- stdout/stderr capture;
- process exit handling;
- TCP/UDP runner interactions;
- fixture cleanup;
- runtime adapters;
- per-runtime expectations.

The primary WPSI-specific runner work should be:

1. supplying the `"wpsi"` import module;
2. executing WAST scripts rather than only standalone `_start`-style programs;
3. exposing multiple preopens when `preopens` is used;
4. configuring WPSI scratch quotas when requested;
5. enabling modern Core Wasm features such as GC, multi-memory, Memory64, and SIMD;
6. correctly transporting WPSI GC-array references through host calls.

This compatibility is intentional. Lower adoption cost is part of the WPSI test-suite design.