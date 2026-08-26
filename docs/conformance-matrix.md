# Facet runtime conformance matrix

**Last updated:** August 26, 2026  
**Facet version:** 0.1

This matrix records complete published executions of the normative Facet conformance suite.

A passing entry requires:

- all 261 canonical imports to match the public ABI inventory;
- the complete canonical import module to compile and instantiate;
- all 137 standard WAST tests to pass;
- all 6 harness-driven tests to pass;
- zero crashes;
- zero timeouts.

## Published results

| Implementation | Runtime | Platform | Standard WAST | Harness | Total | Moving-GC standard suite | Differential representations | Result |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| [`wago-facet` v0.1.0](https://github.com/jtenner/wago-facet/releases/tag/v0.1.0) | Wago `cb32e996cf3f` | Linux amd64 | 137/137 | 6/6 | 143/143 | 137/137 | Memory32, Memory64, GC array | Pass |
| [`wago-facet` v0.1.0](https://github.com/jtenner/wago-facet/releases/tag/v0.1.0) | Wago `cb32e996cf3f` | Linux arm64 | 137/137 | 6/6 | 143/143 | 137/137 | Memory32, Memory64, GC array | Pass |

The published `wago-facet` release pins Facet specification commit `c3d06ad1b3e7f8ad6b83ecb4e96e999c922b5140`.

The moving-GC gate forces Wago's moving nursery to collect on every Wasm GC allocation. It enables root verification, poisoned freed storage, and barrier stress.

The differential integration test transfers one deterministic argument through Memory32, Memory64, and a mutable Wasm GC `array<i8>`. It requires identical lengths, errors, and bytes for all three representations under both the default collector and moving-GC stress.

## Scope

The matrix records observable Facet behavior. It does not claim that every import has a distinct non-empty behavioral scenario.

Source-level WAST coverage separately requires every canonical import to be declared with its exact signature and directly invoked by at least one WAST module.

The Wago implementation also validates exact structural GC-reference imports before guest code starts.

## Known runtime boundaries

The passing results use Wago's current per-instance public-call serialization.

DNS resolution has a finite 30-second deadline and plugin-shutdown cancellation. Immediate propagation of active guest-call cancellation depends on a future Wago callback-context API.

These boundaries do not change the passing Facet 0.1 result. They are tracked as implementation follow-up work in the `wago-facet` repository.
