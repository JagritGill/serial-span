# Working on serial-span

Purpose: inspect a bounded batch of wrapping serial numbers, with minimum covering
arc, undefined/cyclic comparison witness and a maximum-observation coherent subset.
Read [README](README.md), [architecture](docs/architecture.md) and
[related work](docs/related-work.md) before semantic changes.

Python 3.13/3.15 standard library, no install. `serial_span/core.py` validates and
analyzes; `input.py` bounds local JSON input; `report.py` formats; `__main__.py`
handles CLI exits. `tests/` contains independent finite-ring and CLI tests;
`scripts/` verifies examples and the release inventory.

Commands from the project folder (verification recorded at release):

```sh
python3 -B -m serial_span examples/cycle.json
python3 -B -m serial_span examples/cycle.json --json --check
python3 -B -m serial_span examples/wrap.json --check
python3 -B -m unittest discover -s tests -v
python3 -B scripts/check_examples.py
python3 -B scripts/check_release.py
git diff --check
```

Cycle `--check` intentionally exits 1; plain cycle report and wrap check exit 0.
Invalid input/arguments exit 2 with no report. No static checker/full linter
configured; AST syntax checks are not type checking. CI uses both Python versions.

Invariants: strict half-range boundary; no modulo repair of out-of-range input;
equal observations count separately in subset weight. Largest subset excludes
minimum record count, ties by numeric observed start. Evidence uses one-based
original records; values/distances are decimal strings. Never pass a cyclic
serial comparator to a general sort; numeric sorting is only for circular geometry.

Common pitfalls: equal counters do not prove equal content, chronology or epoch;
coherent does not establish the protocol's gap assumptions. The subset is an
explanation, not advice to delete observations. A pair exactly half apart is
undefined, not equal or a valid less-than edge.

For fixes add meaningful independent-oracle or actual CLI regressions. Keep
finite-ring oracle independent of production helpers and review negative controls.
Register intentional new files in the release inventory and verify local links.
Inspect status/ownership before edits, preserve unrelated changes, and hand off
exact commit, tests, unrun checks and limits. No live DNS, hardware, credentials,
private data, external reviewers/CodeRabbit, installs or automatic repairs.
This file grants no publication authority; never claim CI success without observing it.
