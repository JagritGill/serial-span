# Related work and provenance

Research for the November 22, 2026 catch-up build completed before project code.
Queries included `RFC 1982 serial number arithmetic set ordering cycle analyzer`,
`sequence number wraparound ambiguity visualizer half range tool`,
`RFC 1982 Python serial arithmetic github wraparound library`,
`Rust serial number arithmetic crate wraparound sequence comparison`, and
`DNS serial number comparison calculator online`. The local catalog and public
personal repository names/descriptions were checked. No duplicate was identified;
that is not proof of worldwide name availability or idea uniqueness.

## Closest documented tools

- [serial-num](https://github.com/timwie/serial-num) is a Rust serial-number type
  with wraparound and RFC 1982 context. Substantial overlap: bounded serial
  representation and comparison. Our tool audits a supplied batch, emitting a
  global covering arc, an inconsistency witness and a maximum-size compatible
  observation subset; it is not a replacement arithmetic type.
- [serial-uint](https://docs.rs/serial-uint/latest/serial_uint/) documents generic
  wraparound arithmetic and an undefined comparison at exactly half a cycle.
  Search also surfaced source snippets discussing non-transitivity. No snippets,
  implementation or tests were copied. Documentation/source versions can differ;
  this comparison does not assert a particular current Rust trait contract.
- [Twisted SerialNumber](https://docs.twisted.org/en/stable/api/twisted.names._rfc1982.SerialNumber.html)
  documents DNS serial arithmetic. It is another established library-level
  comparator, not the batch-review workflow designed here. We do not import it.
- [stack127 SOA Consistency Checker](https://stack127.com/soa-checker) compares
  live authoritative-server SOA records using wrapping serial arithmetic.
  This is close practical overlap in judging several serial observations.
  serial-span instead reads synthetic/local inputs, supports explicit 2..64-bit
  spaces, and reports batch ambiguity/cycles and a largest half-range subset.
  No DNS requests or use of that service occurred.
- [DNS SOA Serial Number Calculator](https://thehomeserverblog.com/dns-soa-serial-number-calculator/)
  plans next serials and refresh timing. We neither plan live changes nor infer
  propagation, chronology, data equality or safety from matching serials.

These are documentation comparisons, not exhaustive inventories or claims that
other tools cannot provide related analyses. No source repository was cloned.

## Semantics, practical distinction and attribution

[RFC 1982](https://www.rfc-editor.org/rfc/rfc1982) is the primary comparison
reference: a forward distance below half the power-of-two space means precedes;
exactly half is undefined. Repeated valid increments do not create a globally
transitive ordering over all observations. Arithmetic and circular covering-arc
ideas are established, not new algorithms.

The demo has 8-bit observations 0, 100, 200: each selected forward comparison is
valid, but they form a cycle. A separate wrap example 250, 2, 6 is consistent.
A half-range example distinguishes undefined pair ordering from a comparison
cycle. Largest-subset evidence shows which original record numbers fit together;
it is a review aid, not advice to discard observations or change counters.

[RFC 9187](https://datatracker.ietf.org/doc/rfc9187/) discusses sequence extension
and its gap/reordering assumptions. This project does not extend sequences or
recover wrap counts; an apparently coherent batch cannot establish true age.

Implementation, synthetic fixtures and tests are independently written with AI
assistance. Runtime is Python standard library; no competitor dependency or
vendored code. Routine portfolio release/CI conventions are reused with credit in
[NOTICE](../NOTICE.md). See [architecture](architecture.md) for exact scope and
[README](../README.md) for runnable examples and honest limits.
