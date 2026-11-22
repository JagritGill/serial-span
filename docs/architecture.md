# Architecture and tradeoffs

[core.py](../serial_span/core.py) owns strict validation and pure analysis.
[input.py](../serial_span/input.py) loads one bounded local JSON file;
[report.py](../serial_span/report.py) formats the same report consumed by
[the CLI](../serial_span/__main__.py). No input commands, plugins, code evaluation
or network operations. [Core tests](../tests/test_core.py) independently enumerate
finite rings and record subsets; [CLI tests](../tests/test_cli.py) use subprocesses
on synthetic inputs. [Release checks](../scripts/check_release.py) verify the exact
inventory and local Markdown file links.

## Model and algorithms

For width b, M=2^b and H=M/2. A distinct value a precedes c exactly when its
forward distance to c is between 1 and H-1. At distance H, ordering is undefined.
Equal observations are equal in this arithmetic only. Values are numeric integers
internally; JSON serials/distances remain strings for portable exactness.

1. Group original record indices by equal numeric value; sort distinct values
   numerically for circular geometry, never with the wrapping comparator.
2. Inspect empty gaps between consecutive circular values. The complement of a
   largest gap is a shortest covering arc. With one distinct value the gap is M
   and span zero. Equal spans choose the smallest numeric observed start.
3. A span strictly less than H yields a consistent increasing serial order over
   this finite batch. At or above H, no such containing arc exists.
4. Count all observation pairs separated by H, multiplying group sizes. If any
   exist, emit the smallest numeric pair with each first original occurrence.
5. Otherwise an incoherent distinct set is a non-transitive tournament: each
   pair has one direction, but no consistent order. It contains a directed
   triangle. Check numeric triples in lexicographic order and emit the first
   whose three circular forward steps are each below H. No triangle count claimed.
6. For every observed start, collect all observations less than H forward from
   it. Select the candidate with most observations, ties by numeric start.
   Return all retained/excluded original records and their exact arc span.

Why the subset is maximal in size: every compatible nonempty subset has an
observed first value. Its members must lie in that value's strict half window.
Including every other observation in that same window cannot invalidate it.
Checking every observed start therefore includes an optimum. Repeated observations
are weights; no group is partially discarded. This is minimum excluded record
count under the stated model, not a causal diagnosis of which observations are wrong.

The subset tie-break is independent of minimum covering arc tie-break. We report
one optimum, not every optimum or a minimum-span optimum among all equal sizes.
If the full batch is coherent, its order includes duplicates tied by source index.
For incoherent input no total order is fabricated, even if a subset is large.

## Bounds and design choices

At most 128 observations and 64-bit counters; 32 KiB CLI input. Straightforward
window enumeration is O(n^2); the uncommon triangle search is O(u^3) worst case,
where u is distinct values. Stored groups/output are O(n), with O(u) arc candidates.
Small hard bounds favor simple auditable code over a more elaborate sweep or graph
algorithm. No runtime benchmark or production-scale claim. File loading checks
the opened descriptor is regular and bounds the read even if its size changes;
this is not a promise of an atomic snapshot or safe hostile path traversal.

Serial arithmetic and covering-arc reasoning are established concepts. The tool's
contribution is a compact reproducible batch report with witnesses and weighted
subset evidence. See [related work](related-work.md). No epoch/arrival-time data,
wrap extension, DNS semantics, protocol retransmission, clock inference or hardware.

## Verification boundaries

The finite-ring oracle rotates every possible integer cut, not just observed
gaps, and materializes each half window. Exhaustive removal separately verifies
the maximum subset size. Witness edges are checked with literal RFC inequalities.
Tests cover singleton/all-equal input, wrap boundaries, exact half distance,
triangle cycles, duplicate weights, tie rules, 64-bit precision and invalid data.
These finite cases support the implementation, not real-world chronological claims.
