# serial-span

Review wrapping sequence-number batches without guessing their chronology.
This offline Python CLI finds a minimum circular covering arc, explains an
undefined comparison or cycle, and identifies a largest observation subset
that fits **strictly within half the counter space**.

Useful when reviewing a finite set of counter observations for firmware,
network-protocol tests or synthetic replica-version examples. It helps catch
misuse of wrapping comparisons as an ordinary sorting comparator. No device,
DNS or network access, packet capture, automatic repair or external dependencies.

## Quickstart

Python 3.13 or 3.15, standard library only. From this repository; no install step:

```sh
python3 -B -m serial_span examples/cycle.json
```

Exact output:

```text
serial-span: 8-bit batch, 3 observations
coherent=false distinct=3 equal_pairs=0 undefined_pairs=0
minimum arc: 100 -> 0, span=156; required span < 128
comparison cycle: 0 < 100 < 200 < 0
witness records: 1, 2, 3
largest coherent subset: retain=2 exclude=1 start=0 span=100
retained records: 1, 2
excluded records: 3
Comparison model only: no chronology, wrap-count recovery or automatic repair.
```

Each displayed cycle edge follows the [RFC 1982 comparison rule](https://www.rfc-editor.org/rfc/rfc1982).
Those pairwise results cannot form one consistent batch order. Excluding one
observation makes a compatible subset; the report does **not** recommend doing so.

```sh
python3 -B -m serial_span examples/cycle.json --json --check
python3 -B -m serial_span examples/wrap.json --check
python3 -B -m serial_span examples/half.json --json --check
python3 -B -m serial_span examples/weighted.json --json
```

The first and third commands intentionally exit **1**. The wrap example
`250, 2, 6, 2` passes with span **12** and one equal pair. The half example
contains `0, 128, 0`: two observation pairs have undefined ordering. The weighted
example retains records **2, 3, 4, 5**; repeated observations count separately,
so maximizing distinct values alone would answer a different question.

Exit **0**: valid report, or `--check` with a coherent whole batch.
Exit **1**: `--check` found a batch that does not fit strictly within half a turn.
Exit **2**: invalid input/arguments, with no report on stdout.
Without `--check`, an incoherent report still exits 0.

## Input and API

```json
{"bits": 8, "serials": ["250", "2", "6", "2"]}
```

Exactly these two fields. `bits` is an integer from 2 through 64 (not a boolean).
`serials` contains 1..128 **canonical unsigned decimal strings**, each less than
2^bits. Strings preserve 64-bit precision in JSON tooling. No numeric JSON serials,
signs, leading zeros except `"0"`, whitespace, decimal points or automatic modulo
reduction. Duplicate observations are valid. Unknown fields, duplicate JSON object
keys, invalid UTF-8/BOM, non-finite JSON numbers and unsupported shapes are errors.

CLI files must be regular, at most 32 KiB and not final-component symlinks.
Use trusted stable local paths; this is not a filesystem sandbox or protection
against concurrent replacement of parent directories. The API has the same schema
and record bounds but no file-byte requirement.

```python
from serial_span import analyze

report = analyze({"bits": 8, "serials": ["250", "2", "6"]})
assert report["coherent"]
assert report["minimum_arc"]["span"] == "12"
assert report["serial_order_records"] == [1, 2, 3]
```

The API does not mutate input; invalid data raises `InputError`. JSON report
`schema_version: 1` has:

- `minimum_arc`: observed start/end and forward span; equal-span ties choose the
  numerically smallest start. Coherent means span < half_range, not <=.
- `equal_observation_pairs` and `undefined_observation_pairs`: exact counts of
  unordered input-record pairs, including multiplicity.
- `serial_order_records`: one-based source indices in compatible serial order,
  or null for incoherent input. Equal serials tie by source index, not chronology.
- `witness`: null, one half-range pair, or a three-value comparison cycle. A
  half-range pair takes priority when both kinds could exist. Pair/triangle choice
  is lexicographic by numeric serials; use the first source occurrence of each.
- `largest_coherent_subset`: retain/exclude counts and all source indices for
  one maximum-observation subset; ties choose smallest numeric observed start.
  This is one optimum, not enumeration of all optimal subsets.

Serial-sized values and distances are decimal strings in all JSON results;
small record counts, indices and bits are integers. Reports contain the supplied
serials and source indices, so use synthetic inputs when sharing. Not anonymity.

## Verification and design

```sh
python3 -B -m unittest discover -s tests -v
python3 -B scripts/check_examples.py
python3 -B scripts/check_release.py
git diff --check
```

Tests compare 4,680 ordered small batches and 300 seeded larger-ring cases with
an independently materialized finite-ring oracle. Another 100 seven-record
batches check the optimum by enumerating all 127 nonempty record subsets.
Actual CLI tests cover parser limits, 64-bit values, gate exits and local-file
rejections. Release guard negative controls cover inventory, disclosure patterns,
local links, modes, symlinks, syntax and control bytes. CI runs the same checks
on Python 3.13/3.15. Syntax parsing is not static type checking or full lint;
neither is configured. Pattern scanning is heuristic, not a security guarantee.

Read [architecture and tradeoffs](docs/architecture.md),
[research and comparison](docs/related-work.md), [agent guidance](AGENTS.md)
and [attribution](NOTICE.md). Original files use the [MIT license](LICENSE).
Independently implemented with AI assistance; no worldwide novelty, production
usage or performance claims. Machine-specific verification remains outside release.

## Limits

A coherent set does not prove that observations share an epoch, that no full wrap
was missed, that equal counters represent equal content, or that a real protocol's
loss/reordering assumptions hold. Input order is not interpreted as arrival time.
Do not mix unrelated counters, providers or streams and infer their relative age.
This is a bounded static comparison model, not a DNS checker or a sequence-extension
implementation. There is no universal newest value across arbitrary wrapping
observations. The largest subset is mathematical evidence, not operational advice.
