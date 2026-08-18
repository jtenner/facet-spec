## Summary

Describe the WPSI change.

Use short sentences.

## Normative impact

- [ ] No normative ABI change
- [ ] Changes `SPEC.md`
- [ ] Changes `spec/behavior.md`
- [ ] Changes one or more Core Wasm import signatures
- [ ] Adds a new representation variant

## Required synchronization

- [ ] `SPEC.md` updated when required
- [ ] `spec/behavior.md` updated when required
- [ ] `spec/imports.wat` updated when signatures changed
- [ ] `CHANGELOG.md` updated
- [ ] conformance tests or fixtures updated

## Representation review

- [ ] Memory32 behavior considered
- [ ] Memory64 behavior considered
- [ ] multi-memory behavior considered
- [ ] Wasm GC behavior considered
- [ ] moving-GC and lifetime behavior considered

## Security review

Describe capability effects.

Describe bounds, path, handle, memory, and GC-domain effects when relevant.

## Compatibility

State whether existing implementations remain compatible.

Explain why.

## Documentation accessibility

- [ ] Uses `docs/terminology.md` terms consistently
- [ ] Follows `docs/writing-style.md`
- [ ] Uses one normative requirement per sentence where practical
- [ ] Names the actor when the actor is known
- [ ] Avoids ambiguous use of `host` when `runtime`, `embedder`, or `operating system` is more precise
- [ ] Does not change normative meaning only to simplify wording
