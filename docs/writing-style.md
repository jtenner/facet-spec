# Documentation Style Guide

This guide applies to human-facing specification text in this repository.

The goal is simple: a developer should not need advanced English or deep systems knowledge to understand a requirement correctly.

The guide takes ideas from controlled technical English, including ASD-STE100, but this project does not claim formal ASD-STE100 certification.

## Core rules

1. Use one requirement or one main idea per sentence.
2. Prefer short sentences.
3. Name the actor when the actor is known.
4. Prefer active voice.
5. Use one term for one concept.
6. Define technical terms before they are required for understanding.
7. Keep necessary technical terms. Simplify the English around them.
8. Put the normal rule before exceptions.
9. Use examples when an example is clearer than another paragraph.
10. Do not change normative meaning to make a sentence shorter.

## Normative language

The words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** have normative meaning in the specification.

Do not replace these words with weaker alternatives during an editorial rewrite.

Prefer one normative statement per sentence.

Good:

> The runtime MUST validate the handle before use.
>
> The runtime MUST return `ERR_BAD_HANDLE` when the handle is stale.

Avoid:

> The handle must be validated before use and stale handles must return `ERR_BAD_HANDLE` while invalid resource kinds are also rejected.

## Name the actor

Use the project terminology in [`terminology.md`](terminology.md).

Prefer:

> The runtime MUST validate the memory index.

Avoid:

> The memory index MUST be validated.

Use passive voice only when the actor is unknown or not relevant.

## Keep sentences small

Split a sentence when it contains more than one independent rule, condition, result, or exception.

Prefer:

> The operation returns `ERR_RANGE` when the buffer is too small.
>
> The operation MUST NOT modify the destination in this case.

Avoid:

> When the buffer is too small, the operation returns `ERR_RANGE` and must not modify the destination, while the source position also remains unchanged for stateful sources.

## Use lists for sets of conditions

Use a list when a sentence would otherwise contain a long series of requirements.

Prefer:

> The runtime MUST validate all selected child arrays before I/O begins.
>
> Validation includes:
> - a non-null child reference;
> - the element storage type;
> - destination mutability for a read.

## Explain difficult rules

For difficult concepts, use this order when practical:

1. **Rule** — state the normative behavior.
2. **Explanation** — explain why the rule exists.
3. **Example** — show a concrete case.

The explanation and example MUST NOT add new normative requirements unless they use normative language explicitly.

## Use technical terms consistently

Do not use several words for the same actor or concept.

In particular:

- use **guest** for the WebAssembly module that calls the interface;
- use **runtime** for the implementation of imported system functions;
- use **embedder** for the software that creates an instance and grants authority;
- use **operating system** when the text specifically means the external operating system;
- avoid **host** when one of the terms above is more precise.

The word `host` can remain in established names, quoted external terminology, and code identifiers.

## Avoid compressed wording

Avoid slash compounds when ordinary words are clearer.

Prefer:

> filesystem and network authority

Avoid:

> filesystem/network authority

Prefer:

> reads and writes

Avoid:

> read/write behavior

## Define abbreviations

Define an abbreviation the first time it appears in explanatory prose unless it is a Core WebAssembly token or an API identifier that is shown as code.

Examples of project terms that can remain as technical terms include:

- ABI;
- DNS;
- EOF;
- GC;
- I/O;
- UTF-8, UTF-16, and UTF-32;
- WASI;
- WebAssembly value types such as `i32`, `i64`, and `v128`.

## Procedures

Use direct commands in procedures.

Prefer:

> Run the conformance checker.

Avoid:

> The conformance checker should be run.

Keep one action per numbered step when practical.

## Tables

Use tables for compact reference information.

Do not put a long explanation, multiple exceptions, and compatibility notes into one table cell. Move complex behavior into a subsection and keep the table entry short.

## Code and API names

Do not simplify code identifiers.

Keep exact function names, constants, WebAssembly types, import names, and error names.

Use backticks around identifiers in prose.

## Editorial review checklist

Before merging a documentation change, check that:

- each normative sentence has one clear requirement;
- the actor is clear;
- terms match `docs/terminology.md`;
- no sentence weakens or strengthens an existing normative rule by accident;
- examples match the normative text;
- new jargon is defined;
- unnecessary passive voice is removed;
- long lists are formatted as lists;
- semicolons do not hide separate requirements;
- the text is understandable without knowledge that exists only in an issue, pull request, or implementation.
